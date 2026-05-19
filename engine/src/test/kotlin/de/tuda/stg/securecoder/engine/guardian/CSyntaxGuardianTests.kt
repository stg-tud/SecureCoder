package de.tuda.stg.securecoder.engine.guardian

import de.tuda.stg.securecoder.filesystem.InMemoryFileSystem
import de.tuda.stg.securecoder.guardian.AnalyzeRequest
import de.tuda.stg.securecoder.guardian.File
import kotlinx.coroutines.runBlocking
import java.io.IOException
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class CSyntaxGuardianTests {
    @Test
    fun reports_c_syntax_errors_for_standard_header_files() {
        if (!commandAvailable("clang")) return
        runBlocking {
            val fileSystem = InMemoryFileSystem()
            val content = "#include <stdio.h>\nint f(){ return ; }\n"
            fileSystem.upsert("broken.c", content)

            val response = CSyntaxGuardian().run(
                AnalyzeRequest(
                    fileSystem = fileSystem,
                    files = listOf(File("broken.c", content)),
                )
            )

            assertEquals(1, response.violations.size)
            assertEquals("c-syntax", response.violations.single().rule.id)
        }
    }

    @Test
    fun skips_non_standard_header_files() {
        runBlocking {
            val fileSystem = InMemoryFileSystem()
            val content = "#include <sqlite3.h>\nint f(){ return 1; }\n"
            fileSystem.upsert("db.c", content)

            val response = CSyntaxGuardian().run(
                AnalyzeRequest(
                    fileSystem = fileSystem,
                    files = listOf(File("db.c", content)),
                )
            )

            assertTrue(response.violations.isEmpty())
        }
    }

    private fun commandAvailable(name: String): Boolean = try {
        ProcessBuilder("sh", "-c", "command -v $name >/dev/null 2>&1").start().waitFor() == 0
    } catch (_: IOException) {
        false
    }
}
