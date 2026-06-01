package de.tuda.stg.securecoder.engine

import de.tuda.stg.securecoder.engine.file.edit.Changes
import de.tuda.stg.securecoder.engine.stream.StreamEvent
import de.tuda.stg.securecoder.engine.workflow.GuardianRetryPolicy
import de.tuda.stg.securecoder.filesystem.FileSystem

interface Engine {
    suspend fun run(
        prompt: String,
        filesystem: FileSystem,
        onEvent: suspend (StreamEvent) -> Unit,
        context: Context? = null,
    ): EngineResult

    data class Context (val files: Set<String>)

    sealed interface EngineResult {
        data class Success(val changes: Changes) : EngineResult
        sealed interface Failure : EngineResult {
            data class ValidationFailure(
                val retryPolicy: GuardianRetryPolicy,
                val attemptsUsed: Int,
                val reason: String? = null,
            ) : Failure
            object GenerationFailure : Failure
        }
    }
}
