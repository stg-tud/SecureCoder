package de.tuda.stg.securecoder.engine.llm

interface LlmClient : AutoCloseable {
    suspend fun chat(
        messages: List<ChatMessage>,
        params: GenerationParams = GenerationParams(),
    ): String

    data class GenerationParams(
        val temperature: Double? = null,
        val maxTokens: Int? = null
    )
}
