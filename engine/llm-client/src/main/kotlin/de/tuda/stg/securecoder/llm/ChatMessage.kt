package de.tuda.stg.securecoder.llm

data class ChatMessage (val role: Role, val content: String) {
    enum class Role { System, User, Assistant }
}
