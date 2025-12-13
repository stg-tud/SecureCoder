package de.tuda.stg.securecoder.openapibridge

import io.ktor.server.engine.*
import io.ktor.server.netty.*

fun main() {
    val port = System.getenv("PORT")?.toIntOrNull() ?: 8080
    embeddedServer(Netty, port) {

    }.start(wait = true)
}
