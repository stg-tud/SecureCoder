package de.tuda.stg.securecoder.plugin.toolwindow

import com.intellij.icons.AllIcons
import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.DialogWrapper
import com.intellij.ui.components.IconLabelButton
import com.intellij.ui.components.JBScrollPane
import com.intellij.util.ui.JBFont
import com.intellij.util.ui.JBUI
import de.tuda.stg.securecoder.plugin.edit.buildEditFilesPanel
import de.tuda.stg.securecoder.plugin.SecureCoderBundle
import de.tuda.stg.securecoder.plugin.engine.IntelliJProjectFileSystem
import de.tuda.stg.securecoder.plugin.engine.event.UiStreamEvent
import de.tuda.stg.securecoder.plugin.engine.event.UiStreamEvent.EditFilesValidation
import java.awt.Component
import java.awt.Dimension
import javax.swing.BorderFactory
import javax.swing.Box
import javax.swing.BoxLayout
import javax.swing.JButton
import javax.swing.JComponent
import javax.swing.JLabel
import javax.swing.JPanel
import javax.swing.JTextArea

object EventsPanel {
    fun addEventCard(event: UiStreamEvent, project: Project): JPanel {
        val card = object : JPanel() {
            override fun getMaximumSize() = Dimension(Int.MAX_VALUE, preferredSize.height)
        }.apply {
            layout = BoxLayout(this, BoxLayout.Y_AXIS)
            border = BorderFactory.createCompoundBorder(
                JBUI.Borders.customLine(JBUI.CurrentTheme.CustomFrameDecorations.separatorForeground(), 1),
                JBUI.Borders.empty(6)
            )
        }

        val titlePanel = JPanel().apply {
            layout = BoxLayout(this, BoxLayout.X_AXIS)
            border = JBUI.Borders.emptyBottom(4)
            alignmentX = Component.LEFT_ALIGNMENT
        }
        val title = when (event) {
            is UiStreamEvent.Message -> event.title
            is UiStreamEvent.EditFiles -> "Edit Files"
        }
        val icon = when (event) {
            is UiStreamEvent.Message -> event.icon
            is UiStreamEvent.EditFiles -> AllIcons.Actions.EditSource
        }
        val titleLabel = JLabel(title, icon, JLabel.LEADING).apply {
            font = JBFont.label().asBold()
        }
        titlePanel.add(titleLabel)

        if (event is UiStreamEvent.Message && event.debugText != null) {
            val debugButton = IconLabelButton(
                AllIcons.General.InspectionsEye,
                { showDebugTextDialog(project, event.debugText) }
            ).apply {
                toolTipText = SecureCoderBundle.message("toolwindow.events.show.debug.tooltip")
            }
            titlePanel.add(Box.createHorizontalGlue())
            titlePanel.add(debugButton)
        }

        val content = when (event) {
            is UiStreamEvent.Message -> JTextArea(event.description).apply {
                isEditable = false
                lineWrap = true
                wrapStyleWord = true
                border = JBUI.Borders.empty()
                background = card.background
                alignmentX = Component.LEFT_ALIGNMENT
            }
            is UiStreamEvent.EditFiles -> buildEditFilesPanel(
                project,
                event.changes,
                IntelliJProjectFileSystem(project)
            )
        }

        card.add(titlePanel)
        card.add(content)

        if (event is UiStreamEvent.EditFiles) {
            val bottomPanel = JPanel().apply {
                layout = BoxLayout(this, BoxLayout.X_AXIS)
                border = JBUI.Borders.emptyTop(6)
                alignmentX = Component.LEFT_ALIGNMENT
            }

            when (val validation = event.validation) {
                is EditFilesValidation.NotAvailable -> { /* no status shown */ }
                is EditFilesValidation.Running -> bottomPanel.add(
                    JLabel(
                        SecureCoderBundle.message("validation.in_progress"),
                        AllIcons.Actions.Refresh,
                        JLabel.LEADING
                    )
                )
                is EditFilesValidation.Succeeded -> bottomPanel.add(
                    JLabel(
                        SecureCoderBundle.message("validation.succeeded"),
                        AllIcons.General.InspectionsOK,
                        JLabel.LEADING
                    )
                )
                is EditFilesValidation.Failed -> {
                    bottomPanel.add(
                        JLabel(
                            validation.summary,
                            AllIcons.General.Warning,
                            JLabel.LEADING
                        )
                    )
                    val showAllBtn = IconLabelButton(
                        AllIcons.General.InspectionsEye,
                        { showDebugTextDialog(project, validation.details) }
                    ).apply {
                        toolTipText = SecureCoderBundle.message("toolwindow.events.show.debug.tooltip")
                        alignmentX = Component.RIGHT_ALIGNMENT
                    }
                    bottomPanel.add(Box.createHorizontalGlue())
                    bottomPanel.add(showAllBtn)
                }
            }

            if (bottomPanel.componentCount > 0) {
                card.add(bottomPanel)
            }
        }
        return card
    }

    private fun showDebugTextDialog(project: Project, text: String) {
        object : DialogWrapper(project) {
            init {
                title = SecureCoderBundle.message("toolwindow.events.debug.title")
                init()
                setSize(800, 600)
            }

            override fun createCenterPanel(): JComponent {
                val area = JTextArea(text).apply {
                    isEditable = false
                    lineWrap = true
                    wrapStyleWord = true
                    border = JBUI.Borders.empty()
                }
                return JBScrollPane(area).apply {
                    border = JBUI.Borders.empty()
                }
            }
        }.showAndGet()
    }
}
