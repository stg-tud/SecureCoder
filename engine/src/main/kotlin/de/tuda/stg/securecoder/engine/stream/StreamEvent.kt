package de.tuda.stg.securecoder.engine.stream

import de.tuda.stg.securecoder.engine.file.edit.Changes

sealed interface StreamEvent {
    data class SendDebugMessage(val title: String, val description: String, val icon: EventIcon) : StreamEvent

    data class EditFiles(val changes: Changes) : StreamEvent
}
