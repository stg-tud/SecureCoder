package de.tuda.stg.securecoder.engine.llm

import kotlinx.serialization.KSerializer
import kotlinx.serialization.json.Json
import java.security.MessageDigest

class LoggingLlmClient(
    private val delegate: LlmClient
) : LlmClient {
    private val _calls = mutableListOf<LoggedCall>()
    val calls: List<LoggedCall> get() = _calls

    private fun appendLog(
        requestHash: String,
        messages: List<ChatMessage>,
        params: LlmClient.GenerationParams,
        response: String,
    ) {
        _calls += LoggedCall(
            requestHash = requestHash,
            request = messages.toString(),
            params = params.toString(),
            response = response,
        )
    }

    override suspend fun chat(
        messages: List<ChatMessage>,
        params: LlmClient.GenerationParams
    ): String {
        val hash = computeHash(messages, params)
        val response = delegate.chat(messages, params)
        appendLog(hash, messages, params, response)
        return response
    }

    override suspend fun <T> chatStructured(
        messages: List<ChatMessage>,
        serializer: KSerializer<T>,
        params: LlmClient.GenerationParams
    ): T {
        val hash = computeHash(messages, params)
        val result = delegate.chatStructured(messages, serializer, params)
        val json = Json { encodeDefaults = true }
        val response = json.encodeToString(serializer, result)
        appendLog(hash, messages, params, response)
        return result
    }

    override fun close() = delegate.close()

    companion object Commons {
        fun computeHash(
            messages: List<ChatMessage>,
            params: LlmClient.GenerationParams
        ): String {
            val payload = messages.toString() + params.toString()
            val bytes = MessageDigest.getInstance("SHA-256").digest(payload.toByteArray(Charsets.UTF_8))
            return bytes.toHexString()
        }
    }
}

class ReplayLlmClient(
    private val loggedCalls: List<LoggedCall>
) : LlmClient {
    private var idx = 0

    private fun mismatchError(
        expected: LoggedCall,
        calculated: String,
        messages: List<ChatMessage>,
    ): IllegalStateException = IllegalStateException(
        buildString {
            appendLine("ReplayLlmClient: input hash mismatch at call #$idx")
            appendLine("expected: ${expected.requestHash}")
            appendLine("actual:   $calculated")
            appendLine("expected (m): ${expected.request}")
            appendLine("actual (m):   $messages")
        }
    )

    private fun verifyNext(
        messages: List<ChatMessage>,
        params: LlmClient.GenerationParams
    ): LoggedCall {
        if (idx >= loggedCalls.size) error("ReplayLlmClient: no more calls to replay (idx=$idx, size=${loggedCalls.size})")
        val calculated = LoggingLlmClient.computeHash(messages, params)
        val expected = loggedCalls[idx]
        if (calculated != expected.requestHash) throw mismatchError(expected, calculated, messages)
        idx++
        return expected
    }

    override suspend fun chat(
        messages: List<ChatMessage>,
        params: LlmClient.GenerationParams
    ): String {
        return verifyNext(messages, params).response
    }

    override suspend fun <T> chatStructured(
        messages: List<ChatMessage>,
        serializer: KSerializer<T>,
        params: LlmClient.GenerationParams
    ): T {
        val expected = verifyNext(messages, params)
        return Json.decodeFromString(serializer, expected.response)
    }

    override fun close() {}
}
