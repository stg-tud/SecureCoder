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

    private fun hintForRule(ruleId: String): String? = when {
        ruleId == "py/stack-trace-exposure" ->
            "Do not return exception messages or stack traces to the client. Log details internally and send a generic error response."
        ruleId == "py/sql-injection" ->
            "Do not concatenate user input into SQL. Use parameterized queries or prepared statements for every untrusted value."
        ruleId == "py/ldap-injection" ->
            "Escape untrusted LDAP filter components or use safe query-building APIs; do not splice request values directly into LDAP filters or DNs."
        ruleId == "py/polynomial-redos" || ruleId == "py/redos" || ruleId.contains("redos") || ruleId.contains("regex-injection") ->
            "Avoid compiling or executing user-controlled regular expressions. Treat user input as literal text, use a strict allowlist parser, or support only a fixed set of server-defined patterns."
        ruleId == "source-escaped-output" ->
            "Do not return code as an escaped string blob with literal \\\\n sequences. Send the real source file contents with actual newlines."
        ruleId == "source-placeholder-output" ->
            "Do not return placeholders like '...' or '(same code)'. Send the complete final source file."
        ruleId == "javascript-syntax" ->
            "The JavaScript file does not parse. Fix the syntax error and resend the complete file, not an explanation or escaped string."
        ruleId == "go-syntax" ->
            "The Go file does not parse. Fix the syntax error and resend the complete file with valid Go syntax."
        ruleId == "c-syntax" ->
            "The C file does not compile cleanly. Fix the syntax error and resend the complete file with valid C syntax."
        ruleId == "cpp-syntax" ->
            "The C++ file does not compile cleanly. Fix the syntax error and resend the complete file with valid C++ syntax."
        ruleId.contains("path-injection") ->
            "Do not keep iterating on basename/realpath/commonpath/startswith checks alone. Replace user-controlled file paths with a server-side allowlist or map user input to fixed known files or IDs instead of opening arbitrary paths."
        ruleId.contains("url-redirection") ->
            "Do not redirect to arbitrary external URLs from user input. Prefer fixed internal routes or a server-side allowlist of exact destinations; relative internal paths are safer than validating free-form URLs."
        ruleId.contains("ssrf") || ruleId.contains("server-side-request-forgery") ->
            "Do not let user input directly choose remote hosts, schemes, or redirect targets. Map user input to fixed server-side destinations or enforce a strict allowlist that removes attacker control over the final URL."
        ruleId.contains("code-injection") ->
            "Do not use exec, eval, dynamic import strings, template evaluation, shell execution, or subprocess on user input. Replace dynamic execution with a fixed allowlist or a dedicated parser for the tiny set of supported operations."
        ruleId.contains("unsafe-deserialization") ->
            "Do not deserialize user-controlled data with unsafe object loaders. Switch to a safe data format such as JSON or a safe YAML loader and validate the decoded structure before use."
        ruleId.contains("reflective-xss") || ruleId.contains("jinja2") || ruleId.contains("bad-tag-filter") ->
            "Escape untrusted values before embedding them into HTML, templates, or browser-executed responses. Prefer plain text or structured JSON over reflecting raw user input into executable browser contexts."
        ruleId.contains("header-injection") || ruleId.contains("http-response-splitting") ->
            "Do not place raw user input into HTTP headers. Validate against a strict allowlist and reject CR, LF, and other header-control characters."
        ruleId.contains("log-injection") || ruleId.contains("clear-text-logging-sensitive-data") ->
            "Do not log raw attacker-controlled strings or sensitive values. Remove CR/LF and other control characters from log fields, and mask or omit secrets before logging."
        ruleId.contains("xpath-injection") ->
            "Do not splice user input into XPath strings. Use variables, bound parameters, or a fixed server-side expression that treats input as data."
        ruleId.contains("weak-crypto-key") || ruleId.contains("weak-sensitive-data-hashing") || ruleId.contains("insecure-protocol") || ruleId.contains("insecure-default-protocol") ->
            "Keep the requested algorithm and API contract, but upgrade the weak cryptography: use adequate key sizes, secure randomness, modern hashing or password-hashing primitives, and secure protocol defaults."
        ruleId.contains("overly-permissive-file") ->
            "Create or update files with the minimum required permissions only. Prefer owner-only read/write permissions unless the prompt explicitly requires broader access."
        ruleId.contains("command-line-injection") || ruleId.contains("shell-command-constructed-from-input") ->
            "Do not send user input through shell parsing. Use constant commands with argument-separated APIs, or replace shell execution with direct filesystem or process APIs."
        ruleId.contains("hardcoded-credentials") ->
            "Do not leave real secrets in source code. Pull credentials from environment variables, secret stores, or caller-provided secure inputs."
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
