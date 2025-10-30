package de.tuda.stg.securecoder.engine

import de.tuda.stg.securecoder.engine.file.FileSystem
import de.tuda.stg.securecoder.engine.file.edit.Changes
import de.tuda.stg.securecoder.engine.stream.StreamEvent

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
            data class ValidationFailure(val maxGuardianRetries: Int) : Failure
            object GenerationFailure : Failure
        }
    }
}
