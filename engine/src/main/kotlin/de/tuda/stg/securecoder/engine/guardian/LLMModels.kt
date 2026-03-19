package de.tuda.stg.securecoder.engine.guardian

import de.tuda.stg.securecoder.engine.llm.LLMDescription
import de.tuda.stg.securecoder.guardian.AnalyzeResponse
import de.tuda.stg.securecoder.guardian.Location
import de.tuda.stg.securecoder.guardian.RuleRef
import de.tuda.stg.securecoder.guardian.Violation
import kotlinx.serialization.Serializable

@Serializable
@LLMDescription("Response containing security analysis results")
data class LlmAnalyzeResponse(
    @LLMDescription("List of security findings discovered during analysis")
    val findings: List<Finding> = emptyList()
) {
    fun toApi(): AnalyzeResponse = AnalyzeResponse(
        violations = findings.map { it.toApi() }
    )

    @Serializable
    @LLMDescription("Details of a single security finding")
    data class Finding(
        @LLMDescription("Line number where the issue starts, null if not applicable")
        val shortName: String,

        @LLMDescription("Brief description of the security issue")
        val description: String,

        @LLMDescription("The name of the file where the issue was found")
        val fileName: String,

        @LLMDescription("Line number where the issue starts, null if not applicable")
        val line: Int? = null,

        @LLMDescription("Indicates whether this finding make it impossible to apply the changes even with manuel approval")
        val hardReject: Boolean,

        @LLMDescription("The estimated likelihood that this finding is a true positive (e.g., High, Medium, Low)")
        val confidence: String?
    ) {
        fun toApi(): Violation = Violation(
            rule = RuleRef("llm", shortName ),
            message = description,
            location = Location(fileName, line),
            hardReject = hardReject,
            confidence = confidence
        )
    }
}