package de.tuda.stg.securecoder.engine.llm

import kotlinx.serialization.Serializable

@Serializable
data class LoggedCall(
    val requestHash: String,
    val request: String,
    val params: String,
    val response: String,
)

@Serializable
data class LoggedRun(
    val modelName: String,
    val promptKind: String,
    val runIndex: Int,
    val enginePrompt: String,
    val initialFiles: Map<String, String>,
    val calls: List<LoggedCall>,
)

@Serializable
data class LoggedSuite(val runs: List<LoggedRun>)
