package de.tuda.stg.securecoder.plugin.settings

import com.intellij.openapi.components.PersistentStateComponent
import com.intellij.openapi.components.Service
import com.intellij.openapi.components.State
import com.intellij.openapi.components.Storage

@State(name = "SecureCoderSettings", storages = [Storage("SecureCoderSettings.xml")])
@Service(Service.Level.APP)
class SecureCoderSettingsState : PersistentStateComponent<SecureCoderSettingsState.StateData> {
    enum class LlmProvider { OLLAMA, OPENROUTER }

    data class StateData(
        var enricherUrl: String = "http://localhost:7070",
        var llmProvider: LlmProvider = LlmProvider.OLLAMA,
        var ollamaModel: String = "gpt-oss:20b",
        var openrouterApiKey: String = "",
        var openrouterModel: String = "openai/gpt-oss-20b",
    )

    private var state: StateData = StateData()

    override fun getState(): StateData = state

    override fun loadState(state: StateData) {
        this.state = state
    }
}
