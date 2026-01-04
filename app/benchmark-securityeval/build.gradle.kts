plugins {
    id("buildsrc.convention.kotlin-jvm")
    application
    alias(libs.plugins.kotlin.serialization)
}

dependencies {
    implementation(project(":engine:agent"))
    implementation(project(":enricher:client"))
    implementation(libs.kotlinx.coroutines.core)
}
application {
    mainClass.set("de.tuda.stg.securecoder.benchmark.MainKt")
}
