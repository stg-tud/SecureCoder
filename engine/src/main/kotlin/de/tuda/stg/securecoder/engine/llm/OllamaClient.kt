package de.tuda.stg.securecoder.engine.llm

import de.tuda.stg.securecoder.engine.llm.ChatMessage.Role
import de.tuda.stg.securecoder.engine.llm.LlmClient.GenerationParams
import io.ktor.client.*
import io.ktor.client.engine.java.Java
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.client.statement.bodyAsText
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonObject

class OllamaClient(
    baseUrl: String = "http://127.0.0.1:11434",
    private val keepAlive: String = "5m",
    private val json: Json = Json {
        ignoreUnknownKeys = true
        explicitNulls = false
        encodeDefaults = true
    }
) : LlmClient {
    private val http = HttpClient(Java) {
        install(ContentNegotiation) { json(json) }
    }
    private val endpoint = "$baseUrl/api/chat"

    @Serializable
    private data class OllamaMsg(val role: String, val content: String)

    @Serializable
    private data class OllamaChatRequest(
        val model: String,
        val messages: List<OllamaMsg>,
        val stream: Boolean = false,
        val options: JsonObject = buildJsonObject {},
        @SerialName("keep_alive") val keepAlive: String? = null
    )

    @Serializable
    private data class OllamaChatResponse(
        val model: String,
        val message: OllamaMsg
    )

    override suspend fun chat(
        messages: List<ChatMessage>,
        params: GenerationParams
    ): String {
        val mapped = messages.map {
            val r = when (it.role) {
                Role.System -> "system"
                Role.User -> "user"
                Role.Assistant -> "assistant"
            }
            OllamaMsg(role = r, content = it.content)
        }

        val options = buildJsonObject {
            params.temperature?.let { put("temperature", JsonPrimitive(it)) }
            params.maxTokens?.let { put("num_predict", JsonPrimitive(it)) }
        }

        val req = OllamaChatRequest(
            model = params.model,
            messages = mapped,
            options = options,
            keepAlive = keepAlive
        )

        val resp = http.post(endpoint) {
            contentType(ContentType.Application.Json)
            accept(ContentType.Application.Json)
            setBody(req)
        }
        val body = resp.bodyAsText()
        println("got $body")
        val respObj = json.decodeFromString<OllamaChatResponse>(body)

        return respObj.message.content
    }

    override fun close() { http.close() }
}

