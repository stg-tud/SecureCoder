plugins {
    id("buildsrc.convention.kotlin-jvm")
    alias(libs.plugins.kotlin.serialization)
}

base {
    archivesName.set("guardian-api")
}

dependencies {
    api(libs.kotlinx.serialization.json)
    api(project(":filesystem"))
}
