package de.tuda.stg.securecoder.plugin.engine.event

import de.tuda.stg.securecoder.engine.Engine.EngineResult

object EngineResultMapper {
    fun map(result: EngineResult): UiStreamEvent {
        return when (result) {
            EngineResult.Failure.GenerationFailure -> {
                StreamEventMapper.createGenerationError()
            }
            is EngineResult.Failure.ValidationFailure -> {
                StreamEventMapper.createValidationError(result.maxGuardianRetries)
            }
            is EngineResult.Success -> UiStreamEvent.EditFiles(result.changes)
        }
    }
}
