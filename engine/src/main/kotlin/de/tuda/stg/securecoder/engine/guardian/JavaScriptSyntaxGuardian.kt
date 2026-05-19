package de.tuda.stg.securecoder.engine.guardian

import de.tuda.stg.securecoder.guardian.AnalyzeRequest
import de.tuda.stg.securecoder.guardian.AnalyzeResponse
import de.tuda.stg.securecoder.guardian.Guardian
import de.tuda.stg.securecoder.guardian.Location
import de.tuda.stg.securecoder.guardian.RuleRef
import de.tuda.stg.securecoder.guardian.Violation
import java.io.IOException
import java.nio.file.Files

class JavaScriptSyntaxGuardian(
    private val nodeBinary: String = "node",
) : Guardian {
    override suspend fun run(req: AnalyzeRequest): AnalyzeResponse {
        val jsFiles = req.files.filter { it.name.endsWith(".js") || it.name.endsWith(".mjs") || it.name.endsWith(".cjs") }
        if (jsFiles.isEmpty()) return AnalyzeResponse(emptyList())

        val tempDir = Files.createTempDirectory("js-guardian-")
        return try {
            val violations = jsFiles.mapNotNull { file ->
                val tempFile = tempDir.resolve(file.name.substringAfterLast('/'))
                Files.writeString(tempFile, file.content)
                val process = try {
                    ProcessBuilder(nodeBinary, "--check", tempFile.toString())
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
        val line = Regex(""":(\d+)""")
            .find(output.lineSequence().firstOrNull().orEmpty())
            ?.groupValues
            ?.getOrNull(1)
            ?.toIntOrNull()
        val message = output
            .lineSequence()
            .map { it.trim() }
            .filter { it.isNotEmpty() }
            .lastOrNull()
            ?: "JavaScript syntax error"
        return Violation(
            rule = RuleRef(id = "javascript-syntax", name = "javascript_syntax_error"),
            message = message,
            location = Location(file = fileName, startLine = line),
            hardReject = true,
            confidence = "HIGH",
        )
    }
}
