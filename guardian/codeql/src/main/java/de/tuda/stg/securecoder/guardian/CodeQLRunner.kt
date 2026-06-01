package de.tuda.stg.securecoder.guardian

import java.io.File
import java.nio.file.Path
import kotlin.io.path.absolutePathString

class CodeQLRunner(
    private val codeqlBinary: String = "codeql",
) {
    private val createThreads = "1"
    private val analyzeThreads = "1"
    private val createRamMb = "2048"
    private val analyzeRamMb = "2048"

    fun createDatabase(language: String, sourceRoot: Path, dbDir: Path, buildCommand: String?) {
        val args = mutableListOf(
            codeqlBinary, "database", "create", dbDir.absolutePathString(),
            "--language=$language",
            "--source-root", sourceRoot.absolutePathString(),
            "--threads=$createThreads",
            "--ram=$createRamMb",
        )
        if (buildCommand != null) {
            args.add("--command=$buildCommand")
        }
        runProcess(args, sourceRoot)
    }

    fun analyzeDatabase(dbDir: Path, queryPack: String, outSarif: Path) {
        val args = listOf(
            codeqlBinary, "database", "analyze",
            dbDir.absolutePathString(),
            queryPack,
            "--format=sarifv2.1.0",
            "--output", outSarif.absolutePathString(),
            "--threads=$analyzeThreads",
            "--ram=$analyzeRamMb",
        )
        runProcess(args, dbDir)
    }

    private fun runProcess(args: List<String>, cwd: Path?): String {
        val pb = ProcessBuilder(args)
            .redirectErrorStream(true)
        if (cwd != null) {
            pb.directory(cwd.toFile())
        }
        sanitizeEnvironment(pb.environment())
        val proc = pb.start()
        val output = proc.inputStream.bufferedReader().use { it.readText() }
        val code = proc.waitFor()
        if (code != 0) {
            throw IllegalStateException("Command failed (${args.joinToString(" ")}) with exit code $code. Output:\n$output")
        }
        return output
    }

    fun getToolVersion(): String {
        val output = runProcess(listOf(codeqlBinary, "--version"), null)
        val firstLine = output.lineSequence().firstOrNull()?.trim()
            ?: throw IllegalStateException("CodeQL --version produced no output")
        // "CodeQL command-line toolchain release 2.18.0"
        val versionRegex = Regex("\\b\\d+(?:\\.\\d+)+\\b")
        val match = versionRegex.find(firstLine)
        if (match != null) return match.value
        throw IllegalStateException("Unable to parse CodeQL version from: '$firstLine'")
    }

    private fun sanitizeEnvironment(environment: MutableMap<String, String>) {
        val separator = File.pathSeparator
        val systemPaths = listOf("/usr/bin", "/bin", "/usr/sbin", "/sbin")
        val existing = environment["PATH"]
            ?.split(separator)
            ?.filter { entry ->
                entry.isNotBlank() &&
                    !entry.contains(".venv/bin") &&
                    !entry.contains("Library/Application Support/uv/python")
            }
            .orEmpty()
        environment["PATH"] = (systemPaths + existing.filterNot { it in systemPaths }).joinToString(separator)
        environment.remove("VIRTUAL_ENV")
        environment.remove("PYTHONPATH")
        environment.remove("PYTHONHOME")
        environment["CODEQL_JAVA_ARGS"] = "-Xmx${analyzeRamMb}m"
    }
}
