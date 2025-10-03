package de.tuda.stg.securecoder.enricher

import io.ktor.server.engine.*
import io.ktor.server.netty.*

fun main() {
    val port = System.getenv("PORT")?.toIntOrNull() ?: 7070
    val enricher: PromptEnricher = DummyEnricherService()

    embeddedServer(Netty, port) {
        installContentNegotiation()
        installEnricherRoutes(enricher)
    }.start(wait = true)
}
