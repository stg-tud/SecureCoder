package de.tuda.stg.securecoder.openapibridge

import io.ktor.serialization.kotlinx.json.json
import io.ktor.server.application.install
import io.ktor.server.engine.*
import io.ktor.server.netty.*
import io.ktor.server.plugins.contentnegotiation.ContentNegotiation
import io.ktor.server.routing.routing
import kotlinx.serialization.json.Json

fun main() {
    val port = System.getenv("PORT")?.toIntOrNull() ?: 8080
    val engine = EngineFactory.fromEnvironment()
    val agentService = AgentService(engine)
    embeddedServer(Netty, port) {
        install(ContentNegotiation) {
            json(Json {
                prettyPrint = true
                ignoreUnknownKeys = true
                encodeDefaults = true
            })
        }
        routing {
            openAIRoutes(agentService)
        }
    }.start(wait = true)
}
