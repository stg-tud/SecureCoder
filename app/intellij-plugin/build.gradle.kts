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
        create("IC", "2024.2")
    }
}
configurations.all {
    exclude(group = "org.jetbrains.kotlinx", module = "kotlinx-coroutines-core")
    exclude(group = "org.jetbrains.kotlinx", module = "kotlinx-coroutines-jdk8")
}

tasks {
    patchPluginXml {
        changeNotes.set("""
            Initial preview.
        """.trimIndent())
    }

    runIde {
        // ideDir.set(file(System.getProperty("user.home") + "/.cache/JetBrains/Toolbox/apps/IDEA-C/ch-0/242.xxxxx"))
    }

    buildPlugin {}

    verifyPlugin {}
}