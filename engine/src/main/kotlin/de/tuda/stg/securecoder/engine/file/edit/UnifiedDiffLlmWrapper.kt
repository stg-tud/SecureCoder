package de.tuda.stg.securecoder.engine.file.edit

import de.tuda.stg.securecoder.engine.llm.ChatExchange
import de.tuda.stg.securecoder.engine.llm.ChatMessage
import de.tuda.stg.securecoder.engine.llm.ChatMessage.Role
import de.tuda.stg.securecoder.engine.llm.LlmClient
import de.tuda.stg.securecoder.engine.workflow.FeedbackBuilder.buildFeedbackForLlm
import de.tuda.stg.securecoder.engine.workflow.GuardianExecutor
import de.tuda.stg.securecoder.filesystem.FileSystem

class UnifiedDiffLlmWrapper(
    private val llmClient: LlmClient,
) : EditFormatHandler {
    override val formatId: String = "unified_diff"

    private val prompt = """
        Your task it is to produce code. The agent will just parse the code you produce. So dont do a extensive review in your final answer!

        Return ONLY a unified diff.
        Use standard unified diff format with file headers:
        --- a/<path> or --- /dev/null
        +++ b/<path> or +++ /dev/null
        and one or more @@ hunks.

        For new files, use --- /dev/null and +++ b/<path>.
        Do not include prose, markdown fences, or explanations.
    """.trimIndent()

    override suspend fun chat(
        messages: List<ChatMessage>,
        fileSystem: FileSystem,
        params: LlmClient.GenerationParams,
        onParseError: suspend (parseErrors: List<String>, llm: ChatExchange) -> Unit,
        attempts: Int,
    ): EditFormatHandler.ChatResult {
        val messages = messages.toMutableList()
        appendPromptToLastSystem(messages)
        repeat(attempts) {
            val llmInput = messages.toList()
            val response = llmClient.chat(llmInput, params)
            messages += ChatMessage(Role.Assistant, response)
            when (val result = parse(response, fileSystem)) {
                is ParseResult.Ok -> return EditFormatHandler.ChatResult(messages, result.value)
                is ParseResult.Err -> {
                    messages += ChatMessage(Role.User, result.buildMessage())
                    onParseError(result.messages, ChatExchange(llmInput, response))
                }
            }
        }
        return EditFormatHandler.ChatResult(messages, null)
    }

    override fun buildGuardianFeedback(
        guardianResult: GuardianExecutor.GuardianResult,
        reviewMode: ReviewMode,
    ): String = guardianResult.buildFeedbackForLlm(
        responseInstruction = "Respond again with ONLY a unified diff. Do NOT include prose, markdown fences, or explanations.",
        reviewModeInstruction = when (reviewMode) {
            ReviewMode.PATCH -> "Patch the current working version from your previous changes."
            ReviewMode.REPLACE -> "Regenerate the complete fixed patch from scratch against the original context."
        },
    )

    private fun appendPromptToLastSystem(messages: MutableList<ChatMessage>) {
        val lastSystemIndex = messages.indexOfLast { it.role == Role.System }
        if (lastSystemIndex >= 0) {
            val existing = messages[lastSystemIndex]
            messages[lastSystemIndex] = ChatMessage(Role.System, "${existing.content}\n\n$prompt")
        } else {
            messages += ChatMessage(Role.System, prompt)
        }
    }

    private suspend fun parse(content: String, fileSystem: FileSystem): ParseResult {
        val lines = content.lines()
        if (lines.none { it.startsWith("--- ") }) {
            return ParseResult.Err(listOf("Could not find unified diff file headers (`---` / `+++`) in the response."))
        }
        val sections = mutableListOf<FilePatch>()
        var i = 0
        while (i < lines.size) {
            if (!lines[i].startsWith("--- ")) {
                i++
                continue
            }
            if (i + 1 >= lines.size || !lines[i + 1].startsWith("+++ ")) {
                return ParseResult.Err(listOf("Malformed unified diff: missing `+++` after `${lines[i]}`"))
            }
            val oldPath = normalizePath(lines[i].removePrefix("--- ").trim())
            val newPath = normalizePath(lines[i + 1].removePrefix("+++ ").trim())
            i += 2
            val hunks = mutableListOf<List<String>>()
            while (i < lines.size && !lines[i].startsWith("--- ")) {
                if (lines[i].startsWith("@@")) {
                    val hunkLines = mutableListOf<String>()
                    hunkLines += lines[i]
                    i++
                    while (i < lines.size && !lines[i].startsWith("@@") && !lines[i].startsWith("--- ")) {
                        hunkLines += lines[i]
                        i++
                    }
                    hunks += hunkLines
                } else {
                    i++
                }
            }
            sections += FilePatch(oldPath, newPath, hunks)
        }

        val changes = mutableListOf<Changes.SearchReplace>()
        val errors = mutableListOf<String>()
        for (section in sections) {
            val targetPath = when {
                section.newPath != null -> section.newPath
                section.oldPath != null -> section.oldPath
                else -> null
            }
            if (targetPath == null) {
                errors += "Malformed diff section without file path"
                continue
            }
            val originalContent = section.oldPath?.let { fileSystem.getFile(it)?.content() }
            try {
                val updatedContent = applyPatch(originalContent ?: "", section)
                changes += Changes.SearchReplace(
                    fileName = targetPath,
                    searchedText = Changes.SearchedText(originalContent ?: ""),
                    replaceText = updatedContent,
                )
            } catch (e: IllegalArgumentException) {
                errors += e.message ?: "Failed to apply unified diff for $targetPath"
            }
        }
        if (changes.isEmpty()) return ParseResult.Err(errors.ifEmpty { listOf("No changes could be derived from the unified diff.") })
        return ParseResult.Ok(Changes(changes))
    }

    private fun applyPatch(original: String, patch: FilePatch): String {
        if (patch.newPath == null) return ""
        val originalEndsWithNewline = original.endsWith("\n")
        val originalLines = if (original.isEmpty()) mutableListOf<String>() else original.split("\n").toMutableList().also {
            if (originalEndsWithNewline && it.isNotEmpty() && it.last().isEmpty()) it.removeLast()
        }
        val result = mutableListOf<String>()
        var cursor = 0
        for (hunk in patch.hunks) {
            val header = hunk.first()
            val match = HUNK_HEADER.matchEntire(header)
                ?: throw IllegalArgumentException("Malformed hunk header: $header")
            val oldStart = match.groupValues[1].toInt()
            val oldCount = match.groupValues[2].ifEmpty { "1" }.toInt()
            val oldStartIndex = if (oldCount == 0) oldStart else oldStart - 1
            while (cursor < oldStartIndex && cursor < originalLines.size) {
                result += originalLines[cursor++]
            }
            for (line in hunk.drop(1)) {
                when {
                    line.startsWith(" ") -> {
                        val expected = line.drop(1)
                        val actual = originalLines.getOrNull(cursor)
                        require(actual == expected) {
                            "Unified diff context mismatch. Expected `$expected`, found `${actual ?: "<EOF>"}`"
                        }
                        result += expected
                        cursor++
                    }
                    line.startsWith("-") -> {
                        val expected = line.drop(1)
                        val actual = originalLines.getOrNull(cursor)
                        require(actual == expected) {
                            "Unified diff deletion mismatch. Expected `$expected`, found `${actual ?: "<EOF>"}`"
                        }
                        cursor++
                    }
                    line.startsWith("+") -> result += line.drop(1)
                    line == "\\ No newline at end of file" -> Unit
                    else -> throw IllegalArgumentException("Malformed unified diff body line: $line")
                }
            }
        }
        while (cursor < originalLines.size) {
            result += originalLines[cursor++]
        }
        val joined = result.joinToString("\n")
        return if (joined.isEmpty()) joined else "$joined\n"
    }

    private fun normalizePath(path: String): String? = when (path) {
        "/dev/null" -> null
        else -> path.removePrefix("a/").removePrefix("b/")
    }

    private data class FilePatch(
        val oldPath: String?,
        val newPath: String?,
        val hunks: List<List<String>>,
    )

    private sealed interface ParseResult {
        data class Ok(val value: Changes) : ParseResult
        data class Err(val messages: List<String>) : ParseResult {
            fun buildMessage() = buildString {
                appendLine("Your previous output could not be applied.")
                appendLine("It violated the required unified diff format.")
                appendLine("Errors:")
                messages.forEach { appendLine(it) }
                appendLine("Respond again with ONLY a unified diff. Do NOT include prose, markdown fences, or explanations.")
                appendLine("IMPORTANT: Resend the COMPLETE patch you intend to apply from your previous message")
            }
        }
    }

    companion object {
        private val HUNK_HEADER = Regex("""@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@.*""")
    }
}
