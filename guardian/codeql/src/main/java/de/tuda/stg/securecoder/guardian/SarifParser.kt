package de.tuda.stg.securecoder.guardian

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.JsonElement
import kotlinx.serialization.json.JsonNull
import kotlinx.serialization.json.JsonObject
import kotlinx.serialization.json.JsonPrimitive
import kotlinx.serialization.json.int
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject

fun parseSarifToViolations(text: String): List<Violation> {
    println("Parsing sarif: $text")
    val root = Json.parseToJsonElement(text)
    if (root !is JsonObject) return emptyList()

    val runs = root["runs"]?.jsonArray ?: return emptyList()
    val out = mutableListOf<Violation>()
    for (run in runs) {
        val results = run.jsonObject["results"]?.jsonArray ?: continue
        for (res in results) {
            out.add(mapResultToViolation(res))
        }
    }
    return out
}

private fun mapResultToViolation(res: JsonElement): Violation {
    val obj = res.jsonObject
    val ruleId = obj["ruleId"]?.asText() ?: "unknown"
    val message = obj["message"]?.jsonObject?.get("text")?.asText() ?: "CodeQL issue"

    val locations = obj["locations"]?.jsonArray
    val firstLoc = locations?.firstOrNull()?.jsonObject
    val phys = firstLoc?.get("physicalLocation")?.jsonObject
    val artifact = phys?.get("artifactLocation")?.jsonObject
    val region = phys?.get("region")?.jsonObject

    val filePath = artifact?.get("uri")?.asText() ?: artifact?.get("uriBaseId")?.asText() ?: "<unknown>"
    val startLine = region?.get("startLine")?.asInt()
    val endLine = region?.get("endLine")?.asInt() ?: startLine

    val level = obj["level"]?.asText()
    val precision = obj["properties"]?.jsonObject?.get("precision")?.asText()
    val confidence = precision ?: level

    return Violation(
        rule = RuleRef(id = ruleId),
        message = message,
        location = Location(
            file = filePath,
            startLine = startLine,
            endLine = endLine,
        ),
        hardReject = false,
        confidence = confidence,
    )
}

private fun JsonElement.asText(): String? = when (this) {
    is JsonPrimitive -> if (isString) content else toString()
    JsonNull -> null
    else -> toString()
}

private fun JsonElement?.asInt(): Int? = (this as? JsonPrimitive)?.int
