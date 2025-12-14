package de.tuda.stg.securecoder.openapibridge

import de.tuda.stg.securecoder.engine.Engine
import de.tuda.stg.securecoder.engine.llm.OpenRouterClient
import de.tuda.stg.securecoder.engine.workflow.WorkflowEngine
import de.tuda.stg.securecoder.enricher.PromptEnricher
import de.tuda.stg.securecoder.guardian.CodeQLGuardian

object EngineFactory {
    fun fromEnvironment(): Engine {
        return WorkflowEngine(
            PromptEnricher.PASSTHROUGH,
            OpenRouterClient(
                System.getenv("OPENROUTER_KEY"),
                System.getenv("MODEL") ?: "openai/gpt-oss-20b",
                "securecoder/openapi-bridge"
            ),
            listOf(CodeQLGuardian())
        )
    }
}
