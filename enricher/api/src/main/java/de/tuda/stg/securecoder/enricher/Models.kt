package de.tuda.stg.securecoder.enricher

import kotlinx.serialization.Serializable

@Serializable
data class EnrichRequest(
    val prompt: String,
)

@Serializable
data class EnrichResponse(
    val enriched: String,
)
