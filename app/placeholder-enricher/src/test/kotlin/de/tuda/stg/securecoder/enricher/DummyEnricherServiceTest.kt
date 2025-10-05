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
            You are a security expert.
            Your top priority is to design, modify, or review features security overrides speed and scope
            Disallowed: content that facilitates exploitation, bypassing controls or unauthorized access. Provide safe alternatives and mitigations instead.

            How to sanitize inputs?
        """.trimIndent().trim()

        assertEquals(EnrichResponse(expected), resp)
    }
}
