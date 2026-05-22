package de.tuda.stg.securecoder.openaibridge

import de.tuda.stg.securecoder.engine.Engine
import de.tuda.stg.securecoder.engine.file.edit.ApplyChanges.applyEdits
import de.tuda.stg.securecoder.engine.file.edit.Changes
import de.tuda.stg.securecoder.filesystem.InMemoryFileSystem
import io.ktor.http.HttpStatusCode
import java.util.UUID

class AgentService(private val engine: Engine) {
    suspend fun generateResponse(
        messages: List<ChatMessage>,
        model: String
    ): ChatCompletionResponse {
        val fileSystem = InMemoryFileSystem()
        val userPrompt = messages.lastOrNull { it.role == "user" }?.content ?: ""
        val result = engine.run(
            prompt = "$userPrompt\nOnly create ONE file!",
            filesystem = fileSystem,
            onEvent = { event ->
                println("Internal Agent Event: $event")
            }
        )
        val responseText = when (result) {
            is Engine.EngineResult.Success -> formatChanges(fileSystem, result.changes)
            is Engine.EngineResult.Failure.ValidationFailure -> throw OpenAiBridgeException(
                status = HttpStatusCode.UnprocessableEntity,
                code = "validation_failure",
                message = buildString {
                    append("Agent failed validation after ${result.attemptsUsed} attempt(s)")
                    result.reason?.takeIf { it.isNotBlank() }?.let { append(": $it") }
                },
            )
            is Engine.EngineResult.Failure.GenerationFailure -> throw OpenAiBridgeException(
                status = HttpStatusCode.BadGateway,
                code = "generation_failure",
                message = "Agent failed to generate code.",
            )
        }
        return ChatCompletionResponse(
            id = UUID.randomUUID().toString(),
            created = System.currentTimeMillis() / 1000,
            model = model,
            choices = listOf(
                Choice(
                    index = 0,
                    message = ChatMessage(role = "assistant", content = responseText)
                )
            )
        )
    }

    private suspend fun formatChanges(fileSystem: InMemoryFileSystem, changes: Changes): String {
        fileSystem.applyEdits(changes.searchReplaces)
        val filesChanged = changes.searchReplaces.distinctBy { it.fileName }
        if (filesChanged.isEmpty()) {
            throw OpenAiBridgeException(
                status = HttpStatusCode.BadGateway,
                code = "empty_changes",
                message = "Agent did not produce any file content.",
            )
        }
        if (filesChanged.size > 1) {
            throw OpenAiBridgeException(
                status = HttpStatusCode.BadGateway,
                code = "multiple_files",
                message = "Agent produced more than one file for a single-file request.",
            )
        }
        val fileName = filesChanged.first().fileName
        return fileSystem.getFile(fileName)?.content()
            ?: throw OpenAiBridgeException(
                status = HttpStatusCode.BadGateway,
                code = "missing_output_file",
                message = "Agent output file could not be materialized.",
            )
    }
}

class OpenAiBridgeException(
    val status: HttpStatusCode,
    val code: String,
    override val message: String,
) : RuntimeException(message)
