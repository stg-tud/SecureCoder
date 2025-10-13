package de.tuda.stg.securecoder.enricher

import io.ktor.client.HttpClient
import io.ktor.client.call.body
import io.ktor.client.engine.java.Java
import io.ktor.client.plugins.HttpTimeout
import io.ktor.client.plugins.contentnegotiation.ContentNegotiation
import io.ktor.client.request.post
import io.ktor.client.request.setBody
import io.ktor.http.ContentType
import io.ktor.http.contentType
import io.ktor.serialization.kotlinx.json.json
import kotlinx.serialization.json.Json

class EnricherClient(
    private val baseUrl: String,
    private val timeoutMillis: Long = 5_000,
) : PromptEnricher, AutoCloseable {
    private val client: HttpClient = HttpClient(Java) {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = false
                explicitNulls = false
                prettyPrint = true
            })
        }
        install(HttpTimeout) {
            requestTimeoutMillis = timeoutMillis
        }
    }

    override suspend fun enrich(req: EnrichRequest): EnrichResponse {
        val resp = client.post("$baseUrl/v1/enrich") {
            contentType(ContentType.Application.Json)
            setBody(req)
        }
        return resp.body()
    }

    override fun close() = client.close()
}
