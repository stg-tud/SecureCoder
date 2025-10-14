package de.tuda.stg.securecoder.benchmark

import de.tuda.stg.securecoder.engine.Engine
import de.tuda.stg.securecoder.engine.file.InMemoryFileSystem
import de.tuda.stg.securecoder.engine.llm.OllamaClient
import de.tuda.stg.securecoder.engine.stream.EventIcon
import de.tuda.stg.securecoder.engine.stream.StreamEvent
import de.tuda.stg.securecoder.engine.workflow.WorkflowEngine
import de.tuda.stg.securecoder.enricher.EnricherClient
import kotlinx.coroutines.flow.toList
import kotlinx.coroutines.runBlocking
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.StandardOpenOption
import kotlin.io.path.absolutePathString

@Serializable
data class SecurityEvalItem(
    @SerialName("ID") val id: String,
    @SerialName("Prompt") val prompt: String
)

fun readDataset(jsonl: Path): List<SecurityEvalItem> {
    val json = Json { ignoreUnknownKeys = true }
    println("Reading dataset from ${jsonl.absolutePathString()}")
    return Files.readAllLines(jsonl)
        .filter { it.isNotBlank() }
        .map { json.decodeFromString<SecurityEvalItem>(it) }
}

suspend fun runSecurityEval(
    engine: Engine,
    repoRoot: Path,
    outDirName: String
) {
    val datasetPath = repoRoot.resolve("dataset.jsonl")
    val items = readDataset(datasetPath)
    val outDir = repoRoot.resolve(outDirName)
    Files.createDirectories(outDir)

    for (item in items) {
        println("Running item $item")
        val fs = InMemoryFileSystem()
        val onEvent: suspend (StreamEvent) -> Unit = { ev ->
            when (ev) {
                is StreamEvent.EditFiles -> {
                    println(ev)
                    fs.applyEdits(ev.changes.searchReplaces)
                }
                is StreamEvent.Message -> {
                    if (ev.icon != EventIcon.Info) {
                        println("ENGINE: $ev")
                    }
                }
            }
        }
        engine.start(item.prompt, fs, onEvent)
        val files = fs.allFiles().toList()
        if (files.size != 1) {
            println("Expected 1 file, but got ${files.size}")
            continue
        }
        val out = outDir.resolve(item.id)
        val file = files.first()
        println("Writing ${file.name()} to $out with content ${file.content()}")
        Files.write(out, file.content().toByteArray(), StandardOpenOption.CREATE, StandardOpenOption.TRUNCATE_EXISTING)
    }
}

fun main() = runBlocking {
    val repoDir = Path.of(System.getenv("REPO_DIR") ?: "/opt/SecurityEval")
    val outDirName = System.getenv("OUT_DIR_NAME") ?: "Testcases_Custom"

    val engine = WorkflowEngine(
        EnricherClient("http://localhost:7070"),
        OllamaClient("gpt-oss:20b")
    )
    runSecurityEval(engine, repoDir, outDirName)
    println("Generation done ${repoDir.resolve(outDirName)}")
}