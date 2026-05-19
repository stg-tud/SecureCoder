package de.tuda.stg.securecoder.engine.guardian

object SourceTextNormalizer {
    fun normalize(fileName: String, content: String): String {
        val transportTrimmed = trimTransportArtifact(fileName, content) ?: content
        val trimmed = transportTrimmed.trim()
        if (!looksLikeEscapedBlob(fileName, trimmed)) {
            return transportTrimmed
        }
        val decoded = decodeCommonEscapes(trimmed)
        if ("\u0000" in decoded || decoded.count { it == '\n' } <= transportTrimmed.count { it == '\n' }) {
            return transportTrimmed
        }
        return decoded
    }

    fun detectProblems(fileName: String, content: String): List<Problem> {
        val trimmed = content.trim()
        val problems = mutableListOf<Problem>()
        if (trimmed == "...") {
            problems += Problem(
                ruleId = "source-placeholder-output",
                message = "Output is a placeholder ('...') instead of complete source code.",
            )
        }
        if (trimmed == "I failed to generate valid code. Retries exceeded.") {
            problems += Problem(
                ruleId = "source-failure-output",
                message = "Output is a retry-exhaustion failure string instead of source code.",
            )
        }
        if (trimmed == "I encountered an internal generation error.") {
            problems += Problem(
                ruleId = "source-failure-output",
                message = "Output is an internal-error string instead of source code.",
            )
        }
        if ("<full escaped>" in trimmed || "(same code)" in trimmed) {
            problems += Problem(
                ruleId = "source-placeholder-output",
                message = "Output contains placeholder text instead of complete source code.",
            )
        }
        if (looksLikeEscapedBlob(fileName, trimmed)) {
            problems += Problem(
                ruleId = "source-escaped-output",
                message = "Output looks like escaped source text with literal \\\\n sequences instead of real newlines.",
            )
        }
        if (hasTransportArtifact(fileName, trimmed)) {
            problems += Problem(
                ruleId = "source-transport-artifact",
                message = "Output contains structured-edit or JSON transport artifacts mixed into the source code.",
            )
        }
        return problems
    }

    private fun hasTransportArtifact(fileName: String, candidate: String): Boolean =
        trimTransportArtifact(fileName, candidate) != null

    private fun trimTransportArtifact(fileName: String, content: String): String? {
        val ext = fileName.substringAfterLast('.', "")
        if (ext !in SOURCE_FILE_EXTENSIONS) return null
        val trimmed = content.trim()
        if (!startsLikeSource(ext, trimmed)) return null
        val markerIndex = TRANSPORT_MARKERS
            .map { trimmed.indexOf(it) }
            .filter { it >= 40 }
            .minOrNull()
            ?: return null
        val prefix = trimmed.substring(0, markerIndex).trimEnd().removeSuffix("\"").trimEnd()
        if (!startsLikeSource(ext, prefix) || prefix.length < 40) return null
        return prefix
    }

    private fun looksLikeEscapedBlob(fileName: String, candidate: String): Boolean {
        if (candidate.isBlank()) return false
        val ext = fileName.substringAfterLast('.', "")
        if (ext !in SOURCE_FILE_EXTENSIONS) {
            return false
        }
        val escapedNewlines = Regex("""\\n""").findAll(candidate).count()
        val realNewlines = candidate.count { it == '\n' }
        if (escapedNewlines < 3 || realNewlines > 2) {
            return false
        }
        return when (ext) {
            "c", "cc", "cpp", "cxx", "h", "hpp" ->
                listOf("#include", "int main", "std::", "char *", "void ").any(candidate::contains)
            "js", "mjs", "cjs" ->
                listOf("function ", "const ", "let ", "module.exports", "require(").any(candidate::contains)
            "go" ->
                listOf("package ", "func ", "import ").any(candidate::contains)
            "py" ->
                listOf("def ", "import ", "class ").any(candidate::contains)
            "java" ->
                listOf("class ", "public ", "import ").any(candidate::contains)
            else -> false
        }
    }

    private fun startsLikeSource(ext: String, candidate: String): Boolean {
        if (candidate.isBlank()) return false
        return when (ext) {
            "c", "cc", "cpp", "cxx", "h", "hpp" ->
                listOf("#include", "bool ", "int ", "void ", "class ", "struct ").any(candidate::startsWith)
            "js", "mjs", "cjs" ->
                listOf("function ", "const ", "let ", "var ", "module.exports", "exports.", "class ").any(candidate::startsWith)
            "go" ->
                listOf("package ", "import ", "func ").any(candidate::startsWith)
            "py" ->
                listOf("def ", "import ", "from ", "class ").any(candidate::startsWith)
            "java" ->
                listOf("package ", "import ", "public ", "class ").any(candidate::startsWith)
            else -> false
        }
    }

    private fun decodeCommonEscapes(input: String): String {
        val out = StringBuilder(input.length)
        var i = 0
        while (i < input.length) {
            val ch = input[i]
            if (ch != '\\' || i == input.lastIndex) {
                out.append(ch)
                i++
                continue
            }
            when (val next = input[i + 1]) {
                'n' -> {
                    out.append('\n')
                    i += 2
                }
                'r' -> {
                    out.append('\r')
                    i += 2
                }
                't' -> {
                    out.append('\t')
                    i += 2
                }
                '\\' -> {
                    out.append('\\')
                    i += 2
                }
                '"' -> {
                    out.append('"')
                    i += 2
                }
                '\'' -> {
                    out.append('\'')
                    i += 2
                }
                '0' -> {
                    out.append("\\0")
                    i += 2
                }
                'u' -> {
                    val hex = input.substring(i + 2, (i + 6).coerceAtMost(input.length))
                    if (hex.length == 4 && hex.all { it.isDigit() || it.lowercaseChar() in 'a'..'f' }) {
                        out.append(hex.toInt(16).toChar())
                        i += 6
                    } else {
                        out.append('\\').append(next)
                        i += 2
                    }
                }
                else -> {
                    out.append('\\').append(next)
                    i += 2
                }
            }
        }
        return out.toString()
    }

    data class Problem(
        val ruleId: String,
        val message: String,
    )

    private val SOURCE_FILE_EXTENSIONS = setOf("c", "cc", "cpp", "cxx", "h", "hpp", "js", "mjs", "cjs", "go", "py", "java")
    private val TRANSPORT_MARKERS = listOf(
        "\"edits\":",
        "\"filePath\":",
        "\"search\":",
        "\"replace\":",
        "}]}{",
        "\"]}{",
    )
}
