package de.tuda.stg.securecoder.engine.file.edit

import de.tuda.stg.securecoder.engine.llm.ChatMessage
import de.tuda.stg.securecoder.engine.llm.LlmClient
import de.tuda.stg.securecoder.engine.workflow.GuardianExecutor
import de.tuda.stg.securecoder.filesystem.FileSystem

enum class ReviewMode {
    PATCH,
    REPLACE,
}

interface EditFormatHandler {
    val formatId: String

    suspend fun chat(
        messages: List<ChatMessage>,
        fileSystem: FileSystem,
        params: LlmClient.GenerationParams = LlmClient.GenerationParams(),
        onParseError: suspend (parseErrors: List<String>, llm: de.tuda.stg.securecoder.engine.llm.ChatExchange) -> Unit = { _, _ -> },
        attempts: Int = 3,
    ): ChatResult

    fun buildGuardianFeedback(
        guardianResult: GuardianExecutor.GuardianResult,
        reviewMode: ReviewMode,
    ): String

    data class ChatResult(
        val messages: List<ChatMessage>,
        val changes: Changes?,
    ) {
        fun changesMessage() = messages.last { it.role == ChatMessage.Role.Assistant }
    }
}
