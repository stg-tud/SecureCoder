package de.tuda.stg.securecoder.engine.file.edit

import de.tuda.stg.securecoder.engine.llm.ChatExchange
import de.tuda.stg.securecoder.engine.llm.ChatMessage
import de.tuda.stg.securecoder.engine.llm.ChatMessage.Role
import de.tuda.stg.securecoder.engine.llm.LLMDescription
import de.tuda.stg.securecoder.engine.llm.LlmClient
import de.tuda.stg.securecoder.engine.llm.LlmUpstreamException
import de.tuda.stg.securecoder.engine.llm.chatStructured
import de.tuda.stg.securecoder.engine.workflow.FeedbackBuilder.buildFeedbackForLlm
import de.tuda.stg.securecoder.engine.workflow.GuardianExecutor
import de.tuda.stg.securecoder.filesystem.FileSystem
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

class WholeFileJsonLlmWrapper(
    private val llmClient: LlmClient,
) : EditFormatHandler {
    override val formatId: String = "whole_file_json"

    private val prompt = """
        Your task it is to produce code. The agent will just parse the code you produce. So dont do a extensive review in your final answer!

        Return the COMPLETE contents of every file you want to write in a strict JSON object.
        Each file entry must contain:
        - `filePath`: the full file path / uri
        - `content`: the complete desired file contents

        For existing files, `content` must be the entire final file, not a patch.
        For new files, `content` must be the entire file content.
        If you need to fix a file after feedback, resend the entire file contents again.
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
            val structured = try {
                llmClient.chatStructured<WholeFileEdits>(llmInput, params)
            } catch (e: LlmUpstreamException) {
                throw e
            } catch (e: Exception) {
                val message = e.message ?: e.toString()
                val feedback = buildString {
                    appendLine("Your previous output could not be decoded as the required whole-file JSON.")
                    appendLine("Error: $message")
                    appendLine("Respond again with ONLY a JSON object that matches the provided schema. Do NOT include prose, markdown, or explanations.")
                }
                messages += ChatMessage(Role.User, feedback)
                onParseError(listOf(message), ChatExchange(llmInput, feedback))
                return@repeat
            }
            messages += ChatMessage(Role.Assistant, Json.encodeToString(structured))
            when (val result = validateAndConvert(structured, fileSystem)) {
                is ParseResult.Ok -> return EditFormatHandler.ChatResult(messages, result.value)
                is ParseResult.Err -> {
                    messages += ChatMessage(Role.User, result.buildMessage())
                    onParseError(result.messages, ChatExchange(llmInput, messages.last().content))
                }
            }
        }
        return EditFormatHandler.ChatResult(messages, null)
    }

    override fun buildGuardianFeedback(
        guardianResult: GuardianExecutor.GuardianResult,
        reviewMode: ReviewMode,
    ): String = guardianResult.buildFeedbackForLlm(
        responseInstruction = "Respond again with ONLY the whole-file JSON object required by the current schema. Do NOT include prose.",
        reviewModeInstruction = when (reviewMode) {
            ReviewMode.PATCH -> "Patch the current working version by resending complete file contents for the affected files."
            ReviewMode.REPLACE -> "Regenerate the complete fixed file set from scratch against the original context."
        },
    )

    private fun appendPromptToLastSystem(messages: MutableList<ChatMessage>) {
        val lastSystemIndex = messages.indexOfLast { it.role == Role.System }
        if (lastSystemIndex >= 0) {
            val existing = messages[lastSystemIndex]
            messages[lastSystemIndex] = ChatMessage(
                Role.System,
                "${existing.content}\n\n$prompt\n\nRespond ONLY with a JSON object that matches the provided schema. Do not include explanations.",
            )
        } else {
            messages += ChatMessage(Role.System, "$prompt\n\nRespond ONLY with a JSON object that matches the provided schema. Do not include explanations.")
        }
    }

    private suspend fun validateAndConvert(structured: WholeFileEdits, fileSystem: FileSystem): ParseResult {
        val results = mutableListOf<Changes.SearchReplace>()
        val errors = mutableListOf<String>()
        if (structured.files.isEmpty()) {
            errors += "No files provided. Provide at least one file rewrite."
            return ParseResult.Err(errors)
        }
        for (file in structured.files) {
            val filePath = file.filePath.trim()
            if (filePath.isEmpty()) {
                errors += "`filePath` should not be empty"
                continue
            }
            val current = fileSystem.getFile(filePath)?.content()
            if (current == file.content) {
                errors += "File `$filePath` was resent without changes"
                continue
            }
            results += Changes.SearchReplace(
                fileName = filePath,
                searchedText = Changes.SearchedText(current ?: ""),
                replaceText = file.content,
            )
        }
        if (results.isEmpty()) return ParseResult.Err(errors)
        return ParseResult.Ok(Changes(results))
    }

    private sealed interface ParseResult {
        data class Ok(val value: Changes) : ParseResult
        data class Err(val messages: List<String>) : ParseResult {
            fun buildMessage() = buildString {
                appendLine("Your previous output could not be applied.")
                appendLine("It violated the required whole-file format.")
                appendLine("Errors:")
                messages.forEach { appendLine(it) }
                appendLine("Respond again with ONLY a JSON object that matches the provided schema. Do NOT include prose, markdown, or explanations.")
                appendLine("IMPORTANT: Resend the COMPLETE set of files you intend to write from your previous message")
            }
        }
    }

    @Serializable
    data class WholeFileEdits(
        @LLMDescription("List of file rewrites to apply")
        val files: List<FileRewrite>,
    )

    @Serializable
    data class FileRewrite(
        @LLMDescription("The full file path / uri of the file to rewrite")
        val filePath: String,
        @LLMDescription("The complete final contents of the file")
        val content: String,
    )
}
