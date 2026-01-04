package de.tuda.stg.securecoder.engine.file.edit

import de.tuda.stg.securecoder.engine.file.edit.Changes.SearchedText
import de.tuda.stg.securecoder.engine.llm.ChatMessage
import de.tuda.stg.securecoder.engine.llm.ChatMessage.Role
import de.tuda.stg.securecoder.engine.llm.LlmClient
import de.tuda.stg.securecoder.engine.llm.LLMDescription
import de.tuda.stg.securecoder.engine.llm.chatStructured
import de.tuda.stg.securecoder.filesystem.FileSystem
import de.tuda.stg.securecoder.engine.llm.ChatExchange
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import kotlin.collections.plusAssign

class StructuredEditFilesLlmWrapper(
    private val llmClient: LlmClient
) {
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


    suspend fun chat(
        messages: List<ChatMessage>,
        fileSystem: FileSystem,
        params: LlmClient.GenerationParams = LlmClient.GenerationParams(),
        onParseError: suspend (parseErrors: List<String>, llm: ChatExchange) -> Unit = { _, _ -> },
        attempts: Int = 3
    ): ChatResult {
        val messages = messages.toMutableList()
        appendPromptToLastSystem(messages)
        repeat(attempts) {
            val llmInput = messages.toList()
            val structured = llmClient.chatStructured<StructuredEdits>(llmInput, params)
            messages += ChatMessage(Role.Assistant, Json.encodeToString(structured))
            when (val result = validateAndConvert(structured, fileSystem)) {
                is ParseResult.Ok -> return ChatResult(messages, result.value)
                is ParseResult.Err -> {
                    messages += ChatMessage(Role.User, result.buildMessage())
                    onParseError(result.messages, ChatExchange(llmInput, messages.last().content))
                }
            }
        }
        return ChatResult(messages, null)
    }

    data class ChatResult(val messages: List<ChatMessage>, val changes: Changes?) {
        fun changesMessage() = messages.last { it.role == Role.Assistant }
    }

    sealed interface ParseResult {
        data class Ok(val value: Changes) : ParseResult
        data class Err(val messages: List<String>) : ParseResult {
            fun buildMessage() = buildString {
                appendLine("Your previous output could not be applied.")
                appendLine("It violated the required format.")
                appendLine("Errors:")
                messages.forEach { appendLine(it) }
                appendLine("Respond again with ONLY edit blocks that strictly follow the rules. Do NOT include prose, markdown, or explanations.")
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
            val searchPart = e.search
            val replacePart = e.replace
            if (file.isEmpty()) {
                allErrors += "`filePath` should not be empty"
                continue
            }
            if (searchPart == replacePart) {
                allErrors += "`search` and `replace` parameters are the same"
                continue
            }
            val replace = Changes.SearchReplace(file, SearchedText(searchPart), replacePart)
            val content = fileSystem.getFile(file)?.content()
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
