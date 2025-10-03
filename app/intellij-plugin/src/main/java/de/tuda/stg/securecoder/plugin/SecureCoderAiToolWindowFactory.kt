package de.tuda.stg.securecoder.plugin

import com.intellij.openapi.project.DumbAware
import com.intellij.openapi.project.Project
import com.intellij.openapi.ui.Messages
import com.intellij.openapi.wm.ToolWindow
import com.intellij.openapi.wm.ToolWindowFactory
import com.intellij.ui.content.ContentFactory
import com.intellij.ui.components.JBTextArea
import com.intellij.util.ui.JBUI
import java.awt.BorderLayout
import java.awt.Dimension
import javax.swing.Box
import javax.swing.BoxLayout
import javax.swing.JButton
import javax.swing.JPanel
import javax.swing.JScrollPane
import javax.swing.ScrollPaneConstants

class SecureCoderAiToolWindowFactory : ToolWindowFactory, DumbAware {
    override fun createToolWindowContent(project: Project, toolWindow: ToolWindow) {
        val root = JPanel(BorderLayout())
        val row = JPanel()
        row.layout = BoxLayout(row, BoxLayout.X_AXIS)
        row.border = JBUI.Borders.empty(8)

        val inputArea = JBTextArea()
        inputArea.lineWrap = true
        inputArea.wrapStyleWord = true
        inputArea.rows = 5
        inputArea.columns = 30

        val scroll = JScrollPane(inputArea)
        scroll.verticalScrollBarPolicy = ScrollPaneConstants.VERTICAL_SCROLLBAR_AS_NEEDED
        scroll.horizontalScrollBarPolicy = ScrollPaneConstants.HORIZONTAL_SCROLLBAR_NEVER

        val preferredHeight = scroll.preferredSize.height
        scroll.maximumSize = Dimension(Int.MAX_VALUE, preferredHeight)

        val submit = JButton("Submit")
        val submitPref = submit.preferredSize
        submit.maximumSize = Dimension(submitPref.width, preferredHeight)

        row.add(scroll)
        row.add(Box.createRigidArea(Dimension(JBUI.scale(8), 0)))
        row.add(submit)

        root.add(row, BorderLayout.NORTH)

        submit.addActionListener {
            val text = inputArea.text.trim()
            if (text.isEmpty()) {
                Messages.showWarningDialog(project, "Please enter a prompt before submitting.", "SecureCoder AI")
            } else {
                Messages.showInfoMessage(project, "Submitted: $text", "SecureCoder AI")
            }
        }

        val contentFactory = ContentFactory.getInstance()
        val content = contentFactory.createContent(root, null, false)
        toolWindow.contentManager.addContent(content)
    }
}