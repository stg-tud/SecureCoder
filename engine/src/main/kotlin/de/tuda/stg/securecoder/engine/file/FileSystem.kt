package de.tuda.stg.securecoder.engine.file

interface FileSystem {
    /** Does not return directories */
    fun iterateAllFiles() : Iterable<File>

    /** This must be a name you receive from [iterateAllFiles] */
    fun getFile(name : String) : File?

    interface File {
        /** File name might be relative or absolute. But must be unique in a file system */
        fun name(): String

        fun content(): String
    }
}
