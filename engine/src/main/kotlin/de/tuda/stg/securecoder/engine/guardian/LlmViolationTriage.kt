package de.tuda.stg.securecoder.engine.guardian

import de.tuda.stg.securecoder.engine.llm.ChatMessage
import de.tuda.stg.securecoder.engine.llm.LLMDescription
import de.tuda.stg.securecoder.engine.llm.LlmClient
import de.tuda.stg.securecoder.engine.llm.chatStructured
import de.tuda.stg.securecoder.guardian.AnalyzeRequest
import de.tuda.stg.securecoder.guardian.Violation
import de.tuda.stg.securecoder.guardian.ViolationTriage
import kotlinx.serialization.Serializable

class LlmViolationTriage(
    private val llmClient: LlmClient,
    private val snippetRadius: Int = 18,
    private val maxSnippetLines: Int = 80,
    private val rulePromptOverrides: Map<String, String> = emptyMap(),
) : ViolationTriage {
    override suspend fun triage(req: AnalyzeRequest, violations: List<Violation>): List<Violation> {
        if (violations.isEmpty()) return violations
        return violations.mapNotNull { violation ->
            triageOne(req, violation)
        }
    }

    private suspend fun triageOne(req: AnalyzeRequest, violation: Violation): Violation? {
        val fileContent = req.fileSystem.getFile(violation.location.file)?.content()
            ?: req.files.firstOrNull { it.name == violation.location.file }?.content
            ?: return violation
        val snippet = buildSnippet(fileContent, violation.location.startLine, violation.location.endLine)
        val decision = runCatching {
            llmClient.chatStructured<TriageEnvelope>(
                messages = buildMessages(violation, snippet),
                params = LlmClient.GenerationParams(temperature = 0.0, maxTokens = 300),
            )
        }.getOrNull() ?: return violation
        if (!decision.keepFinding) return null
        return violation.copy(
            hardReject = decision.hardReject ?: violation.hardReject,
            confidence = decision.confidence ?: violation.confidence,
            raw = appendRationale(violation.raw, decision.rationale),
        )
    }

    private fun buildMessages(violation: Violation, snippet: String): List<ChatMessage> = listOf(
        ChatMessage(
            ChatMessage.Role.System,
            """
            You are triaging a static-analysis security finding.
            Be conservative about suppressing findings, but do suppress findings that are not supported by the shown code.
            Only keep a finding when the shown code itself contains a plausible vulnerability or clearly vulnerable pattern.
            Set `hardReject=true` only when the candidate should be rejected immediately. Use false or null for findings that should remain repairable.
            Return only the structured result.
            """.trimIndent(),
        ),
        ChatMessage(
            ChatMessage.Role.User,
            """
            Rule id: ${violation.rule.id}
            Message: ${violation.message}
            File: ${violation.location.file}
            Start line: ${violation.location.startLine ?: "unknown"}
            End line: ${violation.location.endLine ?: violation.location.startLine ?: "unknown"}
            Static analyzer confidence: ${violation.confidence ?: "unknown"}

            Relevant source excerpt:
            =====
            $snippet
            =====

            Decide whether this finding should be kept for the guardian retry loop.
            - `keepFinding=true` if the shown code still appears vulnerable.
            - `keepFinding=false` if this looks unsupported, too speculative, or clearly not a real vulnerability in the shown code.
            ${buildRuleSpecificGuidance(violation)}
            """.trimIndent(),
        ),
    )

    private fun buildRuleSpecificGuidance(violation: Violation): String {
        val override = findRulePromptOverride(violation.rule.id)?.trim().orEmpty()
        if (override.isEmpty()) return ""
        return "Additional rule-specific guidance:\n$override"
    }

    private fun findRulePromptOverride(ruleId: String): String? {
        rulePromptOverrides[ruleId]?.let { return it }
        return rulePromptOverrides.entries
            .filter { (pattern, _) -> wildcardMatches(pattern, ruleId) }
            .maxByOrNull { (pattern, _) -> wildcardSpecificity(pattern) }
            ?.value
    }

    private fun wildcardMatches(pattern: String, ruleId: String): Boolean {
        if ('*' !in pattern) return false
        val parts = pattern.split('*')
        var cursor = 0
        if (!pattern.startsWith("*")) {
            val first = parts.first()
            if (!ruleId.startsWith(first)) return false
            cursor = first.length
        }
        for (part in parts.filter { it.isNotEmpty() }) {
            val next = ruleId.indexOf(part, startIndex = cursor)
            if (next < 0) return false
            cursor = next + part.length
        }
        if (!pattern.endsWith("*")) {
            val last = parts.last()
            return ruleId.endsWith(last)
        }
        return true
    }

    private fun wildcardSpecificity(pattern: String): Int = pattern.count { it != '*' }

    private fun buildSnippet(content: String, startLine: Int?, endLine: Int?): String {
        val lines = content.lines()
        if (lines.isEmpty()) return ""
        val startIdx = ((startLine ?: 1) - 1).coerceAtLeast(0)
        val endIdx = ((endLine ?: startLine ?: 1) - 1).coerceAtMost(lines.lastIndex)
        val from = (startIdx - snippetRadius).coerceAtLeast(0)
        val to = (endIdx + snippetRadius).coerceAtMost(lines.lastIndex)
        val selected = lines.subList(from, to + 1)
        val trimmed = if (selected.size > maxSnippetLines) {
            selected.take(maxSnippetLines)
        } else {
            selected
        }
        return trimmed.mapIndexed { index, line ->
            val lineNumber = from + index + 1
            "$lineNumber: $line"
        }.joinToString("\n")
    }

    private fun appendRationale(raw: String?, rationale: String?): String? {
        if (rationale.isNullOrBlank()) return raw
        return listOfNotNull(raw, "triage: $rationale").joinToString("\n")
    }

    @Serializable
    private data class TriageEnvelope(
        @LLMDescription("Whether this static-analysis finding should remain in the guardian result")
        val keepFinding: Boolean,
        @LLMDescription("Set true only when the candidate should be rejected immediately. Use false or null when the issue remains repairable or uncertain.")
        val hardReject: Boolean? = null,
        @LLMDescription("Revised confidence for the finding, such as High, Medium, or Low")
        val confidence: String? = null,
        @LLMDescription("Short rationale for keeping or suppressing the finding")
        val rationale: String? = null,
    )
}
