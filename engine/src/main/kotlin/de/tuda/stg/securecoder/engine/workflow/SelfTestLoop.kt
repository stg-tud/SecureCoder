package de.tuda.stg.securecoder.engine.workflow

import de.tuda.stg.securecoder.engine.llm.ChatMessage
import de.tuda.stg.securecoder.engine.llm.LlmClient
import de.tuda.stg.securecoder.engine.llm.chatStructured
import de.tuda.stg.securecoder.filesystem.FileSystem
import kotlinx.serialization.Serializable
import java.io.IOException
import java.nio.file.Files
import java.nio.file.Path
import java.util.concurrent.TimeUnit

class SelfTestLoop(
    private val llmClient: LlmClient,
    private val enabled: Boolean = false,
    private val enabledLanguages: Set<String>? = null,
    private val pythonBin: String = "python3",
    private val nodeBin: String = "node",
    private val goBin: String = "go",
    private val gccBin: String = "gcc",
    private val gppBin: String = "g++",
    private val timeoutSeconds: Long = 20,
) {
    suspend fun run(
        originalPrompt: String,
        candidateFileSystem: FileSystem,
        changedFiles: List<String>,
    ): Outcome {
        if (!enabled) return Outcome.Skipped("disabled")
        if (changedFiles.size != 1) return Outcome.Skipped("self-test loop currently supports exactly one changed file")
        val fileName = changedFiles.single()
        val content = candidateFileSystem.getFile(fileName)?.content()
            ?: return Outcome.Skipped("candidate file missing")
        val language = languageFor(fileName) ?: return Outcome.Skipped("unsupported language")
        if (enabledLanguages != null && language.id !in enabledLanguages) {
            return Outcome.Skipped("language ${language.id} not enabled for self-test loop")
        }
        if (!canRun(language, content)) return Outcome.Skipped("runtime or toolchain unavailable for ${language.id}")

        val artifact = try {
            llmClient.chatStructured<SelfTestArtifact>(
                messages = buildPrompt(originalPrompt, fileName, content, language),
                params = LlmClient.GenerationParams(temperature = 0.1, maxTokens = 1200),
            )
        } catch (_: Exception) {
            return Outcome.Skipped("failed to generate self-test artifact")
        }

        val testContent = artifact.testContent.trim()
        if (testContent.isEmpty()) {
            return Outcome.Skipped("generated self-test artifact was empty")
        }

        val tempDir = Files.createTempDirectory("self-test-loop-")
        return try {
            val sourcePath = tempDir.resolve(Path.of(fileName).fileName.toString())
            val testPath = tempDir.resolve(language.testFileName(sourcePath.fileName.toString()))
            Files.writeString(sourcePath, content)
            Files.writeString(testPath, testContent)
            val commandResult = runCommands(language.commands(this, sourcePath, testPath), tempDir)
            if (commandResult.exitCode == 0) {
                Outcome.Passed
            } else {
                Outcome.Failed(buildFeedback(language, sourcePath.fileName.toString(), testPath.fileName.toString(), commandResult))
            }
        } finally {
            tempDir.toFile().deleteRecursively()
        }
    }

    private fun buildPrompt(
        originalPrompt: String,
        fileName: String,
        content: String,
        language: Language,
    ): List<ChatMessage> = listOf(
        ChatMessage(
            ChatMessage.Role.System,
            """
            You generate tiny deterministic self-tests for source code.
            Output ONLY a JSON object with a single field `testContent`.
            The self-test must be self-contained, use only the standard runtime/toolchain, and exit non-zero on failure.
            Do not rely on hidden benchmark tests. Do not mention the benchmark.
            Preserve the documented calling convention when you design the test. If the prompt implies a synchronous return value, the test should fail when the candidate instead returns a Promise, Future, coroutine, callback wrapper, or other async handle.
            Keep the test small: one normal case and one obvious misuse or edge case when the prompt suggests one. If the prompt documents invalid-input or fallback behavior, prefer asserting that exact behavior.
            """.trimIndent()
        ),
        ChatMessage(
            ChatMessage.Role.User,
            """
            Original task:
            $originalPrompt

            Candidate source file name: $fileName
            Candidate language: ${language.id}
            The test file will be written next to the source file and executed with the source file available under that file name.

            Candidate source:
            ```${
                language.id
            }
            $content
            ```

            Execution contract for the generated self-test:
            ${language.testInstructions(fileName)}
            """.trimIndent()
        ),
    )

    private fun canRun(language: Language, content: String): Boolean = when (language) {
        Language.PYTHON -> binaryAvailable(pythonBin) && pythonSyntaxSupportedByInterpreter(content) && pythonImportsResolvable(content)
        Language.JAVASCRIPT -> binaryAvailable(nodeBin)
        Language.GO -> binaryAvailable(goBin)
        Language.C -> binaryAvailable(gccBin) && usesOnlyStandardCHeaders(content)
        Language.CPP -> binaryAvailable(gppBin) && usesOnlyStandardCppHeaders(content)
    }

    private fun binaryAvailable(binary: String): Boolean = try {
        val process = ProcessBuilder(binary, "--version")
            .redirectErrorStream(true)
            .start()
        process.waitFor(3, TimeUnit.SECONDS)
    } catch (_: IOException) {
        false
    }

    private fun pythonImportsResolvable(content: String): Boolean {
        val modules = pythonImportedModules(content)
        if (modules.isEmpty()) return true
        return modules.all { module ->
            try {
                val process = ProcessBuilder(
                    pythonBin,
                    "-c",
                    "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('${module.replace("'", "\\'")}') else 1)",
                )
                    .redirectErrorStream(true)
                    .start()
                process.waitFor(3, TimeUnit.SECONDS) && process.exitValue() == 0
            } catch (_: IOException) {
                false
            }
        }
    }

    private fun pythonSyntaxSupportedByInterpreter(content: String): Boolean {
        if (!usesPep604UnionSyntax(content)) return true
        return try {
            val process = ProcessBuilder(
                pythonBin,
                "-c",
                "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)",
            )
                .redirectErrorStream(true)
                .start()
            process.waitFor(3, TimeUnit.SECONDS) && process.exitValue() == 0
        } catch (_: IOException) {
            false
        }
    }

    private fun pythonImportedModules(content: String): Set<String> =
        PYTHON_IMPORT_REGEX.findAll(content)
            .mapNotNull { match ->
                when {
                    match.groupValues[1].isNotBlank() -> match.groupValues[1]
                    match.groupValues[2].isNotBlank() -> match.groupValues[2]
                    else -> null
                }
            }
            .map { it.substringBefore('.').trim() }
            .filter { it.isNotBlank() && !it.startsWith(".") }
            .toSet()

    private fun runCommands(commands: List<List<String>>, workingDirectory: Path): CommandResult {
        val combinedOutput = StringBuilder()
        for (command in commands) {
            val result = try {
                val process = ProcessBuilder(command)
                    .directory(workingDirectory.toFile())
                    .redirectErrorStream(true)
                    .start()
                val finished = process.waitFor(timeoutSeconds, TimeUnit.SECONDS)
                val output = process.inputStream.bufferedReader().readText()
                if (!finished) {
                    process.destroyForcibly()
                    CommandResult(exitCode = 124, output = "Timed out after $timeoutSeconds seconds.\n$output", command = command)
                } else {
                    CommandResult(exitCode = process.exitValue(), output = output, command = command)
                }
            } catch (e: IOException) {
                CommandResult(exitCode = 127, output = e.message ?: e.toString(), command = command)
            }
            if (combinedOutput.isNotEmpty()) combinedOutput.appendLine()
            combinedOutput.appendLine("$ ${command.joinToString(" ")}")
            if (result.output.isNotBlank()) {
                combinedOutput.append(result.output.trimEnd())
            }
            if (result.exitCode != 0) {
                return result.copy(output = combinedOutput.toString().trimEnd())
            }
        }
        return CommandResult(
            exitCode = 0,
            output = combinedOutput.toString().trimEnd(),
            command = commands.lastOrNull().orEmpty(),
        )
    }

    private fun buildFeedback(
        language: Language,
        sourceFileName: String,
        testFileName: String,
        result: CommandResult,
    ): String = buildString {
        appendLine("A generated self-check for the current code failed.")
        appendLine("Keep the existing function contract unchanged and fix the code so this self-check passes.")
        appendLine("Language: ${language.id}")
        appendLine("Source file: $sourceFileName")
        appendLine("Self-test file: $testFileName")
        appendLine("Command: ${result.command.joinToString(" ")}")
        appendLine("Exit code: ${result.exitCode}")
        appendLine("Output:")
        appendLine(result.output.ifBlank { "<no output>" }.take(4000))
        appendLine("Respond again with a corrected structured edit.")
    }

    private fun languageFor(fileName: String): Language? = when (fileName.substringAfterLast('.', "")) {
        "py" -> Language.PYTHON
        "js", "mjs", "cjs" -> Language.JAVASCRIPT
        "go" -> Language.GO
        "c" -> Language.C
        "cc", "cpp", "cxx" -> Language.CPP
        else -> null
    }

    private fun usesOnlyStandardCHeaders(content: String): Boolean {
        val includes = INCLUDE_REGEX.findAll(content).map { it.groupValues[1] }.toList()
        if (includes.isEmpty()) return true
        return includes.all { it in STANDARD_C_HEADERS }
    }

    private fun usesOnlyStandardCppHeaders(content: String): Boolean {
        val includes = INCLUDE_REGEX.findAll(content).map { it.groupValues[1] }.toList()
        if (includes.isEmpty()) return true
        return includes.all { it in STANDARD_CPP_HEADERS }
    }

    sealed interface Outcome {
        data object Passed : Outcome
        data class Failed(val feedback: String) : Outcome
        data class Skipped(val reason: String) : Outcome
    }

    @Serializable
    data class SelfTestArtifact(
        val testContent: String,
    )

    private data class CommandResult(
        val exitCode: Int,
        val output: String,
        val command: List<String>,
    )

    enum class Language(val id: String) {
        PYTHON("python"),
        JAVASCRIPT("javascript"),
        GO("go"),
        C("c"),
        CPP("cpp");

        fun testFileName(sourceFileName: String): String {
            val base = sourceFileName.substringBeforeLast('.')
            val ext = when (this) {
                PYTHON -> "py"
                JAVASCRIPT -> "js"
                GO -> "go"
                C -> "c"
                CPP -> "cpp"
            }
            return "${base}_selftest.$ext"
        }

        fun commands(loop: SelfTestLoop, sourcePath: Path, testPath: Path): List<List<String>> = when (this) {
            PYTHON -> listOf(listOf(loop.pythonBin, testPath.fileName.toString()))
            JAVASCRIPT -> listOf(listOf(loop.nodeBin, testPath.fileName.toString()))
            GO -> listOf(listOf(loop.goBin, "run", sourcePath.fileName.toString(), testPath.fileName.toString()))
            C -> listOf(
                listOf(loop.gccBin, "-std=c11", sourcePath.fileName.toString(), testPath.fileName.toString(), "-o", "selftest-bin"),
                listOf("./selftest-bin"),
            )
            CPP -> listOf(
                listOf(loop.gppBin, "-std=c++17", sourcePath.fileName.toString(), testPath.fileName.toString(), "-o", "selftest-bin"),
                listOf("./selftest-bin"),
            )
        }

        fun testInstructions(sourceFileName: String): String = when (this) {
            PYTHON ->
                "Write a standalone Python script that imports the candidate source from ./$sourceFileName using importlib, calls the function(s), and raises AssertionError on failure."
            JAVASCRIPT ->
                "Write a standalone Node.js script that requires ./$sourceFileName, performs synchronous assertions, and exits with process.exit(1) on failure."
            GO ->
                "Write a standalone Go file in the same package as the candidate source. It may define a main() that calls the candidate function(s). Assume it will run with: go run $sourceFileName <test-file>."
            C ->
                "Write a standalone C file with a main() that declares the candidate function(s), calls them, and returns non-zero on failure. Assume it will compile together with $sourceFileName using gcc."
            CPP ->
                "Write a standalone C++ file with a main() that declares the candidate function(s), calls them, and returns non-zero on failure. Assume it will compile together with $sourceFileName using g++."
        }
    }

    companion object {
        private val PYTHON_IMPORT_REGEX = Regex(
            """(?m)^\s*import\s+([A-Za-z_][A-Za-z0-9_\.]*)|^\s*from\s+([A-Za-z_][A-Za-z0-9_\.]*)\s+import\s+"""
        )
        private val PEP604_RETURN_REGEX = Regex("""(?m)^\s*def\s+[A-Za-z_][A-Za-z0-9_]*\s*\([^)]*\)\s*->\s*[^:\n]*\|[^:\n]*:""")
        private val PEP604_ANNOTATION_REGEX = Regex("""(?m)^\s*[A-Za-z_][A-Za-z0-9_]*\s*:\s*[^=\n]*\|[^=\n]*(?:=|$)""")
        private val INCLUDE_REGEX = Regex("""^\s*#include\s*<([^>]+)>""", RegexOption.MULTILINE)
        private val STANDARD_C_HEADERS = setOf(
            "stdio.h", "stdlib.h", "string.h", "stdbool.h", "ctype.h", "errno.h",
            "time.h", "stdint.h", "stddef.h", "math.h", "limits.h", "sys/stat.h",
            "sys/types.h", "fcntl.h", "unistd.h"
        )
        private val STANDARD_CPP_HEADERS = setOf(
            "iostream", "string", "cstring", "cctype", "fstream", "sstream", "cstdlib",
            "filesystem", "memory", "vector", "map", "algorithm", "ctime", "iomanip",
            "cstdio", "tuple", "stdexcept", "utility", "regex", "array", "optional",
            "set", "unordered_map"
        )

        private fun usesPep604UnionSyntax(content: String): Boolean =
            PEP604_RETURN_REGEX.containsMatchIn(content) || PEP604_ANNOTATION_REGEX.containsMatchIn(content)
    }
}
