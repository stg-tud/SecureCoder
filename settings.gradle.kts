dependencyResolutionManagement {
    @Suppress("UnstableApiUsage")
    repositories {
        mavenCentral()
    }
}

plugins {
    id("org.gradle.toolchains.foojay-resolver-convention") version "0.8.0"
}

rootProject.name = "securecoder"
include("app:intellij-plugin")
include("enricher:api")
include("enricher:client")
include("app:placeholder-enricher")
include("engine")
include("app:benchmark-securityeval")
include("guardian:api")
include("guardian:codeql")
include("filesystem")
include("app:openai-bridge")
include("llm-client")
include("engine:agent")