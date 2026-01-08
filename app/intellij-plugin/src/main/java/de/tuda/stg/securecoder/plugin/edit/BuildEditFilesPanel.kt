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
import com.intellij.notification.Notification
import com.intellij.notification.NotificationType
import com.intellij.notification.Notifications
import com.intellij.openapi.fileEditor.FileDocumentManager
import com.intellij.openapi.progress.ProgressIndicator
import com.intellij.openapi.progress.ProgressManager
import com.intellij.openapi.progress.Task
import com.intellij.openapi.project.Project
import com.intellij.openapi.vfs.*
import com.intellij.ui.components.JBLabel
import com.intellij.util.ui.JBUI
import com.intellij.util.ui.JBUI.Borders
import de.tuda.stg.securecoder.engine.file.edit.ApplyChanges
import de.tuda.stg.securecoder.engine.file.edit.ApplyChanges.applyEdits
import de.tuda.stg.securecoder.filesystem.FileSystem
import de.tuda.stg.securecoder.plugin.SecureCoderBundle
import com.intellij.openapi.diagnostic.Logger
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.runBlocking
import javax.swing.BorderFactory
import javax.swing.SwingUtilities
import kotlin.math.abs

fun buildEditFilesPanel(
    project: Project,
    changes: Changes,
    fileSystem: FileSystem
): JComponent {
    val panel = JPanel().apply {
        layout = BoxLayout(this, BoxLayout.Y_AXIS)
        alignmentX = Component.LEFT_ALIGNMENT
        border = Borders.empty()
    }

    val grouped = changes.searchReplaces.groupBy { it.fileName }
    val summaries = EditFileSummary.of(project, changes)

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

        add(Box.createHorizontalGlue())

        val allEdits = changes.searchReplaces
        val applyBtn = JButton(SecureCoderBundle.message("edit.apply")).apply {
            isEnabled = allEdits.isNotEmpty()
            toolTipText = SecureCoderBundle.message("edit.apply.tooltip")
            addActionListener {
                if (allEdits.isEmpty()) return@addActionListener
                isEnabled = false
                ProgressManager.getInstance().run(object : Task.Backgroundable(
                    project,
                    SecureCoderBundle.message("edit.apply.progress"),
                    true
                ) {
                    override fun run(indicator: ProgressIndicator) {
                        indicator.isIndeterminate = true
                        try {
                            runBlocking(Dispatchers.IO) {
                                fileSystem.applyEdits(allEdits)
                            }

                            SwingUtilities.invokeLater {
                                Notifications.Bus.notify(
                                    notification(
                                        SecureCoderBundle.message("edit.apply.done.title"),
                                        SecureCoderBundle.message("edit.apply.done.body", allEdits.size),
                                        NotificationType.INFORMATION
                                    ),
                                    project
                                )
                            }
                        } catch (throwable: Throwable) {
                            LOG.error("Failed to apply edits", throwable)
                            SwingUtilities.invokeLater {
                                Notifications.Bus.notify(
                                    notification(
                                        SecureCoderBundle.message("edit.apply.error.title"),
                                        throwable.message ?: throwable.toString(),
                                        NotificationType.ERROR
                                    ),
                                    project
                                )
                            }
                        } finally {
                            SwingUtilities.invokeLater { isEnabled = true }
                        }
                    }
                })
            }
        }
        add(applyBtn)
    }
    panel.add(header)

    summaries.forEach { summary ->
        val row = JPanel(BorderLayout()).apply {
            border = BorderFactory.createCompoundBorder(
                Borders.empty(4),
                BorderFactory.createCompoundBorder(
                    Borders.customLine(separatorForeground(), 1),
                    Borders.empty(3)
                )
            )
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

private val LOG: Logger = Logger.getInstance("BuildEditFilesPanel")

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
private fun notification(title: String, content: String, type: NotificationType) =
    Notification(
        "securecoder",
        title,
        content,
        type
    )
