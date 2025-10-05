package de.tuda.stg.securecoder.plugin.engine

import com.intellij.openapi.components.Service
import com.intellij.openapi.diagnostic.thisLogger
import com.intellij.openapi.project.Project
import com.intellij.platform.ide.progress.withBackgroundProgress
import de.tuda.stg.securecoder.engine.llm.OllamaClient
import de.tuda.stg.securecoder.engine.stream.EventIcon
import de.tuda.stg.securecoder.engine.stream.StreamEvent
import de.tuda.stg.securecoder.engine.workflow.WorkflowEngine
import de.tuda.stg.securecoder.enricher.EnricherClient
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
            OllamaClient()
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
                        "Internal engine error",
                        "Uncaught exception within the engine."
                                + " This should not happen and is always a bug: ${exception.message} (${exception.javaClass.simpleName})",
                        EventIcon.Error
                    ))
                } finally {
                    onComplete()
                }
            }
        }
    }
}