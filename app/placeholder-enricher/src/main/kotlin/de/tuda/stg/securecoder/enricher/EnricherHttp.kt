package de.tuda.stg.securecoder.enricher

import io.ktor.serialization.kotlinx.json.*
import io.ktor.server.application.*
import io.ktor.server.plugins.contentnegotiation.*
import io.ktor.server.request.receive
import io.ktor.server.response.respond
import io.ktor.server.response.respondText
import io.ktor.server.routing.get
import io.ktor.server.routing.post
import io.ktor.server.routing.routing
import kotlinx.serialization.json.Json

fun Application.installEnricherRoutes(enricher: PromptEnricher) {
    routing {
        get("/health") { call.respondText("OK") }

        post("/v1/enrich") {
            val req = call.receive<EnrichRequest>()
            val res: EnrichResponse = enricher.enrich(req)
            call.respond(res)
        }
    }
}

fun Application.installContentNegotiation() {
    install(ContentNegotiation) {
        json(
            Json {
                ignoreUnknownKeys = false
                explicitNulls = false
            }
        )
    }
}
