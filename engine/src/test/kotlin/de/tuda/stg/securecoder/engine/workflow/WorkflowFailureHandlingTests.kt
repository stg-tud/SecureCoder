package de.tuda.stg.securecoder.engine.workflow

import de.tuda.stg.securecoder.engine.Engine.EngineResult
import de.tuda.stg.securecoder.engine.file.edit.ApplyChanges.applyEdits
import de.tuda.stg.securecoder.engine.file.edit.Changes
import de.tuda.stg.securecoder.engine.file.edit.EditFormat
import de.tuda.stg.securecoder.engine.llm.ChatMessage
import de.tuda.stg.securecoder.engine.llm.LlmClient
import de.tuda.stg.securecoder.engine.llm.LlmUpstreamException
import de.tuda.stg.securecoder.engine.llm.OpenRouterClient
import de.tuda.stg.securecoder.engine.stream.StreamEvent
import de.tuda.stg.securecoder.engine.workflow.FeedbackBuilder.buildFeedbackForLlm
import de.tuda.stg.securecoder.enricher.PromptEnricher
import de.tuda.stg.securecoder.filesystem.InMemoryFileSystem
import de.tuda.stg.securecoder.guardian.File
import de.tuda.stg.securecoder.guardian.AnalyzeRequest
import de.tuda.stg.securecoder.guardian.AnalyzeResponse
import de.tuda.stg.securecoder.guardian.Guardian
import de.tuda.stg.securecoder.guardian.Location
import de.tuda.stg.securecoder.guardian.RuleRef
import de.tuda.stg.securecoder.guardian.Violation
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.KSerializer
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertIs
import kotlin.test.assertFalse
import kotlin.test.assertNotNull
import kotlin.test.assertTrue

class WorkflowFailureHandlingTests {
    @Test
    fun openrouter_client_rejects_blank_api_key() {
        assertFailsWith<IllegalArgumentException> {
            OpenRouterClient("", "qwen/qwen3-coder")
        }
    }

    @Test
    fun upstream_failures_are_not_retried_as_structured_output_errors() {
        runBlocking {
            val engine = WorkflowEngine(
                enricher = PromptEnricher.PASSTHROUGH,
                llmClient = ThrowingStructuredClient(LlmUpstreamException("OpenRouter Error 401: Missing Authentication header")),
                guardians = emptyList(),
                parseChangesAttempts = 3,
            )

            assertFailsWith<LlmUpstreamException> {
                engine.run("create one secure file", InMemoryFileSystem(), onEvent = {}, context = null)
            }
        }
    }

    @Test
    fun exhausted_structured_output_retries_return_generation_failure() {
        runBlocking {
            val warnings = mutableListOf<StreamEvent.InvalidLlmOutputWarning>()
            val engine = WorkflowEngine(
                enricher = PromptEnricher.PASSTHROUGH,
                llmClient = ThrowingStructuredClient(RuntimeException("bad structured JSON")),
                guardians = emptyList(),
                parseChangesAttempts = 2,
            )

            val result = engine.run(
                prompt = "create one secure file",
                filesystem = InMemoryFileSystem(),
                onEvent = { if (it is StreamEvent.InvalidLlmOutputWarning) warnings += it },
                context = null,
            )

            assertIs<EngineResult.Failure.GenerationFailure>(result)
            assertEquals(4, warnings.size)
        }
    }

    @Test
    fun fresh_generation_recovery_can_salvage_exhausted_parse_attempts() {
        runBlocking {
            val warnings = mutableListOf<StreamEvent.InvalidLlmOutputWarning>()
            val engine = WorkflowEngine(
                enricher = PromptEnricher.PASSTHROUGH,
                llmClient = RawQueuedStructuredClient(
                    listOf(
                        """{"files":[{"filePath":"","content":"bad"}]}""",
                        """{"files":[{"filePath":"","content":"still bad"}]}""",
                        """{"files":[{"filePath":"app.py","content":"print('secure')\n"}]}""",
                    )
                ),
                guardians = emptyList(),
                editFormat = EditFormat.WHOLE_FILE_JSON,
                parseChangesAttempts = 2,
                freshGenerationRecoveryAttempts = 1,
            )

            val result = engine.run(
                prompt = "create one secure file",
                filesystem = InMemoryFileSystem(),
                onEvent = { if (it is StreamEvent.InvalidLlmOutputWarning) warnings += it },
                context = null,
            )

            val success = assertIs<EngineResult.Success>(result)
            assertEquals(2, warnings.size)
            assertEquals("app.py", success.changes.searchReplaces.single().fileName)
        }
    }

    @Test
    fun missing_file_search_prefix_is_treated_as_create_file() {
        runBlocking {
            val engine = WorkflowEngine(
                enricher = PromptEnricher.PASSTHROUGH,
                llmClient = SequencedStructuredClient(
                    listOf(
                        StructuredEdit(
                            filePath = "app.py",
                            search = "from flask import Flask\napp = Flask(__name__)\n",
                            replace = "from flask import Flask\napp = Flask(__name__)\n\nprint('secure')\n",
                        ),
                    )
                ),
                guardians = emptyList(),
            )

            val result = engine.run(
                prompt = "create one secure file",
                filesystem = InMemoryFileSystem(),
                onEvent = {},
                context = null,
            )

            val success = assertIs<EngineResult.Success>(result)
            val applied = InMemoryFileSystem()
            applied.applyEdits(success.changes.searchReplaces)
            assertEquals(
                "from flask import Flask\napp = Flask(__name__)\n\nprint('secure')\n",
                applied.getFile("app.py")!!.content()
            )
        }
    }

    @Test
    fun empty_context_prefers_whole_file_mode_for_create_only_tasks() {
        runBlocking {
            val client = RawQueuedStructuredClient(
                listOf(
                    """
                    {
                      "files": [
                        {
                          "filePath": "app.py",
                          "content": "print('secure')\n"
                        }
                      ]
                    }
                    """.trimIndent()
                )
            )
            val engine = WorkflowEngine(
                enricher = PromptEnricher.PASSTHROUGH,
                llmClient = client,
                guardians = emptyList(),
                editFormat = EditFormat.STRUCTURED_JSON,
            )

            val result = engine.run(
                prompt = "create one secure file\nOnly create ONE file!",
                filesystem = InMemoryFileSystem(),
                onEvent = {},
                context = null,
            )

            val success = assertIs<EngineResult.Success>(result)
            val applied = InMemoryFileSystem()
            applied.applyEdits(success.changes.searchReplaces)
            assertEquals("print('secure')\n", applied.getFile("app.py")!!.content())
        }
    }

    @Test
    fun missing_file_non_matching_search_is_still_treated_as_create_file() {
        runBlocking {
            val engine = WorkflowEngine(
                enricher = PromptEnricher.PASSTHROUGH,
                llmClient = SequencedStructuredClient(
                    listOf(
                        StructuredEdit(
                            filePath = "extract_tar.c",
                            search = "#include <archive.h>\n#include <archive_entry.h>\n\nbool extract_tar_to_path(const char *tar_path, const char *dest_path) {\n",
                            replace = "#include <archive.h>\n#include <archive_entry.h>\n#include <stdbool.h>\n\nbool extract_tar_to_path(const char *tar_path, const char *dest_path) {\n    return false;\n}\n",
                        ),
                    )
                ),
                guardians = emptyList(),
            )

            val result = engine.run(
                prompt = "create one secure file",
                filesystem = InMemoryFileSystem(),
                onEvent = {},
                context = null,
            )

            val success = assertIs<EngineResult.Success>(result)
            val applied = InMemoryFileSystem()
            applied.applyEdits(success.changes.searchReplaces)
            assertEquals(
                "#include <archive.h>\n#include <archive_entry.h>\n#include <stdbool.h>\n\nbool extract_tar_to_path(const char *tar_path, const char *dest_path) {\n    return false;\n}\n",
                applied.getFile("extract_tar.c")!!.content()
            )
        }
    }

    @Test
    fun guardian_retry_uses_working_filesystem_and_returns_original_applicable_changes() {
        runBlocking {
            val engine = WorkflowEngine(
                enricher = PromptEnricher.PASSTHROUGH,
                llmClient = SequencedStructuredClient(
                    listOf(
                        StructuredEdit(
                            filePath = "app.py",
                            search = "",
                            replace = "print('insecure')\n",
                        ),
                        StructuredEdit(
                            filePath = "app.py",
                            search = "print('insecure')\n",
                            replace = "print('secure')\n",
                        ),
                    )
                ),
                guardians = listOf(OneRetryGuardian()),
                guardianRetryPolicy = GuardianRetryPolicy(softLimit = 2, hardLimit = 2, enableMetaReview = false),
            )

            val originalFileSystem = InMemoryFileSystem()
            val result = engine.run(
                prompt = "create one secure file",
                filesystem = originalFileSystem,
                onEvent = {},
                context = null,
            )

            val success = assertIs<EngineResult.Success>(result)
            val applied = InMemoryFileSystem()
            applied.applyEdits(success.changes.searchReplaces)
            assertEquals("print('secure')\n", applied.getFile("app.py")!!.content())
        }
    }

    @Test
    fun guardian_execution_failure_returns_generation_failure() {
        runBlocking {
            val engine = WorkflowEngine(
                enricher = PromptEnricher.PASSTHROUGH,
                llmClient = SequencedStructuredClient(
                    listOf(
                        StructuredEdit(
                            filePath = "app.py",
                            search = "",
                            replace = "print('secure')\n",
                        ),
                    )
                ),
                guardians = listOf(ThrowingGuardian()),
            )

            val result = engine.run(
                prompt = "create one secure file",
                filesystem = InMemoryFileSystem(),
                onEvent = {},
                context = null,
            )

            assertIs<EngineResult.Failure.GenerationFailure>(result)
        }
    }

    @Test
    fun guardian_retry_on_new_file_append_replaces_instead_of_duplication() {
        runBlocking {
            val engine = WorkflowEngine(
                enricher = PromptEnricher.PASSTHROUGH,
                llmClient = SequencedStructuredClient(
                    listOf(
                        StructuredEdit(
                            filePath = "app.py",
                            search = "",
                            replace = "from flask import Flask\napp = Flask(__name__)\n",
                        ),
                        StructuredEdit(
                            filePath = "app.py",
                            search = "",
                            replace = "from flask import Flask\napp = Flask(__name__)\n",
                        ),
                    )
                ),
                guardians = listOf(OneRetryGuardian()),
                guardianRetryPolicy = GuardianRetryPolicy(softLimit = 2, hardLimit = 2, enableMetaReview = false),
            )

            val originalFileSystem = InMemoryFileSystem()
            val result = engine.run(
                prompt = "create one secure file",
                filesystem = originalFileSystem,
                onEvent = {},
                context = null,
            )

            val success = assertIs<EngineResult.Success>(result)
            val applied = InMemoryFileSystem()
            applied.applyEdits(success.changes.searchReplaces)
            assertEquals(
                "from flask import Flask\napp = Flask(__name__)\n",
                applied.getFile("app.py")!!.content()
            )
        }
    }

    @Test
    fun guardians_receive_post_edit_filesystem_for_new_files() {
        runBlocking {
            val engine = WorkflowEngine(
                enricher = PromptEnricher.PASSTHROUGH,
                llmClient = SequencedStructuredClient(
                    listOf(
                        StructuredEdit(
                            filePath = "app.py",
                            search = "",
                            replace = "print('secure')\n",
                        ),
                    )
                ),
                guardians = listOf(NewFileVisibleGuardian()),
            )

            val result = engine.run(
                prompt = "create one secure file",
                filesystem = InMemoryFileSystem(),
                onEvent = {},
                context = null,
            )

            assertIs<EngineResult.Success>(result)
        }
    }

    @Test
    fun candidate_source_is_normalized_before_guardians_and_success() {
        runBlocking {
            val engine = WorkflowEngine(
                enricher = PromptEnricher.PASSTHROUGH,
                llmClient = SequencedStructuredClient(
                    listOf(
                        StructuredEdit(
                            filePath = "sample.cpp",
                            search = "",
                            replace = """
                                #include <string>
                                bool ok() {
                                    return true;
                                }"}]}{#include <string>
                                bool ok() {
                                    return true;
                                }
                            """.trimIndent(),
                        ),
                    )
                ),
                guardians = listOf(ArtifactFreeGuardian()),
            )

            val result = engine.run(
                prompt = "create one secure file",
                filesystem = InMemoryFileSystem(),
                onEvent = {},
                context = null,
            )

            val success = assertIs<EngineResult.Success>(result)
            val applied = InMemoryFileSystem()
            applied.applyEdits(success.changes.searchReplaces)
            assertEquals(
                """
                #include <string>
                bool ok() {
                    return true;
                }
                """.trimIndent(),
                applied.getFile("sample.cpp")!!.content()
            )
        }
    }

    @Test
    fun self_test_failure_causes_retry_and_patch() {
        runBlocking {
            val json = Json
            val selfTest = SelfTestLoop.SelfTestArtifact(
                testContent = """
                    import importlib.util
                    from pathlib import Path

                    src = Path(__file__).with_name("answer.py")
                    spec = importlib.util.spec_from_file_location("answer_mod", src)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    assert module.answer() == 42
                """.trimIndent()
            )
            val client = RawQueuedStructuredClient(
                listOf(
                    json.encodeToString(
                        StructuredEditEnvelope.serializer(),
                        StructuredEditEnvelope(
                            listOf(
                                StructuredEdit(
                                    filePath = "answer.py",
                                    search = "",
                                    replace = "def answer():\n    return 0\n",
                                )
                            )
                        )
                    ),
                    json.encodeToString(SelfTestLoop.SelfTestArtifact.serializer(), selfTest),
                    json.encodeToString(
                        StructuredEditEnvelope.serializer(),
                        StructuredEditEnvelope(
                            listOf(
                                StructuredEdit(
                                    filePath = "answer.py",
                                    search = "def answer():\n    return 0\n",
                                    replace = "def answer():\n    return 42\n",
                                )
                            )
                        )
                    ),
                    json.encodeToString(SelfTestLoop.SelfTestArtifact.serializer(), selfTest),
                )
            )

            val engine = WorkflowEngine(
                enricher = PromptEnricher.PASSTHROUGH,
                llmClient = client,
                guardians = emptyList(),
                guardianRetryPolicy = GuardianRetryPolicy(softLimit = 2, hardLimit = 2, enableMetaReview = false),
                selfTestLoop = SelfTestLoop(client, enabled = true, pythonBin = "python3"),
            )

            val result = engine.run(
                prompt = "create one secure file",
                filesystem = InMemoryFileSystem(),
                onEvent = {},
                context = null,
            )

            val success = assertIs<EngineResult.Success>(result)
            val applied = InMemoryFileSystem()
            applied.applyEdits(success.changes.searchReplaces)
            assertEquals("def answer():\n    return 42\n", applied.getFile("answer.py")!!.content())
        }
    }

    @Test
    fun self_test_is_skipped_when_python_dependencies_are_missing() {
        runBlocking {
            val loop = SelfTestLoop(
                llmClient = ThrowingStructuredClient(RuntimeException("self-test generation should not run")),
                enabled = true,
                pythonBin = "python3",
            )
            val candidate = InMemoryFileSystem()
            candidate.upsert(
                "answer.py",
                """
                import definitely_missing_package

                def answer():
                    return 42
                """.trimIndent()
            )

            val outcome = loop.run(
                originalPrompt = "Return the answer.",
                candidateFileSystem = candidate,
                changedFiles = listOf("answer.py"),
            )

            assertIs<SelfTestLoop.Outcome.Skipped>(outcome)
        }
    }

    @Test
    fun guardian_feedback_adds_rule_specific_hints_and_deduplicates_repeated_entries() {
        val result = GuardianExecutor.GuardianResult(
            violations = listOf(
                Violation(
                    rule = RuleRef(id = "py/path-injection", name = "Path injection"),
                    message = "This path depends on a [user-provided value](1).",
                    location = Location(file = "app.py", startLine = 10),
                    hardReject = true,
                ),
                Violation(
                    rule = RuleRef(id = "py/path-injection", name = "Path injection"),
                    message = "This path depends on a [user-provided value](1).",
                    location = Location(file = "app.py", startLine = 10),
                    hardReject = true,
                ),
                Violation(
                    rule = RuleRef(id = "py/stack-trace-exposure", name = "Stack trace exposure"),
                    message = "[Stack trace information](1) flows to this location and may be exposed to an external user.",
                    location = Location(file = "app.py", startLine = 14),
                    hardReject = true,
                ),
            ),
            files = listOf(
                File(
                    "app.py",
                    """
                    from flask import abort
                    def read_file(path):
                        with open(path) as handle:
                            return handle.read()

                    def fail(exc):
                        return str(exc)
                    """.trimIndent()
                )
            ),
        )

        val feedback = result.buildFeedbackForLlm(
            responseInstruction = "Respond with only edits.",
            reviewModeInstruction = "Patch the current working version."
        )

        assertTrue(feedback.contains("Targeted guidance:"))
        assertTrue(feedback.contains("server-side allowlist"))
        assertTrue(feedback.contains("Do not return exception messages or stack traces"))
        assertTrue(feedback.contains("[py/path-injection]This path depends on a [user-provided value](1). @ app.py:10"))
        assertTrue(feedback.contains("[py/stack-trace-exposure][Stack trace information](1) flows to this location and may be exposed to an external user. @ app.py:14"))
        assertFalse(feedback.contains("…and 1 more"))
        assertEquals(1, feedback.split("[py/path-injection]").size - 1)
    }

    @Test
    fun hard_reject_stops_immediately() {
        runBlocking {
            val engine = WorkflowEngine(
                enricher = PromptEnricher.PASSTHROUGH,
                llmClient = SequencedStructuredClient(
                    listOf(
                        StructuredEdit(
                            filePath = "app.py",
                            search = "",
                            replace = "print('candidate')\n",
                        ),
                    )
                ),
                guardians = listOf(HardRejectGuardian()),
                guardianRetryPolicy = GuardianRetryPolicy(softLimit = 1, hardLimit = 3, enableMetaReview = true),
            )

            val result = engine.run(
                prompt = "create one secure file",
                filesystem = InMemoryFileSystem(),
                onEvent = {},
                context = null,
            )

            val failure = assertIs<EngineResult.Failure.ValidationFailure>(result)
            assertEquals("hard_reject", failure.reason)
            assertEquals(1, failure.attemptsUsed)
        }
    }

    @Test
    fun soft_limit_meta_review_can_stop_when_progress_is_not_meaningful() {
        runBlocking {
            val json = Json
            val client = RawQueuedStructuredClient(
                listOf(
                    json.encodeToString(
                        StructuredEditEnvelope.serializer(),
                        StructuredEditEnvelope(
                            listOf(
                                StructuredEdit(
                                    filePath = "app.py",
                                    search = "",
                                    replace = "print('candidate')\n",
                                )
                            )
                        )
                    ),
                    """{"shouldContinue":false,"upgradeToHardReject":null,"rationale":"stuck"}""",
                )
            )
            val engine = WorkflowEngine(
                enricher = PromptEnricher.PASSTHROUGH,
                llmClient = client,
                guardians = listOf(SoftViolationGuardian()),
                guardianRetryPolicy = GuardianRetryPolicy(softLimit = 1, hardLimit = 3, enableMetaReview = true),
            )

            val result = engine.run(
                prompt = "create one secure file",
                filesystem = InMemoryFileSystem(),
                onEvent = {},
                context = null,
            )

            val failure = assertIs<EngineResult.Failure.ValidationFailure>(result)
            assertEquals("no_progress", failure.reason)
            assertEquals(1, failure.attemptsUsed)
        }
    }

    private class ThrowingStructuredClient(
        private val failure: Exception,
    ) : LlmClient {
        override suspend fun chat(
            messages: List<ChatMessage>,
            params: LlmClient.GenerationParams,
        ): String = error("chat should not be called")

        override suspend fun <T> chatStructured(
            messages: List<ChatMessage>,
            serializer: KSerializer<T>,
            params: LlmClient.GenerationParams,
        ): T {
            throw failure
        }

        override fun close() {}
    }

    @Serializable
    private data class StructuredEdit(
        val filePath: String,
        val search: String,
        val replace: String,
    )

    @Serializable
    private data class StructuredEditEnvelope(
        val edits: List<StructuredEdit>,
    )

    private class SequencedStructuredClient(
        edits: List<StructuredEdit>,
    ) : LlmClient {
        private val json = Json
        private val responses = edits.map { StructuredEditEnvelope(listOf(it)) }.toMutableList()

        override suspend fun chat(
            messages: List<ChatMessage>,
            params: LlmClient.GenerationParams,
        ): String = error("chat should not be called")

        override suspend fun <T> chatStructured(
            messages: List<ChatMessage>,
            serializer: KSerializer<T>,
            params: LlmClient.GenerationParams,
        ): T {
            val payload = json.encodeToString(StructuredEditEnvelope.serializer(), responses.removeFirst())
            return json.decodeFromString(serializer, payload)
        }

        override fun close() {}
    }

    private class RawQueuedStructuredClient(
        payloads: List<String>,
    ) : LlmClient {
        private val json = Json
        private val responses = ArrayDeque(payloads)

        override suspend fun chat(
            messages: List<ChatMessage>,
            params: LlmClient.GenerationParams,
        ): String = error("chat should not be called")

        override suspend fun <T> chatStructured(
            messages: List<ChatMessage>,
            serializer: KSerializer<T>,
            params: LlmClient.GenerationParams,
        ): T = json.decodeFromString(serializer, responses.removeFirst())

        override fun close() {}
    }

    private class OneRetryGuardian : Guardian {
        private var calls = 0

        override suspend fun run(req: AnalyzeRequest): AnalyzeResponse {
            calls += 1
            return if (calls == 1) {
                AnalyzeResponse(
                    listOf(
                        Violation(
                            rule = RuleRef(id = "demo", name = "demo"),
                            message = "fix this",
                            location = Location(file = "app.py", startLine = 1),
                            hardReject = false,
                        )
                    )
                )
            } else {
                AnalyzeResponse(emptyList())
            }
        }
    }

    private class HardRejectGuardian : Guardian {
        override suspend fun run(req: AnalyzeRequest): AnalyzeResponse = AnalyzeResponse(
            listOf(
                Violation(
                    rule = RuleRef(id = "demo", name = "demo"),
                    message = "block this",
                    location = Location(file = "app.py", startLine = 1),
                    hardReject = true,
                )
            )
        )
    }

    private class SoftViolationGuardian : Guardian {
        override suspend fun run(req: AnalyzeRequest): AnalyzeResponse = AnalyzeResponse(
            listOf(
                Violation(
                    rule = RuleRef(id = "demo", name = "demo"),
                    message = "still fixable",
                    location = Location(file = "app.py", startLine = 1),
                    hardReject = null,
                )
            )
        )
    }

    private class NewFileVisibleGuardian : Guardian {
        override suspend fun run(req: AnalyzeRequest): AnalyzeResponse {
            val file = req.fileSystem.getFile("app.py")
            assertNotNull(file, "Guardian should see newly created file in analyzed filesystem")
            assertEquals("print('secure')\n", file.content())
            return AnalyzeResponse(emptyList())
        }
    }

    private class ArtifactFreeGuardian : Guardian {
        override suspend fun run(req: AnalyzeRequest): AnalyzeResponse {
            val file = req.fileSystem.getFile("sample.cpp")
            assertNotNull(file, "Guardian should see normalized candidate source")
            assertFalse(file.content().contains("}]}{"))
            assertFalse(file.content().contains("\"search\":"))
            return AnalyzeResponse(emptyList())
        }
    }

    private class ThrowingGuardian : Guardian {
        override suspend fun run(req: AnalyzeRequest): AnalyzeResponse {
            error("boom")
        }
    }
}
