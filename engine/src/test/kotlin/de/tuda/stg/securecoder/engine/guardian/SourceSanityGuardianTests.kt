package de.tuda.stg.securecoder.engine.guardian

import de.tuda.stg.securecoder.filesystem.InMemoryFileSystem
import de.tuda.stg.securecoder.guardian.AnalyzeRequest
import de.tuda.stg.securecoder.guardian.File
import kotlinx.coroutines.runBlocking
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class SourceSanityGuardianTests {
    @Test
    fun rejects_placeholder_source_output() {
        runBlocking {
            val fileSystem = InMemoryFileSystem()
            fileSystem.upsert("broken.js", "...")

            val response = SourceSanityGuardian().run(
                AnalyzeRequest(
                    fileSystem = fileSystem,
                    files = listOf(File("broken.js", "...")),
                )
            )

            assertEquals(1, response.violations.size)
            assertEquals("source-placeholder-output", response.violations.single().rule.id)
            assertEquals(true, response.violations.single().hardReject)
        }
    }

    @Test
    fun rejects_structured_transport_artifacts_mixed_into_source() {
        runBlocking {
            val broken = """
                #include <string>
                bool ok() { return true; }
                }]}{#include <string>
                bool ok() { return true; }
            """.trimIndent()
            val fileSystem = InMemoryFileSystem()
            fileSystem.upsert("broken.cpp", broken)

            val response = SourceSanityGuardian().run(
                AnalyzeRequest(
                    fileSystem = fileSystem,
                    files = listOf(File("broken.cpp", broken)),
                )
            )

            assertTrue(response.violations.any { it.rule.id == "source-transport-artifact" })
        }
    }

    @Test
    fun rejects_failure_strings_instead_of_source() {
        runBlocking {
            val broken = "I failed to generate valid code. Retries exceeded."
            val fileSystem = InMemoryFileSystem()
            fileSystem.upsert("broken.py", broken)

            val response = SourceSanityGuardian().run(
                AnalyzeRequest(
                    fileSystem = fileSystem,
                    files = listOf(File("broken.py", broken)),
                )
            )

            assertTrue(response.violations.any { it.rule.id == "source-failure-output" })
        }
    }
}
