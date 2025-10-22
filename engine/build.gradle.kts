plugins {
    id("buildsrc.convention.kotlin-jvm")
    alias(libs.plugins.kotlin.serialization)
}

dependencies {
    api(project(":enricher:api"))
    api(project(":guardian:api"))
    implementation(libs.ktor.client.java)
    implementation(libs.ktor.client.content.negotiation)
    implementation(libs.ktor.serialization.json)
}
