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
import kotlinx.serialization.ExperimentalSerializationApi
import kotlinx.serialization.KSerializer
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import kotlinx.serialization.SerializationException
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.buildJsonArray
import kotlinx.serialization.json.buildJsonObject
import kotlinx.serialization.json.put
import org.slf4j.LoggerFactory

@OptIn(ExperimentalSerializationApi::class)
class OpenRouterClient (
    apiKey: String,
    private val model: String,
    private val siteName: String? = null,
    private val providerOrder: List<String> = emptyList(),
) : LlmClient {
    private val apiKey: String = apiKey.also {
        require(it.isNotBlank()) { "OPENROUTER_KEY must be set and non-blank" }
    }
    private val logger = LoggerFactory.getLogger("OpenRouterClient")
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
    private data class OpenRouterMessage(val role: String, val content: String?)

    @Serializable
    private data class OpenRouterChatRequest(
        val model: String,
        val messages: List<OpenRouterMessage>,
        val temperature: Double? = null,
        @SerialName("max_tokens") val maxTokens: Int? = null,
        val stream: Boolean = false,
        val metadata: JsonObject = buildJsonObject {},
        @SerialName("response_format") val responseFormat: JsonObject? = null,
        val provider: JsonObject? = null,
    )

    @Serializable
    private data class OpenRouterChoice(val index: Int, val message: OpenRouterMessage)

    @Serializable
    private data class OpenRouterChatResponse(val choices: List<OpenRouterChoice>)

    private fun mapMessages(messages: List<ChatMessage>): List<OpenRouterMessage> =
        messages.map {
            val role = when (it.role) {
                Role.System -> "system"
                Role.User -> "user"
                Role.Assistant -> "assistant"
            }
            OpenRouterMessage(role, it.content)
        }

    private suspend fun performRequest(
        req: OpenRouterChatRequest,
    ): OpenRouterChatResponse {
        logger.debug("Sending LLM request: {}", req)
        val resp: HttpResponse = try {
            http.post(endpoint) {
                contentType(ContentType.Application.Json)
                accept(ContentType.Application.Json)
                header(HttpHeaders.Authorization, "Bearer $apiKey")
                siteName?.let { header("X-Title", it) }
                setBody(req)
            }
        } catch (e: Exception) {
            throw LlmUpstreamException("OpenRouter request failed: ${e.message ?: e::class.simpleName}", e)
        }

        val body = resp.bodyAsText()
        logger.debug("Got LLM response: {}", body)
        if (!resp.status.isSuccess()) {
            val errorMessage = body.ifBlank { "<Empty response>" }
            throw LlmUpstreamException("OpenRouter Error ${resp.status.value}: $errorMessage")
        }
        return try {
            json.decodeFromString(body)
        } catch (e: SerializationException) {
            val formattedBody = body.ifBlank { "<Empty response>" }
            throw LlmUpstreamException("Failed to parse OpenRouter response body. Raw body: $formattedBody", e)
        }
    }

    override suspend fun chat(
        messages: List<ChatMessage>,
        params: LlmClient.GenerationParams
    ): String {
        val mapped = mapMessages(messages)

        val req = OpenRouterChatRequest(
            model = model,
            messages = mapped,
            temperature = params.temperature,
            maxTokens = params.maxTokens,
            provider = providerPreferences(requireParameters = false),
        )
        val obj = performRequest(req)
        val content = obj.choices.firstOrNull()?.message?.content
            ?: throw LlmUpstreamException("OpenRouter returned no textual response content")
        return content
    }

    override suspend fun <T> chatStructured(
        messages: List<ChatMessage>,
        serializer: KSerializer<T>,
        params: LlmClient.GenerationParams
    ): T {
        val mapped = mapMessages(messages)

        val schema = KxJsonSchemaFormat().format(serializer)
        val responseFormat = buildJsonObject {
            put("type", "json_schema")
            put("json_schema", buildJsonObject {
                put("name", schemaName(serializer))
                put("strict", true)
                put("schema", schema)
                schemaDescription(serializer)?.let { put("description", it) }
            })
        }

        val req = OpenRouterChatRequest(
            model = model,
            messages = mapped,
            temperature = params.temperature,
            maxTokens = params.maxTokens,
            responseFormat = responseFormat,
            provider = providerPreferences(requireParameters = true),
        )
        val obj = performRequest(req)
        val content = obj.choices.firstOrNull()?.message?.content
            ?: throw LlmUpstreamException("OpenRouter returned no textual response content")
        return try {
            json.decodeFromString(serializer, content)
        } catch (e: Exception) {
            throw RuntimeException("Failed to decode OpenRouter structured content into ${serializer.descriptor.serialName}. Content: $content", e)
        }
    }

    override fun close() = http.close()

    private fun schemaName(serializer: KSerializer<*>): String {
        val rawName = serializer.descriptor.serialName
            .substringAfterLast('.')
            .ifBlank { "securecoder_schema" }
        val sanitized = rawName
            .map { c -> if (c.isLetterOrDigit() || c == '_' || c == '-') c else '_' }
            .joinToString("")
            .trim('_', '-')
            .ifBlank { "securecoder_schema" }
        return sanitized.take(64)
    }

    private fun schemaDescription(serializer: KSerializer<*>): String? =
        serializer.descriptor.annotations
            .filterIsInstance<LLMDescription>()
            .firstOrNull()
            ?.text

    private fun providerPreferences(requireParameters: Boolean): JsonObject? {
        if (!requireParameters && providerOrder.isEmpty()) return null
        return buildJsonObject {
            if (providerOrder.isNotEmpty()) {
                val providers = buildJsonArray {
                    providerOrder.forEach { add(JsonPrimitive(it)) }
                }
                put("only", providers)
                put("order", providers)
                put("allow_fallbacks", providerOrder.size > 1)
            }
            if (requireParameters) {
                put("require_parameters", true)
            }
        }
    }
}
