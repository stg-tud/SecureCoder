package de.tuda.stg.securecoder.engine.file.edit

import de.tuda.stg.securecoder.engine.file.edit.Changes.SearchedText
import de.tuda.stg.securecoder.engine.llm.ChatMessage
import de.tuda.stg.securecoder.engine.llm.ChatMessage.Role
import de.tuda.stg.securecoder.engine.llm.LlmClient
import de.tuda.stg.securecoder.engine.llm.LLMDescription
import de.tuda.stg.securecoder.engine.llm.LlmUpstreamException
import de.tuda.stg.securecoder.engine.llm.chatStructured
import de.tuda.stg.securecoder.engine.workflow.FeedbackBuilder.buildFeedbackForLlm
import de.tuda.stg.securecoder.engine.workflow.GuardianExecutor
import de.tuda.stg.securecoder.filesystem.FileSystem
import de.tuda.stg.securecoder.engine.llm.ChatExchange
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlin.collections.plusAssign

class StructuredEditFilesLlmWrapper(
    private val llmClient: LlmClient
) : EditFormatHandler {
    override val formatId: String = "structured_json"
    //TODO path => **uri** ; EditFilesLlmWrapper should be separate from the filesystem implementation
    private val prompt = """
        Your task it is to produce code. The agent will just parse the code you produce. So dont do a extensive review in your final answer!
        
        It's acceptable to add multiple *search/REPLACE* sections if you need to change multiple parts of the file.
        To create a file: search must be empty and replace must contain the entire file content
        Each *search* pattern must match the existing source code exactly once, line for line, character for character, including all comments, docstrings, etc.
        Do not use a part of the line as *search* pattern. You must use full lines.
        Include enough lines to make code inside *search* pattern uniquely identifiable. A *search* pattern that produces multiple matches in the source code will be rejected as an error.
        Do not add backslashes to escape special characters. Write the code exactly as it should appear in the intended programming language.
        Do not use git diff style (+ and - at the beginning of the line) for *search/REPLACE* blocks.
        Do not use line numbers in *search/REPLACE* blocks. Do not enclose the *search/REPLACE* block or any of its components in triple quotes. Use only tags to separate the parameters.
        Do not use the same value for *search* and *REPLACE* parameters, as this will make no changes.
        
        If you need to edit a file again after making changes, use the latest version of the code that includes all your modifications applied during **current session**.
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
        for (attempt in 0 until attempts) {
            val llmInput = messages.toList()
            val structured = try {
                llmClient.chatStructured<StructuredEdits>(llmInput, params)
            } catch (e: LlmUpstreamException) {
                throw e
            } catch (e: Exception) {
                val message = e.message ?: e.toString()
                val feedback = buildString {
                    appendLine("Your previous output could not be decoded as the required structured edit JSON.")
                    appendLine("Error: $message")
                    appendLine("Respond again with ONLY a JSON object that matches the provided schema. Do NOT include prose, markdown, or explanations.")
                }
                messages += ChatMessage(Role.User, feedback)
                onParseError(listOf(message), ChatExchange(llmInput, feedback))
                continue
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

    sealed interface ParseResult {
        data class Ok(val value: Changes) : ParseResult
        data class Err(val messages: List<String>) : ParseResult {
            fun buildMessage() = buildString {
                appendLine("Your previous output could not be applied.")
                appendLine("It violated the required format.")
                appendLine("Errors:")
                messages.forEach { appendLine(it) }
                appendLine("Respond again with ONLY a JSON object that matches the provided schema. Do NOT include prose, markdown, or explanations.")
                appendLine("IMPORTANT: Resend the COMPLETE set of edits you intend to apply from your previous message")
            }
        }
    }

    private suspend fun validateAndConvert(structured: StructuredEdits, fileSystem: FileSystem): ParseResult {
        val results = mutableListOf<Changes.SearchReplace>()
        val allErrors = mutableListOf<String>()
        if (structured.edits.isEmpty()) {
            allErrors += "No edits provided. Provide at least one edit block."
            return ParseResult.Err(allErrors)
        }
        for (e in structured.edits) {
            val file = e.filePath.trim()
            var searchPart = e.search
            val replacePart = e.replace
            if (file.isEmpty()) {
                allErrors += "`filePath` should not be empty"
                continue
            }
            if (searchPart == replacePart) {
                allErrors += "`search` and `replace` parameters are the same"
                continue
            }
            val content = fileSystem.getFile(file)?.content()
            if (content == null && searchPart.isNotEmpty() && replacePart.isNotEmpty()) {
                searchPart = ""
            }
            val replace = Changes.SearchReplace(file, SearchedText(searchPart), replacePart)
            val match = ApplyChanges.match(content, replace.searchedText)
            if (match is Matcher.MatchResult.Error) {
                allErrors += ApplyChanges.buildErrorMessage(file, searchPart, match)
                continue
            }
            results += replace
        }
        if (results.isEmpty()) return ParseResult.Err(allErrors)
        return ParseResult.Ok(Changes(results))
    }

    private fun appendPromptToLastSystem(messages: MutableList<ChatMessage>) {
        val lastSystemIndex = messages.indexOfLast { it.role == Role.System }
        if (lastSystemIndex >= 0) {
            val existing = messages[lastSystemIndex]
            val combined = "${existing.content}\n\n$prompt\n\nRespond ONLY with a JSON object that matches the provided schema. Do not include explanations."
            messages[lastSystemIndex] = ChatMessage(Role.System, combined)
        } else {
            messages += ChatMessage(Role.System, "$prompt\n\nRespond ONLY with a JSON object that matches the provided schema. Do not include explanations.")
        }
    }

    override fun buildGuardianFeedback(
        guardianResult: GuardianExecutor.GuardianResult,
        reviewMode: ReviewMode,
    ): String = guardianResult.buildFeedbackForLlm(
        responseInstruction = "Respond again with ONLY the structured JSON edit object required by the current schema. Do NOT include prose.",
        reviewModeInstruction = when (reviewMode) {
            ReviewMode.PATCH -> "Patch the current working version from your previous changes."
            ReviewMode.REPLACE -> "Regenerate the complete fixed file set from scratch against the original context."
        },
    )

    @Serializable
    data class StructuredEdits(
        @LLMDescription("List of edit operations to apply")
        val edits: List<EditOperation>
    )

    @Serializable
    data class EditOperation(
        @LLMDescription("The full **uri** of the file that will be modified")
        val filePath: String,
        @LLMDescription("A continuous, yet concise block of lines to search for in the existing source code (*search* pattern). If this section is empty, the lines from `replace` will be added to the end of the file.")
        val search: String,
        @LLMDescription("The lines to replace the existing code found using `search`. If this section is empty, the lines specified in `search` will be removed.")
        val replace: String,
    )
}
