package de.tuda.stg.securecoder.engine.file

import de.tuda.stg.securecoder.engine.file.edit.ApplyChanges
import de.tuda.stg.securecoder.engine.file.edit.Changes
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

class InMemoryFileSystem : FileSystem {
    private val files = linkedMapOf<String, MemFile>()

    override fun allFiles(): Flow<FileSystem.File> = flow { files.values.forEach { emit(it) } }

    override fun getFile(name: String): FileSystem.File? = files[name]

    fun upsert(name: String, content: String) {
        files[name] = MemFile(name, content)
    }

    suspend fun applyEdits(edits: List<Changes.SearchReplace>) {
        edits.groupBy { it.fileName }.forEach { (fileName, list) ->
            val original = getFile(fileName)?.content() ?: ""
            val updated = ApplyChanges.applyInText(original, list)
            upsert(fileName, updated)
        }
    }

    private data class MemFile(val fileName: String, var current: String) : FileSystem.File {
        override fun name(): String = fileName
        override suspend fun content(): String = current
    }
}
