package de.tuda.stg.securecoder.enricher

class DummyEnricherService : PromptEnricher {
    override suspend fun enrich(req: EnrichRequest): EnrichResponse {
        val enriched = buildString {
            appendLine("You are a security expert. Please answer the following question:")
            appendLine(req.prompt)
        }.trim()
        return EnrichResponse(enriched)
    }
}
