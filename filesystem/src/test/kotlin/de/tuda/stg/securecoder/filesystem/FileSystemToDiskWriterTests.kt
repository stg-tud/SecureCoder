package de.tuda.stg.securecoder.filesystem

import java.nio.file.Files
import kotlinx.coroutines.runBlocking
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class FileSystemToDiskWriterTests {
    @Test
    fun `single file keeps its filename when written to temp`() = runBlocking {
        val fileSystem = InMemoryFileSystem()
        fileSystem.upsert("app.py", "print('hello')\n")

        val root = FileSystemToDiskWriter.writeFileSystemToTemp(fileSystem)
        val file = root.resolve("app.py")

        assertTrue(Files.isRegularFile(file))
        assertEquals("print('hello')\n", Files.readString(file))
    }
}
