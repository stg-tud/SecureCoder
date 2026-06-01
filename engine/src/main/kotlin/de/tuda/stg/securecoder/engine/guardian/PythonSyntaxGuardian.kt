package de.tuda.stg.securecoder.engine.guardian

import de.tuda.stg.securecoder.guardian.AnalyzeRequest
import de.tuda.stg.securecoder.guardian.AnalyzeResponse
import de.tuda.stg.securecoder.guardian.Guardian
import de.tuda.stg.securecoder.guardian.Location
import de.tuda.stg.securecoder.guardian.RuleRef
import de.tuda.stg.securecoder.guardian.Violation
import java.io.IOException
import java.nio.file.Files

class PythonSyntaxGuardian(
    private val pythonBinary: String = "python3",
) : Guardian {
    override suspend fun run(req: AnalyzeRequest): AnalyzeResponse {
        val pythonFiles = req.files.filter { it.name.endsWith(".py") }
        if (pythonFiles.isEmpty()) {
            return AnalyzeResponse(emptyList())
        }

        val sourceRoot = Files.createTempDirectory("python-guardian-")
        return try {
            val violations = pythonFiles.mapNotNull { file ->
                val relativeName = file.name.removePrefix("/").ifBlank { "snippet.py" }
                val target = sourceRoot.resolve(relativeName)
                target.parent?.let(Files::createDirectories)
                Files.writeString(target, file.content)
                val process = try {
                    ProcessBuilder(
                        pythonBinary,
                        "-m",
                        "py_compile",
                        target.toString(),
                    )
                        .redirectErrorStream(true)
                        .start()
                } catch (_: IOException) {
                    return AnalyzeResponse(emptyList())
                }
                val output = process.inputStream.bufferedReader().readText()
                if (process.waitFor() == 0) {
                    null
                } else {
                    buildViolation(file.name, output)
                }
            }
            AnalyzeResponse(violations)
        } finally {
            sourceRoot.toFile().deleteRecursively()
        }
    }

    private fun buildViolation(fileName: String, output: String): Violation {
        val line = Regex("""line (\d+)""")
            .find(output)
            ?.groupValues
            ?.getOrNull(1)
            ?.toIntOrNull()
        val message = output
            .lineSequence()
            .map { it.trim() }
            .filter { it.isNotEmpty() }
            .lastOrNull()
            ?: "Python syntax error"
        return Violation(
            rule = RuleRef(id = "python-syntax", name = "python_syntax_error"),
            message = message,
            location = Location(file = fileName, startLine = line),
            hardReject = true,
            confidence = "HIGH",
        )
    }
}
