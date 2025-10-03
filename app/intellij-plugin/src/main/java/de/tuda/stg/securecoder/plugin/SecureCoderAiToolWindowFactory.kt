package de.tuda.stg.securecoder.plugin

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
import java.awt.BorderLayout
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
            border = JBUI.Borders.empty(8)
        }
        eventsScrollPane = JBScrollPane(eventsPanel).apply {
            verticalScrollBarPolicy = ScrollPaneConstants.VERTICAL_SCROLLBAR_AS_NEEDED
            horizontalScrollBarPolicy = ScrollPaneConstants.HORIZONTAL_SCROLLBAR_NEVER
            border = JBUI.Borders.empty()
        }
        add(eventsScrollPane, BorderLayout.CENTER)
        setupSubmitAction(project, inputArea, submit)
    }

    private fun buildInputRow(scroll: JBScrollPane, submit: JButton): JPanel {
        val row = JPanel().apply {
            layout = BoxLayout(this, BoxLayout.X_AXIS)
            border = JBUI.Borders.empty(8)
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
    }

    private fun wrapTextInScrollPane(inputArea: JBTextArea): JBScrollPane = JBScrollPane(inputArea).apply {
        verticalScrollBarPolicy = ScrollPaneConstants.VERTICAL_SCROLLBAR_AS_NEEDED
        horizontalScrollBarPolicy = ScrollPaneConstants.HORIZONTAL_SCROLLBAR_NEVER
    }

    private fun createSubmitButton(height: Int): JButton = JButton("Submit").apply {
        maximumSize = Dimension(preferredSize.width, height)
    }

    private fun setupSubmitAction(project: Project, inputArea: JBTextArea, submit: JButton) {
        submit.addActionListener {
            val text = inputArea.text.trim()
            if (text.isEmpty()) {
                Messages.showWarningDialog(project, "Please enter a prompt before submitting.", "SecureCoder AI")
            } else {
                submit.isEnabled = false
                submit.text = "Streaming..."

                eventsPanel.removeAll()
                eventsPanel.revalidate()
                eventsPanel.repaint()
                DummyAgentStreamer().startDummyStream(
                    text,
                    onEvent = { title, desc, icon ->
                        SwingUtilities.invokeLater { addEventCard(title, desc, icon) }
                    },
                    onComplete = {
                        SwingUtilities.invokeLater {
                            submit.isEnabled = true
                            submit.text = "Submit"
                        }
                    }
                )
            }
        }
    }

    private fun addEventCard(title: String, description: String, icon: Icon) {
        val card = JPanel().apply {
            layout = BoxLayout(this, BoxLayout.Y_AXIS)
            border = JBUI.Borders.empty(8)
        }

        val titlePanel = JPanel().apply {
            layout = BoxLayout(this, BoxLayout.X_AXIS)
            border = JBUI.Borders.emptyBottom(4)
        }
        val titleLabel = JLabel(title, icon, JLabel.LEADING).apply {
            font = JBFont.label().asBold()
        }
        titlePanel.add(titleLabel)

        val descArea = JTextArea(description).apply {
            isEditable = false
            lineWrap = true
            wrapStyleWord = true
            border = JBUI.Borders.empty()
            background = card.background
        }

        card.add(titlePanel)
        card.add(descArea)
        card.border = JBUI.Borders.customLine(JBUI.CurrentTheme.CustomFrameDecorations.separatorForeground(), 1, 1, 1, 1)

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
