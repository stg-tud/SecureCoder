package de.tuda.stg.securecoder.engine.file.edit

import de.tuda.stg.securecoder.engine.file.edit.Matcher.MatchResult
import de.tuda.stg.securecoder.engine.file.edit.Matcher.MatchResult.Error
import de.tuda.stg.securecoder.engine.file.edit.Matcher.MatchResult.Success

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
                append(original, 0, match.start)
                append(action.replaceText)
                append(original, match.end, original.length)
            }
        }
    }
    
    fun match(text: String, search: Changes.SearchedText): MatchResult {
        return Matcher.RootMatcher.match(text, search)
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
}
