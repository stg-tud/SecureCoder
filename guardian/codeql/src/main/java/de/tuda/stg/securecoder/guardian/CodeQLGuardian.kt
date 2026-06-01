package de.tuda.stg.securecoder.guardian

import de.tuda.stg.securecoder.filesystem.FileSystemToDiskWriter
import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.attribute.PosixFilePermission
import kotlin.io.path.exists

class CodeQLGuardian(
    private val codeQlBinary: String = "codeql",
    private val enabledLanguages: Set<String>? = null,
    private val violationTriage: ViolationTriage? = null,
    private val queryPackCandidatesByLanguage: Map<String, List<String>> = defaultQueryPackCandidates(),
) : Guardian {
    override suspend fun run(req: AnalyzeRequest): AnalyzeResponse {
        val workRoot = Files.createTempDirectory("codeql-guardian-")
        var sourceRoot: Path? = null
        println("using work root $workRoot")
        try {
            sourceRoot = FileSystemToDiskWriter.writeFileSystemToTemp(req.fileSystem)

            val languages = detectLanguages(req.files)
                .filter { enabledLanguages == null || it in enabledLanguages }
            val sarifPaths = mutableListOf<Path>()
            println("detected languages $languages for files ${req.files.joinToString(",")}")
            
            val runner = CodeQLRunner(codeQlBinary)
            for (language in languages) {
                val dbDir = workRoot.resolve("db-$language")
                val outSarif = workRoot.resolve("results-$language.sarif")

                val buildCmd = detectBuildCommand(language, sourceRoot)
                val queryPacks = queryPacksForLanguage(language)
                if (queryPacks.isEmpty()) continue

                try {
                    runner.createDatabase(language, sourceRoot, dbDir, buildCmd)
                } catch (e: IllegalStateException) {
                    if (shouldSkipCreateFailure(language, e.message.orEmpty())) {
                        println("Skipping CodeQL for $language after database create failure: ${e.message}")
                        continue
                    }
                    throw e
                }

                val analyzed = analyzeWithFallback(
                    runner = runner,
                    language = language,
                    dbDir = dbDir,
                    queryPacks = queryPacks,
                    outSarif = outSarif,
                )
                if (!analyzed) continue

                if (outSarif.exists()) sarifPaths.add(outSarif)
            }

            val violations = sarifPaths.flatMap { path ->
                val text = Files.readString(path)
                parseSarifToViolations(text)
            }
            val triagedViolations = violationTriage?.triage(req, violations) ?: violations
            return AnalyzeResponse(triagedViolations)
        } finally {
            sourceRoot?.toFile()?.deleteRecursively()
            workRoot.toFile().deleteRecursively()
        }
    }

    internal fun detectBuildCommand(language: String, sourceRoot: Path): String? {
        if (language == "python") {
            return "/usr/bin/true"
        }
        if (language == "javascript") {
            return writeBuildScript(
                sourceRoot,
                ".securecoder-codeql-js-build.sh",
                """
                #!/bin/sh
                find . \( -name "*.js" -o -name "*.mjs" -o -name "*.cjs" \) -exec node --check {} \;
                """.trimIndent(),
            )
        }
        if (language == "go") {
            return writeBuildScript(
                sourceRoot,
                ".securecoder-codeql-go-build.sh",
                """
                #!/bin/sh
                find . -name "*.go" -exec go build {} \;
                """.trimIndent(),
            )
        }
        if (language == "cpp") {
            return writeBuildScript(
                sourceRoot,
                ".securecoder-codeql-cpp-build.sh",
                """
                #!/bin/sh
                find . -name "*.c" -exec clang -std=c11 -c {} -o /tmp/codeql-snippet-c.o \;
                find . \( -name "*.cc" -o -name "*.cpp" -o -name "*.cxx" \) -exec clang++ -std=c++17 -c {} -o /tmp/codeql-snippet-cpp.o \;
                """.trimIndent(),
            )
        }
        if (language != "java") {
            return null
        }
        val gradleKts = java.io.File(sourceRoot.toFile(), "build.gradle.kts")
        val gradle = java.io.File(sourceRoot.toFile(), "build.gradle")
        val mvn = java.io.File(sourceRoot.toFile(), "pom.xml")
        return when {
            gradleKts.exists() || gradle.exists() -> "./gradlew --no-daemon -q clean build || gradle --no-daemon -q clean build"
            mvn.exists() -> "mvn -q -DskipTests package"
            else -> "find . -name \"*.java\" -exec javac {} +"
        }
    }

    internal fun queryPackForLanguage(language: String): String? = queryPacksForLanguage(language).firstOrNull()

    internal fun queryPacksForLanguage(language: String): List<String> = queryPackCandidatesByLanguage[language].orEmpty()

    companion object {
        fun defaultQueryPackCandidates(): Map<String, List<String>> = mapOf(
            "javascript" to listOf(
                "codeql/javascript-queries:codeql-suites/javascript-code-scanning.qls",
                "codeql/javascript-queries:codeql-suites/javascript-security-extended.qls",
            ),
            "python" to listOf(
                "codeql/python-queries:codeql-suites/python-code-scanning.qls",
                "codeql/python-queries:codeql-suites/python-security-extended.qls",
            ),
            "java" to listOf("codeql/java-queries:codeql-suites/java-security-extended.qls"),
            "cpp" to listOf(
                "codeql/cpp-queries:codeql-suites/cpp-code-scanning.qls",
                "codeql/cpp-queries:codeql-suites/cpp-security-extended.qls",
            ),
            "csharp" to listOf("codeql/csharp-queries:codeql-suites/csharp-security-extended.qls"),
            "ruby" to listOf("codeql/ruby-queries:codeql-suites/ruby-security-extended.qls"),
            "go" to listOf(
                "codeql/go-queries:codeql-suites/go-code-scanning.qls",
                "codeql/go-queries:codeql-suites/go-security-extended.qls",
            ),
            "swift" to listOf("codeql/swift-queries:codeql-suites/swift-security-extended.qls"),
        )
    }

    private fun analyzeWithFallback(
        runner: CodeQLRunner,
        language: String,
        dbDir: Path,
        queryPacks: List<String>,
        outSarif: Path,
    ): Boolean {
        var lastFailure: IllegalStateException? = null
        for ((index, queryPack) in queryPacks.withIndex()) {
            try {
                runner.analyzeDatabase(dbDir, queryPack, outSarif)
                return true
            } catch (e: IllegalStateException) {
                lastFailure = e
                if (index + 1 < queryPacks.size && shouldRetryWithFallback(language, e.message.orEmpty())) {
                    println("Retrying CodeQL for $language with fallback pack after failure: ${e.message}")
                    continue
                }
                if (shouldSkipAnalyzeFailure(language, e.message.orEmpty())) {
                    println("Skipping CodeQL for $language after analyze failure: ${e.message}")
                    return false
                }
                throw e
            }
        }
        if (lastFailure != null && shouldSkipAnalyzeFailure(language, lastFailure.message.orEmpty())) {
            println("Skipping CodeQL for $language after repeated analyze failures: ${lastFailure.message}")
            return false
        }
        throw lastFailure ?: IllegalStateException("CodeQL analyze failed for $language without details")
    }

    private fun shouldRetryWithFallback(language: String, message: String): Boolean =
        language in setOf("python", "javascript", "go", "cpp") && isRecoverableToolFailure(message)

    private fun shouldSkipCreateFailure(language: String, message: String): Boolean =
        language in setOf("cpp", "javascript", "python", "go") &&
            (
                message.contains("No supported build system detected.") ||
                    message.contains("no required module provides package", ignoreCase = true) ||
                    message.contains("No such file or directory", ignoreCase = true) ||
                    message.contains("fatal error:", ignoreCase = true) ||
                    message.contains("undefined reference", ignoreCase = true) ||
                    message.contains("Malformed expansion", ignoreCase = true) ||
                    message.contains("unexpected EOF while looking for matching", ignoreCase = true) ||
                    message.contains("syntax error: unexpected end of file", ignoreCase = true) ||
                    isRecoverableToolFailure(message)
                )

    private fun shouldSkipAnalyzeFailure(language: String, message: String): Boolean =
        language in setOf("python", "javascript", "go", "cpp") && isRecoverableToolFailure(message)

    private fun isRecoverableToolFailure(message: String): Boolean =
        message.contains("SIGSEGV") ||
            message.contains("OutOfMemoryError") ||
            message.contains("NullPointerException") ||
            message.contains("EvaluationSchedule.allocateDfsSeqnums") ||
            message.contains("QueryEvaluator.setPriorityIfNecessary") ||
            message.contains("Oops! A fatal internal error occurred", ignoreCase = true) ||
            message.contains("fatal internal error occurred", ignoreCase = true) ||
            message.contains("hs_err_pid") ||
            message.contains("Cannot invoke \"com.google.re2j.Machine.init(int)\"") ||
            message.contains("OpenJDK Runtime Environment") ||
            message.contains("Aborted")

    private fun writeBuildScript(sourceRoot: Path, fileName: String, body: String): String {
        val scriptPath = sourceRoot.resolve(fileName)
        Files.writeString(scriptPath, body + "\n")
        runCatching {
            Files.setPosixFilePermissions(
                scriptPath,
                setOf(
                    PosixFilePermission.OWNER_READ,
                    PosixFilePermission.OWNER_WRITE,
                    PosixFilePermission.OWNER_EXECUTE,
                ),
            )
        }
        return scriptPath.toAbsolutePath().toString()
    }
}
