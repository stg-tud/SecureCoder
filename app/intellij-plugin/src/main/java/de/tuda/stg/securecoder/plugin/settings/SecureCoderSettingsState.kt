package de.tuda.stg.securecoder.plugin.settings

import com.intellij.openapi.components.PersistentStateComponent
import com.intellij.openapi.components.Service
import com.intellij.openapi.components.State
import com.intellij.openapi.components.Storage
import com.intellij.util.messages.Topic

@State(name = "SecureCoderSettings", storages = [Storage("SecureCoderSettings.xml")])
@Service(Service.Level.APP)
class SecureCoderSettingsState : PersistentStateComponent<SecureCoderSettingsState.StateData> {
    enum class LlmProvider {
        OLLAMA,
        OPENROUTER;

        override fun toString(): String {
            return when (this) {
                OLLAMA -> "Ollama"
                OPENROUTER -> "OpenRouter"
            }
        }
    }

    data class LlmConfig(
        var provider: LlmProvider = LlmProvider.OPENROUTER,
        var ollamaModel: String = "gpt-oss:20b",
        var openrouterApiKey: String = "",
        var openrouterModel: String = "openai/gpt-oss-20b",
    ) {
        fun isValid() = provider == LlmProvider.OLLAMA || openrouterApiKey.isNotBlank()
    }

    data class StateData(
        var enricherUrl: String = "http://localhost:7070",
        var enablePromptEnriching: Boolean = true,
        var enableDummyGuardian: Boolean = true,
        var enableCodeQLGuardian: Boolean = false,
        var enableLlmGuardian: Boolean = true,
        var useMainLlmForGuardian: Boolean = true,
        var codeqlBinary: String = "codeql",
        var mainLlm: LlmConfig = LlmConfig(),
        var guardianLlm: LlmConfig = LlmConfig(),
    ) {
        fun hasLLMProviderConfigured() = mainLlm.isValid()
    }

    fun interface SecureCoderSettingsListener {
        fun settingsChanged(state: StateData)
    }

    companion object {
        val topic: Topic<SecureCoderSettingsListener> = Topic.create(
            "SecureCoderSettingsChanged",
            SecureCoderSettingsListener::class.java
        )
    }

    private var state: StateData = StateData()

    override fun getState(): StateData = state

    override fun loadState(state: StateData) {
        this.state = state
    }
}
