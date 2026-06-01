package de.tuda.stg.securecoder.engine.workflow

import de.tuda.stg.securecoder.engine.Engine
import de.tuda.stg.securecoder.engine.Engine.Context
import de.tuda.stg.securecoder.engine.Engine.EngineResult
import de.tuda.stg.securecoder.engine.llm.ChatMessage
import de.tuda.stg.securecoder.engine.llm.ChatMessage.Role
import de.tuda.stg.securecoder.engine.file.FilesInContextPromptBuilder
import de.tuda.stg.securecoder.engine.file.edit.ApplyChanges.applyEdits
import de.tuda.stg.securecoder.engine.file.edit.Changes
import de.tuda.stg.securecoder.engine.file.edit.EditFormat
import de.tuda.stg.securecoder.engine.file.edit.EditFormatHandler
import de.tuda.stg.securecoder.engine.file.edit.EditModeFactory
import de.tuda.stg.securecoder.engine.file.edit.ReviewMode
import de.tuda.stg.securecoder.engine.guardian.SourceTextNormalizer
import de.tuda.stg.securecoder.engine.llm.LlmClient
import de.tuda.stg.securecoder.engine.stream.StreamEvent
import de.tuda.stg.securecoder.engine.stream.ProposalId
import de.tuda.stg.securecoder.enricher.PromptEnricher
import de.tuda.stg.securecoder.filesystem.FileSystem
import de.tuda.stg.securecoder.filesystem.InMemoryFileSystem
import de.tuda.stg.securecoder.guardian.Guardian
import kotlinx.coroutines.flow.toList
import java.util.UUID

class WorkflowEngine (
    enricher: PromptEnricher,
    private val llmClient: LlmClient,
    guardians: List<Guardian> = emptyList(),
    private val editFormat: EditFormat = EditFormat.STRUCTURED_JSON,
    private val reviewMode: ReviewMode = ReviewMode.PATCH,
    private val guardianRetryPolicy: GuardianRetryPolicy = GuardianRetryPolicy(),
    private val parseChangesAttempts: Int = 5,
    private val selfTestLoop: SelfTestLoop = SelfTestLoop(llmClient),
    private val traceLogger: WorkflowTraceLogger = WorkflowTraceLogger.NO_OP,
    private val preferWholeFileOnEmptyContext: Boolean = true,
    private val freshGenerationRecoveryAttempts: Int = 1,
) : Engine {
    private val promptEnrichRunner = PromptEnrichRunner(enricher)
    private val editFiles: EditFormatHandler = EditModeFactory.create(editFormat, llmClient)
    private val wholeFileEditFiles: EditFormatHandler = EditModeFactory.create(EditFormat.WHOLE_FILE_JSON, llmClient)
    private val guardianExecutor = GuardianExecutor(guardians)
    private val guardianRetryDecider = GuardianRetryDecider(llmClient)

    override suspend fun run(
        prompt: String,
        filesystem: FileSystem,
        onEvent: suspend (StreamEvent) -> Unit,
        context: Context?,
    ): EngineResult {
        val runId = UUID.randomUUID().toString()
        val filesInContext = resolveContext(context, filesystem)
        val originalFiles = loadContentsByName(filesystem)
        val originalSnapshot = snapshot(filesystem)
        var workingFileSystem = snapshot(filesystem)
        val enrichedPrompt = promptEnrichRunner.enrichPrompt(onEvent, filesInContext, prompt)
        val selectedEditFiles = selectEditHandler(filesInContext, enrichedPrompt)
        val messages = mutableListOf(
            ChatMessage(Role.System, "You are a Security Engineering Agent mainly for writing secure code"),
            ChatMessage(Role.User, enrichedPrompt),
            ChatMessage(Role.User, FilesInContextPromptBuilder.build(filesInContext, edit = true)),
        )
        val baseMessages = messages.toList()
        traceLogger.log(
            WorkflowTraceRecord(
                runId = runId,
                type = "run_started",
                format = selectedEditFiles.formatId,
                reviewMode = reviewMode.name.lowercase(),
                messages = messages.toTraceMessages(),
            )
        )
        val guardianHistory = mutableListOf<GuardianRetryDecider.AttemptSummary>()
        repeat(guardianRetryPolicy.hardLimit) {
            val attempt = it + 1
            val initialOut = selectedEditFiles.chat(
                messages = messages,
                fileSystem = workingFileSystem,
                onParseError = { parseErrors, chatExchange ->
                    traceLogger.log(
                        WorkflowTraceRecord(
                            runId = runId,
                            type = "parse_error",
                            format = selectedEditFiles.formatId,
                            reviewMode = reviewMode.name.lowercase(),
                            attempt = attempt,
                            phase = "proposal",
                            messages = chatExchange.input.toTraceMessages(),
                            text = chatExchange.output,
                            errors = parseErrors,
                        )
                    )
                    onEvent(StreamEvent.InvalidLlmOutputWarning(parseErrors, chatExchange))
                },
                attempts = parseChangesAttempts
            )
            val out = if (initialOut.changes != null) {
                initialOut
            } else {
                tryFreshGenerationRecovery(
                    runId = runId,
                    selectedEditFiles = selectedEditFiles,
                    baseMessages = baseMessages,
                    fileSystem = workingFileSystem,
                    attempt = attempt,
                    onEvent = onEvent,
                ) ?: initialOut
            }
            traceLogger.log(
                WorkflowTraceRecord(
                    runId = runId,
                    type = "proposal_exchange",
                    format = selectedEditFiles.formatId,
                    reviewMode = reviewMode.name.lowercase(),
                    attempt = attempt,
                    phase = "proposal",
                    messages = messages.toTraceMessages(),
                    text = out.messages.lastOrNull()?.content,
                )
            )
            val changes = out.changes ?: run {
                traceLogger.log(
                    WorkflowTraceRecord(
                        runId = runId,
                        type = "result",
                        format = selectedEditFiles.formatId,
                        reviewMode = reviewMode.name.lowercase(),
                        text = "generation_failure",
                    )
                )
                return EngineResult.Failure.GenerationFailure
            }
            val normalizedChanges = normalizeRetryAppends(
                changes = changes,
                originalFiles = originalFiles,
                workingFileSystem = workingFileSystem,
            )
            val normalizedCandidateChanges = normalizeCandidateSource(
                baseFileSystem = workingFileSystem,
                changes = normalizedChanges,
            )
            messages += out.changesMessage()
            val proposalId = ProposalId.newId()
            traceLogger.log(
                WorkflowTraceRecord(
                    runId = runId,
                    type = "event",
                    format = selectedEditFiles.formatId,
                    reviewMode = reviewMode.name.lowercase(),
                    attempt = attempt,
                    text = StreamEvent.ProposedEdits(proposalId, normalizedCandidateChanges).describe(),
                )
            )
            onEvent(StreamEvent.ProposedEdits(proposalId, normalizedCandidateChanges))
            when (val selfTestResult = selfTestLoop.run(
                originalPrompt = enrichedPrompt,
                candidateFileSystem = materializeCandidate(workingFileSystem, normalizedCandidateChanges),
                changedFiles = normalizedCandidateChanges.searchReplaces.map { it.fileName }.distinct(),
            )) {
                is SelfTestLoop.Outcome.Passed,
                is SelfTestLoop.Outcome.Skipped -> Unit
                is SelfTestLoop.Outcome.Failed -> {
                    traceLogger.log(
                        WorkflowTraceRecord(
                        runId = runId,
                        type = "self_test_failure",
                        format = selectedEditFiles.formatId,
                            reviewMode = reviewMode.name.lowercase(),
                            attempt = attempt,
                            text = selfTestResult.feedback,
                        )
                    )
                    if (reviewMode == ReviewMode.PATCH) {
                        workingFileSystem.applyEdits(normalizedCandidateChanges.searchReplaces)
                    } else {
                        workingFileSystem = snapshot(originalSnapshot)
                    }
                    messages += ChatMessage(Role.User, selfTestResult.feedback)
                    return@repeat
                }
            }
            onEvent(StreamEvent.ValidationStarted(proposalId))
            val guardianResult = guardianExecutor.analyze(workingFileSystem, normalizedCandidateChanges)
            if (guardianResult.failures.isNotEmpty()) {
                traceLogger.log(
                    WorkflowTraceRecord(
                        runId = runId,
                        type = "result",
                        format = selectedEditFiles.formatId,
                        reviewMode = reviewMode.name.lowercase(),
                        attempt = attempt,
                        text = "guardian_failure",
                        errors = guardianResult.failures.map { "${it.guardian}:${it.message}" },
                    )
                )
                return EngineResult.Failure.GenerationFailure
            }
            if (guardianResult.hasNoViolations()) {
                workingFileSystem.applyEdits(normalizedCandidateChanges.searchReplaces)
                traceLogger.log(
                    WorkflowTraceRecord(
                        runId = runId,
                        type = "event",
                        format = selectedEditFiles.formatId,
                        reviewMode = reviewMode.name.lowercase(),
                        attempt = attempt,
                        text = StreamEvent.ValidationSucceeded(proposalId).describe(),
                    )
                )
                onEvent(StreamEvent.ValidationSucceeded(proposalId))
                traceLogger.log(
                    WorkflowTraceRecord(
                        runId = runId,
                        type = "result",
                        format = selectedEditFiles.formatId,
                        reviewMode = reviewMode.name.lowercase(),
                        text = "success",
                    )
                )
                return EngineResult.Success(materializeChanges(filesystem, workingFileSystem))
            }
            guardianHistory += GuardianRetryDecider.AttemptSummary.from(attempt, guardianResult.violations)
            if (guardianResult.hasBlockingHardReject()) {
                traceLogger.log(
                    WorkflowTraceRecord(
                        runId = runId,
                        type = "result",
                        format = selectedEditFiles.formatId,
                        reviewMode = reviewMode.name.lowercase(),
                        attempt = attempt,
                        text = "hard_reject",
                        errors = guardianResult.violations
                            .filter { it.hardReject == true }
                            .map { "${it.rule.id}:${it.message}" },
                    )
                )
                return EngineResult.Failure.ValidationFailure(
                    retryPolicy = guardianRetryPolicy,
                    attemptsUsed = attempt,
                    reason = "hard_reject",
                )
            }
            val retryDecision = guardianRetryDecider.review(
                policy = guardianRetryPolicy,
                attempt = attempt,
                history = guardianHistory,
            )
            if (retryDecision != null) {
                traceLogger.log(
                    WorkflowTraceRecord(
                        runId = runId,
                        type = "retry_review",
                        format = selectedEditFiles.formatId,
                        reviewMode = reviewMode.name.lowercase(),
                        attempt = attempt,
                        text = retryDecision.rationale ?: "shouldContinue=${retryDecision.shouldContinue}, upgradeToHardReject=${retryDecision.upgradeToHardReject}",
                    )
                )
            }
            if (retryDecision?.upgradeToHardReject == true) {
                traceLogger.log(
                    WorkflowTraceRecord(
                        runId = runId,
                        type = "result",
                        format = selectedEditFiles.formatId,
                        reviewMode = reviewMode.name.lowercase(),
                        attempt = attempt,
                        text = "meta_hard_reject",
                    )
                )
                return EngineResult.Failure.ValidationFailure(
                    retryPolicy = guardianRetryPolicy,
                    attemptsUsed = attempt,
                    reason = "meta_hard_reject",
                )
            }
            if (retryDecision?.shouldContinue == false) {
                traceLogger.log(
                    WorkflowTraceRecord(
                        runId = runId,
                        type = "result",
                        format = selectedEditFiles.formatId,
                        reviewMode = reviewMode.name.lowercase(),
                        attempt = attempt,
                        text = "no_progress",
                    )
                )
                return EngineResult.Failure.ValidationFailure(
                    retryPolicy = guardianRetryPolicy,
                    attemptsUsed = attempt,
                    reason = "no_progress",
                )
            }
            if (reviewMode == ReviewMode.PATCH) {
                workingFileSystem.applyEdits(normalizedCandidateChanges.searchReplaces)
            } else {
                workingFileSystem = snapshot(originalSnapshot)
            }
            traceLogger.log(
                WorkflowTraceRecord(
                        runId = runId,
                        type = "guardian_warning",
                        format = selectedEditFiles.formatId,
                    reviewMode = reviewMode.name.lowercase(),
                    attempt = attempt,
                    errors = guardianResult.violations.map { "${it.rule.id}:${it.message}" } + guardianResult.failures.map { "${it.guardian}:${it.message}" },
                )
            )
            onEvent(StreamEvent.GuardianWarning(proposalId, guardianResult))
            messages += ChatMessage(Role.User, selectedEditFiles.buildGuardianFeedback(guardianResult, reviewMode))
        }
        traceLogger.log(
            WorkflowTraceRecord(
                runId = runId,
                type = "result",
                format = selectedEditFiles.formatId,
                reviewMode = reviewMode.name.lowercase(),
                text = "validation_failure",
            )
        )
        return EngineResult.Failure.ValidationFailure(
            retryPolicy = guardianRetryPolicy,
            attemptsUsed = guardianRetryPolicy.hardLimit,
            reason = "hard_limit_exhausted",
        )
    }

    private suspend fun tryFreshGenerationRecovery(
        runId: String,
        selectedEditFiles: EditFormatHandler,
        baseMessages: List<ChatMessage>,
        fileSystem: FileSystem,
        attempt: Int,
        onEvent: suspend (StreamEvent) -> Unit,
    ): EditFormatHandler.ChatResult? {
        if (freshGenerationRecoveryAttempts <= 0) return null
        repeat(freshGenerationRecoveryAttempts) { recoveryAttempt ->
            val recoveryPrompt = ChatMessage(
                Role.User,
                """
                Start over from scratch.
                Your previous attempts did not produce a valid edit payload for the required schema.
                Ignore prior invalid outputs and respond again with ONLY the required ${selectedEditFiles.formatId} JSON object.
                """.trimIndent(),
            )
            val recoveryMessages = baseMessages + recoveryPrompt
            val recovery = selectedEditFiles.chat(
                messages = recoveryMessages,
                fileSystem = fileSystem,
                onParseError = { parseErrors, chatExchange ->
                    traceLogger.log(
                        WorkflowTraceRecord(
                            runId = runId,
                            type = "parse_error",
                            format = selectedEditFiles.formatId,
                            reviewMode = reviewMode.name.lowercase(),
                            attempt = attempt,
                            phase = "fresh_recovery_${recoveryAttempt + 1}",
                            messages = chatExchange.input.toTraceMessages(),
                            text = chatExchange.output,
                            errors = parseErrors,
                        )
                    )
                    onEvent(StreamEvent.InvalidLlmOutputWarning(parseErrors, chatExchange))
                },
                attempts = parseChangesAttempts,
            )
            traceLogger.log(
                WorkflowTraceRecord(
                    runId = runId,
                    type = "proposal_exchange",
                    format = selectedEditFiles.formatId,
                    reviewMode = reviewMode.name.lowercase(),
                    attempt = attempt,
                    phase = "fresh_recovery_${recoveryAttempt + 1}",
                    messages = recoveryMessages.toTraceMessages(),
                    text = recovery.messages.lastOrNull()?.content,
                )
            )
            if (recovery.changes != null) {
                return recovery
            }
        }
        return null
    }

    private fun selectEditHandler(filesInContext: List<FileSystem.File>, prompt: String): EditFormatHandler {
        if (!preferWholeFileOnEmptyContext) return editFiles
        if (editFormat != EditFormat.STRUCTURED_JSON) return editFiles
        if (filesInContext.isNotEmpty()) return editFiles
        if (!prompt.contains("only create one file", ignoreCase = true)) return editFiles
        return wholeFileEditFiles
    }

    private suspend fun snapshot(fileSystem: FileSystem): InMemoryFileSystem {
        val copy = InMemoryFileSystem()
        fileSystem.allFiles().toList().forEach { file ->
            copy.upsert(file.name(), file.content())
        }
        return copy
    }

    private suspend fun normalizeRetryAppends(
        changes: Changes,
        originalFiles: Map<String, String>,
        workingFileSystem: FileSystem,
    ): Changes {
        val normalized = changes.searchReplaces.map { edit ->
            if (!edit.isAppend() || originalFiles.containsKey(edit.fileName)) {
                return@map edit
            }
            val currentContent = workingFileSystem.getFile(edit.fileName)?.content() ?: return@map edit
            Changes.SearchReplace(
                fileName = edit.fileName,
                searchedText = Changes.SearchedText(currentContent),
                replaceText = edit.replaceText,
            )
        }
        return Changes(normalized)
    }

    private suspend fun normalizeCandidateSource(
        baseFileSystem: FileSystem,
        changes: Changes,
    ): Changes {
        val candidate = materializeCandidate(baseFileSystem, changes)
        changes.searchReplaces
            .map { it.fileName }
            .distinct()
            .forEach { fileName ->
                val content = candidate.getFile(fileName)?.content() ?: return@forEach
                val normalized = SourceTextNormalizer.normalize(fileName, content)
                if (normalized != content) {
                    candidate.upsert(fileName, normalized)
                }
        }
        return materializeChanges(baseFileSystem, candidate)
    }

    private suspend fun materializeCandidate(
        baseFileSystem: FileSystem,
        changes: Changes,
    ): InMemoryFileSystem {
        val candidate = snapshot(baseFileSystem)
        candidate.applyEdits(changes.searchReplaces)
        return candidate
    }

    private suspend fun materializeChanges(original: FileSystem, current: FileSystem): Changes {
        val originalFiles = loadContentsByName(original)
        val currentFiles = loadContentsByName(current)
        val changedFiles = linkedSetOf<String>()
        changedFiles += originalFiles.keys
        changedFiles += currentFiles.keys
        val searchReplaces = changedFiles.mapNotNull { fileName ->
            val originalContent = originalFiles[fileName]
            val currentContent = currentFiles[fileName]
            if (originalContent == currentContent) {
                null
            } else {
                Changes.SearchReplace(
                    fileName = fileName,
                    searchedText = Changes.SearchedText(originalContent ?: ""),
                    replaceText = currentContent ?: "",
                )
            }
        }
        return Changes(searchReplaces)
    }

    private suspend fun loadContentsByName(fileSystem: FileSystem): Map<String, String> {
        val contents = linkedMapOf<String, String>()
        fileSystem.allFiles().toList().forEach { file ->
            contents[file.name()] = file.content()
        }
        return contents
    }
}
