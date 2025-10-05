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
import kotlinx.coroutines.flow.toList

class WorkflowEngine (
    val enricher: PromptEnricher,
    llmClient: LlmClient,
) : Engine {
    private val editFiles = EditFilesLlmWrapper(llmClient)

    override suspend fun start(
        prompt: String,
        filesystem: FileSystem,
        onEvent: suspend (StreamEvent) -> Unit,
    ) {
        val files = filesystem.allFiles().toList()
        onEvent(StreamEvent.Message("Got files", files.joinToString { it.name() }, EventIcon.Info))
        onEvent(StreamEvent.Message("Enriching prompt...", "Sending prompt to enrichment service...", EventIcon.Info))
        val filesForPrompt = files.map { EnrichFileForContext(it.name(), it.content()) }
        val prompt = enricher.enrich(EnrichRequest(prompt, filesForPrompt))
        onEvent(StreamEvent.Message("Prompt enriched", "Updated prompt: ${prompt.enriched}", EventIcon.Info))
        val out = editFiles.chat(
            listOf(
                ChatMessage(Role.System, "You are a Security Engineering Agent mainly for writing secure code"),
                ChatMessage(Role.User, prompt.enriched),
                ChatMessage(Role.System, FilesInContextPromptBuilder.build(files, edit = true)),
            ),
            LlmClient.GenerationParams("gpt-oss:20b"),
            filesystem,
            { onEvent(StreamEvent.Message("Malicious LLM output", it.joinToString(), EventIcon.Warning)) }
        )
        when (out) {
            null -> onEvent(StreamEvent.Message("Failed generating changeset", "Failed to parse the output of the llm. Maximum amount on retries exceeded! Look for parsing errors above", EventIcon.Info))
            is Changes -> onEvent(StreamEvent.EditFiles(out))
        }
        onEvent(StreamEvent.Message("Finished", "The workflow engine has finished execution", EventIcon.Info))
    }
}
