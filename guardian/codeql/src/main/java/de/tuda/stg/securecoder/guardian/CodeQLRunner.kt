package de.tuda.stg.securecoder.guardian

import java.nio.file.Path
import kotlin.io.path.absolutePathString

class CodeQLRunner(
    private val codeqlBinary: String = "codeql",
) {
    fun createDatabase(language: String, sourceRoot: Path, dbDir: Path, buildCommand: String?) {
        val args = mutableListOf(
            codeqlBinary, "database", "create", dbDir.absolutePathString(),
            "--language=$language",
            "--source-root", sourceRoot.absolutePathString(),
            "--threads=0",
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
            "--threads=0",
            "--download"
        )
        runProcess(args, dbDir)
    }

    private fun runProcess(args: List<String>, cwd: Path) {
        val pb = ProcessBuilder(args)
            .directory(cwd.toFile())
            .redirectErrorStream(true)
        val proc = pb.start()
        val output = proc.inputStream.bufferedReader().use { it.readText() }
        val code = proc.waitFor()
        println(output)
        if (code != 0) {
            throw IllegalStateException("Command failed (${args.joinToString(" ")}) with exit code $code. Output:\n$output")
        }
    }
}
