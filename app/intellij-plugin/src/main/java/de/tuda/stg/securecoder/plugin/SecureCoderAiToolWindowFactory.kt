package de.tuda.stg.securecoder.plugin

import com.intellij.openapi.project.DumbAware
import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import com.intellij.openapi.wm.ToolWindow
import com.intellij.openapi.wm.ToolWindowFactory
import com.intellij.ui.components.JBScrollPane
import com.intellij.ui.components.JBTextArea
import com.intellij.ui.content.ContentFactory
import com.intellij.util.ui.JBUI
import java.awt.BorderLayout
import java.awt.Dimension
import javax.swing.Box
import javax.swing.BoxLayout
import javax.swing.JButton
import javax.swing.JPanel
import javax.swing.ScrollPaneConstants

class SecureCoderAiToolWindowFactory : ToolWindowFactory, DumbAware {
    override fun createToolWindowContent(project: Project, toolWindow: ToolWindow) {
        val root = JPanel(BorderLayout())
        val inputArea = createInputArea()
        val scroll = wrapTextInScrollPane(inputArea)
        val preferredHeight = scroll.preferredSize.height
        scroll.maximumSize = Dimension(Int.MAX_VALUE, preferredHeight)
        val submit = createSubmitButton(preferredHeight)
        val row = buildInputRow(scroll, submit)
        root.add(row, BorderLayout.NORTH)
        setupSubmitAction(project, inputArea, submit)
        addToToolWindow(toolWindow, root)
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
                Messages.showInfoMessage(project, "Submitted: $text", "SecureCoder AI")
            }
        }
    }

    private fun addToToolWindow(toolWindow: ToolWindow, root: JPanel) {
        val contentFactory = ContentFactory.getInstance()
        val content = contentFactory.createContent(root, null, false)
        toolWindow.contentManager.addContent(content)
    }
}
