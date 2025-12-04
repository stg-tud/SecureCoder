package de.tuda.stg.securecoder.guardian

import de.tuda.stg.securecoder.filesystem.FileSystem
import kotlinx.serialization.Serializable

@Serializable
data class File(
    val name: String,
    val content: String,
)

@Serializable
data class AnalyzeRequest(val fileSystem: FileSystem, val files: List<File>) /* TODO do we need ALL files? */

@Serializable
data class AnalyzeResponse(
    val violations: List<Violation>,
)

@Serializable
data class Violation(
    val rule: RuleRef,
    val message: String,
    val location: Location,
    val hardReject: Boolean,
    val confidence: String? = null,
)

@Serializable
data class RuleRef(
    val id: String,
    val name: String? = null,
    val description: String? = null,
    val cwe: String? = null,
    val owasp: String? = null
)

@Serializable
data class Location(
    val file: String,
    val startLine: Int? = null,
    val endLine: Int? = null,
    val startColumn: Int? = null,
    val endColumn: Int? = null
)
