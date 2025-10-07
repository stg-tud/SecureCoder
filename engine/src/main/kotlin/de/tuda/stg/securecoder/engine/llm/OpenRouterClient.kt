package de.tuda.stg.securecoder.engine.llm

import de.tuda.stg.securecoder.engine.llm.ChatMessage.Role
import io.ktor.client.HttpClient
import io.ktor.client.engine.java.Java
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.request.accept
import io.ktor.client.request.header
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.client.statement.HttpResponse
import io.ktor.client.statement.bodyAsText
import io.ktor.http.ContentType
import io.ktor.http.HttpHeaders
import io.ktor.http.contentType
import io.ktor.http.isSuccess
import io.ktor.serialization.kotlinx.json.json
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.buildJsonObject

class OpenRouterClient (
    private val apiKey: String,
    private val model: String,
    private val siteName: String? = null,
) : LlmClient {
    private val json: Json = Json {
        ignoreUnknownKeys = true
        explicitNulls = false
        encodeDefaults = true
    }
    private val http = HttpClient(Java) {
        install(ContentNegotiation) { json(json) }
    }
    private val baseUrl = "https://openrouter.ai/api/v1"
    private val endpoint = "$baseUrl/chat/completions"

    @Serializable
    private data class OpenRouterMessage(val role: String, val content: String)

    @Serializable
    private data class OpenRouterChatRequest(
        val model: String,
        val messages: List<OpenRouterMessage>,
        val temperature: Double? = null,
        @SerialName("max_tokens") val maxTokens: Int? = null,
        val stream: Boolean = false,
        val metadata: JsonObject = buildJsonObject {}
    )

    @Serializable
    private data class OpenRouterChoice(val index: Int, val message: OpenRouterMessage)

    @Serializable
    private data class OpenRouterChatResponse(val choices: List<OpenRouterChoice>)

    override suspend fun chat(
        messages: List<ChatMessage>,
        params: LlmClient.GenerationParams
    ): String {
        val mapped = messages.map {
            val role = when (it.role) {
                Role.System -> "system"
                Role.User -> "user"
                Role.Assistant -> "assistant"
            }
            OpenRouterMessage(role, it.content)
        }

        val req = OpenRouterChatRequest(
            model = model,
            messages = mapped,
            temperature = params.temperature,
            maxTokens = params.maxTokens
        )

        val resp: HttpResponse = http.post(endpoint) {
            contentType(ContentType.Application.Json)
            accept(ContentType.Application.Json)
            header(HttpHeaders.Authorization, "Bearer $apiKey")
            siteName?.let { header("X-Title", it) }
            setBody(req)
        }

        val body = resp.bodyAsText()
        if (!resp.status.isSuccess()) {
            error("OpenRouter Error ${resp.status.value}: $body")
        }

        println("OpenRouter response: $body")
        val obj = json.decodeFromString<OpenRouterChatResponse>(body)
        val content = obj.choices.firstOrNull()?.message?.content
            ?: error("OpenRouter lieferte keine Antwortnachricht.")
        return content
    }

    override fun close() = http.close()
}