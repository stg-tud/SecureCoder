package de.tuda.stg.securecoder.engine.llm

import kotlinx.serialization.KSerializer
import kotlinx.serialization.serializer

class LlmUpstreamException(message: String, cause: Throwable? = null) : RuntimeException(message, cause)

data class UsageStats(
    val promptTokens: Int = 0,
    val completionTokens: Int = 0,
    val totalTokens: Int = 0,
    val estimatedCost: Double? = null,
) {
    operator fun plus(other: UsageStats): UsageStats = UsageStats(
        promptTokens = promptTokens + other.promptTokens,
        completionTokens = completionTokens + other.completionTokens,
        totalTokens = totalTokens + other.totalTokens,
        estimatedCost = when {
            estimatedCost == null && other.estimatedCost == null -> null
            else -> (estimatedCost ?: 0.0) + (other.estimatedCost ?: 0.0)
        },
    )

    fun isEmpty(): Boolean = promptTokens == 0 && completionTokens == 0 && totalTokens == 0 && estimatedCost == null
}

interface UsageCollectingLlmClient : LlmClient {
    suspend fun <T> collectUsage(block: suspend () -> T): Pair<T, UsageStats?>
}

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
