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
import de.tuda.stg.securecoder.plugin.settings.SecureCoderSettingsState.LlmConfig
import de.tuda.stg.securecoder.plugin.settings.SecureCoderSettingsState.LlmProvider
import java.io.IOException
import java.nio.file.Path
import javax.swing.JButton
import javax.swing.JComponent


class SecureCoderSettingsConfigurable : BoundConfigurable(SecureCoderBundle.message("settings.configurable.display.name")) {
    private val settings = service<SecureCoderSettingsState>()

    override fun createPanel() = panel {
        createLlmConfigSection(
            SecureCoderBundle.message("settings.group.llmProvider"),
            settings.state.mainLlm
        ).bottomGap(BottomGap.MEDIUM)

        group(SecureCoderBundle.message("settings.group.security")) {
            group(SecureCoderBundle.message("settings.group.enricher")) {
                val enricher = JBCheckBox(SecureCoderBundle.message("settings.enricher.enabled"))
                row {
                    cell(enricher).bindSelected(settings.state::enablePromptEnriching)
                }
                row(SecureCoderBundle.message("settings.enricher.url")) {
                    textField()
                        .bindText(settings.state::enricherUrl)
                        .columns(COLUMNS_MEDIUM)
                }.enabledIf(enricher.selected)
            }.bottomGap(BottomGap.MEDIUM)
            group(SecureCoderBundle.message("settings.group.guardians")) {
                group(SecureCoderBundle.message("settings.group.guardian.dummy")) {
                    row {
                        checkBox(SecureCoderBundle.message("settings.guardian.dummy"))
                            .bindSelected(settings.state::enableDummyGuardian)
                    }
                }.bottomGap(BottomGap.MEDIUM)
                group(SecureCoderBundle.message("settings.group.guardian.codeql")) {
                    val codeql = JBCheckBox(SecureCoderBundle.message("settings.guardian.codeql.enable"))
                    row {
                        cell(codeql).bindSelected(settings.state::enableCodeQLGuardian)
                    }
                    row(SecureCoderBundle.message("settings.codeql.binary")) {
                        val codeqlPathCell = textFieldWithBrowseButton(
                            FileChooserDescriptorFactory.singleFile()
                        )
                            .bindText(settings.state::codeqlBinary)
                            .columns(COLUMNS_MEDIUM)

                        val codeqlPathField = codeqlPathCell.component

                        button(SecureCoderBundle.message("settings.codeql.test")) { event ->
                            val loadingBalloon = JBPopupFactory.getInstance()
                                .createHtmlTextBalloonBuilder(
                                    SecureCoderBundle.message("settings.codeql.checking"),
                                    AnimatedIcon.Default.INSTANCE,
                                    null, null, null
                                )
                                .createBalloon()

                            loadingBalloon.show(
                                RelativePoint.getSouthOf(event.source as JComponent),
                                Balloon.Position.below
                            )

                            ApplicationManager.getApplication().executeOnPooledThread {
                                val bin = settings.state.codeqlBinary.ifBlank { "codeql" }
                                val (message, type) = try {
                                    SecureCoderBundle.message(
                                        "settings.codeql.found",
                                        CodeQLRunner(bin).getToolVersion()
                                    ) to MessageType.INFO
                                } catch (e: Exception) {
                                    SecureCoderBundle.message(
                                        "settings.codeql.error",
                                        (e.message ?: e.toString())
                                    ) to MessageType.ERROR
                                }

                                ApplicationManager.getApplication().invokeLater(
                                    {
                                        loadingBalloon.hide()
                                        JBPopupFactory.getInstance()
                                            .createHtmlTextBalloonBuilder(message, type, null)
                                            .createBalloon()
                                            .show(
                                                RelativePoint.getSouthOf(event.source as JComponent),
                                                Balloon.Position.below
                                            )
                                    },
                                    ModalityState.any()
                                )
                            }
                        }

                        button(SecureCoderBundle.message("settings.codeql.download")) { event ->
                            val button = event.source as JButton
                            button.isEnabled = false

                            ProgressManager.getInstance().run(object : Task.Backgroundable(
                                null,
                                SecureCoderBundle.message("settings.codeql.installing"),
                                true
                            ) {
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
                                    button.isEnabled = true
                                    when {
                                        exception != null -> {
                                            JBPopupFactory.getInstance()
                                                .createHtmlTextBalloonBuilder(
                                                    SecureCoderBundle.message(
                                                        "settings.codeql.install.failed",
                                                        exception!!.message ?: exception!!.toString()
                                                    ),
                                                    MessageType.ERROR,
                                                    null
                                                )
                                                .createBalloon()
                                                .show(RelativePoint.getSouthOf(button), Balloon.Position.below)
                                        }
                                        resultPath != null -> {
                                            val path = resultPath.toString()
                                            settings.state.codeqlBinary = path
                                            codeqlPathField.text = path
                                            JBPopupFactory.getInstance()
                                                .createHtmlTextBalloonBuilder(
                                                    SecureCoderBundle.message("settings.codeql.downloaded"),
                                                    MessageType.INFO,
                                                    null
                                                )
                                                .createBalloon()
                                                .show(RelativePoint.getSouthOf(button), Balloon.Position.below)
                                        }
                                    }
                                }

                                override fun onCancel() {
                                    button.isEnabled = true
                                }
                            })
                        }
                    }.enabledIf(codeql.selected)
                }.bottomGap(BottomGap.MEDIUM)

                group(SecureCoderBundle.message("settings.group.guardian.llm")) {
                    val llmGuardian = JBCheckBox(SecureCoderBundle.message("settings.guardian.llm.enable"))
                    row {
                        cell(llmGuardian).bindSelected(settings.state::enableLlmGuardian)
                    }

                    createLlmConfigSection(
                        SecureCoderBundle.message("settings.group.llmGuardian"),
                        settings.state.guardianLlm
                    ).enabledIf(llmGuardian.selected)
                }
            }
        }
    }


    override fun apply() {
        super.apply()
        ApplicationManager.getApplication()
            .messageBus
            .syncPublisher(SecureCoderSettingsState.topic)
            .settingsChanged(settings.state)
    }

    private fun Panel.createLlmConfigSection(
        title: String,
        config: LlmConfig,
    ): Row {
        return group(title) {
            val providerBox = ComboBox(EnumComboBoxModel(LlmProvider::class.java))
            row(SecureCoderBundle.message("settings.provider")) {
                val providerBinding: MutableProperty<LlmProvider?> = MutableProperty(
                    { config.provider },
                    { config.provider = it ?: LlmProvider.OLLAMA }
                )
                cell(providerBox).bindItem(providerBinding)
            }
            rowsRange {
                row(SecureCoderBundle.message("settings.ollama.model")) {
                    textField()
                        .bindText(config::ollamaModel)
                        .columns(COLUMNS_MEDIUM)
                }
            }.visibleIf(providerBox.selectedValueMatches { it == LlmProvider.OLLAMA })
            rowsRange {
                row(SecureCoderBundle.message("settings.openrouter.api.key")) {
                    passwordField()
                        .bindText(config::openrouterApiKey)
                        .columns(COLUMNS_MEDIUM)
                }
                row(SecureCoderBundle.message("settings.openrouter.model")) {
                    textField()
                        .bindText(config    ::openrouterModel)
                        .columns(COLUMNS_MEDIUM)
                }
            }.visibleIf(providerBox.selectedValueMatches { it == LlmProvider.OPENROUTER })
        }
    }
}
