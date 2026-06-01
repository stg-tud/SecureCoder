package de.tuda.stg.securecoder.guardian

fun interface ViolationTriage {
    suspend fun triage(req: AnalyzeRequest, violations: List<Violation>): List<Violation>
}
