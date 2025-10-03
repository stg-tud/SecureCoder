package de.tuda.stg.securecoder.engine

import de.tuda.stg.securecoder.engine.stream.EventIcon

interface Engine {
    suspend fun start(
        prompt: String,
        onEvent: suspend (title: String, description: String, icon: EventIcon) -> Unit,
        onComplete: suspend () -> Unit
    )
}
