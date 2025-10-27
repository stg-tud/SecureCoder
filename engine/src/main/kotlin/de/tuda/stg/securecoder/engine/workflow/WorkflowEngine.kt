package de.tuda.stg.securecoder.engine.workflow

import de.tuda.stg.securecoder.engine.Engine
import de.tuda.stg.securecoder.engine.Engine.Context
import de.tuda.stg.securecoder.engine.Engine.EngineResult
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

class WorkflowEngine (
    enricher: PromptEnricher,
    llmClient: LlmClient,
    guardians: List<Guardian> = emptyList(),
    private val maxGuardianRetries: Int = 6,
) : Engine {
    private val promptEnrichRunner = PromptEnrichRunner(enricher)
    private val editFiles = EditFilesLlmWrapper(llmClient)
    private val guardianExecutor = GuardianExecutor(guardians)

    override suspend fun run(
        prompt: String,
        filesystem: FileSystem,
        onEvent: suspend (StreamEvent) -> Unit,
        context: Context?,
    ): EngineResult {
        val filesInContext = resolveContext(context, filesystem)
        val enrichedPrompt = promptEnrichRunner.enrichPrompt(onEvent, filesInContext, prompt)
        val messages = mutableListOf(
            ChatMessage(Role.System, "You are a Security Engineering Agent mainly for writing secure code"),
            ChatMessage(Role.User, enrichedPrompt),
            ChatMessage(Role.System, FilesInContextPromptBuilder.build(filesInContext, edit = true)),
        )
        repeat(maxGuardianRetries) {
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
            val changes = out.changes ?: return EngineResult.Failure.GenerationFailure
            val guardianResult = guardianExecutor.analyze(filesystem, changes)
            if (guardianResult.hasNoViolations()) {
                return EngineResult.Success(changes)
            }
            onEvent(StreamEvent.Message(
                "Guardian result",
                guardianResult.violations.toString(),
                EventIcon.Warning
            ))
            messages += ChatMessage(Role.User, guardianResult.buildFeedbackForLlm())
        }
        return EngineResult.Failure.ValidationFailure(maxGuardianRetries)
    }
}
