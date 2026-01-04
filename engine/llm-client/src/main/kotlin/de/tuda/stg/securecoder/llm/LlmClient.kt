package de.tuda.stg.securecoder.llm

import kotlinx.serialization.KSerializer
import kotlinx.serialization.serializer

interface LlmClient : AutoCloseable {
    suspend fun chat(
        messages: List<ChatMessage>,
        params: GenerationParams = GenerationParams(),
    ): String

    suspend fun <T> chatStructured(
        messages: List<ChatMessage>,
        serializer: KSerializer<T>,
        params: GenerationParams = GenerationParams(),
    ): T

    data class GenerationParams(
        val temperature: Double? = null,
        val maxTokens: Int? = null
    )
}

suspend inline fun <reified T> LlmClient.chatStructured(
    messages: List<ChatMessage>,
    params: LlmClient.GenerationParams = LlmClient.GenerationParams(),
): T = this.chatStructured(messages, serializer(), params)
