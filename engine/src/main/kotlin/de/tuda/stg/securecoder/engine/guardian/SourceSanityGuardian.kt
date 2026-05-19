package de.tuda.stg.securecoder.engine.guardian

import de.tuda.stg.securecoder.guardian.AnalyzeRequest
import de.tuda.stg.securecoder.guardian.AnalyzeResponse
import de.tuda.stg.securecoder.guardian.Guardian
import de.tuda.stg.securecoder.guardian.Location
import de.tuda.stg.securecoder.guardian.RuleRef
import de.tuda.stg.securecoder.guardian.Violation

class SourceSanityGuardian : Guardian {
    override suspend fun run(req: AnalyzeRequest): AnalyzeResponse {
        val violations = req.files.flatMap { file ->
            SourceTextNormalizer.detectProblems(file.name, file.content).map { problem ->
                Violation(
                    rule = RuleRef(id = problem.ruleId, name = problem.ruleId),
                    message = problem.message,
                    location = Location(file = file.name, startLine = 1),
                    hardReject = true,
                    confidence = "HIGH",
                )
            }
        }
        return AnalyzeResponse(violations)
    }
}
