package de.tuda.stg.securecoder.plugin.settings

import com.intellij.openapi.components.*
import com.intellij.openapi.options.BoundConfigurable
import com.intellij.openapi.ui.ComboBox
import com.intellij.ui.EnumComboBoxModel
import com.intellij.ui.dsl.builder.*
import com.intellij.ui.layout.selectedValueMatches
import de.tuda.stg.securecoder.plugin.settings.SecureCoderSettingsState.LlmProvider
import de.tuda.stg.securecoder.plugin.SecureCoderBundle

class SecureCoderSettingsConfigurable : BoundConfigurable(SecureCoderBundle.message("settings.configurable.display.name")) {
    private val settings = service<SecureCoderSettingsState>()

    override fun createPanel() = panel {
        group(SecureCoderBundle.message("settings.group.llmProvider")) {
            val providerBox = ComboBox(EnumComboBoxModel(LlmProvider::class.java))
            row(SecureCoderBundle.message("settings.provider")) {
                val providerBinding: MutableProperty<LlmProvider?> = MutableProperty(
                    { settings.state.llmProvider },
                    { settings.state.llmProvider = it ?: LlmProvider.OLLAMA }
                )
                cell(providerBox).bindItem(providerBinding)
            }
            rowsRange {
                row(SecureCoderBundle.message("settings.ollama.model")) {
                    textField()
                        .bindText(settings.state::ollamaModel)
                        .columns(COLUMNS_MEDIUM)
                }
            }.visibleIf(providerBox.selectedValueMatches { it == LlmProvider.OLLAMA })
            rowsRange {
                row(SecureCoderBundle.message("settings.openrouter.api.key")) {
                    passwordField()
                        .bindText(settings.state::openrouterApiKey)
                        .columns(COLUMNS_MEDIUM)
                }
                row(SecureCoderBundle.message("settings.openrouter.model")) {
                    textField()
                        .bindText(settings.state::openrouterModel)
                        .columns(COLUMNS_MEDIUM)
                }
            }.visibleIf(providerBox.selectedValueMatches { it == LlmProvider.OPENROUTER })
        }
        group(SecureCoderBundle.message("settings.group.security")) {
            row {
                checkBox(SecureCoderBundle.message("settings.enricher.enabled"))
                    .bindSelected(settings.state::enablePromptEnriching)
            }
            row(SecureCoderBundle.message("settings.enricher.url")) {
                textField()
                    .bindText(settings.state::enricherUrl)
                    .columns(COLUMNS_MEDIUM)
            }
        }
    }
}
