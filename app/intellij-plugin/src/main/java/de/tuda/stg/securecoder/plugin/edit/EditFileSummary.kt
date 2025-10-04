package de.tuda.stg.securecoder.plugin.edit

import com.intellij.openapi.fileEditor.UniqueVFilePathBuilder
import com.intellij.openapi.project.Project
import com.intellij.openapi.vfs.VfsUtilCore
import com.intellij.openapi.vfs.VirtualFileManager
import de.tuda.stg.securecoder.engine.file.edit.Changes

data class EditFileSummary(
    val project: Project,
    val fileUrl: String,
    val changes: List<Changes.SearchReplace>,
) {
    companion object {
        fun of(project: Project, changes: Changes): List<EditFileSummary> {
            val grouped = changes.searchReplaces.groupBy { it.fileName }
            return grouped.map { (fileUrl, list) -> EditFileSummary(project, fileUrl, list) }
                .sortedBy { it.presentableName().lowercase() }
        }
    }

    fun presentableName(): String {
        val virtualFile = VirtualFileManager.getInstance().findFileByUrl(fileUrl)
        return virtualFile
            ?.let { UniqueVFilePathBuilder.getInstance().getUniqueVirtualFilePath(project, it) }
            ?: VfsUtilCore.urlToPath(fileUrl)
    }

    fun changesCount(): Int = changes.size

    fun deltaLines(): Int = changes.sumOf { it.deltaLinesSnippet() }
}