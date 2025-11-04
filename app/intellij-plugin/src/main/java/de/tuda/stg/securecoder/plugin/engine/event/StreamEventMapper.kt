package de.tuda.stg.securecoder.plugin.engine.event

import com.intellij.icons.AllIcons
import de.tuda.stg.securecoder.engine.stream.StreamEvent
import de.tuda.stg.securecoder.plugin.SecureCoderBundle

object StreamEventMapper {
    fun map(event: StreamEvent): UiStreamEvent = when (event) {
        is StreamEvent.EditFiles -> UiStreamEvent.EditFiles(event.changes)

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
            UiStreamEvent.Message(
                title = SecureCoderBundle.message("warning.guardian.title"),
                description = SecureCoderBundle.message("warning.guardian.description", event.violations),
                icon = AllIcons.General.Warning
            )
        }

        is StreamEvent.InvalidLlmOutputWarning -> {
            UiStreamEvent.Message(
                title = SecureCoderBundle.message("warning.llm.title"),
                description = SecureCoderBundle.message("warning.llm.description", event.parseErrors.joinToString("\n")),
                icon = AllIcons.General.Warning
            )
        }
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
