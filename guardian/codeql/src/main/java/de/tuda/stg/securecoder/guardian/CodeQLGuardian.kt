package de.tuda.stg.securecoder.guardian

import de.tuda.stg.securecoder.filesystem.FileSystemToDiskWriter
import java.nio.file.Files
import java.nio.file.Path
import kotlin.io.path.absolutePathString
import kotlin.io.path.exists

class CodeQLGuardian(
    private val codeqlBinary: String = "codeql",
    private val defaultQueryPacksByLanguage: Map<String, String> = mapOf(
        "javascript" to "codeql/javascript-queries",
        "python" to "codeql/python-queries",
        "java" to "codeql/java-queries",
        "cpp" to "codeql/cpp-queries",
        "csharp" to "codeql/csharp-queries",
        "ruby" to "codeql/ruby-queries",
        "go" to "codeql/go-queries",
        "swift" to "codeql/swift-queries",
    ),
) : Guardian {
    override suspend fun run(req: AnalyzeRequest): AnalyzeResponse {
        val workRoot = Files.createTempDirectory("codeql-guardian-")
        println("using work root $workRoot")
        try {
            val sourceRoot = FileSystemToDiskWriter.writeFileSystemToTemp(req.fileSystem)

            val languages = detectLanguages(req.files)
            val sarifPaths = mutableListOf<Path>()
            println("detected languages $languages for files ${req.files.joinToString(",")}")

            for (language in languages) {
                val dbDir = workRoot.resolve("db-$language")
                val outSarif = workRoot.resolve("results-$language.sarif")

                createDatabase(language, sourceRoot, dbDir)
                analyzeDatabase(language, dbDir, outSarif)

                if (outSarif.exists()) sarifPaths.add(outSarif)
            }

            val violations = sarifPaths.flatMap { path ->
                val text = Files.readString(path)
                parseSarifToViolations(text)
            }
            return AnalyzeResponse(violations)
        } finally {
            // workRoot.toFile().deleteRecursively()
        }
    }


    private fun createDatabase(language: String, sourceRoot: Path, dbDir: Path) {
        val args = mutableListOf(
            codeqlBinary, "database", "create", dbDir.absolutePathString(),
            "--language=$language",
            "--source-root", sourceRoot.absolutePathString(),
            "--threads=0",
        )

        val buildCmd = detectBuildCommand(language, sourceRoot)
        if (buildCmd != null) {
            args.add("--command=$buildCmd")
        }

        runProcess(args, sourceRoot)
    }

    private fun detectBuildCommand(language: String, sourceRoot: Path): String? {
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

    private fun analyzeDatabase(language: String, dbDir: Path, outSarif: Path) {
        val queryPack = defaultQueryPacksByLanguage[language] ?: return
        println("using query pack $queryPack")
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
