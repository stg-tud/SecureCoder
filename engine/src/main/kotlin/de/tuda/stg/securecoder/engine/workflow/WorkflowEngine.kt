package de.tuda.stg.securecoder.engine.workflow

import de.tuda.stg.securecoder.engine.Engine
import de.tuda.stg.securecoder.engine.stream.EventIcon
import de.tuda.stg.securecoder.enricher.EnrichRequest
import de.tuda.stg.securecoder.enricher.PromptEnricher

class WorkflowEngine (
    val enricher: PromptEnricher
) : Engine {
    override suspend fun start(
        prompt: String,
        onEvent: suspend (title: String, description: String, icon: EventIcon) -> Unit,
        onComplete: suspend () -> Unit
    ) {
        onEvent("Enriching prompt...", "Sending prompt to enrichment service...", EventIcon.Info)
        val prompt = enricher.enrich(EnrichRequest(prompt))
        onEvent("Prompt enriched", "Updated prompt: $prompt", EventIcon.Info)
        onComplete()
    }
}