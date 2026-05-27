package de.tuda.stg.securecoder.openaibridge

import de.tuda.stg.securecoder.engine.Engine
import de.tuda.stg.securecoder.engine.file.edit.ApplyChanges.applyEdits
import de.tuda.stg.securecoder.engine.file.edit.Changes
import de.tuda.stg.securecoder.engine.llm.UsageCollectingLlmClient
import de.tuda.stg.securecoder.engine.llm.UsageStats
import de.tuda.stg.securecoder.filesystem.InMemoryFileSystem
import io.ktor.http.HttpStatusCode
import kotlinx.coroutines.flow.toList
import java.util.UUID

class AgentService(
    private val engine: Engine,
    private val usageClient: UsageCollectingLlmClient? = null,
) {
    suspend fun generateResponse(
        messages: List<ChatMessage>,
        model: String
    ): ChatCompletionResponse {
        val fileSystem = InMemoryFileSystem()
        val userPrompt = messages.lastOrNull { it.role == "user" }?.content ?: ""
        val (result, usage) = collectUsage {
            engine.run(
                prompt = "$userPrompt\nOnly create ONE file!",
                filesystem = fileSystem,
                onEvent = { event ->
                    println("Internal Agent Event: $event")
                }
            )
        }
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
            ),
            usage = usage?.toOpenAiUsage(),
        )
    }

    suspend fun generateEditResponse(request: AgentEditRequest): AgentEditResponse {
        val fileSystem = InMemoryFileSystem()
        request.files.forEach { file ->
            fileSystem.upsert(file.path, file.content)
        }
        val context = request.context_files
            ?.map { it.trim() }
            ?.filter { it.isNotEmpty() }
            ?.toSet()
            ?.takeIf { it.isNotEmpty() }
            ?.let { Engine.Context(it) }
        val (result, usage) = collectUsage {
            engine.run(
                prompt = request.prompt,
                filesystem = fileSystem,
                onEvent = { event ->
                    println("Internal Agent Event: $event")
                },
                context = context,
            )
        }
        return when (result) {
            is Engine.EngineResult.Success -> formatProjectChanges(fileSystem, result.changes, request.model, usage)
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
                message = "Agent failed to generate project edits.",
            )
        }
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

    private suspend fun formatProjectChanges(
        fileSystem: InMemoryFileSystem,
        changes: Changes,
        model: String,
        usage: UsageStats?,
    ): AgentEditResponse {
        fileSystem.applyEdits(changes.searchReplaces)
        val changedFiles = changes.searchReplaces
            .map { it.fileName }
            .distinct()
            .sorted()
        val files = fileSystem.allFiles().toList()
            .map { ProjectFile(it.name(), it.content()) }
            .sortedBy { it.path }
        return AgentEditResponse(
            id = UUID.randomUUID().toString(),
            created = System.currentTimeMillis() / 1000,
            model = model,
            files = files,
            changed_files = changedFiles,
            usage = usage?.toOpenAiUsage(),
        )
    }

    private fun UsageStats.toOpenAiUsage(): Usage = Usage(
        prompt_tokens = promptTokens,
        completion_tokens = completionTokens,
        total_tokens = totalTokens,
        estimated_cost = estimatedCost,
    )

    private suspend fun <T> collectUsage(block: suspend () -> T): Pair<T, UsageStats?> =
        usageClient?.collectUsage(block) ?: (block() to null)
}

class OpenAiBridgeException(
    val status: HttpStatusCode,
    val code: String,
    override val message: String,
) : RuntimeException(message)
