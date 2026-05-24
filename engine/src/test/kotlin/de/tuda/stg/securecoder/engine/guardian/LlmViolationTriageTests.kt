package de.tuda.stg.securecoder.engine.guardian

import de.tuda.stg.securecoder.engine.llm.ChatMessage
import de.tuda.stg.securecoder.engine.llm.LlmClient
import de.tuda.stg.securecoder.filesystem.InMemoryFileSystem
import de.tuda.stg.securecoder.guardian.AnalyzeRequest
import de.tuda.stg.securecoder.guardian.File
import de.tuda.stg.securecoder.guardian.Location
import de.tuda.stg.securecoder.guardian.RuleRef
import de.tuda.stg.securecoder.guardian.Violation
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.KSerializer
import kotlinx.serialization.json.Json
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue
import kotlin.test.assertNull

class LlmViolationTriageTests {
    @Test
    fun triage_can_drop_false_positive_finding() = runBlocking {
        val triage = LlmViolationTriage(
            llmClient = StaticStructuredClient("""{"keepFinding":false,"hardReject":null,"confidence":"Low","rationale":"not supported"}"""),
        )
        val fileSystem = InMemoryFileSystem().apply {
            upsert("app.py", "print('ok')\n")
        }
        val violations = listOf(
            Violation(
                rule = RuleRef(id = "py/fake"),
                message = "suspicious",
                location = Location(file = "app.py", startLine = 1, endLine = 1),
                hardReject = false,
                confidence = "medium",
                raw = "raw",
            )
        )

        val result = triage.triage(
            AnalyzeRequest(fileSystem, listOf(File("app.py", "print('ok')\n"))),
            violations,
        )

        assertEquals(0, result.size)
    }

    @Test
    fun triage_can_upgrade_kept_finding_metadata() = runBlocking {
        val triage = LlmViolationTriage(
            llmClient = StaticStructuredClient("""{"keepFinding":true,"hardReject":true,"confidence":"High","rationale":"direct sink"}"""),
        )
        val fileSystem = InMemoryFileSystem().apply {
            upsert("app.py", "print('ok')\n")
        }
        val violation = Violation(
            rule = RuleRef(id = "py/fake"),
            message = "suspicious",
            location = Location(file = "app.py", startLine = 1, endLine = 1),
            hardReject = null,
            confidence = "medium",
            raw = "raw",
        )

        val result = triage.triage(
            AnalyzeRequest(fileSystem, listOf(File("app.py", "print('ok')\n"))),
            listOf(violation),
        )

        assertEquals(1, result.size)
        assertEquals(true, result.single().hardReject)
        assertEquals("High", result.single().confidence)
        assertEquals("raw\ntriage: direct sink", result.single().raw)
    }

    @Test
    fun triage_keeps_original_finding_when_llm_fails() = runBlocking {
        val triage = LlmViolationTriage(
            llmClient = object : LlmClient {
                override suspend fun chat(
                    messages: List<ChatMessage>,
                    params: LlmClient.GenerationParams,
                ): String = error("unused")

                override suspend fun <T> chatStructured(
                    messages: List<ChatMessage>,
                    serializer: KSerializer<T>,
                    params: LlmClient.GenerationParams,
                ): T = error("boom")

                override fun close() {}
            },
        )
        val fileSystem = InMemoryFileSystem().apply {
            upsert("app.py", "print('ok')\n")
        }
        val violation = Violation(
            rule = RuleRef(id = "py/fake"),
            message = "suspicious",
            location = Location(file = "app.py", startLine = 1, endLine = 1),
        )

        val result = triage.triage(
            AnalyzeRequest(fileSystem, listOf(File("app.py", "print('ok')\n"))),
            listOf(violation),
        )

        assertEquals(1, result.size)
        assertNull(result.single().hardReject)
    }

    @Test
    fun triage_includes_rule_specific_prompt_override() = runBlocking {
        val client = CapturingStructuredClient("""{"keepFinding":true,"hardReject":null,"confidence":"Medium","rationale":"ok"}""")
        val triage = LlmViolationTriage(
            llmClient = client,
            rulePromptOverrides = mapOf("*path-injection*" to "Only keep this when user input can still reach the final filesystem path."),
        )
        val fileSystem = InMemoryFileSystem().apply {
            upsert("app.py", "print('ok')\n")
        }

        triage.triage(
            AnalyzeRequest(
                fileSystem,
                listOf(File("app.py", "print('ok')\n")),
            ),
            listOf(
                Violation(
                    rule = RuleRef(id = "py/path-injection"),
                    message = "maybe path issue",
                    location = Location(file = "app.py", startLine = 1, endLine = 1),
                )
            ),
        )

        assertTrue(client.lastMessages.any { it.content.contains("Only keep this when user input can still reach the final filesystem path.") })
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

    private class CapturingStructuredClient(
        private val payload: String,
    ) : LlmClient {
        private val json = Json
        var lastMessages: List<ChatMessage> = emptyList()

        override suspend fun chat(
            messages: List<ChatMessage>,
            params: LlmClient.GenerationParams,
        ): String = error("unused")

        override suspend fun <T> chatStructured(
            messages: List<ChatMessage>,
            serializer: KSerializer<T>,
            params: LlmClient.GenerationParams,
        ): T {
            lastMessages = messages
            return json.decodeFromString(serializer, payload)
        }

        override fun close() {}
    }
}
