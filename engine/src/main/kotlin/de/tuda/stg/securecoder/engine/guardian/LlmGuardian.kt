package de.tuda.stg.securecoder.engine.guardian

import de.tuda.stg.securecoder.engine.llm.ChatMessage
import de.tuda.stg.securecoder.engine.llm.LlmClient
import de.tuda.stg.securecoder.engine.llm.chatStructured
import de.tuda.stg.securecoder.guardian.AnalyzeRequest
import de.tuda.stg.securecoder.guardian.AnalyzeResponse
import de.tuda.stg.securecoder.guardian.Guardian

class LlmGuardian(
    private val client: LlmClient,
    private val systemPrompt: String = DEFAULT_SYSTEM_PROMPT,
) : Guardian {
    override suspend fun run(req: AnalyzeRequest): AnalyzeResponse {
        val messages = buildMessages(req)
        val llmResp = client.chatStructured<LlmAnalyzeResponse>(
            messages = messages,
            params = LlmClient.GenerationParams(
                temperature = 0.0
            )
        )
        return llmResp.toApi()
    }

    private fun buildMessages(req: AnalyzeRequest): List<ChatMessage> {
        return listOf(
            ChatMessage(ChatMessage.Role.System, systemPrompt),
            ChatMessage(ChatMessage.Role.User, buildString {
                appendLine("You are given a set of source files to analyze for security issues.")
                appendLine("Only consider the provided files; do not assume hidden context.")
                appendLine()
                req.files.forEach { file ->
                    appendLine("===== FILE: ${file.name} =====")
                    appendLine(withLineNumbers(file.content))
                    appendLine("===== END FILE: ${file.name} =====")
                    appendLine()
                }
                appendLine("Return your analysis strictly using the structured schema provided by the tool.")
            })
        )
    }

    private fun withLineNumbers(text: String): String = buildString {
        text.lineSequence().forEachIndexed { idx, line ->
            append(idx + 1)
            append(": ")
            append(line)
            append('\n')
        }
    }.removeSuffix("\n")

    companion object {
        private const val DEFAULT_SYSTEM_PROMPT: String =
            """
            You are SecureCoder Guardian. Analyze code for security vulnerabilities.
            Use conservative judgment; highlight clear issues or suspicious patterns.
            Provide precise file and line locations when possible. If unsure, leave
            optional fields null. Do not include any prose outside the structured result.
            """
    }
}
