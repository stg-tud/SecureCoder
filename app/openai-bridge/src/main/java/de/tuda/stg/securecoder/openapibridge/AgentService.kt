package de.tuda.stg.securecoder.openapibridge

import de.tuda.stg.securecoder.engine.Engine
import de.tuda.stg.securecoder.engine.file.edit.ApplyChanges.applyEdits
import de.tuda.stg.securecoder.engine.file.edit.Changes
import de.tuda.stg.securecoder.filesystem.InMemoryFileSystem
import java.util.UUID

class AgentService(private val engine: Engine) {
    suspend fun generateResponse(
        messages: List<ChatMessage>,
        model: String
    ): ChatCompletionResponse {
        val fileSystem = InMemoryFileSystem()
        val userPrompt = messages.lastOrNull { it.role == "user" }?.content ?: ""
        val result = engine.run(
            prompt = userPrompt,
            filesystem = fileSystem,
            onEvent = { event ->
                println("Internal Agent Event: $event")
            }
        )
        val responseText = when (result) {
            is Engine.EngineResult.Success -> formatChanges(fileSystem, result.changes)
            is Engine.EngineResult.Failure.ValidationFailure -> "I failed to generate valid code. Retries exceeded."
            is Engine.EngineResult.Failure.GenerationFailure -> "I encountered an internal generation error."
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
        if (filesChanged.isEmpty()) return "No changes were made"
        if (filesChanged.size > 1) return "Changed more than one file."
        return fileSystem.getFile(filesChanged.first().fileName)?.content() ?: ""
    }
}
