package de.tuda.stg.securecoder.engine.guardian

import de.tuda.stg.securecoder.filesystem.InMemoryFileSystem
import de.tuda.stg.securecoder.guardian.AnalyzeRequest
import de.tuda.stg.securecoder.guardian.File
import kotlinx.coroutines.runBlocking
import java.io.IOException
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class GoSyntaxGuardianTests {
    @Test
    fun reports_go_syntax_errors_when_gofmt_is_available() {
        if (!commandAvailable("gofmt")) return
        runBlocking {
            val fileSystem = InMemoryFileSystem()
            val content = "package main\n\nfunc main( {\n"
            fileSystem.upsert("main.go", content)

            val response = GoSyntaxGuardian().run(
                AnalyzeRequest(
                    fileSystem = fileSystem,
                    files = listOf(File("main.go", content)),
                )
            )

            assertEquals(1, response.violations.size)
            assertEquals("go-syntax", response.violations.single().rule.id)
            assertEquals(true, response.violations.single().hardReject)
        }
    }

    @Test
    fun skips_validation_when_gofmt_is_unavailable() {
        runBlocking {
            val fileSystem = InMemoryFileSystem()
            val content = "package main\n\nfunc main( {\n"
            fileSystem.upsert("main.go", content)

            val response = GoSyntaxGuardian("__definitely_missing_gofmt__").run(
                AnalyzeRequest(
                    fileSystem = fileSystem,
                    files = listOf(File("main.go", content)),
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
