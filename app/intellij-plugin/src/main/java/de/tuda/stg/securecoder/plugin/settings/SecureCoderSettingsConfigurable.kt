package de.tuda.stg.securecoder.plugin.settings

import com.intellij.openapi.components.*
import com.intellij.openapi.options.BoundConfigurable
import com.intellij.openapi.ui.ComboBox
import com.intellij.ui.EnumComboBoxModel
import com.intellij.ui.dsl.builder.*
import com.intellij.ui.layout.selectedValueMatches
import de.tuda.stg.securecoder.plugin.settings.SecureCoderSettingsState.LlmProvider

class SecureCoderSettingsConfigurable : BoundConfigurable("SecureCoder") {
    private val settings = service<SecureCoderSettingsState>()

    override fun createPanel() = panel {
        group("Connection") {
            row("Enricher URL:") {
                textField()
                    .bindText(settings.state::enricherUrl)
                    .columns(COLUMNS_MEDIUM)
            }
        }

        group("LLM Provider") {
            val providerBox = ComboBox(EnumComboBoxModel(LlmProvider::class.java))
            row("Provider:") {
                val providerBinding: MutableProperty<LlmProvider?> = MutableProperty(
                    { settings.state.llmProvider },
                    { settings.state.llmProvider = it ?: LlmProvider.OLLAMA }
                )
                cell(providerBox).bindItem(providerBinding)
            }
            rowsRange {
                row("Ollama Model:") {
                    textField()
                        .bindText(settings.state::ollamaModel)
                        .columns(COLUMNS_MEDIUM)
                }
            }.visibleIf(providerBox.selectedValueMatches { it == LlmProvider.OLLAMA })
            rowsRange {
                row("OpenRouter API Key:") {
                    passwordField()
                        .bindText(settings.state::openrouterApiKey)
                        .columns(COLUMNS_MEDIUM)
                }
                row("OpenRouter Model:") {
                    textField()
                        .bindText(settings.state::openrouterModel)
                        .columns(COLUMNS_MEDIUM)
                }
            }.visibleIf(providerBox.selectedValueMatches { it == LlmProvider.OPENROUTER })
        }
    }
}
