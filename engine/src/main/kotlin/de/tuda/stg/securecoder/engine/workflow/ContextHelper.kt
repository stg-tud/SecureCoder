package de.tuda.stg.securecoder.engine.workflow

import de.tuda.stg.securecoder.engine.Engine
import de.tuda.stg.securecoder.engine.file.FileSystem
import kotlinx.coroutines.flow.toList
import org.slf4j.LoggerFactory

private val logger = LoggerFactory.getLogger("ContextResolver")

suspend fun resolveContext(context: Engine.Context?, fileSystem: FileSystem): List<FileSystem.File> {
    if (context == null) {
        return fileSystem.allFiles().toList()
    }
    return context.files.mapNotNull {
        val file = fileSystem.getFile(it)
        if (file == null) {
            logger.warn("File $it specified in context not found on the filesystem")
        }
        file
    }
}
