package de.tuda.stg.securecoder.enricher

import kotlinx.serialization.Serializable

@Serializable
data class EnrichRequest(
    val prompt: String,
    val files: List<EnrichFileForContext> = emptyList(),
)

@Serializable
data class EnrichFileForContext(
    val name: String,
    val content: String,
)

@Serializable
data class EnrichResponse(
    val enriched: String,
)
