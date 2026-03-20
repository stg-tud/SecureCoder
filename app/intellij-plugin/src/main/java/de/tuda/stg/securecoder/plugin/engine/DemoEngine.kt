package de.tuda.stg.securecoder.plugin.engine

import de.tuda.stg.securecoder.engine.Engine
import de.tuda.stg.securecoder.engine.file.edit.Changes
import de.tuda.stg.securecoder.engine.file.edit.Changes.SearchReplace
import de.tuda.stg.securecoder.engine.file.edit.Changes.SearchedText
import de.tuda.stg.securecoder.engine.stream.ProposalId
import de.tuda.stg.securecoder.engine.stream.StreamEvent
import de.tuda.stg.securecoder.engine.workflow.GuardianExecutor.GuardianResult
import de.tuda.stg.securecoder.filesystem.FileSystem
import de.tuda.stg.securecoder.guardian.File
import de.tuda.stg.securecoder.guardian.Location
import de.tuda.stg.securecoder.guardian.RuleRef
import de.tuda.stg.securecoder.guardian.Violation
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.toList

class DemoEngine : Engine {

    override suspend fun run(
        prompt: String,
        filesystem: FileSystem,
        onEvent: suspend (StreamEvent) -> Unit,
        context: Engine.Context?
    ): Engine.EngineResult {
        print(filesystem.allFiles().toList().map { it.name() })

        val targetFile = "file:///Users/david/IdeaProjects/untitled/src/ArchiveUtils.kt"
        val unsafeProposalId = ProposalId.newId()

        val unsafeCode = """
            fun unzip(zipFile: File, destDir: File) {
                ZipInputStream(FileInputStream(zipFile)).use { zis ->
                    var entry = zis.nextEntry
                    while (entry != null) {
                        val newFile = File(destDir, entry.name)
                        if (entry.isDirectory) {
                            newFile.mkdirs()
                        } else {
                            newFile.parentFile.mkdirs()
                            FileOutputStream(newFile).use { fos ->
                                zis.copyTo(fos)
                            }
                        }
                        entry = zis.nextEntry
                    }
                }
            }
        """.trimIndent()

        val unsafeChanges = Changes(
            searchReplaces = listOf(
                SearchReplace(
                    fileName = targetFile,
                    searchedText = SearchedText.append(),
                    replaceText = unsafeCode
                )
            )
        )
        delay(4800)

        onEvent(StreamEvent.ProposedEdits(unsafeProposalId, unsafeChanges))
        onEvent(StreamEvent.ValidationStarted(unsafeProposalId))

        delay(2800)

        val zipSlipViolation = Violation(
            rule = RuleRef(
                id = "S6096",
                name = "Zip Slip Vulnerability",
                description = "Extracting archives without validating the destination path can allow arbitrary file overwrite.",
                cwe = "CWE-22",
                owasp = "A01:2021-Broken Access Control"
            ),
            message = "Unsafe zip extraction. The code uses 'entry.name' directly without verifying the resulting path is within 'destDir'.",
            location = Location(targetFile, 5, 6),
            hardReject = true,
            raw = "val newFile = File(destDir, entry.name)"
        )

        val guardianResult = GuardianResult(
            violations = listOf(zipSlipViolation),
            files = listOf(File(targetFile, unsafeCode))
        )

        onEvent(StreamEvent.GuardianWarning(unsafeProposalId, guardianResult))

        // Simulate LLM "thinking" about the fix
        delay(800)

        // --- 3. Generate Second Proposal (Safe Fix) ---
        val safeProposalId = ProposalId.newId()

        val safeCode = """
            fun unzip(zipFile: File, destDir: File) {
                val destDirPath = destDir.canonicalPath
                ZipInputStream(FileInputStream(zipFile)).use { zis ->
                    var entry = zis.nextEntry
                    while (entry != null) {
                        val newFile = File(destDir, entry.name)
                        
                        if (!newFile.canonicalPath.startsWith(destDirPath)) {
                            throw SecurityException("Zip entry is outside of the target dir: " + entry.name)
                        }

                        if (entry.isDirectory) {
                            newFile.mkdirs()
                        } else {
                            newFile.parentFile.mkdirs()
                            FileOutputStream(newFile).use { fos ->
                                zis.copyTo(fos)
                            }
                        }
                        entry = zis.nextEntry
                    }
                }
            }
        """.trimIndent()

        val safeChanges = Changes(
            searchReplaces = listOf(
                SearchReplace(
                    fileName = targetFile,
                    searchedText = SearchedText.append(),
                    replaceText = safeCode
                )
            )
        )
        delay(3200)

        onEvent(StreamEvent.ProposedEdits(safeProposalId, safeChanges))
        onEvent(StreamEvent.ValidationStarted(safeProposalId))

        // Simulate successful validation
        delay(1200)
        onEvent(StreamEvent.ValidationSucceeded(safeProposalId))

        // --- 4. Return Final Result ---
        return Engine.EngineResult.Success(safeChanges)
    }
}