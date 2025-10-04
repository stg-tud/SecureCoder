package de.tuda.stg.securecoder.engine.stream

sealed interface StreamEvent {
    data class Message(val title: String, val description: String, val icon: EventIcon) : StreamEvent
}