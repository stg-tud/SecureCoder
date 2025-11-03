package de.tuda.stg.securecoder.plugin.engine

import com.intellij.openapi.components.Service
import com.intellij.openapi.components.service
import com.intellij.openapi.diagnostic.thisLogger
import com.intellij.openapi.fileEditor.FileEditorManager
import com.intellij.openapi.project.Project
import com.intellij.platform.ide.progress.withBackgroundProgress
import de.tuda.stg.securecoder.engine.Engine.EngineResult
import de.tuda.stg.securecoder.engine.Engine
import de.tuda.stg.securecoder.engine.llm.OllamaClient
import de.tuda.stg.securecoder.engine.llm.OpenRouterClient
import de.tuda.stg.securecoder.engine.stream.EventIcon
import de.tuda.stg.securecoder.engine.stream.StreamEvent
import de.tuda.stg.securecoder.engine.workflow.WorkflowEngine
import de.tuda.stg.securecoder.enricher.EnricherClient
import de.tuda.stg.securecoder.enricher.PromptEnricher
import de.tuda.stg.securecoder.guardian.DummyGuardian
import de.tuda.stg.securecoder.plugin.SecureCoderBundle
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
        
        //return EngineHandle(DummyAgentStreamer(), {})
        return EngineHandle(
            WorkflowEngine(enricher, llm, listOf(DummyGuardian())),
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
        onEvent: suspend (StreamEvent) -> Unit,
        onComplete: suspend () -> Unit,
        reduceContextToOpenFiles: Boolean = false,
    ) {
        cs.launch(Dispatchers.IO) {
            withBackgroundProgress(project, "Running engine…", cancellable = false) {
                val fileSystem = IntelliJProjectFileSystem(project)
                var handle: EngineHandle? = null
                try {
                    handle = buildEngine()
                    when (val result = handle.engine.run(text, fileSystem, onEvent, buildContext(reduceContextToOpenFiles))) {
                        EngineResult.Failure.GenerationFailure -> {
                            onEvent(StreamEvent.Message(
                                SecureCoderBundle.message("error.generation.title"),
                                SecureCoderBundle.message("error.generation.description"),
                                EventIcon.Error
                            ))
                        }
                        is EngineResult.Failure.ValidationFailure -> {
                            onEvent(StreamEvent.Message(
                                SecureCoderBundle.message("error.validation.title"),
                                SecureCoderBundle.message("error.validation.description", result.maxGuardianRetries),
                                EventIcon.Error
                            ))
                        }
                        is EngineResult.Success -> {
                            onEvent(StreamEvent.EditFiles(result.changes))
                        }
                    }
                } catch (exception: Exception) {
                    thisLogger().error("Uncaught exception within the engine", exception)
                    onEvent(StreamEvent.Message(
                        SecureCoderBundle.message("error.uncaught.title"),
                        SecureCoderBundle.message(
                            "error.uncaught.description",
                            exception.message ?: "N/A",
                            exception.javaClass.simpleName
                        ),
                        EventIcon.Error
                    ))
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