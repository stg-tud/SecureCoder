plugins {
    id("buildsrc.convention.kotlin-jvm")
    alias(libs.plugins.kotlin.serialization)
}

dependencies {
    api(libs.kotlinx.serialization.json)
    api(":filesystem")
}
