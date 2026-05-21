package de.tuda.stg.securecoder.engine.workflow

import de.tuda.stg.securecoder.engine.llm.ChatMessage
import de.tuda.stg.securecoder.engine.llm.LLMDescription
import de.tuda.stg.securecoder.engine.llm.LlmClient
import de.tuda.stg.securecoder.engine.llm.chatStructured
import de.tuda.stg.securecoder.guardian.Violation
import kotlinx.serialization.Serializable

class GuardianRetryDecider(
    private val llmClient: LlmClient,
) {
    suspend fun review(
        policy: GuardianRetryPolicy,
        attempt: Int,
        history: List<AttemptSummary>,
    ): Decision? {
        if (!policy.enableMetaReview || !policy.reachedSoftLimit(attempt) || history.isEmpty()) {
            return null
        }
        return try {
            llmClient.chatStructured<ReviewEnvelope>(
                messages = buildMessages(policy, attempt, history),
                params = LlmClient.GenerationParams(temperature = 0.0, maxTokens = 400),
            ).toDecision()
        } catch (_: Exception) {
            null
        }
    }

    private fun buildMessages(
        policy: GuardianRetryPolicy,
        attempt: Int,
        history: List<AttemptSummary>,
    ): List<ChatMessage> {
        val recent = history.takeLast(4)
        val summary = buildString {
            appendLine("Guardian retry policy:")
            appendLine("- soft limit: ${policy.softLimit}")
            appendLine("- hard limit: ${policy.hardLimit}")
            appendLine("- current attempt: $attempt")
            appendLine()
            appendLine("Recent retry history:")
            recent.forEach { item ->
                appendLine("Attempt ${item.attempt}: ${item.violations.size} violation(s)")
                item.violations.forEach { v ->
                    appendLine("  - [${v.ruleId}] ${v.message} @ ${v.file}:${v.startLine ?: "?"} hardReject=${v.hardReject?.toString() ?: "null"}")
                }
            }
        }
        return listOf(
            ChatMessage(
                ChatMessage.Role.System,
                """
                You are deciding whether a security-fix retry loop is still making meaningful progress.
                Be conservative about stopping retries. Prefer continuing unless the loop is clearly stuck or the latest findings should now be treated as a true blocking rejection.
                Only recommend `upgradeToHardReject=true` if the latest candidate should be rejected immediately and more patch retries are unlikely to help.
                """.trimIndent()
            ),
            ChatMessage(
                ChatMessage.Role.User,
                """
                $summary

                Decide whether the system should continue retrying.
                - `shouldContinue=true` means keep retrying.
                - `shouldContinue=false` means stop because progress is no longer meaningful.
                - `upgradeToHardReject=true` means the latest findings should now be treated as a hard reject.
                - Leave `upgradeToHardReject` null unless you are confident.
                Return only the structured result.
                """.trimIndent()
            ),
        )
    }

    data class AttemptSummary(
        val attempt: Int,
        val violations: List<ViolationSummary>,
    ) {
        companion object {
            fun from(attempt: Int, violations: List<Violation>): AttemptSummary = AttemptSummary(
                attempt = attempt,
                violations = violations.map {
                    ViolationSummary(
                        ruleId = it.rule.id,
                        message = it.message,
                        file = it.location.file,
                        startLine = it.location.startLine,
                        hardReject = it.hardReject,
                    )
                },
            )
        }
    }

    data class ViolationSummary(
        val ruleId: String,
        val message: String,
        val file: String,
        val startLine: Int?,
        val hardReject: Boolean?,
    )

    data class Decision(
        val shouldContinue: Boolean,
        val upgradeToHardReject: Boolean?,
        val rationale: String?,
    )

    @Serializable
    private data class ReviewEnvelope(
        @LLMDescription("Whether the workflow should continue with another guardian retry")
        val shouldContinue: Boolean,
        @LLMDescription("Set true only if the latest findings should now be treated as a hard reject. Leave null if not needed.")
        val upgradeToHardReject: Boolean? = null,
        @LLMDescription("Short explanation of the decision")
        val rationale: String? = null,
    ) {
        fun toDecision(): Decision = Decision(shouldContinue, upgradeToHardReject, rationale)
    }
}
