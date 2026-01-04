package de.tuda.stg.securecoder.plugin.engine

import com.intellij.openapi.components.Service
import com.intellij.openapi.components.service
import com.intellij.openapi.diagnostic.thisLogger
import com.intellij.openapi.fileEditor.FileEditorManager
import com.intellij.openapi.project.Project
import com.intellij.platform.ide.progress.withBackgroundProgress
import de.tuda.stg.securecoder.engine.Engine
import de.tuda.stg.securecoder.llm.OllamaClient
import de.tuda.stg.securecoder.llm.OpenRouterClient
import de.tuda.stg.securecoder.engine.workflow.WorkflowEngine
import de.tuda.stg.securecoder.enricher.EnricherClient
import de.tuda.stg.securecoder.enricher.PromptEnricher
import de.tuda.stg.securecoder.guardian.CodeQLGuardian
import de.tuda.stg.securecoder.guardian.DummyGuardian
import de.tuda.stg.securecoder.plugin.engine.event.EngineResultMapper
import de.tuda.stg.securecoder.plugin.engine.event.StreamEventMapper
import de.tuda.stg.securecoder.plugin.engine.event.UiStreamEvent
import de.tuda.stg.securecoder.plugin.settings.SecureCoderSettingsState
import de.tuda.stg.securecoder.plugin.settings.SecureCoderSettingsState.LlmProvider
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

@Service(Service.Level.PROJECT)
class EngineRunnerService(
    private val project: Project,
    private val cs: CoroutineScope,
) {
    private val settings = service<SecureCoderSettingsState>()

    private data class EngineHandle(
        val engine: Engine,
        val close: () -> Unit,
    )

    private fun buildEngine(): EngineHandle {
        val settings = settings.state
        val llm = when (settings.llmProvider) {
            LlmProvider.OPENROUTER -> OpenRouterClient(
                settings.openrouterApiKey,
                settings.openrouterModel,
                "securecoder"
            )
            LlmProvider.OLLAMA -> OllamaClient(settings.ollamaModel)
        }
        
        val enricher = if (settings.enablePromptEnriching) {
            EnricherClient(settings.enricherUrl)
        } else {
            PromptEnricher.PASSTHROUGH
        }
        val guardians = listOfNotNull(
            if (settings.enableDummyGuardian) DummyGuardian(sleepMillis = 2000) else null,
            if (settings.enableCodeQLGuardian) CodeQLGuardian(settings.codeqlBinary) else null
        )
        
        //return EngineHandle(DummyAgentStreamer(), {})
        return EngineHandle(
            WorkflowEngine(enricher, llm, guardians),
            {
                llm.close()
                if (enricher is AutoCloseable) {
                    enricher.close()
                }
            }
        )
    }

    fun runEngine(
        text: String,
        onUiEvent: suspend (UiStreamEvent) -> Unit,
        onComplete: suspend () -> Unit,
        reduceContextToOpenFiles: Boolean = false,
    ) {
        cs.launch(Dispatchers.IO) {
            withBackgroundProgress(project, "Running engine…", cancellable = false) {
                val fileSystem = IntelliJProjectFileSystem(project)
                var handle: EngineHandle? = null
                val mapper = StreamEventMapper()

                try {
                    handle = buildEngine()
                    val result = handle.engine.run(
                        text,
                        fileSystem,
                        { engineEvent -> onUiEvent(mapper.map(engineEvent)) },
                        buildContext(reduceContextToOpenFiles)
                    )
                    EngineResultMapper.map(mapper, result)?.let { onUiEvent(it) }
                } catch (exception: Exception) {
                    thisLogger().error("Uncaught exception within the engine", exception)
                    onUiEvent(mapper.mapException(exception))
                } finally {
                    runCatching { handle?.close?.invoke() }.onFailure {
                        thisLogger().warn("Failed closing engine handle", it)
                    }
                    onComplete()
                }
            }
        }
    }

    private fun buildContext(reduceContextToOpenFiles: Boolean): Engine.Context? {
        if (!reduceContextToOpenFiles) {
            return null
        }
        return Engine.Context(
            FileEditorManager.getInstance(project)
                .openFiles
                .map { it.url }
                .toSet()
        )
    }
}
