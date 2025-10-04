package de.tuda.stg.securecoder.engine.file.edit

object ApplyChanges {
    fun applyInText(original: String, edits: List<Changes.SearchReplace>): String {
        var text = original
        edits.forEach { sr ->
            if (sr.isAppend()) {
                text += sr.replaceText
            } else {
                val idx = text.indexOf(sr.searchedText)
                if (idx >= 0) {
                    text = text.take(idx) + sr.replaceText + text.substring(idx + sr.searchedText.length)
                }
            }
        }
        return text
    }
}
