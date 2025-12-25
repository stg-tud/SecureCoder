package de.tuda.stg.securecoder.plugin.toolwindow

import com.intellij.openapi.options.ShowSettingsUtil
import com.intellij.openapi.project.Project
import com.intellij.util.ui.JBFont
import com.intellij.util.ui.JBUI
import de.tuda.stg.securecoder.plugin.SecureCoderBundle
import de.tuda.stg.securecoder.plugin.settings.SecureCoderSettingsConfigurable
import java.awt.BorderLayout
import java.awt.Component
import java.awt.Dimension
import javax.swing.Box
import javax.swing.BoxLayout
import javax.swing.JButton
import javax.swing.JLabel
import javax.swing.JPanel

object NotConfiguredPanel {
    fun build(project: Project): JPanel = JPanel(BorderLayout()).apply {
        border = JBUI.Borders.empty(12)
        val panel = JPanel().apply {
            layout = BoxLayout(this, BoxLayout.Y_AXIS)
            alignmentX = Component.LEFT_ALIGNMENT
        }
        val title = JLabel(SecureCoderBundle.message("toolwindow.notConfigured.title")).apply {
            font = JBFont.h2()
            border = JBUI.Borders.emptyBottom(6)
        }
        val desc = JLabel(SecureCoderBundle.message("toolwindow.notConfigured.desc"))
        val openSettings = JButton(SecureCoderBundle.message("toolwindow.notConfigured.openSettings")).apply {
            alignmentX = Component.LEFT_ALIGNMENT
            addActionListener {
                ShowSettingsUtil.getInstance()
                    .showSettingsDialog(project, SecureCoderSettingsConfigurable::class.java)
            }
        }
        panel.add(title)
        panel.add(desc)
        panel.add(Box.createRigidArea(Dimension(0, JBUI.scale(8))))
        panel.add(openSettings)
        add(panel, BorderLayout.NORTH)
    }
}
