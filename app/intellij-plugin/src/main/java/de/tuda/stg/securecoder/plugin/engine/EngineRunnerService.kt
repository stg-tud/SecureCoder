package de.tuda.stg.securecoder.plugin.engine

import com.intellij.openapi.components.Service
import com.intellij.openapi.diagnostic.thisLogger
import com.intellij.openapi.project.Project
import com.intellij.platform.ide.progress.withBackgroundProgress
import de.tuda.stg.securecoder.engine.llm.OllamaClient
import de.tuda.stg.securecoder.engine.llm.OpenRouterClient
import de.tuda.stg.securecoder.engine.stream.EventIcon
import de.tuda.stg.securecoder.engine.stream.StreamEvent
import de.tuda.stg.securecoder.engine.workflow.WorkflowEngine
import de.tuda.stg.securecoder.enricher.EnricherClient
import de.tuda.stg.securecoder.plugin.SecureCoderBundle
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

@Service(Service.Level.PROJECT)
class EngineRunnerService(
    private val project: Project,
    private val cs: CoroutineScope
) {
    private val engine by lazy {
        //DummyAgentStreamer()
        WorkflowEngine(
            EnricherClient("http://localhost:7070"),
            OpenRouterClient(
                "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",
                "openai/gpt-oss-20b",
                "securecoder"
            )
            //OllamaClient("gpt-oss:20b")
        )
    }

    fun runEngine(
        text: String,
        onEvent: suspend (StreamEvent) -> Unit,
        onComplete: suspend () -> Unit
    ) {
        cs.launch(Dispatchers.IO) {
            withBackgroundProgress(project, "Running engine…", cancellable = false) {
                val fileSystem = IntelliJProjectFileSystem(project)
                try {
                    engine.start(text, fileSystem, onEvent)
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
                    onComplete()
                }
            }
        }
    }
}