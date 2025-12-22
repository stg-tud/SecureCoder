package de.tuda.stg.securecoder.plugin

import com.intellij.icons.AllIcons
import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.application.EDT
import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.components.service
import com.intellij.openapi.options.ShowSettingsUtil
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
import de.tuda.stg.securecoder.plugin.edit.buildEditFilesPanel
import de.tuda.stg.securecoder.plugin.engine.EngineRunnerService
import de.tuda.stg.securecoder.plugin.engine.IntelliJProjectFileSystem
import de.tuda.stg.securecoder.plugin.engine.event.UiStreamEvent
import de.tuda.stg.securecoder.plugin.settings.SecureCoderSettingsConfigurable
import de.tuda.stg.securecoder.plugin.settings.SecureCoderSettingsState
import de.tuda.stg.securecoder.plugin.settings.SecureCoderSettingsState.SecureCoderSettingsListener
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.awt.BorderLayout
import java.awt.Component
import java.awt.Dimension
import javax.swing.BorderFactory
import javax.swing.Box
import javax.swing.BoxLayout
import javax.swing.JButton
import javax.swing.JCheckBox
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
        toolWindow.setIcon(AllIcons.Ultimate.Lock) // AllIcons.Ide.Readonly
        toolWindow.setTitleActions(listOf(
            object : AnAction(
                SecureCoderBundle.message("toolwindow.settings"),
                null,
                AllIcons.General.Settings
            ), DumbAware {
                override fun actionPerformed(e: AnActionEvent) {
                    ShowSettingsUtil.getInstance()
                        .showSettingsDialog(project, SecureCoderSettingsConfigurable::class.java)
                }
            }
        ))

        val connection = ApplicationManager.getApplication().messageBus.connect(toolWindow.disposable)
        connection.subscribe(SecureCoderSettingsState.topic, SecureCoderSettingsListener {
            SwingUtilities.invokeLater {
                content.component = createRoot(project)
            }
        })
    }

    private fun createRoot(project: Project): JPanel {
        if (!service<SecureCoderSettingsState>().state.hasLLMProviderConfigured()) {
            return JPanel(BorderLayout()).apply {
                border = Borders.empty(12)
                val panel = JPanel().apply {
                    layout = BoxLayout(this, BoxLayout.Y_AXIS)
                    alignmentX = Component.LEFT_ALIGNMENT
                }
                val title = JLabel(SecureCoderBundle.message("toolwindow.notConfigured.title")).apply {
                    font = JBFont.h2()
                    border = Borders.emptyBottom(6)
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

        return JPanel(BorderLayout()).apply {
            val inputArea = createInputArea()
            val scroll = wrapTextInScrollPane(inputArea)
            val preferredHeight = scroll.preferredSize.height
            scroll.maximumSize = Dimension(Int.MAX_VALUE, preferredHeight)
            val submit = createSubmitButton(preferredHeight)
            val checkBox = JCheckBox(SecureCoderBundle.message("toolwindow.useWholeProject"), true).apply {
                alignmentX = Component.LEFT_ALIGNMENT
                border = Borders.emptyLeft(4)
                toolTipText = SecureCoderBundle.message("toolwindow.useWholeProject.tooltip")
            }
            val header = JPanel().apply {
                layout = BoxLayout(this, BoxLayout.Y_AXIS)
                border = Borders.empty(8)
                alignmentX = Component.LEFT_ALIGNMENT
            }
            val textRow = buildTextRow(scroll)
            val controlsRow = buildControlsRow(checkBox, submit)

            header.add(textRow)
            header.add(Box.createRigidArea(Dimension(0, JBUI.scale(8))))
            header.add(controlsRow)
            add(header, BorderLayout.NORTH)

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
    }

    private fun buildControlsRow(checkBox: JCheckBox, submit: JButton): JPanel = JPanel().apply {
        layout = BoxLayout(this, BoxLayout.X_AXIS)
        border = Borders.empty()
        checkBox.alignmentY = Component.CENTER_ALIGNMENT
        checkBox.maximumSize = checkBox.preferredSize
        submit.alignmentY = Component.CENTER_ALIGNMENT
        submit.maximumSize = Dimension(submit.preferredSize.width, submit.preferredSize.height)
        add(checkBox)
        add(Box.createHorizontalGlue())
        add(submit)
    }

    private fun createInputArea(): JBTextArea = JBTextArea().apply {
        lineWrap = true
        wrapStyleWord = true
        rows = 5
        columns = 30
        border = Borders.empty(8)
        getEmptyText().setText(SecureCoderBundle.message("edit.placeholder"));
    }

    private fun wrapTextInScrollPane(inputArea: JBTextArea): JBScrollPane = JBScrollPane(inputArea).apply {
        verticalScrollBarPolicy = ScrollPaneConstants.VERTICAL_SCROLLBAR_AS_NEEDED
        horizontalScrollBarPolicy = ScrollPaneConstants.HORIZONTAL_SCROLLBAR_NEVER
    }

    private fun createSubmitButton(height: Int): JButton = JButton(SecureCoderBundle.message("toolwindow.submit")).apply {
        maximumSize = Dimension(preferredSize.width, height)
    }

    private fun buildTextRow(scroll: JBScrollPane): JPanel = JPanel().apply {
        layout = BoxLayout(this, BoxLayout.X_AXIS)
        border = Borders.empty()
        add(scroll.apply {
            alignmentX = Component.LEFT_ALIGNMENT
            maximumSize = Dimension(Int.MAX_VALUE, preferredSize.height)
        })
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
                    onUiEvent = { event ->
                        withContext(Dispatchers.EDT) { addEventCard(event, project) }
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

    private fun addEventCard(event: UiStreamEvent, project: Project) {
        val card = object : JPanel() {
            override fun getMaximumSize() = Dimension(Int.MAX_VALUE, preferredSize.height)
        }.apply {
            layout = BoxLayout(this, BoxLayout.Y_AXIS)
            border = BorderFactory.createCompoundBorder(
                Borders.customLine(separatorForeground(), 1),
                Borders.empty(6)
            )
        }

        val titlePanel = JPanel().apply {
            layout = BoxLayout(this, BoxLayout.X_AXIS)
            border = Borders.emptyBottom(4)
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

        val content = when (event) {
            is UiStreamEvent.Message -> JTextArea(event.description).apply {
                isEditable = false
                lineWrap = true
                wrapStyleWord = true
                border = Borders.empty()
                background = card.background
                alignmentX = Component.LEFT_ALIGNMENT
            }
            is UiStreamEvent.EditFiles -> buildEditFilesPanel(project, event.changes, IntelliJProjectFileSystem(project))
        }

        card.add(titlePanel)
        card.add(content)

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

