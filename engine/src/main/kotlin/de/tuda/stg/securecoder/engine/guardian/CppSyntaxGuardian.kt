package de.tuda.stg.securecoder.engine.guardian

import de.tuda.stg.securecoder.guardian.AnalyzeRequest
import de.tuda.stg.securecoder.guardian.AnalyzeResponse
import de.tuda.stg.securecoder.guardian.Guardian
import de.tuda.stg.securecoder.guardian.Location
import de.tuda.stg.securecoder.guardian.RuleRef
import de.tuda.stg.securecoder.guardian.Violation
import java.io.IOException
import java.nio.file.Files

class CppSyntaxGuardian(
    private val clangppBinary: String = "clang++",
) : Guardian {
    override suspend fun run(req: AnalyzeRequest): AnalyzeResponse {
        val cppFiles = req.files.filter {
            it.name.endsWith(".cpp") || it.name.endsWith(".cc") || it.name.endsWith(".cxx")
        }.filter { usesOnlyStandardHeaders(it.content) }
        if (cppFiles.isEmpty()) return AnalyzeResponse(emptyList())

        val tempDir = Files.createTempDirectory("cpp-guardian-")
        return try {
            val violations = cppFiles.mapNotNull { file ->
                val tempFile = tempDir.resolve(file.name.substringAfterLast('/'))
                Files.writeString(tempFile, file.content)
                val process = try {
                    ProcessBuilder(
                        clangppBinary,
                        "-std=c++17",
                        "-fsyntax-only",
                        tempFile.toString(),
                    ).redirectErrorStream(true).start()
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
        val line = Regex(""":(\d+):\d+:""")
            .find(output.lineSequence().firstOrNull().orEmpty())
            ?.groupValues
            ?.getOrNull(1)
            ?.toIntOrNull()
        val message = output.lineSequence()
            .map { it.trim() }
            .firstOrNull { it.isNotEmpty() }
            ?: "C++ syntax error"
        return Violation(
            rule = RuleRef(id = "cpp-syntax", name = "cpp_syntax_error"),
            message = message,
            location = Location(file = fileName, startLine = line),
            hardReject = true,
            confidence = "HIGH",
        )
    }

    private fun usesOnlyStandardHeaders(content: String): Boolean {
        val includes = INCLUDE_REGEX.findAll(content).map { it.groupValues[1] }.toList()
        if (includes.isEmpty()) return true
        return includes.all { it in STANDARD_HEADERS }
    }

    companion object {
        private val INCLUDE_REGEX = Regex("""^\s*#include\s*<([^>]+)>""", RegexOption.MULTILINE)
        private val STANDARD_HEADERS = setOf(
            "iostream", "string", "cstring", "cctype", "fstream", "sstream", "cstdlib",
            "unistd.h", "filesystem", "memory", "vector", "map", "algorithm", "ctime",
            "iomanip", "cstdio", "tuple", "stdexcept", "utility", "regex", "array",
            "optional", "set", "unordered_map"
        )
    }
}
