package de.tuda.stg.securecoder.plugin.engine

import de.tuda.stg.securecoder.engine.Engine
import de.tuda.stg.securecoder.engine.stream.EventIcon
import kotlinx.coroutines.delay
import java.util.concurrent.ThreadLocalRandom

class DummyAgentStreamer : Engine {
    override suspend fun start(
        prompt: String,
        onEvent: suspend (title: String, description: String, icon: EventIcon) -> Unit,
        onComplete: suspend () -> Unit
    ) {
        val titles = listOf(
            "Analyzing your prompt",
            "Scanning project",
            "Generating suggestions",
            "Reviewing security checks",
            "Summarizing findings",
            "Optimizing fix",
        )
        val descriptions = listOf(
            "Looking for potential vulnerabilities and patterns...",
            "Collecting context from open files and project configuration...",
            "Preparing actionable remediation steps...",
            "Cross-checking against common CWE entries...",
            "Packaging results for display...",
        )

        repeat(24) { idx ->
            val title = randomPick(titles) + " (${idx + 1}/24)"
            val desc = randomPick(descriptions)
            val icon = randomPick(EventIcon.entries)
            onEvent(title, desc, icon)
            delay(1000)
        }
        onComplete()
    }

    private fun <T> randomPick(list: List<T>): T = list[ThreadLocalRandom.current().nextInt(list.size)]
}