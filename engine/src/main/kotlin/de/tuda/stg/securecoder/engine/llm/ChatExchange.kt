package de.tuda.stg.securecoder.engine.llm

data class ChatExchange(
    val input: List<ChatMessage>,
    val output: String
)
