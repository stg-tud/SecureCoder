package de.tuda.stg.securecoder.engine.guardian

import de.tuda.stg.securecoder.filesystem.InMemoryFileSystem
import de.tuda.stg.securecoder.guardian.AnalyzeRequest
import de.tuda.stg.securecoder.guardian.File
import kotlinx.coroutines.runBlocking
import java.io.IOException
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class JavaScriptSyntaxGuardianTests {
    @Test
    fun reports_javascript_syntax_errors_when_node_is_available() {
        if (!commandAvailable("node")) return
        runBlocking {
            val fileSystem = InMemoryFileSystem()
            val content = "function broken( { return 1; }\n"
            fileSystem.upsert("broken.js", content)

            val response = JavaScriptSyntaxGuardian().run(
                AnalyzeRequest(
                    fileSystem = fileSystem,
                    files = listOf(File("broken.js", content)),
                )
            )

            assertEquals(1, response.violations.size)
            assertEquals("javascript-syntax", response.violations.single().rule.id)
            assertEquals(true, response.violations.single().hardReject)
        }
    }

    @Test
    fun skips_validation_when_node_is_unavailable() {
        runBlocking {
            val fileSystem = InMemoryFileSystem()
            val content = "function broken( { return 1; }\n"
            fileSystem.upsert("broken.js", content)

            val response = JavaScriptSyntaxGuardian("__definitely_missing_node__").run(
                AnalyzeRequest(
                    fileSystem = fileSystem,
                    files = listOf(File("broken.js", content)),
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
