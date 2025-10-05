package de.tuda.stg.securecoder.engine.file.edit

import de.tuda.stg.securecoder.engine.file.edit.ApplyChanges.MatchResult.Error
import de.tuda.stg.securecoder.engine.file.edit.ApplyChanges.MatchResult.Success

object ApplyChanges {
    fun applyInText(original: String, edits: List<Changes.SearchReplace>): String {
        var text = original
        edits.forEach { sr ->
            when (val match = match(text, sr.searchedText)) {
                is Success -> text = applyInText(text, sr, match)
                is Error -> throw IllegalStateException("Match is not possible anymore: $match")
            }
        }
        return text
    }

    fun applyInText(original: String, action: Changes.SearchReplace, match: Success): String {
        return when (match) {
            is Success.Append -> original + action.replaceText
            is Success.Match -> buildString { 
                append(original.take(match.index))
                append(action.replaceText)
                append(action.searchedText.text.length)
            }
        }
    }
    
    fun match(text: String, search: Changes.SearchedText): MatchResult {
        if (search.isAppend()) {
            return Success.Append
        }
        if (text.isEmpty()) {
            return Error.ReplaceOnEmpty
        }
        val idx = text.indexesOf(search.text)
        return when (idx.size) {
            1 -> Success.Match(idx.first())
            0 -> Error.NoMatch
            else -> Error.MultipleMatch(idx)
        }
    }

    sealed interface MatchResult {
        sealed interface Error : MatchResult {
            object ReplaceOnEmpty : Error
            object NoMatch : Error
            data class MultipleMatch (val matches: List<Int>) : Error
        }
        sealed interface Success : MatchResult {
            object Append : Success
            class Match (val index: Int) : Success
        }
    }

    fun buildErrorMessage(file: String, failedPattern: String, matchResult: Error): String = buildString {
        val separatorLine = "\n-------------------------------------------------\n"
        val headerMessage: String = when (matchResult) {
            is Error.NoMatch ->
                "your *SEARCH* pattern not found in file $file"
            is Error.ReplaceOnEmpty ->
                "can only append to file $file as it is empty or does not exist but your *SEARCH* pattern is not empty"
            is Error.MultipleMatch ->
                "your *SEARCH* pattern has several matches in $file"
        }
        append("""
            |ERROR: $headerMessage:
            |Failed *SEARCH* pattern:
            |```
            |$failedPattern
            |```
            |
            """.trimMargin()
        )
        append(separatorLine)
        /*msg += "*SEARCH* pattern should match exact lines of the original code"
        msg += "Here is the most similar chunk of code in the file:"
        msg += separatorLine
        msg += printed
        msg += separatorLine*/
        if (matchResult is Error.MultipleMatch) {
            appendLine("Here are the matches of your *SEARCH* pattern in the file:")
            matchResult.matches.forEach {
                appendLine(" - at index $it")
                appendLine(separatorLine)
            }
            appendLine("Include enough lines to make the *SEARCH* pattern uniquely match the lines to change.")
            appendLine()
        }
    }

    private fun String.indexesOf(needle: String): List<Int> {
        require(needle.isNotEmpty()) { "needle must not be empty" }
        val result = mutableListOf<Int>()
        var start = 0
        while (true) {
            val i = indexOf(needle, start)
            if (i < 0) break
            result += i
            start = i + 1
        }
        return result
    }
}
