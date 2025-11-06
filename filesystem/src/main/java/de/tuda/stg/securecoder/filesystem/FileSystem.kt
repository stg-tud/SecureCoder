package de.tuda.stg.securecoder.filesystem

import kotlinx.coroutines.flow.Flow

interface FileSystem {
    /** Does not return directories */
    fun allFiles(): Flow<File>

    /** This must be a name you receive from [allFiles] */
    fun getFile(name : String): File?

    suspend fun upsert(name: String, content: String)

    interface File {
        /** File name might be relative or absolute. But must be unique in a file system */
        fun name(): String

        suspend fun content(): String
    }
}
