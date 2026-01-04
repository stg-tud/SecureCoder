package de.tuda.stg.securecoder.engine.workflow

import de.tuda.stg.securecoder.engine.file.edit.ApplyChanges
import de.tuda.stg.securecoder.engine.file.edit.Changes
import de.tuda.stg.securecoder.filesystem.FileSystem
import de.tuda.stg.securecoder.guardian.AnalyzeRequest
import de.tuda.stg.securecoder.guardian.File
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
    data class GuardianResult(
        val violations: List<Violation>,
        val files: List<File>,
        val failures: List<GuardianFailure> = emptyList(),
    ) {
        fun hasNoViolations() = violations.isEmpty()
    }

    data class GuardianFailure(
        val guardian: String,
        val message: String,
    )

    suspend fun analyze(fileSystem: FileSystem, changes: Changes): GuardianResult {
        val files = mutableListOf<File>()
        ApplyChanges.applyAll(
            changes,
            { fileSystem.getFile(it)?.content() },
            { file, content -> files.add(File(file, content)) }
        )
        return execute(AnalyzeRequest(fileSystem, files))
    }

    private suspend fun execute(request: AnalyzeRequest): GuardianResult = coroutineScope {
        data class Outcome(val violations: List<Violation>, val failure: GuardianFailure?)

        val deferred = guardians.map { guardian ->
            async(dispatcher) {
                try {
                    val resp = guardian.run(request)
                    Outcome(resp.violations, null)
                } catch (throwable: Throwable) {
                    val name = guardian.javaClass.simpleName
                    Outcome(emptyList(), GuardianFailure(name, throwable.message ?: throwable.toString()))
                }
            }
        }
        val outcomes = deferred.awaitAll()
        val violations = outcomes.flatMap { it.violations }
        val failures = outcomes.mapNotNull { it.failure }
        GuardianResult(violations, request.files, failures)
    }
}
