package de.tuda.stg.securecoder.plugin.toolwindow

import com.intellij.icons.AllIcons
import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.application.EDT
import com.intellij.openapi.components.service
import com.intellij.openapi.options.ShowSettingsUtil
import com.intellij.openapi.project.DumbAware
import com.intellij.openapi.project.Project
import com.intellij.openapi.wm.ToolWindow
import com.intellij.openapi.wm.ToolWindowFactory
import com.intellij.ui.components.JBScrollPane
import com.intellij.ui.content.ContentFactory
import com.intellij.util.ui.JBUI
import de.tuda.stg.securecoder.plugin.SecureCoderBundle
import de.tuda.stg.securecoder.plugin.engine.EngineRunnerService
import de.tuda.stg.securecoder.plugin.engine.event.UiStreamEvent
import de.tuda.stg.securecoder.plugin.settings.SecureCoderSettingsConfigurable
import de.tuda.stg.securecoder.plugin.settings.SecureCoderSettingsState
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.awt.BorderLayout
import java.awt.Dimension
import javax.swing.Box
import javax.swing.BoxLayout
import javax.swing.JPanel
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
        connection.subscribe(
            SecureCoderSettingsState.topic,
            SecureCoderSettingsState.SecureCoderSettingsListener {
                SwingUtilities.invokeLater {
                    content.component = createRoot(project)
                }
            })
    }

    private fun createRoot(project: Project): JPanel {
        if (!service<SecureCoderSettingsState>().state.hasLLMProviderConfigured()) {
            return NotConfiguredPanel.build(project)
        }

        val root = JPanel(BorderLayout())

        val promptPanel = PromptInputPanel(project) { promptText, onStreaming, onFinished ->
            onStreaming()

            val runner = project.service<EngineRunnerService>()
            eventsPanel.removeAll()
            eventsPanel.revalidate()
            eventsPanel.repaint()

            runner.runEngine(
                promptText,
                onUiEvent = { event -> withContext(Dispatchers.EDT) {
                    addEventCard(event, project)
                }},
                onComplete = { withContext(Dispatchers.EDT) { onFinished() } }
            )
        }
        root.add(promptPanel.component, BorderLayout.NORTH)

        eventsPanel = JPanel().apply {
            layout = BoxLayout(this, BoxLayout.Y_AXIS)
            border = JBUI.Borders.empty(8)
        }
        eventsScrollPane = JBScrollPane(eventsPanel).apply {
            verticalScrollBarPolicy = ScrollPaneConstants.VERTICAL_SCROLLBAR_AS_NEEDED
            horizontalScrollBarPolicy = ScrollPaneConstants.HORIZONTAL_SCROLLBAR_NEVER
            border = JBUI.Borders.empty()
        }
        root.add(eventsScrollPane, BorderLayout.CENTER)

        return root
    }

    private fun addEventCard(
        event: UiStreamEvent,
        project: Project
    ) {
        val card = EventsPanel.addEventCard(event, project)
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