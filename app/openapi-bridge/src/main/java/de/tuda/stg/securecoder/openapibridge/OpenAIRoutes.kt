package de.tuda.stg.securecoder.openapibridge

import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*

fun Route.openAIRoutes(agentService: AgentService) {
    route("/v1/chat/completions") {
        post {
            val request = call.receive<ChatCompletionRequest>()
            val response = agentService.generateResponse(request.messages, request.model)
            call.respond(response)
        }
    }
}
