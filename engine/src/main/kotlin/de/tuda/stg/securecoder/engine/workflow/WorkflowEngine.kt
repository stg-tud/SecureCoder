package de.tuda.stg.securecoder.engine.workflow

import de.tuda.stg.securecoder.engine.Engine
import de.tuda.stg.securecoder.engine.file.FileSystem
import de.tuda.stg.securecoder.engine.file.edit.Changes
import de.tuda.stg.securecoder.engine.llm.ChatMessage
import de.tuda.stg.securecoder.engine.llm.ChatMessage.Role
import de.tuda.stg.securecoder.engine.file.edit.EditFilesLlmWrapper
import de.tuda.stg.securecoder.engine.llm.FilesInContextPromptBuilder
import de.tuda.stg.securecoder.engine.llm.LlmClient
import de.tuda.stg.securecoder.engine.stream.EventIcon
import de.tuda.stg.securecoder.engine.stream.StreamEvent
import de.tuda.stg.securecoder.enricher.EnrichFileForContext
import de.tuda.stg.securecoder.enricher.EnrichRequest
import de.tuda.stg.securecoder.enricher.PromptEnricher
import de.tuda.stg.securecoder.guardian.Guardian
import kotlinx.coroutines.async
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.supervisorScope
import kotlinx.coroutines.withTimeoutOrNull
import kotlin.time.TimeSource.Monotonic

class WorkflowEngine (
    val enricher: PromptEnricher,
    llmClient: LlmClient,
    guardians: List<Guardian> = emptyList(),
) : Engine {
    private val editFiles = EditFilesLlmWrapper(llmClient)
    private val guardianExecutor = GuardianExecutor(guardians)

    override suspend fun start(
        prompt: String,
        filesystem: FileSystem,
        onEvent: suspend (StreamEvent) -> Unit,
    ) {
        val files = filesystem.allFiles().toList()
        val enrichedPrompt = enrichPrompt(onEvent, files, prompt)
        val out = editFiles.chat(
            listOf(
                ChatMessage(Role.System, "You are a Security Engineering Agent mainly for writing secure code"),
                ChatMessage(Role.User, enrichedPrompt),
                ChatMessage(Role.System, FilesInContextPromptBuilder.build(files, edit = true)),
            ),
            filesystem,
            onParseError = {
                onEvent(StreamEvent.Message(
                    "Malicious LLM output",
                    it.joinToString(),
                    EventIcon.Warning
                ))
            },
        )
        when (out) {
            null -> onEvent(StreamEvent.Message(
                "Failed generating changeset",
                "Failed to parse the output of the llm. Maximum amount on retries exceeded! Look for parsing errors above",
                EventIcon.Error
            ))
            is Changes -> {
                onEvent(StreamEvent.EditFiles(out))
                onEvent(StreamEvent.Message(
                    "Guardian result",
                    guardianExecutor.analyze(filesystem, out).violations.toString(),
                    EventIcon.Info
                ))
            }
        }
        onEvent(StreamEvent.Message("Finished", "The workflow engine has finished execution", EventIcon.Info))
    }

    private suspend fun enrichPrompt(
        onEvent: suspend (StreamEvent) -> Unit,
        files: List<FileSystem.File>,
        prompt: String,
        warnAfterMillis: Long = 300,
    ): String = supervisorScope {
        val filesForPrompt = files.map { EnrichFileForContext(it.name(), it.content()) }
        val mark = Monotonic.markNow()
        val deferred = async { enricher.enrich(EnrichRequest(prompt, filesForPrompt)) }
        val result = runCatching {
            val early = withTimeoutOrNull(warnAfterMillis) { deferred.await() }
            if (early == null) {
                onEvent(
                    StreamEvent.Message(
                        "Enriching prompt…",
                        "Enrichment is taking longer than $warnAfterMillis ms.",
                        EventIcon.Info
                    )
                )
                deferred.await()
            } else {
                early
            }
        }
        val elapsed = mark.elapsedNow()
        result.fold(
            onSuccess = { resp ->
                onEvent(StreamEvent.Message(
                    "Prompt enriched",
                    "Updated prompt (took ${elapsed.inWholeMilliseconds} ms): ${resp.enriched}",
                    EventIcon.Info
                ))
                resp.enriched
            },
            onFailure = { t ->
                onEvent(StreamEvent.Message(
                    "Enrichment failed",
                    "Using original prompt. Reason: ${t.message ?: t::class.simpleName}",
                    EventIcon.Warning
                ))
                prompt
            }
        )
    }
}
