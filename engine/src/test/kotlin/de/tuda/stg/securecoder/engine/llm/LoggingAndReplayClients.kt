package de.tuda.stg.securecoder.engine.llm

import java.security.MessageDigest

class LoggingLlmClient(
    private val delegate: LlmClient
) : LlmClient {
    private val _calls = mutableListOf<LoggedCall>()
    val calls: List<LoggedCall> get() = _calls

    override suspend fun chat(
        messages: List<ChatMessage>,
        params: LlmClient.GenerationParams
    ): String {
        val hash = computeHash(messages, params)
        val response = delegate.chat(messages, params)
        _calls += LoggedCall(
            requestHash = hash,
            request = messages.toString(),
            params = params.toString(),
            response = response,
        )
        return response
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

    override suspend fun chat(
        messages: List<ChatMessage>,
        params: LlmClient.GenerationParams
    ): String {
        if (idx >= loggedCalls.size) error("ReplayLlmClient: no more calls to replay (idx=$idx, size=${loggedCalls.size})")
        val calculated = LoggingLlmClient.computeHash(messages, params)
        val expected = loggedCalls[idx]
        if (calculated != expected.requestHash) {
            throw IllegalStateException(
                buildString {
                    appendLine("ReplayLlmClient: input hash mismatch at call #$idx")
                    appendLine("expected: ${expected.requestHash}")
                    appendLine("actual:   $calculated")
                    appendLine("expected (m): ${expected.request}")
                    appendLine("actual (m):   $messages")
                }
            )
        }
        return loggedCalls[idx++].response
    }

    override fun close() {}
}
