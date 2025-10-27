package de.tuda.stg.securecoder.engine.workflow

import de.tuda.stg.securecoder.engine.Engine
import de.tuda.stg.securecoder.engine.file.FileSystem
import kotlinx.coroutines.flow.toList

suspend fun resolveContext(context: Engine.Context?, fileSystem: FileSystem): List<FileSystem.File> {
    if (context == null) {
        return fileSystem.allFiles().toList()
    }
    return context.files.map { fileSystem.getFile(it)!! }
}
