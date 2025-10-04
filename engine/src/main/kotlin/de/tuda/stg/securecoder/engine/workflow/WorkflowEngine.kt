package de.tuda.stg.securecoder.engine.workflow

import de.tuda.stg.securecoder.engine.Engine
import de.tuda.stg.securecoder.engine.file.FileSystem
import de.tuda.stg.securecoder.engine.llm.ChatMessage
import de.tuda.stg.securecoder.engine.llm.ChatMessage.Role
import de.tuda.stg.securecoder.engine.llm.EditFilesLlmClient
import de.tuda.stg.securecoder.engine.llm.LlmClient
import de.tuda.stg.securecoder.engine.stream.EventIcon
import de.tuda.stg.securecoder.enricher.EnrichRequest
import de.tuda.stg.securecoder.enricher.PromptEnricher

class WorkflowEngine (
    val enricher: PromptEnricher,
    val llmClient: LlmClient,
) : Engine {
    override suspend fun start(
        prompt: String,
        filesystem: FileSystem,
        onEvent: suspend (title: String, description: String, icon: EventIcon) -> Unit,
        onComplete: suspend () -> Unit
    ) {
        onEvent("Got files", filesystem.iterateAllFiles().joinToString { it.name() }, EventIcon.Info)
        onEvent("Enriching prompt...", "Sending prompt to enrichment service...", EventIcon.Info)
        val prompt = enricher.enrich(EnrichRequest(prompt))
        onEvent("Prompt enriched", "Updated prompt: ${prompt.enriched}", EventIcon.Info)
        val out = llmClient.chat(
            listOf(ChatMessage(ChatMessage.Role.User, prompt.enriched)),
            LlmClient.GenerationParams("gpt-oss:20b")
        )
        onEvent("LLM output", out.toString(), EventIcon.Info)
        onComplete()
    }
}