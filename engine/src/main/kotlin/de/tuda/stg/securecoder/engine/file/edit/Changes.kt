package de.tuda.stg.securecoder.engine.file.edit

data class Changes (
    val searchReplaces: List<SearchReplace>
) {
    data class SearchReplace(
        val fileName: String,
        val searchedText: String,
        val replaceText: String
    ) {
        fun deltaLinesSnippet(): Int =
            if (isAppend()) countLines(replaceText)
            else countLines(replaceText) - countLines(searchedText)

        fun isAppend(): Boolean = searchedText.isEmpty()
    }
}

private fun countLines(s: String): Int =
    if (s.isEmpty()) 0 else s.count { it == '\n' } + 1
