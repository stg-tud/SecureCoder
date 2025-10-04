package de.tuda.stg.securecoder.engine.file.edit

data class Changes (
    val searchReplaces: List<SearchReplace>
) {
    data class SearchReplace(
        val fileName: String,
        val searchedText: String,
        val replaceText: String
    )
}
