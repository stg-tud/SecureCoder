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
        return llmResp
            .filteredForRequest(req)
            .toApi()
    }

    private fun buildMessages(req: AnalyzeRequest): List<ChatMessage> {
        return listOf(
            ChatMessage(ChatMessage.Role.System, systemPrompt),
            ChatMessage(ChatMessage.Role.User, buildString {
                appendLine("You are given a set of source files to analyze for security issues.")
                appendLine("Only consider the provided files; do not assume hidden context.")
                appendLine("Respect the code's explicit contract and intended data flow when judging risk.")
                appendLine("Do not report hypothetical misuse by unseen callers as a vulnerability in the shown code.")
                appendLine("Do not report vulnerabilities that require the returned value to be misused later by another unseen component.")
                appendLine("The claimed vulnerability type must match an actual sink or operation in the shown code.")
                appendLine("For example, do not report filesystem traversal when the code only parses or returns URLs and never performs filesystem operations.")
                appendLine("Do not report parser differential, null-byte, or edge-case bypass theories unless the shown code itself contains the relevant vulnerable sink or interpretation step.")
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
            Use conservative judgment; highlight only clear issues with a concrete exploit path in the shown code.
            Respect the explicit contract of the code. Do not flag a function as insecure
            merely because it returns, serializes, or hands back a value that the function
            is explicitly supposed to generate and return, unless the shown code also logs it,
            stores it insecurely, exposes it to an unrelated sink, or otherwise misuses it.
            Favor concrete exploit paths over speculative "this might be exposed later" reasoning.
            Never report a vulnerability whose sink category is absent from the shown code.
            For example, do not report path traversal without filesystem access, do not report command injection without command execution, and do not report SSRF or open redirect without an actual network or redirect sink.
            If you cannot point to the relevant sink in the shown code, omit the finding.
            Only mark hardReject=true for issues that are clearly present in the shown code itself and should cause an immediate rejection.
            If an issue looks repairable through another retry, prefer hardReject=false or null.
            Use null when you are unsure whether the issue should be a blocking rejection.
            Provide precise file and line locations when possible. If unsure, leave
            optional fields null. Do not include any prose outside the structured result.
            """
    }
}
