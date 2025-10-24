package de.tuda.stg.securecoder.guardian

import kotlin.random.Random

class DummyGuardian(
    private val flagProbabilityPerFile: Double = 0.8,
    private val hardRejet: Boolean = false,
    private val rng: Random = Random,
) : Guardian {
    override fun run(req: AnalyzeRequest): AnalyzeResponse {
        val violations = req.files
            .filter { rng.nextDouble() < flagProbabilityPerFile }
            .map { randomViolationFor(it) }
        return AnalyzeResponse(violations)
    }

    private fun randomViolationFor(file: File): Violation {
        val lines = file.content.split('\n')
        val totalLines = lines.size.coerceAtLeast(1)
        val line = rng.nextInt(1, totalLines + 1)
        val message = "Potential security issue on line $line"

        return Violation(
            rule = RuleRef(
                id = "ABC-001",
                name = "Suspicious Pattern",
            ),
            message = message,
            location = Location(
                file = file.name,
                startLine = line,
                endLine = line,
            ),
            hardReject = hardRejet,
            confidence = listOf("low", "medium", "high", null).random(rng),
        )
    }
}
