package de.tuda.stg.securecoder.openaibridge

import de.tuda.stg.securecoder.engine.Engine
import de.tuda.stg.securecoder.engine.guardian.CSyntaxGuardian
import de.tuda.stg.securecoder.engine.guardian.GoSyntaxGuardian
import de.tuda.stg.securecoder.engine.guardian.CppSyntaxGuardian
import de.tuda.stg.securecoder.engine.guardian.JavaScriptSyntaxGuardian
import de.tuda.stg.securecoder.engine.guardian.LlmGuardian
import de.tuda.stg.securecoder.engine.guardian.LlmViolationTriage
import de.tuda.stg.securecoder.engine.guardian.PythonSyntaxGuardian
import de.tuda.stg.securecoder.engine.guardian.SourceSanityGuardian
import de.tuda.stg.securecoder.engine.file.edit.EditFormat
import de.tuda.stg.securecoder.engine.file.edit.ReviewMode
import de.tuda.stg.securecoder.engine.llm.LlmClient
import de.tuda.stg.securecoder.engine.llm.OllamaClient
import de.tuda.stg.securecoder.engine.llm.OpenRouterClient
import de.tuda.stg.securecoder.engine.workflow.GuardianRetryPolicy
import de.tuda.stg.securecoder.engine.workflow.SelfTestLoop
import de.tuda.stg.securecoder.engine.workflow.WorkflowEngine
import de.tuda.stg.securecoder.engine.workflow.PersistentWorkflowTraceLogger
import de.tuda.stg.securecoder.engine.workflow.WorkflowTraceLogger
import de.tuda.stg.securecoder.enricher.PromptEnricher
import de.tuda.stg.securecoder.guardian.CodeQLGuardian
import de.tuda.stg.securecoder.guardian.CodeQLRunner
import de.tuda.stg.securecoder.guardian.Guardian
import kotlinx.serialization.json.Json
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive
import java.nio.file.Path
import kotlin.io.path.exists
import kotlin.io.path.readText

object EngineFactory {
    fun fromEnvironment(): Engine {
        val llmClient = createLlmClientFromEnvironment()
        val codeQlBinary = propOrEnv("CODEQL_BIN") ?: "codeql"
        val promptEnricher = if (boolPropOrEnv("ENABLE_HEURISTIC_PROMPT_ENRICHER", default = true)) {
            HeuristicPromptEnricher
        } else {
            PromptEnricher.PASSTHROUGH
        }
        val guardians = buildGuardians(llmClient, codeQlBinary)
        val editFormat = EditFormat.from(propOrEnv("EDIT_FORMAT"))
        val reviewMode = ReviewMode.valueOf((propOrEnv("REVIEW_MODE") ?: "PATCH").trim().uppercase())
        val legacyHardRetryLimit = propOrEnv("MAX_GUARDIAN_RETRIES")
            ?.trim()
            ?.toIntOrNull()
        val hardGuardianRetries = propOrEnv("HARD_GUARDIAN_RETRIES")
            ?.trim()
            ?.toIntOrNull()
            ?: legacyHardRetryLimit
            ?: 14
        val softGuardianRetries = propOrEnv("SOFT_GUARDIAN_RETRIES")
            ?.trim()
            ?.toIntOrNull()
            ?.coerceAtMost(hardGuardianRetries)
            ?: 7.coerceAtMost(hardGuardianRetries)
        val guardianRetryPolicy = GuardianRetryPolicy(
            softLimit = softGuardianRetries,
            hardLimit = hardGuardianRetries,
            enableMetaReview = boolPropOrEnv("ENABLE_GUARDIAN_META_REVIEW", default = true),
        )
        val selfTestLoop = SelfTestLoop(
            llmClient = llmClient,
            enabled = boolPropOrEnv("ENABLE_SELF_TEST_LOOP", default = false),
            enabledLanguages = propOrEnv("SELF_TEST_LANGUAGES")
                ?.split(",")
                ?.map { it.trim().lowercase() }
                ?.filter { it.isNotEmpty() }
                ?.toSet()
                ?.takeIf { it.isNotEmpty() },
            pythonBin = propOrEnv("PYTHON_BIN") ?: "python3",
            nodeBin = propOrEnv("NODE_BIN") ?: "node",
            goBin = propOrEnv("GO_BIN") ?: "go",
            gccBin = propOrEnv("GCC_BIN") ?: "gcc",
            gppBin = propOrEnv("GPP_BIN") ?: "g++",
            timeoutSeconds = propOrEnv("SELF_TEST_TIMEOUT_SECONDS")
                ?.trim()
                ?.toLongOrNull()
                ?: 20L,
        )
        val traceLogger = createTraceLogger()
        return WorkflowEngine(
            promptEnricher,
            llmClient,
            guardians,
            editFormat = editFormat,
            reviewMode = reviewMode,
            guardianRetryPolicy = guardianRetryPolicy,
            selfTestLoop = selfTestLoop,
            traceLogger = traceLogger,
        )
    }

    private fun propOrEnv(name: String): String? = System.getProperty(name) ?: System.getenv(name)

    private fun buildGuardians(llmClient: LlmClient, codeQlBinary: String): List<Guardian> {
        val guardians = mutableListOf<Guardian>()
        if (boolPropOrEnv("ENABLE_SOURCE_SANITY_GUARDIAN", default = true)) {
            guardians += SourceSanityGuardian()
        }
        if (boolPropOrEnv("ENABLE_PYTHON_SYNTAX_GUARDIAN", default = true)) {
            guardians += PythonSyntaxGuardian(propOrEnv("PYTHON_BIN") ?: "python3")
        }
        if (boolPropOrEnv("ENABLE_JAVASCRIPT_SYNTAX_GUARDIAN", default = true)) {
            guardians += JavaScriptSyntaxGuardian(propOrEnv("NODE_BIN") ?: "node")
        }
        if (boolPropOrEnv("ENABLE_GO_SYNTAX_GUARDIAN", default = true)) {
            guardians += GoSyntaxGuardian(propOrEnv("GOFMT_BIN") ?: "gofmt")
        }
        if (boolPropOrEnv("ENABLE_C_SYNTAX_GUARDIAN", default = true)) {
            guardians += CSyntaxGuardian(propOrEnv("CLANG_BIN") ?: "clang")
        }
        if (boolPropOrEnv("ENABLE_CPP_SYNTAX_GUARDIAN", default = true)) {
            guardians += CppSyntaxGuardian(propOrEnv("CLANGXX_BIN") ?: "clang++")
        }
        val enableBaseCodeQl = boolPropOrEnv("ENABLE_CODEQL_GUARDIAN", default = true)
        val enableSensitiveCodeQl = boolPropOrEnv("ENABLE_CODEQL_SENSITIVE_GUARDIAN", default = false)
        if (enableBaseCodeQl || enableSensitiveCodeQl) {
            ensureCodeQlAvailable(codeQlBinary)
        }
        if (enableBaseCodeQl) {
            val codeQlLanguages = propOrEnv("CODEQL_GUARDIAN_LANGUAGES")
                ?.toLanguageSet()
            val queryPackOverrides = loadStringListMapConfig(
                jsonName = "CODEQL_QUERY_PACKS_JSON",
                fileName = "CODEQL_QUERY_PACKS_FILE",
            )
            guardians += CodeQLGuardian(
                codeQlBinary,
                enabledLanguages = codeQlLanguages,
                violationTriage = null,
                queryPackCandidatesByLanguage = CodeQLGuardian.defaultQueryPackCandidates()
                    .withCustomQueryPacks(queryPackOverrides),
            )
        }
        if (enableSensitiveCodeQl) {
            val sensitiveLanguages = (propOrEnv("CODEQL_SENSITIVE_GUARDIAN_LANGUAGES")
                ?: propOrEnv("CODEQL_GUARDIAN_LANGUAGES"))
                ?.toLanguageSet()
            val sensitiveQueryPackOverrides = loadStringListMapConfig(
                jsonName = "CODEQL_SENSITIVE_QUERY_PACKS_JSON",
                fileName = "CODEQL_SENSITIVE_QUERY_PACKS_FILE",
                resourceName = "/codeql-sensitive-query-packs.json",
            )
            val codeQlTriage = if (boolPropOrEnv("ENABLE_CODEQL_SENSITIVE_LLM_TRIAGE", default = true)) {
                LlmViolationTriage(
                    llmClient,
                    rulePromptOverrides = loadStringMapConfig(
                        jsonName = "CODEQL_SENSITIVE_LLM_TRIAGE_PROMPTS_JSON",
                        fileName = "CODEQL_SENSITIVE_LLM_TRIAGE_PROMPTS_FILE",
                        resourceName = "/codeql-sensitive-triage-prompts.json",
                    ),
                )
            } else {
                null
            }
            guardians += CodeQLGuardian(
                codeQlBinary,
                enabledLanguages = sensitiveLanguages,
                violationTriage = codeQlTriage,
                queryPackCandidatesByLanguage = CodeQLGuardian.defaultQueryPackCandidates()
                    .withCustomQueryPacks(sensitiveQueryPackOverrides),
            )
        }
        if (boolPropOrEnv("ENABLE_LLM_GUARDIAN", default = true)) {
            guardians += LlmGuardian(llmClient)
        }
        return guardians
    }

    private fun boolPropOrEnv(name: String, default: Boolean): Boolean {
        val raw = propOrEnv(name)?.trim()?.lowercase() ?: return default
        return when (raw) {
            "1", "true", "yes", "on" -> true
            "0", "false", "no", "off" -> false
            else -> default
        }
    }

    private fun ensureCodeQlAvailable(codeQlBinary: String) {
        try {
            CodeQLRunner(codeQlBinary).getToolVersion()
        } catch (ex: Exception) {
            throw IllegalStateException(
                "CodeQL guardian is enabled, but the configured CODEQL_BIN '$codeQlBinary' is not executable. " +
                    "Set CODEQL_BIN to a working CodeQL binary or disable ENABLE_CODEQL_GUARDIAN.",
                ex,
            )
        }
    }

    private fun createTraceLogger(): WorkflowTraceLogger {
        val path = propOrEnv("PERSISTENT_CHAT_LOG_PATH") ?: return WorkflowTraceLogger.NO_OP
        return PersistentWorkflowTraceLogger(Path.of(path))
    }

    private fun String.toLanguageSet(): Set<String> = split(",")
        .map { it.trim().lowercase() }
        .filter { it.isNotEmpty() }
        .toSet()

    private fun loadStringMapConfig(
        jsonName: String,
        fileName: String,
        resourceName: String? = null,
    ): Map<String, String> {
        val text = propOrEnv(jsonName)?.takeIf { it.isNotBlank() }
            ?: propOrEnv(fileName)?.takeIf { it.isNotBlank() }?.let { path ->
                val configPath = Path.of(path)
                if (!configPath.exists()) {
                    throw IllegalStateException("$fileName points to missing file: $configPath")
                }
                configPath.readText()
            }
            ?: resourceName?.let { loadResourceText(it) }
            ?: return emptyMap()
        val root = Json.parseToJsonElement(text).jsonObject
        return root.mapValues { (_, value) -> value.jsonPrimitive.content }
    }

    private fun loadStringListMapConfig(
        jsonName: String,
        fileName: String,
        resourceName: String? = null,
    ): Map<String, List<String>> {
        val text = propOrEnv(jsonName)?.takeIf { it.isNotBlank() }
            ?: propOrEnv(fileName)?.takeIf { it.isNotBlank() }?.let { path ->
                val configPath = Path.of(path)
                if (!configPath.exists()) {
                    throw IllegalStateException("$fileName points to missing file: $configPath")
                }
                configPath.readText()
            }
            ?: resourceName?.let { loadResourceText(it) }
            ?: return emptyMap()
        val root = Json.parseToJsonElement(text).jsonObject
        return root.mapValues { (_, value) ->
            value.jsonArray.map { it.jsonPrimitive.content }
        }
    }

    private fun loadResourceText(resourceName: String): String? =
        EngineFactory::class.java.getResourceAsStream(resourceName)?.bufferedReader()?.use { it.readText() }

    private fun Map<String, List<String>>.withCustomQueryPacks(
        overrides: Map<String, List<String>>,
    ): Map<String, List<String>> {
        if (overrides.isEmpty()) return this
        val merged = toMutableMap()
        for ((language, customPacks) in overrides) {
            val existing = merged[language].orEmpty()
            merged[language] = (customPacks + existing).distinct()
        }
        return merged
    }

    private fun configuredModelName(): String? = propOrEnv("MODEL") ?: propOrEnv("DEFAULT_MODEL")

    private fun createLlmClientFromEnvironment(): LlmClient {
        val openRouterKey = propOrEnv("OPENROUTER_KEY") ?: propOrEnv("OPENROUTER_API_KEY")
        if (openRouterKey != null && openRouterKey.isBlank()) {
            throw IllegalStateException("OPENROUTER_KEY/OPENROUTER_API_KEY is set but blank")
        }
        if (openRouterKey != null) {
            val timeoutMs = propOrEnv("OPENROUTER_TIMEOUT_MS")
                ?.trim()
                ?.toLongOrNull()
                ?: 120_000L
            return OpenRouterClient(
                openRouterKey,
                configuredModelName() ?: "openai/gpt-oss-20b",
                "securecoder/openapi-bridge",
                propOrEnv("OPENROUTER_PROVIDERS")
                    ?.split(",")
                    ?.map { it.trim() }
                    ?.filter { it.isNotEmpty() }
                    ?: propOrEnv("OPENROUTER_PROVIDER")
                    ?.let { listOf(it.trim()) }
                        ?.filter { it.isNotEmpty() }
                    ?: emptyList(),
                timeoutMs = timeoutMs,
            )
        }
        return OllamaClient(
            model = configuredModelName()
                ?: throw IllegalStateException("Need at least one of OPENROUTER_KEY, OPENROUTER_API_KEY, MODEL, or DEFAULT_MODEL to be set"),
            baseUrl = propOrEnv("OLLAMA_BASE_URL") ?: "http://127.0.0.1:11434",
            keepAlive = propOrEnv("OLLAMA_KEEP_ALIVE") ?: "5m"
        )
    }
}
