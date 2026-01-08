plugins {
    id("buildsrc.convention.kotlin-jvm")
    alias(libs.plugins.kotlin.serialization)
    application
}

dependencies {
    api(project(":engine"))
    api(project(":guardian:codeql"))
    implementation(libs.ktor.server.core)
    implementation(libs.ktor.server.netty)
    implementation(libs.ktor.serialization.json)
    implementation(libs.ktor.server.content.negotiation)
    runtimeOnly(libs.logback)
}

application {
    mainClass.set("de.tuda.stg.securecoder.openaibridge.MainKt")
}
