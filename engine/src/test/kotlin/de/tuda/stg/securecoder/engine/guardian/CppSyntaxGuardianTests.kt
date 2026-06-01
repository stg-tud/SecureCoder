package de.tuda.stg.securecoder.engine.guardian

import de.tuda.stg.securecoder.filesystem.InMemoryFileSystem
import de.tuda.stg.securecoder.guardian.AnalyzeRequest
import de.tuda.stg.securecoder.guardian.File
import kotlinx.coroutines.runBlocking
import java.io.IOException
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class CppSyntaxGuardianTests {
    @Test
    fun reports_cpp_syntax_errors_for_standard_header_files() {
        if (!commandAvailable("clang++")) return
        runBlocking {
            val fileSystem = InMemoryFileSystem()
            val content = "#include <string>\nstd::string f(){ return \"x }\n"
            fileSystem.upsert("broken.cpp", content)

            val response = CppSyntaxGuardian().run(
                AnalyzeRequest(
                    fileSystem = fileSystem,
                    files = listOf(File("broken.cpp", content)),
                )
            )

            assertEquals(1, response.violations.size)
            assertEquals("cpp-syntax", response.violations.single().rule.id)
        }
    }

    @Test
    fun skips_non_standard_header_files() {
        runBlocking {
            val fileSystem = InMemoryFileSystem()
            val content = "#include <archive.h>\n#include <string>\nstd::string f(){ return \"x\"; }\n"
            fileSystem.upsert("archive.cpp", content)

            val response = CppSyntaxGuardian().run(
                AnalyzeRequest(
                    fileSystem = fileSystem,
                    files = listOf(File("archive.cpp", content)),
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
