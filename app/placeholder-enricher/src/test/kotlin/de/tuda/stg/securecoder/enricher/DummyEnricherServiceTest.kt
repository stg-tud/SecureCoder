package de.tuda.stg.securecoder.enricher

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlinx.coroutines.test.runTest

class DummyEnricherServiceTest {

    @Test
    fun test() = runTest {
        val service = DummyEnricherService()
        val req = EnrichRequest("How to sanitize inputs?")
        val resp = service.enrich(req)

        val expected = """
            You are a security expert. Please answer the following question:
            How to sanitize inputs?
        """.trimIndent().trim()

        assertEquals(EnrichResponse(expected), resp)
    }
}
