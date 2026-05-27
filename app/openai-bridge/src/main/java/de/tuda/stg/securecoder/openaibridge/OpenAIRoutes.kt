package de.tuda.stg.securecoder.openaibridge

import io.ktor.server.request.*
import io.ktor.server.response.*
import io.ktor.server.routing.*

fun Route.openAIRoutes(agentService: AgentService) {
    route("/v1/chat/completions") {
        post {
            try {
                val request = call.receive<ChatCompletionRequest>()
                val response = agentService.generateResponse(request.messages, request.model)
                call.respond(response)
            } catch (ex: OpenAiBridgeException) {
                call.respond(
                    ex.status,
                    OpenAiErrorEnvelope(
                        error = OpenAiErrorBody(
                            message = ex.message,
                            code = ex.code,
                        )
                    )
                )
            }
        }
    }
    route("/v1/agent/edit") {
        post {
            try {
                val request = call.receive<AgentEditRequest>()
                val response = agentService.generateEditResponse(request)
                call.respond(response)
            } catch (ex: OpenAiBridgeException) {
                call.respond(
                    ex.status,
                    OpenAiErrorEnvelope(
                        error = OpenAiErrorBody(
                            message = ex.message,
                            code = ex.code,
                        )
                    )
                )
            }
        }
    }
}
