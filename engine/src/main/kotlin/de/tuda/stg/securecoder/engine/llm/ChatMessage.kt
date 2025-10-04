package de.tuda.stg.securecoder.engine.llm

class ChatMessage (val role: Role, val content: String) {
    enum class Role { System, User, Assistant }
}
