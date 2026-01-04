package de.tuda.stg.securecoder.llm

import de.tuda.stg.securecoder.llm.ChatMessage.Role
import de.tuda.stg.securecoder.llm.LlmClient.GenerationParams
import io.ktor.client.*
import io.ktor.client.engine.java.Java
import io.ktor.client.plugins.contentnegotiation.*
import io.ktor.client.request.*
import io.ktor.client.statement.bodyAsText
import io.ktor.http.*
import io.ktor.serialization.kotlinx.json.*
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.SerializationException
import kotlinx.serialization.KSerializer
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonObject
import org.slf4j.LoggerFactory

class OllamaClient(
    private val model: String,
    baseUrl: String = "http://127.0.0.1:11434",
    private val keepAlive: String = "5m",
) : LlmClient {
    private val logger = LoggerFactory.getLogger("OllamaClient")
    private val json: Json = Json {
        ignoreUnknownKeys = true
        explicitNulls = false
        encodeDefaults = true
    }
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
        @SerialName("keep_alive") val keepAlive: String? = null,
        val format: JsonObject? = null,
    )

    @Serializable
    private data class OllamaChatResponse(
        val model: String,
        val message: OllamaMsg
    )

    @Serializable
    private data class OllamaError(val error: String)

    private fun mapMessages(messages: List<ChatMessage>): List<OllamaMsg> =
        messages.map {
            val role = when (it.role) {
                Role.System -> "system"
                Role.User -> "user"
                Role.Assistant -> "assistant"
            }
            OllamaMsg(role, it.content)
        }

    private fun buildOptions(params: GenerationParams) = buildJsonObject {
        params.temperature?.let { put("temperature", JsonPrimitive(it)) }
        params.maxTokens?.let { put("num_predict", JsonPrimitive(it)) }
    }

    private suspend fun performRequest(req: OllamaChatRequest): OllamaChatResponse {
        logger.debug("Sending LLM request: {}", req)
        val resp = http.post(endpoint) {
            contentType(ContentType.Application.Json)
            accept(ContentType.Application.Json)
            setBody(req)
        }
        val body = resp.bodyAsText()
        logger.debug("Got LLM response: {}", body)
        if (!resp.status.isSuccess()) {
            val errorMessage = try {
                json.decodeFromString<OllamaError>(body).error
            } catch (_: SerializationException) {
                body.ifBlank { "<Empty response>" }
            }
            throw RuntimeException("Failed to call Ollama got ${resp.status}: $errorMessage")
        }
        return json.decodeFromString(body)
    }

    override suspend fun chat(
        messages: List<ChatMessage>,
        params: GenerationParams
    ): String {
        val req = OllamaChatRequest(
            model = model,
            messages = mapMessages(messages),
            options = buildOptions(params),
            keepAlive = keepAlive
        )
        val respObj = performRequest(req)
        return respObj.message.content
    }

    override suspend fun <T> chatStructured(
        messages: List<ChatMessage>,
        serializer: KSerializer<T>,
        params: GenerationParams
    ): T {
        val schema = KxJsonSchemaFormat().format(serializer)
        val req = OllamaChatRequest(
            model = model,
            messages = mapMessages(messages),
            options = buildOptions(params),
            keepAlive = keepAlive,
            format = schema
        )
        val respObj = performRequest(req)
        val content = respObj.message.content
        return try {
            json.decodeFromString(serializer, content)
        } catch (e: Exception) {
            throw RuntimeException("Failed to decode Ollama structured content. Content: $content", e)
        }
    }

    override fun close() = http.close()
}
