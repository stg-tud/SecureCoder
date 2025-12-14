package de.tuda.stg.securecoder.openapibridge

import de.tuda.stg.securecoder.engine.Engine
import de.tuda.stg.securecoder.engine.llm.LlmClient
import de.tuda.stg.securecoder.engine.llm.OllamaClient
import de.tuda.stg.securecoder.engine.llm.OpenRouterClient
import de.tuda.stg.securecoder.engine.workflow.WorkflowEngine
import de.tuda.stg.securecoder.enricher.PromptEnricher
import de.tuda.stg.securecoder.guardian.CodeQLGuardian

object EngineFactory {
    fun fromEnvironment(): Engine {
        return WorkflowEngine(
            PromptEnricher.PASSTHROUGH,
            createLlmClientFromEnvironment(),
            listOf(CodeQLGuardian())
        )
    }

    private fun createLlmClientFromEnvironment(): LlmClient {
        val openRouterKey = System.getenv("OPENROUTER_KEY")
        if (openRouterKey != null) {
            return OpenRouterClient(
                openRouterKey,
                System.getenv("MODEL") ?: "openai/gpt-oss-20b",
                "securecoder/openapi-bridge"
            )
        }
        return OllamaClient(
            model = System.getenv("MODEL"),
            baseUrl = System.getenv("OLLAMA_BASE_URL") ?: "http://127.0.0.1:11434",
            keepAlive = System.getenv("OLLAMA_KEEP_ALIVE") ?: "5m"
        )
    }
}
