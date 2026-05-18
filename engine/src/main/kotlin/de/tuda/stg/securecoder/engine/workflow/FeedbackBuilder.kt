package de.tuda.stg.securecoder.engine.workflow

import de.tuda.stg.securecoder.engine.workflow.GuardianExecutor.GuardianResult

object FeedbackBuilder {
    fun GuardianResult.buildFeedbackForLlm(
        responseInstruction: String,
        reviewModeInstruction: String,
        maxListedViolations: Int = 20,
        linesAround: Int = 6,
    ) = buildString {
        appendLine("Security analysis found ${violations.size} violation(s). Address all of them and resend the COMPLETE set of edits.")
        appendLine(reviewModeInstruction)
        appendLine(responseInstruction)
        val ruleHints = collectRuleHints(violations)
        if (ruleHints.isNotEmpty()) {
            appendLine("Targeted guidance:")
            ruleHints.forEach { appendLine("- $it") }
        }
        val prioritizedViolations = prioritizeViolations(violations)
        val listedViolations = prioritizedViolations.take(maxListedViolations)
        listedViolations.forEachIndexed { idx, v ->
            val loc = listOfNotNull(v.location.file, v.location.startLine?.toString()).joinToString(":")
            appendLine("${idx + 1}. [${v.rule.id}]${v.message} @ $loc")
            val fileContent = files.find { it.name == v.location.file }?.content
            if (fileContent == null) throw IllegalStateException("File content not found: ${v.location.file}")
            appendLine("SNIPPET: ${v.location.file}")
            appendLine("<<<")
            appendLine(makeSnippet(
                fileContent = fileContent,
                startLine = v.location.startLine,
                endLine = v.location.endLine,
                linesAround = linesAround,
            ))
            appendLine(">>>")
        }
        if (prioritizedViolations.size > listedViolations.size) {
            appendLine("…and ${prioritizedViolations.size - listedViolations.size} more")
        }
    }

    private fun prioritizeViolations(
        violations: List<de.tuda.stg.securecoder.guardian.Violation>,
    ): List<de.tuda.stg.securecoder.guardian.Violation> {
        val grouped = violations.groupBy {
            ViolationKey(
                ruleId = it.rule.id,
                message = it.message,
                file = it.location.file,
                startLine = it.location.startLine,
                endLine = it.location.endLine,
            )
        }
        val ordered = linkedMapOf<ViolationKey, de.tuda.stg.securecoder.guardian.Violation>()
        grouped.forEach { (key, group) -> ordered[key] = group.first() }
        return ordered.values.toList()
    }

    private fun collectRuleHints(
        violations: List<de.tuda.stg.securecoder.guardian.Violation>,
    ): List<String> {
        val ruleIds = violations.map { it.rule.id }.distinct()
        return ruleIds.mapNotNull(::hintForRule)
    }

    private fun hintForRule(ruleId: String): String? = when (ruleId) {
        "py/path-injection" ->
            "Do not keep iterating on basename/realpath/commonpath/startswith checks alone. Replace user-controlled file paths with a server-side allowlist or map user input to fixed known files or IDs instead of opening arbitrary paths."
        "py/url-redirection" ->
            "Do not redirect to arbitrary external URLs from user input. Prefer fixed internal routes or a server-side allowlist of exact destinations; relative internal paths are safer than validating free-form URLs."
        "py/code-injection" ->
            "Do not use exec, eval, dynamic import strings, shell execution, or subprocess on user input. Replace dynamic execution with a fixed allowlist or a dedicated parser for the tiny set of supported operations."
        "py/unsafe-deserialization" ->
            "Do not deserialize user-controlled data with pickle or other unsafe formats. Switch to a safe format such as JSON and validate the decoded structure before use."
        "py/reflective-xss" ->
            "Escape untrusted values before embedding them into HTML, or return structured plain text/JSON instead of reflecting raw user input into an HTML response."
        "py/stack-trace-exposure" ->
            "Do not return exception messages or stack traces to the client. Log details internally and send a generic error response."
        "py/sql-injection" ->
            "Do not concatenate user input into SQL. Use parameterized queries or prepared statements for every untrusted value."
        "py/ldap-injection" ->
            "Escape untrusted LDAP filter components or use safe query-building APIs; do not splice request values directly into LDAP filters or DNs."
        "py/header-injection", "py/http-response-splitting" ->
            "Do not place raw user input into HTTP headers. Validate against a strict allowlist and reject CR, LF, and other header-control characters."
        "py/polynomial-redos" ->
            "Avoid complex regex validation on user input when a strict allowlist parser or exact-match allowlist would do. Simpler parsing is safer than patching the same regex repeatedly."
        "source-escaped-output" ->
            "Do not return code as an escaped string blob with literal \\\\n sequences. Send the real source file contents with actual newlines."
        "source-placeholder-output" ->
            "Do not return placeholders like '...' or '(same code)'. Send the complete final source file."
        "javascript-syntax" ->
            "The JavaScript file does not parse. Fix the syntax error and resend the complete file, not an explanation or escaped string."
        "go-syntax" ->
            "The Go file does not parse. Fix the syntax error and resend the complete file with valid Go syntax."
        "c-syntax" ->
            "The C file does not compile cleanly. Fix the syntax error and resend the complete file with valid C syntax."
        "cpp-syntax" ->
            "The C++ file does not compile cleanly. Fix the syntax error and resend the complete file with valid C++ syntax."
        else -> null
    }

    private fun makeSnippet(
        fileContent: String,
        startLine: Int?,
        endLine: Int?,
        linesAround: Int,
    ): String {
        val lines = fileContent.split('\n')
        val from = ((startLine ?: 1) - linesAround).coerceIn(1, lines.size)
        val to = ((endLine ?: startLine ?: 20) + linesAround).coerceIn(1, lines.size)
        val builder = StringBuilder()
        for (i in from..to) {
            val line = lines[i - 1]
            builder.append(String.format("%5d | %s%n", i, line))
        }
        return builder.toString()
    }

    private data class ViolationKey(
        val ruleId: String,
        val message: String,
        val file: String?,
        val startLine: Int?,
        val endLine: Int?,
    )
}
