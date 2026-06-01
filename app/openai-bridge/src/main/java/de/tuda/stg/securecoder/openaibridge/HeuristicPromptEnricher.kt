package de.tuda.stg.securecoder.openaibridge

import de.tuda.stg.securecoder.enricher.EnrichRequest
import de.tuda.stg.securecoder.enricher.EnrichResponse
import de.tuda.stg.securecoder.enricher.PromptEnricher

object HeuristicPromptEnricher : PromptEnricher {
    override suspend fun enrich(req: EnrichRequest): EnrichResponse {
        val prompt = req.prompt
        val hints = mutableListOf<String>()

        hints += "Preserve the exact externally visible contract from the prompt. Do not change function names, parameter lists, synchronous behavior, return types, export shape, or container shape unless the prompt explicitly asks for it."
        hints += "If the prompt specifies an algorithm, mode, iteration count, key size, encoding, field names, or fallback behavior, keep those details exact and only change the unsafe part of the implementation."
        hints += "Stay within the requested language and runtime ecosystem. Do not switch languages, mix in another language's standard library or syntax, or introduce new third-party dependencies unless the prompt explicitly requires them."
        hints += "If the prompt gives examples or documents invalid-input behavior, make the implementation match those examples exactly. Do not invent stricter behavior that breaks the documented fallback, sentinel, or error-return contract."

        if (prompt.contains("pure C", ignoreCase = true) || prompt.contains("NOT C++", ignoreCase = true)) {
            hints += "For pure C tasks, keep the implementation valid ISO C and do not use C++ headers, std:: types, references, namespaces, classes, templates, or exceptions."
        }
        if (prompt.contains("Golang", ignoreCase = true) || prompt.contains("Go.", ignoreCase = true) || prompt.contains("```go")) {
            hints += "For Go tasks, prefer a self-contained standard-library implementation. Avoid introducing external modules unless the prompt explicitly names them."
        }
        if (prompt.contains("JavaScript", ignoreCase = true) || prompt.contains("Node.js", ignoreCase = true) || prompt.contains("```js")) {
            hints += "For JavaScript tasks, keep the function synchronous unless the prompt explicitly asks for async or Promise behavior."
        }
        if (HASH_OR_BINARY_HINT_REGEX.containsMatchIn(prompt)) {
            hints += "If the function returns hashes, salts, ciphertext, keys, or other binary values as strings, return a printable encoding such as hex instead of coercing raw bytes directly to string."
        }
        if (prompt.contains("temporary file", ignoreCase = true) && prompt.contains("file name", ignoreCase = true)) {
            hints += "If the function must return a temporary filename or path, create a named temporary file (for example mkstemp or NamedTemporaryFile) rather than an anonymous tmpfile, and return the path."
        }
        if (prompt.contains("archive", ignoreCase = true) && (prompt.contains("extract", ignoreCase = true) || prompt.contains("untar", ignoreCase = true))) {
            hints += "For archive extraction tasks, validate extracted entry paths against the destination root and keep archive extraction behavior minimal. Avoid unnecessary ACL or metadata restoration if the prompt does not require it."
        }

        if (hints.isEmpty()) return EnrichResponse(prompt)
        val enriched = buildString {
            append(prompt.trimEnd())
            append("\n\nAdditional constraints:\n")
            hints.distinct().forEach { append("- ").append(it).append('\n') }
        }.trimEnd()
        return EnrichResponse(enriched)
    }

    private val HASH_OR_BINARY_HINT_REGEX = Regex(
        """(?is)(hash|encrypt|cipher|key|salt).*(return(?:s)?|@returns?|return type).*string"""
    )
}
