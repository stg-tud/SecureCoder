package de.tuda.stg.securecoder.engine.file.edit

import de.tuda.stg.securecoder.engine.llm.LlmClient

enum class EditFormat(val wireName: String) {
    STRUCTURED_JSON("structured_json"),
    XML_SEARCH_REPLACE("xml_search_replace"),
    UNIFIED_DIFF("unified_diff"),
    WHOLE_FILE_JSON("whole_file_json");

    companion object {
        fun from(value: String?): EditFormat =
            entries.firstOrNull { it.wireName.equals(value?.trim(), ignoreCase = true) }
                ?: STRUCTURED_JSON
    }
}

object EditModeFactory {
    fun create(format: EditFormat, llmClient: LlmClient): EditFormatHandler = when (format) {
        EditFormat.STRUCTURED_JSON -> StructuredEditFilesLlmWrapper(llmClient)
        EditFormat.XML_SEARCH_REPLACE -> EditFilesLlmWrapper(llmClient)
        EditFormat.UNIFIED_DIFF -> UnifiedDiffLlmWrapper(llmClient)
        EditFormat.WHOLE_FILE_JSON -> WholeFileJsonLlmWrapper(llmClient)
    }
}
