package de.tuda.stg.securecoder.llm

data class ChatExchange(
    val input: List<ChatMessage>,
    val output: String
)
