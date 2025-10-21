package de.tuda.stg.securecoder.engine.workflow

import de.tuda.stg.securecoder.guardian.AnalyzeRequest
import de.tuda.stg.securecoder.guardian.Guardian
import de.tuda.stg.securecoder.guardian.Violation
import kotlinx.coroutines.CoroutineDispatcher
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.async
import kotlinx.coroutines.awaitAll
import kotlinx.coroutines.coroutineScope
import kotlin.collections.map

class GuardianExecutor (
    private val guardians: List<Guardian>,
    private val dispatcher: CoroutineDispatcher = Dispatchers.Default
) {
    suspend fun execute(req: AnalyzeRequest): List<Violation> = coroutineScope {
        val deferred = guardians.map { guardian ->
            async(dispatcher) { guardian.run(req) }
        }
        deferred.awaitAll().flatMap { it.violations }
    }
}