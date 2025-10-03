package de.tuda.stg.securecoder.plugin

import com.intellij.icons.AllIcons
import com.intellij.openapi.application.EDT
import com.intellij.openapi.components.service
import com.intellij.openapi.project.DumbAware
import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import com.intellij.openapi.wm.ToolWindow
import com.intellij.openapi.wm.ToolWindowFactory
import com.intellij.ui.components.JBScrollPane
import com.intellij.ui.components.JBTextArea
import com.intellij.ui.content.ContentFactory
import com.intellij.util.ui.JBFont
import com.intellij.util.ui.JBUI
import com.intellij.util.ui.JBUI.Borders
import com.intellij.util.ui.JBUI.CurrentTheme.CustomFrameDecorations.separatorForeground
import de.tuda.stg.securecoder.engine.stream.EventIcon
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.awt.BorderLayout
import java.awt.Component
import java.awt.Dimension
import javax.swing.Box
import javax.swing.BoxLayout
import javax.swing.Icon
import javax.swing.JButton
import javax.swing.JLabel
import javax.swing.JPanel
import javax.swing.JTextArea
import javax.swing.ScrollPaneConstants
import javax.swing.SwingUtilities

class SecureCoderAiToolWindowFactory : ToolWindowFactory, DumbAware {
    private lateinit var eventsPanel: JPanel
    private lateinit var eventsScrollPane: JBScrollPane

    override fun createToolWindowContent(project: Project, toolWindow: ToolWindow) {
        val root = createRoot(project)
        val contentFactory = ContentFactory.getInstance()
        val content = contentFactory.createContent(root, null, false)
        toolWindow.contentManager.addContent(content)
    }

    private fun createRoot(project: Project): JPanel = JPanel(BorderLayout()).apply {
        val inputArea = createInputArea()
        val scroll = wrapTextInScrollPane(inputArea)
        val preferredHeight = scroll.preferredSize.height
        scroll.maximumSize = Dimension(Int.MAX_VALUE, preferredHeight)
        val submit = createSubmitButton(preferredHeight)
        val row = buildInputRow(scroll, submit)
        add(row, BorderLayout.NORTH)

        eventsPanel = JPanel().apply {
            layout = BoxLayout(this, BoxLayout.Y_AXIS)
            border = Borders.empty(8)
        }
        eventsScrollPane = JBScrollPane(eventsPanel).apply {
            verticalScrollBarPolicy = ScrollPaneConstants.VERTICAL_SCROLLBAR_AS_NEEDED
            horizontalScrollBarPolicy = ScrollPaneConstants.HORIZONTAL_SCROLLBAR_NEVER
            border = Borders.empty()
        }
        add(eventsScrollPane, BorderLayout.CENTER)
        setupSubmitAction(project, inputArea, submit)
    }

    private fun buildInputRow(scroll: JBScrollPane, submit: JButton): JPanel {
        val row = JPanel().apply {
            layout = BoxLayout(this, BoxLayout.X_AXIS)
            border = Borders.empty(8)
        }
        row.add(scroll)
        row.add(Box.createRigidArea(Dimension(JBUI.scale(8), 0)))
        row.add(submit)
        return row
    }

    private fun createInputArea(): JBTextArea = JBTextArea().apply {
        lineWrap = true
        wrapStyleWord = true
        rows = 5
        columns = 30
        border = Borders.empty(8)
    }

    private fun wrapTextInScrollPane(inputArea: JBTextArea): JBScrollPane = JBScrollPane(inputArea).apply {
        verticalScrollBarPolicy = ScrollPaneConstants.VERTICAL_SCROLLBAR_AS_NEEDED
        horizontalScrollBarPolicy = ScrollPaneConstants.HORIZONTAL_SCROLLBAR_NEVER
    }

    private fun createSubmitButton(height: Int): JButton = JButton(SecureCoderBundle.message("toolwindow.submit")).apply {
        maximumSize = Dimension(preferredSize.width, height)
    }

    private fun setupSubmitAction(project: Project, inputArea: JBTextArea, submit: JButton) {
        submit.addActionListener {
            val text = inputArea.text.trim()
            if (text.isEmpty()) {
                Messages.showWarningDialog(
                    project,
                    SecureCoderBundle.message("warning.emptyPrompt"),
                    SecureCoderBundle.message("product.name")
                )
            } else {
                submit.isEnabled = false
                submit.text = SecureCoderBundle.message("toolwindow.streaming")

                eventsPanel.removeAll()
                eventsPanel.revalidate()
                eventsPanel.repaint()
                val runner = project.service<EngineRunnerService>()
                runner.runEngine(
                    text,
                    onEvent = { title, desc, icon ->
                        withContext(Dispatchers.EDT) { addEventCard(title, desc, when (icon) {
                            EventIcon.Info -> AllIcons.General.Information
                            EventIcon.Warning -> AllIcons.General.Warning
                        })}
                    },
                    onComplete = {
                        withContext(Dispatchers.EDT) {
                            submit.isEnabled = true
                            submit.text = SecureCoderBundle.message("toolwindow.submit")
                        }
                    }
                )
            }
        }
    }

    private fun addEventCard(title: String, description: String, icon: Icon) {
        val card = JPanel().apply {
            layout = BoxLayout(this, BoxLayout.Y_AXIS)
            border = Borders.empty(8)
        }

        val titlePanel = JPanel().apply {
            layout = BoxLayout(this, BoxLayout.X_AXIS)
            border = Borders.emptyBottom(4)
            alignmentX = Component.LEFT_ALIGNMENT
        }
        val titleLabel = JLabel(title, icon, JLabel.LEADING).apply {
            font = JBFont.label().asBold()
        }
        titlePanel.add(titleLabel)

        val descArea = JTextArea(description).apply {
            isEditable = false
            lineWrap = true
            wrapStyleWord = true
            border = Borders.empty()
            background = card.background
            alignmentX = Component.LEFT_ALIGNMENT
        }

        card.add(titlePanel)
        card.add(descArea)
        card.border = Borders.customLine(separatorForeground(), 1)
        card.maximumSize = Dimension(Int.MAX_VALUE, card.preferredSize.height)

        eventsPanel.add(card)
        eventsPanel.add(Box.createRigidArea(Dimension(0, JBUI.scale(8))))
        eventsPanel.revalidate()
        eventsPanel.repaint()

        SwingUtilities.invokeLater {
            val vBar = eventsScrollPane.verticalScrollBar
            vBar.value = vBar.maximum
        }
    }
}
