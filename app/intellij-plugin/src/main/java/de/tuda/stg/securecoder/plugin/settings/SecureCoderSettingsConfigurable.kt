package de.tuda.stg.securecoder.plugin.settings

import com.intellij.openapi.components.service
import com.intellij.openapi.options.Configurable
import com.intellij.openapi.ui.ComboBox
import com.intellij.ui.EnumComboBoxModel
import com.intellij.ui.components.JBTextField
import com.intellij.util.ui.FormBuilder
import de.tuda.stg.securecoder.plugin.settings.SecureCoderSettingsState.LlmProvider
import java.awt.event.ItemEvent
import javax.swing.JComponent
import javax.swing.JLabel
import javax.swing.JPanel

class SecureCoderSettingsConfigurable : Configurable {
    private val settings = service<SecureCoderSettingsState>()

    private var mainPanel: JPanel? = null

    private val enricherUrlField = JBTextField()
    private val llmProviderCombo = ComboBox(EnumComboBoxModel(LlmProvider::class.java))

    private val ollamaModelField = JBTextField()

    private val openrouterApiKeyField = JBTextField()
    private val openrouterModelField = JBTextField()

    private lateinit var ollamaPanel: JPanel
    private lateinit var openrouterPanel: JPanel

    override fun getDisplayName(): String = "SecureCoder"

    override fun createComponent(): JComponent {
        ollamaPanel = FormBuilder.createFormBuilder()
            .addLabeledComponent(JLabel("Ollama Model:"), ollamaModelField, 1, false)
            .panel

        openrouterPanel = FormBuilder.createFormBuilder()
            .addLabeledComponent(JLabel("OpenRouter API Key:"), openrouterApiKeyField, 1, false)
            .addLabeledComponent(JLabel("OpenRouter Model:"), openrouterModelField, 1, false)
            .panel

        val form = FormBuilder.createFormBuilder()
            .addLabeledComponent(JLabel("Enricher URL:"), enricherUrlField, 1, false)
            .addLabeledComponent(JLabel("LLM Provider:"), llmProviderCombo, 1, false)
            .addSeparator()
            .addComponent(ollamaPanel, 1)
            .addComponent(openrouterPanel, 1)
            .panel

        llmProviderCombo.addItemListener { e ->
            if (e.stateChange == ItemEvent.SELECTED) {
                updateProviderPanelsVisibility()
            }
        }

        mainPanel = form
        reset()
        updateProviderPanelsVisibility()
        return form
    }

    private fun updateProviderPanelsVisibility() {
        val provider = (llmProviderCombo.selectedItem as? LlmProvider) ?: LlmProvider.OLLAMA
        val showOllama = provider == LlmProvider.OLLAMA
        ollamaPanel.isVisible = showOllama
        openrouterPanel.isVisible = !showOllama
        mainPanel?.revalidate()
        mainPanel?.repaint()
    }

    override fun isModified(): Boolean {
        val s = settings.state
        return enricherUrlField.text != s.enricherUrl ||
                llmProviderCombo.selectedItem != s.llmProvider ||
                ollamaModelField.text != s.ollamaModel ||
                openrouterApiKeyField.text != s.openrouterApiKey ||
                openrouterModelField.text != s.openrouterModel
    }

    override fun apply() {
        val s = settings.state
        s.enricherUrl = enricherUrlField.text.trim()
        s.llmProvider = (llmProviderCombo.selectedItem as? LlmProvider ?: LlmProvider.OLLAMA)
        s.ollamaModel = ollamaModelField.text.trim()
        s.openrouterApiKey = openrouterApiKeyField.text.trim()
        s.openrouterModel = openrouterModelField.text.trim()
    }

    override fun reset() {
        val s = settings.state
        enricherUrlField.text = s.enricherUrl
        llmProviderCombo.selectedItem = s.llmProvider
        ollamaModelField.text = s.ollamaModel
        openrouterApiKeyField.text = s.openrouterApiKey
        openrouterModelField.text = s.openrouterModel
        updateProviderPanelsVisibility()
    }

    override fun disposeUIResources() {
        mainPanel = null
    }
}
