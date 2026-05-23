package de.tuda.stg.securecoder.openaibridge

import de.tuda.stg.securecoder.enricher.EnrichFileForContext
import de.tuda.stg.securecoder.enricher.EnrichRequest
import kotlinx.coroutines.runBlocking
import kotlin.test.Test
import kotlin.test.assertTrue
import kotlin.test.assertFalse

class HeuristicPromptEnricherTests {
    @Test
    fun adds_javascript_sync_and_binary_hints() = runBlocking {
        val prompt = """
            You should implement the function in JavaScript.
            Hash the given certificate and return it as a string.
        """.trimIndent()

        val enriched = HeuristicPromptEnricher.enrich(EnrichRequest(prompt, emptyList<EnrichFileForContext>())).enriched

        assertTrue(enriched.contains("keep the function synchronous"))
        assertTrue(enriched.contains("printable encoding such as hex"))
    }

    @Test
    fun reinforces_exact_contract_when_prompt_specifies_behavioral_details() = runBlocking {
        val prompt = """
            You should implement the function in Python.
            Keep the function signature exactly as provided.
            Use hashlib.pbkdf2_hmac with SHA-256 and 10000 iterations.
            Return an empty string on any error.
        """.trimIndent()

        val enriched = HeuristicPromptEnricher.enrich(EnrichRequest(prompt, emptyList<EnrichFileForContext>())).enriched

        assertTrue(enriched.contains("Do not change function names, parameter lists"))
        assertTrue(enriched.contains("algorithm, mode, iteration count"))
        assertTrue(enriched.contains("invalid-input behavior"))
    }

    @Test
    fun adds_tempfile_and_archive_hints_when_relevant() = runBlocking {
        val prompt = """
            Create a temporary file and return the file name.
            Extract the tar archive into the destination path.
        """.trimIndent()

        val enriched = HeuristicPromptEnricher.enrich(EnrichRequest(prompt, emptyList<EnrichFileForContext>())).enriched

        assertTrue(enriched.contains("named temporary file"))
        assertTrue(enriched.contains("archive extraction"))
        assertTrue(enriched.contains("Avoid unnecessary ACL"))
    }

    @Test
    fun leaves_irrelevant_prompts_lightweight() = runBlocking {
        val prompt = "Implement the function in Python and return the input unchanged."

        val enriched = HeuristicPromptEnricher.enrich(EnrichRequest(prompt, emptyList<EnrichFileForContext>())).enriched

        assertTrue(enriched.contains("Preserve the exact externally visible contract"))
        assertFalse(enriched.contains("archive extraction"))
    }
}
