package de.tuda.stg.securecoder.engine.guardian

import de.tuda.stg.securecoder.guardian.AnalyzeRequest
import de.tuda.stg.securecoder.guardian.AnalyzeResponse
import de.tuda.stg.securecoder.guardian.Guardian
import de.tuda.stg.securecoder.guardian.Location
import de.tuda.stg.securecoder.guardian.RuleRef
import de.tuda.stg.securecoder.guardian.Violation
import java.io.IOException
import java.nio.file.Files

class GoSyntaxGuardian(
    private val gofmtBinary: String = "gofmt",
) : Guardian {
    override suspend fun run(req: AnalyzeRequest): AnalyzeResponse {
        val goFiles = req.files.filter { it.name.endsWith(".go") }
        if (goFiles.isEmpty()) return AnalyzeResponse(emptyList())

        val tempDir = Files.createTempDirectory("go-guardian-")
        return try {
            val violations = goFiles.mapNotNull { file ->
                val tempFile = tempDir.resolve(file.name.substringAfterLast('/'))
                Files.writeString(tempFile, file.content)
                val process = try {
                    ProcessBuilder(gofmtBinary, "-e", tempFile.toString())
                        .redirectErrorStream(true)
                        .start()
                } catch (_: IOException) {
                    return AnalyzeResponse(emptyList())
                }
                val output = process.inputStream.bufferedReader().readText()
                if (process.waitFor() == 0) null else buildViolation(file.name, output)
            }
            AnalyzeResponse(violations)
        } finally {
            tempDir.toFile().deleteRecursively()
        }
    }

    private fun buildViolation(fileName: String, output: String): Violation {
        val line = Regex(""":(\d+):(\d+)""")
            .find(output.lineSequence().firstOrNull().orEmpty())
            ?.groupValues
            ?.getOrNull(1)
            ?.toIntOrNull()
        val message = output
            .lineSequence()
            .map { it.trim() }
            .filter { it.isNotEmpty() }
            .firstOrNull()
            ?: "Go syntax error"
        return Violation(
            rule = RuleRef(id = "go-syntax", name = "go_syntax_error"),
            message = message,
            location = Location(file = fileName, startLine = line),
            hardReject = true,
            confidence = "HIGH",
        )
    }
}
