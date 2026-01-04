package de.tuda.stg.securecoder.engine.stream

import de.tuda.stg.securecoder.engine.file.edit.Changes
import de.tuda.stg.securecoder.llm.ChatExchange
import de.tuda.stg.securecoder.engine.workflow.GuardianExecutor.GuardianResult

sealed interface StreamEvent {
    data class SendDebugMessage(
        val title: String,
        val description: String,
        val icon: EventIcon
    ) : StreamEvent

    data class EnrichmentWarning(
        val errorMessage: String
    ) : StreamEvent
    
    data class InvalidLlmOutputWarning(
        val parseErrors: List<String>,
        val chatExchange: ChatExchange
    ) : StreamEvent

    data class ProposedEdits(
        val id: ProposalId,
        val changes: Changes
    ) : StreamEvent

    data class ValidationStarted(
        val id: ProposalId,
    ) : StreamEvent

    data class GuardianWarning(
        val id: ProposalId,
        val result: GuardianResult
    ) : StreamEvent

    data class ValidationSucceeded(
        val id: ProposalId
    ) : StreamEvent
}
