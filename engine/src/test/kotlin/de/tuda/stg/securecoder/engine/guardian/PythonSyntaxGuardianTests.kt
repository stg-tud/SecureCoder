package de.tuda.stg.securecoder.engine.guardian

import de.tuda.stg.securecoder.filesystem.InMemoryFileSystem
import de.tuda.stg.securecoder.guardian.AnalyzeRequest
import de.tuda.stg.securecoder.guardian.File
import kotlinx.coroutines.runBlocking
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class PythonSyntaxGuardianTests {
    @Test
    fun reports_python_syntax_errors() {
        runBlocking {
            val fileSystem = InMemoryFileSystem()
            fileSystem.upsert(
                "broken.py",
                """
                def broken():
                    return (
                """.trimIndent()
            )

            val response = PythonSyntaxGuardian().run(
                AnalyzeRequest(
                    fileSystem = fileSystem,
                    files = listOf(File("broken.py", fileSystem.getFile("broken.py")!!.content())),
                )
            )

            assertEquals(1, response.violations.size)
            assertEquals("broken.py", response.violations.single().location.file)
            assertEquals(true, response.violations.single().hardReject)
        }
    }

    @Test
    fun ignores_valid_python_files() {
        runBlocking {
            val fileSystem = InMemoryFileSystem()
            fileSystem.upsert(
                "ok.py",
                """
                def ok():
                    return 1
                """.trimIndent()
            )

            val response = PythonSyntaxGuardian().run(
                AnalyzeRequest(
                    fileSystem = fileSystem,
                    files = listOf(File("ok.py", fileSystem.getFile("ok.py")!!.content())),
                )
            )

            assertTrue(response.violations.isEmpty())
        }
    }

    @Test
    fun handles_absolute_style_python_paths() {
        runBlocking {
            val fileSystem = InMemoryFileSystem()
            fileSystem.upsert(
                "/tmp/results_writer.py",
                """
                def write_results(value: str) -> str:
                    return value
                """.trimIndent()
            )

            val response = PythonSyntaxGuardian().run(
                AnalyzeRequest(
                    fileSystem = fileSystem,
                    files = listOf(File("/tmp/results_writer.py", fileSystem.getFile("/tmp/results_writer.py")!!.content())),
                )
            )

            assertTrue(response.violations.isEmpty())
        }
    }
}
