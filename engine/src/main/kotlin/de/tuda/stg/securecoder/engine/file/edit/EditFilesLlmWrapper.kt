package de.tuda.stg.securecoder.engine.file.edit

import de.tuda.stg.securecoder.engine.file.edit.Changes.SearchedText
import de.tuda.stg.securecoder.engine.llm.ChatMessage
import de.tuda.stg.securecoder.engine.llm.ChatMessage.Role
import de.tuda.stg.securecoder.engine.llm.LlmClient
import de.tuda.stg.securecoder.filesystem.FileSystem
import de.tuda.stg.securecoder.engine.llm.ChatExchange
import kotlin.collections.plusAssign

class EditFilesLlmWrapper(
    private val llmClient: LlmClient
) {
    //TODO path => **uri** ; EditFilesLlmWrapper should be separate from the filesystem implementation
    private val prompt = """
        Your task it is to produce code. The agent will just parse the code you produce. So dont do a extensive review in your final answer!
        
        The edits must be described with *SEARCH/REPLACE* blocks enclosed in XML tags <EDITN>, where N represents the sequence number of *SEARCH/REPLACE* block.
        It's acceptable to add multiple *SEARCH/REPLACE* sections if you need to change multiple parts of the file.
        *SEARCH/REPLACE* block Rules:
        
        Every *SEARCH/REPLACE* block must contain 3 sections, each enclosed in XML tags:
        - <FILE_PATH>: The full **uri** of the file that will be modified.
        - <SEARCH>: A continuous, yet concise block of lines to search for in the existing source code (*SEARCH* pattern). If this section is empty, the lines from <REPLACE> will be added to the end of the file.
        - <REPLACE>: The lines to replace the existing code found using <SEARCH>. If this section is empty, the lines specified in <SEARCH> will be removed.
        All of these sections must be included in each *SEARCH/REPLACE* block.
        
        Each *SEARCH* pattern must match the existing source code exactly once, line for line, character for character, including all comments, docstrings, etc.
        Do not use a part of the line as *SEARCH* pattern. You must use full lines.
        Include enough lines to make code inside *SEARCH* pattern uniquely identifiable. A *SEARCH* pattern that produces multiple matches in the source code will be rejected as an error.
        Do not add backslashes to escape special characters. Write the code exactly as it should appear in the intended programming language.
        Do not use git diff style (+ and - at the beginning of the line) for *SEARCH/REPLACE* blocks.
        Do not use line numbers in *SEARCH/REPLACE* blocks. Do not enclose the *SEARCH/REPLACE* block or any of its components in triple quotes. Use only tags to separate the parameters.
        Do not use the same value for *SEARCH* and *REPLACE* parameters, as this will make no changes.
        
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
            val response = llmClient.chat(llmInput, params)
            messages += ChatMessage(Role.Assistant, response)
            when (val result = parse(response, fileSystem)) {
                is ParseResult.Ok -> return ChatResult(messages, result.value)
                is ParseResult.Err -> {
                    messages += ChatMessage(Role.User, result.buildMessage())
                    onParseError(result.messages, ChatExchange(llmInput, response))
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

    suspend fun parse(content: String, fileSystem: FileSystem): ParseResult {
        val results = mutableListOf<Changes.SearchReplace>()
        val allErrors = mutableListOf<String>()
        val contentCopy = if (content.endsWith("\n")) content else content + "\n"
        val editsRegex = Regex(
            "<EDIT(\\d{0,2})>(.*?)</EDIT\\1>",
            setOf(RegexOption.MULTILINE, RegexOption.DOT_MATCHES_ALL)
        )
        val matches = editsRegex.findAll(contentCopy).toList()

        if (matches.isEmpty()) {
            allErrors += """
                Could not find any edit blocks in the response.
                Example for the expected format:
                <EDIT1>
                <FILE_PATH>src/Main.java</FILE_PATH>
                <SEARCH>
                ...exact old text...
                </SEARCH>
                <REPLACE>
                ...new text...
                </REPLACE>
                </EDIT1>
                <EDIT2>
                <FILE_PATH>src/new.java</FILE_PATH>
                <SEARCH></SEARCH>
                <REPLACE>append</REPLACE>
                </EDIT2>
                """.trimIndent()
            return ParseResult.Err(allErrors)
        }

        for (match in matches) {
            val editContent = (match.groups[2]?.value ?: "").trim()
            if (editContent.isEmpty()) continue

            val currentFileName = getTextByXMLTag(editContent, "FILE_PATH")?.trim()
            val searchPartRaw = getTextByXMLTag(editContent, "SEARCH")
            val replacePartRaw = getTextByXMLTag(editContent, "REPLACE")

            val searchPart = removeStartingEmptyLine(searchPartRaw)
            val replacePart = removeStartingEmptyLine(replacePartRaw)

            if (currentFileName == null) {
                allErrors += "Missing or empty filename"
                continue
            }
            if (searchPartRaw == null) {
                allErrors += "Missing `<SEARCH>` section"
                continue
            }
            if (replacePartRaw == null) {
                allErrors += "Missing `<REPLACE>` section"
                continue
            }
            if (searchPart == replacePart) {
                allErrors += "`<SEARCH>` and `<REPLACE>` parameters are the same"
                continue
            }
            val replace = Changes.SearchReplace(currentFileName, SearchedText(searchPart ?: ""), replacePart ?: "")
            val content = fileSystem.getFile(currentFileName)?.content()
            val match = ApplyChanges.match(content, replace.searchedText)
            if (match is Matcher.MatchResult.Error) {
                allErrors += ApplyChanges.buildErrorMessage(currentFileName, searchPart ?: "", match)
                continue
            }
            results += replace
        }

        if (results.isEmpty()) {
            return ParseResult.Err(allErrors)
        }

        return ParseResult.Ok(Changes(results))
    }

    private fun getTextByXMLTag(container: String, tag: String): String? {
        val regex = Regex(
            "<$tag>(.*?)</$tag>",
            setOf(RegexOption.MULTILINE, RegexOption.DOT_MATCHES_ALL)
        )
        return regex.find(container)?.groups?.get(1)?.value
    }

    private fun removeStartingEmptyLine(content: String?): String? {
        if (content == null) return null
        return content.replaceFirst(Regex("^\\n"), "")
    }

    private fun appendPromptToLastSystem(messages: MutableList<ChatMessage>) {
        val lastSystemIndex = messages.indexOfLast { it.role == Role.System }
        if (lastSystemIndex >= 0) {
            val existing = messages[lastSystemIndex]
            val combined = "${existing.content}\n\n$prompt"
            messages[lastSystemIndex] = ChatMessage(Role.System, combined)
        } else {
            messages += ChatMessage(Role.System, prompt)
        }
    }
}
