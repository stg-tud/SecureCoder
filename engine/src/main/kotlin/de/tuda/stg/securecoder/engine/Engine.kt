package de.tuda.stg.securecoder.engine

import de.tuda.stg.securecoder.engine.file.FileSystem
import de.tuda.stg.securecoder.engine.stream.StreamEvent

interface Engine {
    suspend fun start(
        prompt: String,
        filesystem: FileSystem,
        onEvent: suspend (StreamEvent) -> Unit,
    )
}
