package de.tuda.stg.securecoder.plugin.toolwindow

import com.intellij.openapi.project.Project
import com.intellij.ui.components.JBScrollPane
import com.intellij.ui.components.JBTextArea
import com.intellij.util.ui.JBUI
import de.tuda.stg.securecoder.plugin.SecureCoderBundle
import java.awt.Component
import java.awt.Dimension
import javax.swing.Box
import javax.swing.BoxLayout
import javax.swing.JButton
import javax.swing.JCheckBox
import javax.swing.JPanel
import javax.swing.ScrollPaneConstants
import com.intellij.openapi.ui.Messages

class PromptInputPanel(
    private val project: Project,
    private val onSubmit: (promptText: String, projectAsContext: Boolean, onFinished: () -> Unit) -> Unit
) {
    val component: JPanel

    private val inputArea: JBTextArea = JBTextArea().apply {
        lineWrap = true
        wrapStyleWord = true
        rows = 5
        columns = 30
        border = JBUI.Borders.empty(8)
        getEmptyText().setText(SecureCoderBundle.message("edit.placeholder"))
    }

    private fun wrapTextInScrollPane(): JBScrollPane = JBScrollPane(inputArea).apply {
        verticalScrollBarPolicy = ScrollPaneConstants.VERTICAL_SCROLLBAR_AS_NEEDED
        horizontalScrollBarPolicy = ScrollPaneConstants.HORIZONTAL_SCROLLBAR_NEVER
    }

    init {
        val scroll = wrapTextInScrollPane()
        val preferredHeight = scroll.preferredSize.height
        scroll.maximumSize = Dimension(Int.MAX_VALUE, preferredHeight)

        val submit = JButton(SecureCoderBundle.message("toolwindow.submit")).apply {
            maximumSize = Dimension(preferredSize.width, preferredHeight)
        }

        val checkBox = JCheckBox(SecureCoderBundle.message("toolwindow.useWholeProject"), true).apply {
            alignmentX = Component.LEFT_ALIGNMENT
            border = JBUI.Borders.emptyLeft(4)
            toolTipText = SecureCoderBundle.message("toolwindow.useWholeProject.tooltip")
        }

        val textRow = JPanel().apply {
            layout = BoxLayout(this, BoxLayout.X_AXIS)
            border = JBUI.Borders.empty()
            add(scroll.apply {
                alignmentX = Component.LEFT_ALIGNMENT
                maximumSize = Dimension(Int.MAX_VALUE, preferredHeight)
            })
        }

        val controlsRow = JPanel().apply {
            layout = BoxLayout(this, BoxLayout.X_AXIS)
            border = JBUI.Borders.empty()
            checkBox.alignmentY = Component.CENTER_ALIGNMENT
            checkBox.maximumSize = checkBox.preferredSize
            submit.alignmentY = Component.CENTER_ALIGNMENT
            submit.maximumSize = Dimension(submit.preferredSize.width, submit.preferredSize.height)
            add(checkBox)
            add(Box.createHorizontalGlue())
            add(submit)
        }

        component = JPanel().apply {
            layout = BoxLayout(this, BoxLayout.Y_AXIS)
            border = JBUI.Borders.empty(8)
            alignmentX = Component.LEFT_ALIGNMENT
            add(textRow)
            add(Box.createRigidArea(Dimension(0, JBUI.scale(8))))
            add(controlsRow)
        }

        submit.addActionListener {
            val text = inputArea.text.trim()
            if (text.isEmpty()) {
                Messages.showWarningDialog(
                    project,
                    SecureCoderBundle.message("warning.emptyPrompt"),
                    SecureCoderBundle.message("product.name")
                )
                return@addActionListener
            }

            submit.isEnabled = false
            submit.text = SecureCoderBundle.message("toolwindow.streaming")

            val onFinished = {
                submit.isEnabled = true
                submit.text = SecureCoderBundle.message("toolwindow.submit")
            }

            onSubmit(text, checkBox.isSelected, onFinished)
        }
    }
}
