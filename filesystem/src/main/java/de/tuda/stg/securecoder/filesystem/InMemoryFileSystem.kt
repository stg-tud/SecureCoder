package de.tuda.stg.securecoder.filesystem

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

class InMemoryFileSystem : FileSystem {
    private val files = linkedMapOf<String, MemFile>()

    override fun allFiles(): Flow<FileSystem.File> = flow { files.values.forEach { emit(it) } }

    override fun getFile(name: String): FileSystem.File? = files[name]

    override suspend fun upsert(name: String, content: String) {
        files[name] = MemFile(name, content)
    }

    private data class MemFile(val fileName: String, var current: String) : FileSystem.File {
        override fun name(): String = fileName
        override suspend fun content(): String = current
    }
}
