package de.tuda.stg.securecoder.engine.workflow

import de.tuda.stg.securecoder.engine.llm.ChatMessage
import de.tuda.stg.securecoder.engine.stream.StreamEvent
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.StandardOpenOption
import java.time.Instant

interface WorkflowTraceLogger {
    suspend fun log(record: WorkflowTraceRecord)

    companion object {
        val NO_OP: WorkflowTraceLogger = object : WorkflowTraceLogger {
            override suspend fun log(record: WorkflowTraceRecord) = Unit
        }
    }
}

@Serializable
data class WorkflowTraceRecord(
    val runId: String,
    val timestamp: String = Instant.now().toString(),
    val type: String,
    val format: String? = null,
    val reviewMode: String? = null,
    val attempt: Int? = null,
    val phase: String? = null,
    val messages: List<TraceChatMessage> = emptyList(),
    val text: String? = null,
    val errors: List<String> = emptyList(),
)

@Serializable
data class TraceChatMessage(
    val role: String,
    val content: String,
)

class PersistentWorkflowTraceLogger(
    private val path: Path,
    private val json: Json = Json { prettyPrint = false },
) : WorkflowTraceLogger {
    private val lock = Any()

    init {
        path.parent?.let { Files.createDirectories(it) }
    }

    override suspend fun log(record: WorkflowTraceRecord) {
        val line = json.encodeToString(record) + "\n"
        synchronized(lock) {
            Files.writeString(
                path,
                line,
                StandardOpenOption.CREATE,
                StandardOpenOption.WRITE,
                StandardOpenOption.APPEND,
            )
        }
    }
}

internal fun List<ChatMessage>.toTraceMessages(): List<TraceChatMessage> =
    map { TraceChatMessage(it.role.name.lowercase(), it.content) }

internal fun StreamEvent.describe(): String = when (this) {
    is StreamEvent.SendDebugMessage -> "SendDebugMessage(title=$title)"
    is StreamEvent.EnrichmentWarning -> "EnrichmentWarning(error=$errorMessage)"
    is StreamEvent.InvalidLlmOutputWarning -> "InvalidLlmOutputWarning(errors=${parseErrors.size})"
    is StreamEvent.ProposedEdits -> "ProposedEdits(id=$id, files=${changes.searchReplaces.map { it.fileName }.distinct()})"
    is StreamEvent.ValidationStarted -> "ValidationStarted(id=$id)"
    is StreamEvent.GuardianWarning -> "GuardianWarning(id=$id, violations=${result.violations.size}, failures=${result.failures.size})"
    is StreamEvent.ValidationSucceeded -> "ValidationSucceeded(id=$id)"
}
