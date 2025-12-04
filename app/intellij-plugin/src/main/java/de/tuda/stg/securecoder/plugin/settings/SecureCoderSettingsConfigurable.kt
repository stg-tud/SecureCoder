package de.tuda.stg.securecoder.plugin.settings

import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.application.ModalityState
import com.intellij.openapi.components.*
import com.intellij.openapi.fileChooser.FileChooserDescriptorFactory
import com.intellij.openapi.options.BoundConfigurable
import com.intellij.openapi.progress.ProgressIndicator
import com.intellij.openapi.progress.ProgressManager
import com.intellij.openapi.progress.Task
import com.intellij.openapi.ui.ComboBox
import com.intellij.openapi.ui.MessageType
import com.intellij.openapi.ui.popup.Balloon
import com.intellij.openapi.ui.popup.JBPopupFactory
import com.intellij.ui.AnimatedIcon
import com.intellij.ui.EnumComboBoxModel
import com.intellij.ui.awt.RelativePoint
import com.intellij.ui.components.JBCheckBox
import com.intellij.ui.dsl.builder.*
import com.intellij.ui.layout.selected
import com.intellij.ui.layout.selectedValueMatches
import de.tuda.stg.securecoder.guardian.CodeQLRunner
import de.tuda.stg.securecoder.plugin.SecureCoderBundle
import de.tuda.stg.securecoder.plugin.settings.SecureCoderSettingsState.LlmProvider
import java.io.IOException
import java.nio.file.Path
import javax.swing.JButton
import javax.swing.JComponent


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
            val enricher = JBCheckBox(SecureCoderBundle.message("settings.enricher.enabled"))
            row {
                cell(enricher).bindSelected(settings.state::enablePromptEnriching)
            }
            row(SecureCoderBundle.message("settings.enricher.url")) {
                textField()
                    .bindText(settings.state::enricherUrl)
                    .columns(COLUMNS_MEDIUM)
            }.enabledIf(enricher.selected).bottomGap(BottomGap.SMALL)
            row {
                checkBox("Dummy guardian").bindSelected(settings.state::enableDummyGuardian)
            }
            val codeql = JBCheckBox("Enable CodeQL guardian")
            row {
                cell(codeql).bindSelected(settings.state::enableCodeQLGuardian)
            }
            row("CodeQL binary") {
                val codeqlPathCell = textFieldWithBrowseButton(
                    browseDialogTitle = "Select CodeQL binary",
                    fileChooserDescriptor = FileChooserDescriptorFactory.createSingleFileDescriptor()
                )
                    .bindText(settings.state::codeqlBinary)
                    .columns(COLUMNS_MEDIUM)
                val codeqlPathField = codeqlPathCell.component
                button("Test") { event ->
                    val loadingBalloon = JBPopupFactory.getInstance()
                        .createHtmlTextBalloonBuilder("Checking...", AnimatedIcon.Default.INSTANCE, null, null, null)
                        .createBalloon()

                    loadingBalloon.show(
                        RelativePoint.getSouthOf(event.source as JComponent),
                        Balloon.Position.below
                    )
                    ApplicationManager.getApplication().executeOnPooledThread {
                        val bin = settings.state.codeqlBinary.ifBlank { "codeql" }
                        val (message, type) = try {
                            "Found CodeQL ${CodeQLRunner(bin).getToolVersion()}" to MessageType.INFO
                        } catch (e: Exception) {
                            "Error: " + (e.message ?: e.toString()) to MessageType.ERROR
                        }
                        ApplicationManager.getApplication().invokeLater(
                            {
                                loadingBalloon.hide()
                                val balloon = JBPopupFactory.getInstance()
                                    .createHtmlTextBalloonBuilder(message, type, null)
                                    .createBalloon()
                                balloon.show(
                                    RelativePoint.getSouthOf(event.source as JComponent),
                                    Balloon.Position.below
                                )
                            },
                            ModalityState.any()
                        )
                    }
                }
                button("Download") { event ->
                    val button = event.source as JButton
                    button.setEnabled(false)
                    ProgressManager.getInstance().run(object : Task.Backgroundable(null, "Installing CodeQL", true) {
                        private var resultPath: Path? = null
                        private var exception: Exception? = null

                        override fun run(indicator: ProgressIndicator) {
                            val installer = CodeQLInstaller()
                            try {
                                resultPath = installer.getOrInstallCodeQL(indicator)
                            } catch (e: IOException) {
                                exception = e
                            }
                        }

                        override fun onSuccess() {
                            button.setEnabled(true)
                            if (exception != null) {
                                JBPopupFactory.getInstance()
                                    .createHtmlTextBalloonBuilder("Failed to install CodeQL: ${exception!!.message}", MessageType.ERROR, null)
                                    .createBalloon()
                                    .show(RelativePoint.getSouthOf(button), Balloon.Position.below)
                            } else if (resultPath != null) {
                                val path = resultPath.toString()
                                // Update settings and the visible input field so the user sees it immediately
                                settings.state.codeqlBinary = path
                                codeqlPathField.text = path
                                JBPopupFactory.getInstance()
                                    .createHtmlTextBalloonBuilder("Downloaded!", MessageType.INFO, null)
                                    .createBalloon()
                                    .show(RelativePoint.getSouthOf(button), Balloon.Position.below)
                            }
                        }

                        override fun onCancel() {
                            button.setEnabled(true)
                        }
                    })
                }
            }.enabledIf(codeql.selected)
        }
    }
}
