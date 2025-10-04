package de.tuda.stg.securecoder.plugin.edit

import com.intellij.openapi.vfs.VfsUtilCore
import com.intellij.openapi.vfs.VirtualFileManager
import de.tuda.stg.securecoder.engine.file.edit.Changes

data class EditFileSummary(
    val fileUrl: String,
    val changes: List<Changes.SearchReplace>,
) {
    companion object {
        fun of(changes: Changes): List<EditFileSummary> {
            val grouped = changes.searchReplaces.groupBy { it.fileName }
            return grouped.map { (fileUrl, list) -> EditFileSummary(fileUrl, list) }
                .sortedBy { it.presentableName().lowercase() }
        }
    }

    fun presentableName(): String {
        val vf = VirtualFileManager.getInstance().findFileByUrl(fileUrl)
        return vf?.presentableUrl ?: VfsUtilCore.urlToPath(fileUrl)
    }

    fun changesCount(): Int = changes.size

    fun deltaLines(): Int = changes.sumOf { it.deltaLinesSnippet() }
}