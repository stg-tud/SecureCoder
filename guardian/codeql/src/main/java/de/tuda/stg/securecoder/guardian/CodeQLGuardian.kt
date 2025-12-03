package de.tuda.stg.securecoder.guardian

import de.tuda.stg.securecoder.filesystem.FileSystemToDiskWriter
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
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

            val violations = sarifPaths.flatMap { parseSarifToViolations(it) }
            return AnalyzeResponse(violations)
        } finally {
            // workRoot.toFile().deleteRecursively()
        }
    }

    private fun detectLanguages(files: List<File>): Set<String> {
        val exts = files.map { it.name.substringAfterLast('.', missingDelimiterValue = "").lowercase() }
        val langs = mutableSetOf<String>()
        for (ext in exts) {
            when (ext) {
                "kt", "kts", "java" -> langs.add("java")
                "js", "jsx", "ts", "tsx" -> langs.add("javascript")
                "py" -> langs.add("python")
                "rb" -> langs.add("ruby")
                "go" -> langs.add("go")
                "swift" -> langs.add("swift")
                "c", "cc", "cpp", "cxx", "h", "hh", "hpp", "hxx" -> langs.add("cpp")
                "cs" -> langs.add("csharp")
            }
        }
        return langs
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

    private fun parseSarifToViolations(sarifPath: Path): List<Violation> {
        val text = Files.readString(sarifPath)
        val root = Json.parseToJsonElement(text)
        if (root !is JsonObject) return emptyList()

        val runs = root["runs"]?.jsonArray ?: return emptyList()
        val out = mutableListOf<Violation>()
        for (run in runs) {
            val results = run.jsonObject["results"]?.jsonArray ?: continue
            for (res in results) {
                out.add(mapResultToViolation(res))
            }
        }
        return out
    }

    private fun mapResultToViolation(res: JsonElement): Violation {
        val obj = res.jsonObject
        val ruleId = obj["ruleId"]?.asText() ?: "unknown"
        val message = obj["message"]?.jsonObject?.get("text")?.asText() ?: "CodeQL issue"

        val locations = obj["locations"]?.jsonArray
        val firstLoc = locations?.firstOrNull()?.jsonObject
        val phys = firstLoc?.get("physicalLocation")?.jsonObject
        val artifact = phys?.get("artifactLocation")?.jsonObject
        val region = phys?.get("region")?.jsonObject

        val filePath = artifact?.get("uri")?.asText() ?: artifact?.get("uriBaseId")?.asText() ?: "<unknown>"
        val startLine = region?.get("startLine")?.asInt()
        val endLine = region?.get("endLine")?.asInt() ?: startLine

        val level = obj["level"]?.asText()
        val precision = obj["properties"]?.jsonObject?.get("precision")?.asText()
        val confidence = precision ?: level

        return Violation(
            rule = RuleRef(id = ruleId),
            message = message,
            location = Location(
                file = filePath,
                startLine = startLine,
                endLine = endLine,
            ),
            hardReject = false,
            confidence = confidence,
        )
    }

    private fun JsonElement.asText(): String? = when (this) {
        is JsonPrimitive -> if (isString) content else toString()
        JsonNull -> null
        else -> toString()
    }

    private fun JsonElement.asInt(): Int? = (this as? JsonPrimitive)?.asInt()
}




