package de.tuda.stg.securecoder.enricher

class DummyEnricherService : PromptEnricher {
    override suspend fun enrich(req: EnrichRequest): EnrichResponse {
        val enriched = buildString {
            appendLine("You are a security expert.")
            appendLine("Your top priority is to design, modify, or review features security overrides speed and scope")
            appendLine("Disallowed: content that facilitates exploitation, bypassing controls or unauthorized access. Provide safe alternatives and mitigations instead.")
            appendLine()
            appendLine(req.prompt)
        }.trim()
        return EnrichResponse(enriched)
    }
}
