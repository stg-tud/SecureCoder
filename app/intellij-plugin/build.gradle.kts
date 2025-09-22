plugins {
    id("buildsrc.convention.kotlin-jvm")
    alias(libs.plugins.intellij)
}

intellij {
    version.set("2024.2")
    type.set("IC")
    plugins.set(listOf()) // java
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