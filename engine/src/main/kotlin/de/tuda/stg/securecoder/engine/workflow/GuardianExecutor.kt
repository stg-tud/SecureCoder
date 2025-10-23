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
        println(result.buildFeedbackForLlm())
        return result
    }

    private suspend fun execute(request: AnalyzeRequest): GuardianResult = coroutineScope {
        val deferred = guardians.map { guardian ->
            async(dispatcher) { guardian.run(request) }
        }
        val violations = deferred.awaitAll().flatMap { it.violations }
        GuardianResult(violations, request.files)
    }

    fun GuardianResult.buildFeedbackForLlm(
        maxListedViolations: Int = 20,
        linesAround: Int = 6,
    ) = buildString {
        appendLine("Security analysis found ${violations.size} violation(s). Address all of them and resend the COMPLETE set of edits.")
        appendLine("Respond again with ONLY <EDITN> blocks. Do NOT include prose.")
        violations.take(maxListedViolations).forEachIndexed { idx, v ->
            val loc = listOfNotNull(v.location.file, v.location.startLine?.toString()).joinToString(":")
            appendLine("${idx + 1}. [${v.rule.id}]${v.message} @ $loc")
            val fileContent = files.find { it.name == v.location.file }?.content
            if (fileContent == null) throw IllegalStateException("File content not found: ${v.location.file}")
            appendLine("SNIPPET: ${v.location.file}")
            appendLine("<<<")
            appendLine(makeSnippet(
                fileContent = fileContent,
                startLine = v.location.startLine,
                endLine = v.location.endLine,
                linesAround = linesAround,
            ))
            appendLine(">>>")
        }
        if (violations.size > maxListedViolations) {
            appendLine("…and ${violations.size - maxListedViolations} more")
        }
    }

    private fun makeSnippet(
        fileContent: String,
        startLine: Int?,
        endLine: Int?,
        linesAround: Int,
    ): String {
        val lines = fileContent.split('\n')
        val from = ((startLine ?: 1) - linesAround).coerceIn(1, lines.size)
        val to = ((endLine ?: startLine ?: 20) + linesAround).coerceIn(1, lines.size)
        val builder = StringBuilder()
        for (i in from..to) {
            val line = lines[i - 1]
            builder.append(String.format("%5d | %s%n", i, line))
        }
        return builder.toString()
    }
}
