package de.tuda.stg.securecoder.engine.guardian

import de.tuda.stg.securecoder.engine.llm.ChatMessage
import de.tuda.stg.securecoder.engine.llm.LlmClient
import de.tuda.stg.securecoder.filesystem.InMemoryFileSystem
import de.tuda.stg.securecoder.guardian.AnalyzeRequest
import de.tuda.stg.securecoder.guardian.File
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.KSerializer
import kotlinx.serialization.json.Json
import kotlin.test.Test
import kotlin.test.assertEquals

class LlmGuardianTests {
    @Test
    fun filters_speculative_filesystem_finding_from_url_helper() = runBlocking {
        val guardian = LlmGuardian(
            client = StaticStructuredClient(
                """
                {
                  "findings": [
                    {
                      "shortName": "Potential Path Traversal",
                      "description": "If the returned URL is later used in file system operations, it could lead to path traversal vulnerabilities.",
                      "fileName": "src/utils.py",
                      "line": 10,
                      "hardReject": false,
                      "confidence": "Medium"
                    }
                  ]
                }
                """.trimIndent()
            )
        )
        val content = """
            from urllib.parse import urlparse

            def get_target_for_redirect(target: str, domain: str) -> str:
                parsed_target = urlparse(target)
                return target
        """.trimIndent()
        val fs = InMemoryFileSystem().apply { upsert("src/utils.py", content) }

        val result = guardian.run(AnalyzeRequest(fs, listOf(File("src/utils.py", content))))

        assertEquals(0, result.violations.size)
    }

    @Test
    fun keeps_log_injection_when_logging_sink_exists() = runBlocking {
        val guardian = LlmGuardian(
            client = StaticStructuredClient(
                """
                {
                  "findings": [
                    {
                      "shortName": "Log Injection",
                      "description": "Attacker-controlled input is logged directly and can inject misleading log structure.",
                      "fileName": "app.py",
                      "line": 3,
                      "hardReject": false,
                      "confidence": "High"
                    }
                  ]
                }
                """.trimIndent()
            )
        )
        val content = """
            import logging
            def greet(name: str):
                logging.info(f"user={name}")
        """.trimIndent()
        val fs = InMemoryFileSystem().apply { upsert("app.py", content) }

        val result = guardian.run(AnalyzeRequest(fs, listOf(File("app.py", content))))

        assertEquals(1, result.violations.size)
    }

    @Test
    fun keeps_open_redirect_when_redirect_sink_exists() = runBlocking {
        val guardian = LlmGuardian(
            client = StaticStructuredClient(
                """
                {
                  "findings": [
                    {
                      "shortName": "Open Redirect",
                      "description": "User-controlled redirect target still influences the redirect destination.",
                      "fileName": "views.py",
                      "line": 4,
                      "hardReject": false,
                      "confidence": "High"
                    }
                  ]
                }
                """.trimIndent()
            )
        )
        val content = """
            from django.http import HttpResponseRedirect
            def go(next_url: str):
                return HttpResponseRedirect(next_url)
        """.trimIndent()
        val fs = InMemoryFileSystem().apply { upsert("views.py", content) }

        val result = guardian.run(AnalyzeRequest(fs, listOf(File("views.py", content))))

        assertEquals(1, result.violations.size)
    }

    private class StaticStructuredClient(
        private val payload: String,
    ) : LlmClient {
        private val json = Json

        override suspend fun chat(
            messages: List<ChatMessage>,
            params: LlmClient.GenerationParams,
        ): String = error("unused")

        override suspend fun <T> chatStructured(
            messages: List<ChatMessage>,
            serializer: KSerializer<T>,
            params: LlmClient.GenerationParams,
        ): T = json.decodeFromString(serializer, payload)

        override fun close() {}
    }
}
