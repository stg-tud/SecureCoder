package de.tuda.stg.securecoder.plugin.edit

import com.intellij.openapi.vfs.VirtualFile
import com.intellij.openapi.vfs.VirtualFileManager
import com.intellij.util.ui.JBFont
import com.intellij.util.ui.JBUI.CurrentTheme.CustomFrameDecorations.separatorForeground
import de.tuda.stg.securecoder.engine.file.edit.Changes
import java.awt.BorderLayout
import java.awt.Component
import java.awt.Cursor
import java.awt.Dimension
import javax.swing.Box
import javax.swing.BoxLayout
import javax.swing.JButton
import javax.swing.JComponent
import javax.swing.JLabel
import javax.swing.JPanel

import com.intellij.diff.DiffContentFactory
import com.intellij.diff.DiffManager
import com.intellij.diff.requests.SimpleDiffRequest
import com.intellij.icons.AllIcons
import com.intellij.openapi.fileEditor.FileDocumentManager
import com.intellij.openapi.project.Project
import com.intellij.openapi.vfs.*
import com.intellij.ui.components.JBLabel
import com.intellij.util.ui.JBUI
import com.intellij.util.ui.JBUI.Borders
import de.tuda.stg.securecoder.engine.file.edit.ApplyChanges
import de.tuda.stg.securecoder.plugin.SecureCoderBundle
import kotlin.math.abs

fun buildEditFilesPanel(project: Project, changes: Changes): JComponent {
    val panel = JPanel().apply {
        layout = BoxLayout(this, BoxLayout.Y_AXIS)
        alignmentX = Component.LEFT_ALIGNMENT
        border = Borders.empty()
    }

    val grouped = changes.searchReplaces.groupBy { it.fileName }
    val summaries = EditFileSummary.of(changes)

    val header = JPanel().apply {
        layout = BoxLayout(this, BoxLayout.X_AXIS)
        alignmentX = Component.LEFT_ALIGNMENT
        border = Borders.emptyBottom(6)
        val files = summaries.size
        val changesCount = summaries.sumOf { it.changesCount() }
        val delta = summaries.sumOf { abs(it.deltaLines()) }
        add(JBLabel(SecureCoderBundle.message("edit.summary", files, changesCount, delta)).apply {
            font = JBFont.label().asBold()
        })
    }
    panel.add(header)

    summaries.forEach { summary ->
        val row = JPanel(BorderLayout()).apply {
            border = Borders.merge(Borders.customLine(separatorForeground(), 1), Borders.empty(6), true)
            alignmentX = Component.LEFT_ALIGNMENT
            cursor = Cursor.getPredefinedCursor(Cursor.HAND_CURSOR)
            toolTipText = SecureCoderBundle.message("edit.show.diff.tooltip")
        }

        val title = JLabel(summary.presentableName()).apply { font = JBFont.label().asBold() }
        val meta = JLabel(SecureCoderBundle.message("edit.changes.meta", summary.changesCount(), summary.deltaLines()))

        val textPanel = JPanel().apply {
            layout = BoxLayout(this, BoxLayout.Y_AXIS)
            isOpaque = false
            add(title)
            add(Box.createVerticalStrut(JBUI.scale(2)))
            add(meta)
        }

        val openBtn = JButton(AllIcons.Actions.Diff).apply {
            toolTipText = SecureCoderBundle.message("edit.show.diff.tooltip")
            addActionListener {
                openDiffForFile(project, summary.fileUrl, grouped[summary.fileUrl].orEmpty())
            }
        }

        row.add(textPanel, BorderLayout.CENTER)
        row.add(openBtn, BorderLayout.EAST)
        row.addMouseListener(object : java.awt.event.MouseAdapter() {
            override fun mouseClicked(e: java.awt.event.MouseEvent?) {
                openDiffForFile(project, summary.fileUrl, grouped[summary.fileUrl].orEmpty())
            }
        })

        panel.add(row)
        panel.add(Box.createRigidArea(Dimension(0, JBUI.scale(2))))
    }

    return panel
}

private fun openDiffForFile(project: Project, fileUrl: String, edits: List<Changes.SearchReplace>) {
    val vfm = VirtualFileManager.getInstance()
    val vFile: VirtualFile? = vfm.findFileByUrl(fileUrl)

    val originalText: String = vFile?.let {
        FileDocumentManager.getInstance().getDocument(it)?.text
    } ?: ""

    val patchedText = ApplyChanges.applyInText(originalText, edits)

    val contentFactory = DiffContentFactory.getInstance()
    val left = contentFactory.create(project, originalText)
    val right = contentFactory.create(project, patchedText)

    val name = vFile?.name ?: VfsUtilCore.urlToPath(fileUrl).substringAfterLast('/').ifEmpty { "(neu)" }
    val title = if (vFile == null) SecureCoderBundle.message("edit.proposed.new.file.title", name)
    else SecureCoderBundle.message("edit.proposed.changes.title", name)

    val request = SimpleDiffRequest(
        title,
        left,  right,
        if (vFile == null) SecureCoderBundle.message("edit.empty") else SecureCoderBundle.message("edit.current.content"),
        SecureCoderBundle.message("edit.with.changes")
    )

    DiffManager.getInstance().showDiff(project, request)
}
