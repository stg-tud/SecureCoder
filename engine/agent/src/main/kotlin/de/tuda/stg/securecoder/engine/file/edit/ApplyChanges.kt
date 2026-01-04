package de.tuda.stg.securecoder.engine.file.edit

import de.tuda.stg.securecoder.engine.file.edit.Matcher.MatchResult
import de.tuda.stg.securecoder.engine.file.edit.Matcher.MatchResult.Error
import de.tuda.stg.securecoder.engine.file.edit.Matcher.MatchResult.Success
import de.tuda.stg.securecoder.filesystem.FileSystem

object ApplyChanges {
    fun applyInText(original: String, edits: List<de.tuda.stg.securecoder.engine.file.edit.Changes.SearchReplace>): String {
        var text = original
        edits.forEach { sr ->
            when (val match = match(text, sr.searchedText)) {
                is Success -> text = applyInText(text, sr, match)
                is Error -> throw IllegalStateException("Match is not possible anymore: $match")
            }
        }
        return text
    }

    fun applyInText(original: String, action: de.tuda.stg.securecoder.engine.file.edit.Changes.SearchReplace, match: Success): String {
        return when (match) {
            is Success.Append -> original + action.replaceText
            is Success.Match -> buildString {
                if (match.end > original.length) {
                    throw IllegalStateException(
                        "Match end index (${match.end}) is out of bounds for string of length ${original.length}. "
                                + "Range: [${match.start}, ${match.end}), Replacement: '${action.replaceText}'"
                    )
                }
                append(original, 0, match.start)
                append(action.replaceText)
                append(original, match.end, original.length)
            }
        }
    }

    suspend fun applyAll(
        changes: de.tuda.stg.securecoder.engine.file.edit.Changes,
        loadFile: suspend (file: String) -> String?,
        saveFile: suspend (file: String, content: String) -> Unit
    ) {
        val byFile = changes.searchReplaces.groupBy(_root_ide_package_.de.tuda.stg.securecoder.engine.file.edit.Changes.SearchReplace::fileName)
        for ((file, edits) in byFile) {
            val original = loadFile(file) ?: ""
            val result = applyInText(original, edits)
            saveFile(file, result)
        }
    }

    fun match(text: String?, search: de.tuda.stg.securecoder.engine.file.edit.Changes.SearchedText): MatchResult {
        return _root_ide_package_.de.tuda.stg.securecoder.engine.file.edit.Matcher.RootMatcher.match(text, search)
    }

    fun buildErrorMessage(file: String, failedPattern: String, matchResult: Error): String = buildString {
        val separatorLine = "\n-------------------------------------------------\n"
        val headerMessage: String = when (matchResult) {
            is Error.NoMatch ->
                "your *SEARCH* pattern not found in file $file"
            is Error.ReplaceOnNotExistent ->
                "can only append to file $file as it is does not exist but your *SEARCH* pattern is not empty"
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

    suspend fun FileSystem.applyEdits(edits: List<de.tuda.stg.securecoder.engine.file.edit.Changes.SearchReplace>) {
        edits.groupBy { it.fileName }.forEach { (fileName, list) ->
            val original = getFile(fileName)?.content() ?: ""
            val updated = applyInText(original, list)
            upsert(fileName, updated)
        }
    }
}
