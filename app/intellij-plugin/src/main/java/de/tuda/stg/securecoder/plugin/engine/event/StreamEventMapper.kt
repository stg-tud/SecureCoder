package de.tuda.stg.securecoder.plugin.engine.event

import com.intellij.icons.AllIcons
import de.tuda.stg.securecoder.engine.stream.StreamEvent
import de.tuda.stg.securecoder.plugin.SecureCoderBundle
import de.tuda.stg.securecoder.plugin.engine.event.UiStreamEvent.EditFilesValidation

class StreamEventMapper {
    private val proposals = mutableMapOf<String, UiStreamEvent.EditFiles>()

    fun map(event: StreamEvent): UiStreamEvent = when (event) {
        is StreamEvent.ProposedEdits -> {
            val pid = event.id.value
            val current = proposals[pid]
            val merged = (current ?: UiStreamEvent.EditFiles(
                changes = event.changes,
                proposalId = pid,
                validation = EditFilesValidation.NotAvailable,
            )).copy(changes = event.changes)
            proposals[pid] = merged
            merged
        }
        is StreamEvent.ValidationStarted -> {
            val pid = event.id.value
            updateProposalValidation(pid, EditFilesValidation.Running)
        }
        is StreamEvent.ValidationSucceeded -> {
            val pid = event.id.value
            updateProposalValidation(pid, EditFilesValidation.Succeeded)
        }

        is StreamEvent.SendDebugMessage -> {
            UiStreamEvent.Message(
                title = event.title,
                description = event.description,
                icon = event.icon.toIntellijIcon()
            )
        }

        is StreamEvent.EnrichmentWarning -> {
            UiStreamEvent.Message(
                title = SecureCoderBundle.message("warning.enrichment.title"),
                description = SecureCoderBundle.message("warning.enrichment.description", event.errorMessage),
                icon = AllIcons.General.Warning
            )
        }

        is StreamEvent.GuardianWarning -> {
            val hints = event.result.violations.map { v ->
                if (v.rule.name.isNullOrBlank()) v.rule.id else v.rule.name!!
            } + event.result.failures.map { f ->
                "Guardian '${f.guardian}' failed: ${f.message}"
            }

            val pid = event.id.value
            updateProposalValidation(pid, EditFilesValidation.Failed(hints))
        }

        is StreamEvent.InvalidLlmOutputWarning -> {
            UiStreamEvent.Message(
                title = SecureCoderBundle.message("warning.llm.title"),
                description = SecureCoderBundle.message("warning.llm.description", event.parseErrors.joinToString("\n")),
                icon = AllIcons.General.Warning,
                debugText = buildExchangeText(event)
            )
        }
    }

    private fun updateProposalValidation(pid: String, newValidation: EditFilesValidation): UiStreamEvent.EditFiles {
        val current = proposals[pid] ?: throw IllegalStateException("Unknown proposal $pid")
        val merged = current.copy(validation = newValidation)
        proposals[pid] = merged
        return merged
    }

    private fun buildExchangeText(event: StreamEvent.InvalidLlmOutputWarning): String {
        val sb = StringBuilder()
        sb.appendLine("Input messages:")
        event.chatExchange.input.forEachIndexed { idx, msg ->
            sb.appendLine("#${idx + 1} ${msg.role}:")
            sb.appendLine(msg.content)
            sb.appendLine()
        }
        sb.appendLine("Model output:")
        sb.appendLine(event.chatExchange.output)
        sb.appendLine()
        sb.appendLine("Parse errors:")
        event.parseErrors.forEachIndexed { index, error ->
            sb.appendLine("#${index + 1}: $error")
        }
        return sb.toString()
    }

    fun mapException(exception: Exception): UiStreamEvent.Message {
        return UiStreamEvent.Message(
            title = SecureCoderBundle.message("error.uncaught.title"),
            description = SecureCoderBundle.message(
                "error.uncaught.description",
                exception.message ?: "N/A",
                exception.javaClass.simpleName
            ),
            icon = AllIcons.General.Error
        )
    }

    fun createValidationError(maxGuardianRetries: Int): UiStreamEvent.Message {
        return UiStreamEvent.Message(
            title = SecureCoderBundle.message("error.validation.title"),
            description = SecureCoderBundle.message("error.validation.description", maxGuardianRetries),
            icon = AllIcons.General.Error
        )
    }

    fun createGenerationError(): UiStreamEvent.Message {
        return UiStreamEvent.Message(
            title = SecureCoderBundle.message("error.generation.title"),
            description = SecureCoderBundle.message("error.generation.description"),
            icon = AllIcons.General.Error
        )
    }
}
