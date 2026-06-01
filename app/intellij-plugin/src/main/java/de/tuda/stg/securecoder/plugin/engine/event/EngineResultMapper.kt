package de.tuda.stg.securecoder.plugin.engine.event

import de.tuda.stg.securecoder.engine.Engine.EngineResult

object EngineResultMapper {
    fun map(mapper: StreamEventMapper, result: EngineResult): UiStreamEvent? {
        return when (result) {
            EngineResult.Failure.GenerationFailure -> {
                mapper.createGenerationError()
            }
            is EngineResult.Failure.ValidationFailure -> {
                mapper.createValidationError(result.retryPolicy.hardLimit)
            }
            is EngineResult.Success -> null
        }
    }
}
