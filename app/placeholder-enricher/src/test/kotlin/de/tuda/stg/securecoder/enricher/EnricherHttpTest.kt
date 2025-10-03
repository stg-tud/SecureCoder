package de.tuda.stg.securecoder.enricher

import io.ktor.client.request.*
import io.ktor.client.statement.bodyAsText
import io.ktor.http.ContentType
import io.ktor.http.HttpStatusCode
import io.ktor.http.contentType
import io.ktor.server.testing.*
import kotlinx.serialization.json.Json
import kotlin.test.Test
import kotlin.test.assertEquals

class EnricherHttpTest {

    @Test
    fun testGetHealth() = testApplication {
        application {
            val testEnricher = PromptEnricher { _ -> throw Exception("Should not be called") }
            installEnricherRoutes(testEnricher)
        }
        client.get("/health").apply {
            assertEquals(HttpStatusCode.OK, status)
            assertEquals("OK", bodyAsText())
        }
    }

    @Test
    fun testPostEnrich() = testApplication {
        application {
            installContentNegotiation()
            val testEnricher = PromptEnricher { req -> EnrichResponse("TEST:" + req.prompt) }
            installEnricherRoutes(testEnricher)
        }
        val response = client.post("/v1/enrich") {
            contentType(ContentType.Application.Json)
            setBody("""{"prompt":"How to write secure Kotlin code?"}""")
        }
        assertEquals(HttpStatusCode.OK, response.status)
        val body = response.bodyAsText()
        val res: EnrichResponse = Json.decodeFromString(body)
        val expected = "TEST:How to write secure Kotlin code?"
        assertEquals(expected, res.enriched)
    }
}