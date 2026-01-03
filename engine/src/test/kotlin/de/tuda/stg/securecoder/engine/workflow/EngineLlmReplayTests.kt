package de.tuda.stg.securecoder.engine.workflow

import de.tuda.stg.securecoder.engine.Engine.EngineResult
import de.tuda.stg.securecoder.engine.llm.*
import de.tuda.stg.securecoder.engine.stream.StreamEvent
import de.tuda.stg.securecoder.enricher.PromptEnricher
import de.tuda.stg.securecoder.filesystem.InMemoryFileSystem
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlin.test.Test
import java.nio.file.Files
import java.nio.file.Path

class EngineLlmReplayTests {
    private val json = Json { prettyPrint = true; ignoreUnknownKeys = true; encodeDefaults = true }
    private val logsPath: Path = Path.of("build", "llm_logs", "log.json")

    @Test
    fun generator_collects_real_llm_responses() = runBlocking {
        Files.createDirectories(logsPath.parent)

        val prompts = listOf(
            "create_project" to "Create a minimal Hello World project with one file Main.java printing Hello",
            "edit_project" to "Modify the project to add a Utils.java with a function greet(name) and use it in Main.java",
        )

        val models = buildList {
            val apiKey = System.getenv("API_KEy") ?: "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"
            add("OR:llama3.2:latest" to OpenRouterClient(apiKey, "meta-llama/llama-3.2-3b-instruct"))
            add("OR:gpt-oss:20b" to OpenRouterClient(apiKey, "openai/gpt-oss-20b"))
            //val olBase = System.getenv("OLLAMA_URL") ?: "http://127.0.0.1:11434"
            //add("ollama:llama3.2:latest" to OllamaClient("llama3.2:latest", baseUrl = olBase))
            //add("ollama:gpt-oss:20b" to OllamaClient("gpt-oss:20b", baseUrl = olBase))
        }

        val runs = mutableListOf<LoggedRun>()
        for ((modelName, rawClient) in models) {
            rawClient.use { base ->
                for ((kind, userPrompt) in prompts) {
                    repeat(15) { idx ->
                        println("Recording #${idx + 1} for $kind on $modelName")
                        val logging = LoggingLlmClient(base)
                        val fs = InMemoryFileSystem()
                        val initialFiles = when (kind) {
                            "edit_project" -> mapOf(
                                "src/Main.java" to """
                                    public class Main {
                                        public static void main(String[] args) {
                                            System.out.println("Hello");
                                        }
                                    }
                                """.trimIndent()
                            )
                            else -> emptyMap()
                        }
                        for ((name, content) in initialFiles) fs.upsert(name, content)

                        val engine = WorkflowEngine(
                            enricher = PromptEnricher.PASSTHROUGH,
                            llmClient = logging,
                            guardians = emptyList(),
                        )
                        engine.run(userPrompt, fs, onEvent = { /* ignore */ }, context = null)
                        if (logging.calls.isEmpty()) throw IllegalStateException("No calls recorded!")
                        runs += LoggedRun(
                            modelName = modelName,
                            promptKind = kind,
                            runIndex = idx,
                            enginePrompt = userPrompt,
                            initialFiles = initialFiles,
                            calls = logging.calls.toList(),
                        )
                    }
                }
            }
        }
        val suite = LoggedSuite(runs)
        Files.writeString(logsPath, json.encodeToString(suite))
        println("Wrote logs to $logsPath")
    }

    @Test
    fun replay_test_uses_recorded_responses_and_counts_success() = runBlocking {
        if (!Files.exists(logsPath)) {
            println("No log file at $logsPath; nothing to replay. Test will be a no-op.")
            return@runBlocking
        }
        val suite = json.decodeFromString<LoggedSuite>(Files.readString(logsPath))

        data class Group(
            val modelName: String,
            val promptKind: String,
            var total: Int = 0,
            var successes: Int  = 0,
            var parseFails: Int  = 0
        )

        suite.runs
            .groupBy { it.modelName to it.promptKind }
            .map { (key, runs) ->
                val (model, kind) = key
                val group = Group(model, kind)
                for (run in runs) {
                    val fs = InMemoryFileSystem()
                    for ((name, content) in run.initialFiles) fs.upsert(name, content)

                    val client = ReplayLlmClient(run.calls)
                    val engine = WorkflowEngine(
                        PromptEnricher.PASSTHROUGH,
                        client,
                        guardians = emptyList(),
                    )
                    group.total++
                    var l = 0
                    val result = engine.run(run.enginePrompt, fs, onEvent = {
                        if (it !is StreamEvent.InvalidLlmOutputWarning) return@run
                        group.parseFails++
                        if (l++ >= 2) {
                            println("=======ERROR=======")
                            println("=======ERROR=======")
                            println("=======ERROR=======")
                            println(it.parseErrors.joinToString("\n"))
                            println()
                            println()
                            println(it.chatExchange.output)
                        }
                    })
                    if (result is EngineResult.Success) {
                        group.successes++
                    }
                }
                group
            }
            .forEach {
                println("Group ${it.modelName} / ${it.promptKind}: replayed runs: ${it.total}, successes: ${it.successes} (${it.parseFails} parse failures)")
            }
    }
}
