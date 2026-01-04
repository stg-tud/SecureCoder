package de.tuda.stg.securecoder.engine.file.edit

data class Changes (
    val searchReplaces: List<SearchReplace>
) {
    data class SearchedText(val text: String) {
        fun isAppend(): Boolean = text.isEmpty()

        companion object {
            fun append() = SearchedText("")
        }
    }

    data class SearchReplace(
        val fileName: String,
        val searchedText: SearchedText,
        val replaceText: String
    ) {
        fun deltaLinesSnippet(): Int =
            if (isAppend()) countLines(replaceText)
            else countLines(replaceText) - countLines(searchedText.text)

        fun isAppend(): Boolean = searchedText.isAppend()
    }
}

private fun countLines(s: String): Int =
    if (s.isEmpty()) 0 else s.count { it == '\n' } + 1
