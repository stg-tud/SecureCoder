package de.tuda.stg.securecoder.engine.stream

import de.tuda.stg.securecoder.engine.file.edit.Changes
import de.tuda.stg.securecoder.engine.llm.ChatExchange

sealed interface StreamEvent {
    data class SendDebugMessage(val title: String, val description: String, val icon: EventIcon) : StreamEvent

    data class EditFiles(val changes: Changes) : StreamEvent
    
    data class EnrichmentWarning(val errorMessage: String) : StreamEvent
    
    data class GuardianWarning(val violations: String) : StreamEvent
    
    data class InvalidLlmOutputWarning(
        val parseErrors: List<String>,
        val chatExchange: ChatExchange
    ) : StreamEvent
}
