package de.tuda.stg.securecoder.enricher

fun interface PromptEnricher {
    suspend fun enrich(req: EnrichRequest): EnrichResponse

    companion object {
        val PASSTHROUGH: PromptEnricher = PromptEnricher { req -> EnrichResponse(req.prompt) }
    }
}
