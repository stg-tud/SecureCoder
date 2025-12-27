plugins {
    id("buildsrc.convention.kotlin-jvm")
    alias(libs.plugins.intellij)
}

repositories {
    mavenCentral()
    intellijPlatform {
        defaultRepositories()
    }
}

dependencies {
    implementation(project(":engine"))
    implementation(project(":guardian:codeql"))
    implementation(project(":enricher:client"))
    intellijPlatform {
        create("IC", "2025.2.5")
    }
}
kotlin {
    jvmToolchain(21)
}

tasks {
    patchPluginXml {
        changeNotes.set("""
            Initial preview.
        """.trimIndent())
    }

    buildPlugin {}

    verifyPlugin {}
}