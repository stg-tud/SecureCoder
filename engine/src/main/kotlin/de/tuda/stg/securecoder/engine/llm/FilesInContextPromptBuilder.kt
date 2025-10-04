package de.tuda.stg.securecoder.engine.llm

import de.tuda.stg.securecoder.engine.file.FileSystem

object FilesInContextPromptBuilder {
    fun build(files: Iterable<FileSystem.File>) = buildString {
        appendLine("The following files are in the context:")
        for (file in files) {
            appendLine("<<<FILE path=\"${file.name()}\">>>")
            append(file.content())
            appendLine("<<<END FILE>>>")
        }
    }
}
