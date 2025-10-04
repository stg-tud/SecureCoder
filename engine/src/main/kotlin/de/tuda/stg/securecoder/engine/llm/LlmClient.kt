package de.tuda.stg.securecoder.engine.llm

interface LlmClient : AutoCloseable {
    suspend fun chat(
        messages: List<ChatMessage>,
        params: GenerationParams,
    ): String

    data class GenerationParams(
        val model: String,
        val temperature: Double? = null,
        val maxTokens: Int? = null
    )
}
