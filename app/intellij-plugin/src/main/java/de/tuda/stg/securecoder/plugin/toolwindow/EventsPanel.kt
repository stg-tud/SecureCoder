package de.tuda.stg.securecoder.plugin.toolwindow

import com.intellij.icons.AllIcons
import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.DialogWrapper
import com.intellij.ui.components.JBScrollPane
import com.intellij.util.ui.JBFont
import com.intellij.util.ui.JBUI
import de.tuda.stg.securecoder.plugin.edit.buildEditFilesPanel
import de.tuda.stg.securecoder.plugin.SecureCoderBundle
import de.tuda.stg.securecoder.plugin.engine.IntelliJProjectFileSystem
import de.tuda.stg.securecoder.plugin.engine.event.UiStreamEvent
import java.awt.Component
import java.awt.Dimension
import javax.swing.BorderFactory
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
            val debugButton = JButton(AllIcons.General.Information).apply {
                border = JBUI.Borders.empty()
                isContentAreaFilled = false
                toolTipText = SecureCoderBundle.message("toolwindow.events.show.debug.tooltip")
                addActionListener { _ ->
                    showDebugTextDialog(project, event.debugText)
                }
            }
            titlePanel.add(JPanel().apply {
                layout = BoxLayout(this, BoxLayout.X_AXIS)
            })
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
