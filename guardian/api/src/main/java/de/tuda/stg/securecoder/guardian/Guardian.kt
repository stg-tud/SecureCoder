package de.tuda.stg.securecoder.guardian

interface Guardian {
    suspend fun run(req: AnalyzeRequest): AnalyzeResponse
}
