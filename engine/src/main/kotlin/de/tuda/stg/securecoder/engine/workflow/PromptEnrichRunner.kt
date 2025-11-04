package de.tuda.stg.securecoder.engine.workflow

import de.tuda.stg.securecoder.engine.file.FileSystem
import de.tuda.stg.securecoder.engine.stream.EventIcon
import de.tuda.stg.securecoder.engine.stream.StreamEvent
import de.tuda.stg.securecoder.enricher.EnrichFileForContext
import de.tuda.stg.securecoder.enricher.EnrichRequest
import de.tuda.stg.securecoder.enricher.PromptEnricher
import kotlinx.coroutines.async
import kotlinx.coroutines.supervisorScope
import kotlinx.coroutines.withTimeoutOrNull
import kotlin.time.TimeSource.Monotonic

class PromptEnrichRunner (
    val enricher: PromptEnricher,
) {
    suspend fun enrichPrompt(
        onEvent: suspend (StreamEvent) -> Unit,
        files: List<FileSystem.File>,
        prompt: String,
        warnAfterMillis: Long = 300,
    ): String = supervisorScope {
        val filesForPrompt = files.map { EnrichFileForContext(it.name(), it.content()) }
        val mark = Monotonic.markNow()
        val deferred = async { enricher.enrich(EnrichRequest(prompt, filesForPrompt)) }
        val result = runCatching {
            val early = withTimeoutOrNull(warnAfterMillis) { deferred.await() }
            if (early == null) {
                onEvent(
                    StreamEvent.SendDebugMessage(
                        "Enriching prompt…",
                        "Enrichment is taking longer than $warnAfterMillis ms.",
                        EventIcon.Info
                    )
                )
                deferred.await()
            } else {
                early
            }
        }
        val elapsed = mark.elapsedNow()
        result.fold(
            onSuccess = { resp ->
                onEvent(StreamEvent.SendDebugMessage(
                    "Prompt enriched",
                    "Updated prompt (took ${elapsed.inWholeMilliseconds} ms): ${resp.enriched}",
                    EventIcon.Info
                ))
                resp.enriched
            },
            onFailure = { t ->
                onEvent(StreamEvent.EnrichmentWarning(
                    t.message ?: t::class.simpleName.toString()
                ))
                prompt
            }
        )
    }
}
