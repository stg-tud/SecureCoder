package de.tuda.stg.securecoder.openaibridge

import kotlinx.serialization.Serializable

@Serializable
data class ChatCompletionRequest(
    val model: String,
    val messages: List<ChatMessage>,
    val stream: Boolean = false
)

@Serializable
data class AgentEditRequest(
    val model: String,
    val prompt: String,
    val files: List<ProjectFile> = emptyList(),
    val context_files: List<String>? = null,
)

@Serializable
data class ChatMessage(
    val role: String,
    val content: String
)

@Serializable
data class ProjectFile(
    val path: String,
    val content: String,
)

@Serializable
data class ChatCompletionResponse(
    val id: String,
    val obj: String = "chat.completion",
    val created: Long,
    val model: String,
    val choices: List<Choice>,
    val usage: Usage? = null
)

@Serializable
data class AgentEditResponse(
    val id: String,
    val created: Long,
    val model: String,
    val files: List<ProjectFile>,
    val changed_files: List<String>,
    val usage: Usage? = null,
)

@Serializable
data class Choice(
    val index: Int,
    val message: ChatMessage,
    val finish_reason: String = "stop"
)

@Serializable
data class Usage(
    val prompt_tokens: Int = 0,
    val completion_tokens: Int = 0,
    val total_tokens: Int = 0,
    val estimated_cost: Double? = null,
)

@Serializable
data class OpenAiErrorEnvelope(
    val error: OpenAiErrorBody,
)

@Serializable
data class OpenAiErrorBody(
    val message: String,
    val code: String,
)
