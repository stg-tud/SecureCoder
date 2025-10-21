package de.tuda.stg.securecoder.guardian

interface Guardian {
    fun run(req: AnalyzeRequest): AnalyzeResponse
}
