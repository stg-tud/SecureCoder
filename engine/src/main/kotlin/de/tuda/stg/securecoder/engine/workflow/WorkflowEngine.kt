package de.tuda.stg.securecoder.engine.workflow

import de.tuda.stg.securecoder.engine.Engine
import de.tuda.stg.securecoder.engine.file.FileSystem
import de.tuda.stg.securecoder.engine.llm.ChatMessage
import de.tuda.stg.securecoder.engine.llm.ChatMessage.Role
import de.tuda.stg.securecoder.engine.file.edit.EditFilesLlmWrapper
import de.tuda.stg.securecoder.engine.llm.FilesInContextPromptBuilder
import de.tuda.stg.securecoder.engine.llm.LlmClient
import de.tuda.stg.securecoder.engine.stream.EventIcon
import de.tuda.stg.securecoder.engine.stream.StreamEvent
import de.tuda.stg.securecoder.engine.workflow.FeedbackBuilder.buildFeedbackForLlm
import de.tuda.stg.securecoder.enricher.PromptEnricher
import de.tuda.stg.securecoder.guardian.Guardian
import kotlinx.coroutines.flow.toList

class WorkflowEngine (
    enricher: PromptEnricher,
    llmClient: LlmClient,
    guardians: List<Guardian> = emptyList(),
    private val maxGuardianRetries: Int = 6,
) : Engine {
    private val promptEnrichRunner = PromptEnrichRunner(enricher)
    private val editFiles = EditFilesLlmWrapper(llmClient)
    private val guardianExecutor = GuardianExecutor(guardians)

    override suspend fun start(
        prompt: String,
        filesystem: FileSystem,
        onEvent: suspend (StreamEvent) -> Unit,
    ) {
        val files = filesystem.allFiles().toList()
        val enrichedPrompt = promptEnrichRunner.enrichPrompt(onEvent, files, prompt)
        val messages = mutableListOf(
            ChatMessage(Role.System, "You are a Security Engineering Agent mainly for writing secure code"),
            ChatMessage(Role.User, enrichedPrompt),
            ChatMessage(Role.System, FilesInContextPromptBuilder.build(files, edit = true)),
        )
        repeat(maxGuardianRetries) { attempt ->
            val out = editFiles.chat(
                messages = messages,
                fileSystem = filesystem,
                onParseError = {
                    onEvent(StreamEvent.Message(
                        "Malicious or invalid LLM output",
                        it.joinToString("\n"),
                        EventIcon.Warning
                    ))
                },
            )
            messages += out.changesMessage()
            val changes = out.changes
            if (changes == null) {
                onEvent(StreamEvent.Message(
                    "Failed generating changeset",
                    "Failed to parse the output of the llm. Maximum amount on retries exceeded! Look for parsing errors above",
                    EventIcon.Error
                ))
                return@repeat
            }
            val guardianResult = guardianExecutor.analyze(filesystem, changes)
            if (guardianResult.hasNoViolations()) {
                onEvent(StreamEvent.Message(
                    "Guardian result",
                    "No violations found. Applying edits.",
                    EventIcon.Info
                ))
                onEvent(StreamEvent.EditFiles(changes))
                return@repeat
            }
            if (attempt == maxGuardianRetries - 1) {
                onEvent(
                    StreamEvent.Message(
                        "Guardian max retries reached",
                        "Maximum amount of retries exceeded after $maxGuardianRetries tries.",
                        EventIcon.Error
                    )
                )
                return@repeat
            }
            val feedback = guardianResult.buildFeedbackForLlm()
            onEvent(StreamEvent.Message(
                "Guardian result",
                guardianResult.violations.toString(),
                EventIcon.Warning
            ))
            messages += ChatMessage(Role.User, feedback)
        }
        onEvent(StreamEvent.Message("Finished", "The workflow engine has finished execution", EventIcon.Info))
    }

}
