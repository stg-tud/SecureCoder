package de.tuda.stg.securecoder.plugin

import com.intellij.icons.AllIcons
import com.intellij.openapi.application.ApplicationManager
import javax.swing.Icon
import java.util.concurrent.ThreadLocalRandom

class DummyAgentStreamer {
    fun startDummyStream(prompt: String, onEvent: (title: String, description: String, icon: Icon) -> Unit) {
        ApplicationManager.getApplication().executeOnPooledThread {
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
            val icons = listOf(
                AllIcons.General.Information,
                AllIcons.General.Warning,
                AllIcons.General.Balloon,
                AllIcons.General.BalloonInformation,
                AllIcons.General.Error
            )

            repeat(8) { idx ->
                val title = randomPick(titles) + " (${idx + 1}/5)"
                val desc = randomPick(descriptions)
                val icon = randomPick(icons)
                onEvent(title, desc, icon)
                try {
                    Thread.sleep(1000)
                } catch (_: InterruptedException) {
                    return@executeOnPooledThread
                }
            }
        }
    }

    private fun <T> randomPick(list: List<T>): T = list[ThreadLocalRandom.current().nextInt(list.size)]
}
