package de.tuda.stg.securecoder.engine.file

import de.tuda.stg.securecoder.filesystem.FileSystem

object FilesInContextPromptBuilder {
    suspend fun build(files: Iterable<FileSystem.File>, edit: Boolean = false) = buildString {
        if (files.count() == 0) {
            appendLine("You have no files in the context.")
            appendLine("If you saw files they are only part of the prompt and dont exists yet!")
            if (edit) {
                appendLine("You may create new files (keep in mind that searched text needs to be empty in this case!)")
            }
            return@buildString
        }
        appendLine("The following files are in the context:")
        for (file in files) {
            append("<<<FILE path=\"${file.name()}\">>>")
            append(file.content())
            appendLine("<<<END FILE>>>")
        }
    }
}