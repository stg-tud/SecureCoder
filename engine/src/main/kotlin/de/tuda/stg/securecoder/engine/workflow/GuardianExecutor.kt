package de.tuda.stg.securecoder.engine.workflow

import de.tuda.stg.securecoder.engine.file.FileSystem
import de.tuda.stg.securecoder.engine.file.edit.ApplyChanges
import de.tuda.stg.securecoder.engine.file.edit.Changes
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
    )

    suspend fun analyze(fileSystem: FileSystem, changes: Changes): GuardianResult {
        val files = mutableListOf<File>()
        ApplyChanges.applyAll(
            changes,
            { fileSystem.getFile(it)?.content() },
            { file, content -> files.add(File(file, content)) }
        )
        val request = AnalyzeRequest(files)
        val result = execute(request)
        return result
    }

    private suspend fun execute(request: AnalyzeRequest): GuardianResult = coroutineScope {
        val deferred = guardians.map { guardian ->
            async(dispatcher) { guardian.run(request) }
        }
        val violations = deferred.awaitAll().flatMap { it.violations }
        GuardianResult(violations, request.files)
    }
}
