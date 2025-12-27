plugins {
    id("buildsrc.convention.kotlin-jvm")
}

dependencies {
    implementation(project(":guardian:api"))
    implementation(libs.kotlinx.serialization.json)
}
