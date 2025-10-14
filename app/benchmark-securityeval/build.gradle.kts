plugins {
    id("buildsrc.convention.kotlin-jvm")
    application
    alias(libs.plugins.kotlin.serialization)
}

dependencies {
    implementation(project(":engine"))
    implementation(project(":enricher:client"))
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.10.2")
}
application {
    mainClass.set("de.tuda.stg.securecoder.benchmark.MainKt")
}
