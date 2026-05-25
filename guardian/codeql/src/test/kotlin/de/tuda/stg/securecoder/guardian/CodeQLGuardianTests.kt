package de.tuda.stg.securecoder.guardian

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class CodeQLGuardianTests {
    @Test
    fun python_guardian_uses_code_scanning_suite_first() {
        val guardian = CodeQLGuardian()

        assertEquals(
            "codeql/python-queries:codeql-suites/python-code-scanning.qls",
            guardian.queryPackForLanguage("python"),
        )
    }

    @Test
    fun guardian_uses_stable_primary_suites_for_supported_languages() {
        val guardian = CodeQLGuardian()

        assertEquals(
            "codeql/javascript-queries:codeql-suites/javascript-code-scanning.qls",
            guardian.queryPackForLanguage("javascript"),
        )
        assertEquals(
            "codeql/java-queries:codeql-suites/java-security-extended.qls",
            guardian.queryPackForLanguage("java"),
        )
        assertEquals(
            "codeql/cpp-queries:codeql-suites/cpp-code-scanning.qls",
            guardian.queryPackForLanguage("cpp"),
        )
        assertEquals(
            "codeql/csharp-queries:codeql-suites/csharp-security-extended.qls",
            guardian.queryPackForLanguage("csharp"),
        )
        assertEquals(
            "codeql/ruby-queries:codeql-suites/ruby-security-extended.qls",
            guardian.queryPackForLanguage("ruby"),
        )
        assertEquals(
            "codeql/go-queries:codeql-suites/go-code-scanning.qls",
            guardian.queryPackForLanguage("go"),
        )
        assertEquals(
            "codeql/swift-queries:codeql-suites/swift-security-extended.qls",
            guardian.queryPackForLanguage("swift"),
        )
    }

    @Test
    fun guardian_exposes_fallback_query_packs_for_crash_prone_languages() {
        val guardian = CodeQLGuardian()

        assertEquals(
            listOf(
                "codeql/python-queries:codeql-suites/python-code-scanning.qls",
                "codeql/python-queries:codeql-suites/python-security-extended.qls",
            ),
            guardian.queryPacksForLanguage("python"),
        )
        assertEquals(
            listOf(
                "codeql/javascript-queries:codeql-suites/javascript-code-scanning.qls",
                "codeql/javascript-queries:codeql-suites/javascript-security-extended.qls",
            ),
            guardian.queryPacksForLanguage("javascript"),
        )
        assertEquals(
            listOf(
                "codeql/go-queries:codeql-suites/go-code-scanning.qls",
                "codeql/go-queries:codeql-suites/go-security-extended.qls",
            ),
            guardian.queryPacksForLanguage("go"),
        )
        assertEquals(
            listOf(
                "codeql/cpp-queries:codeql-suites/cpp-code-scanning.qls",
                "codeql/cpp-queries:codeql-suites/cpp-security-extended.qls",
            ),
            guardian.queryPacksForLanguage("cpp"),
        )
    }

    @Test
    fun guardian_detects_snippet_build_commands_for_benchmark_languages() {
        val guardian = CodeQLGuardian()
        val root = java.nio.file.Files.createTempDirectory("codeql-guardian-test")
        try {
            assertEquals("/usr/bin/true", guardian.detectBuildCommand("python", root))
            val jsBuild = guardian.detectBuildCommand("javascript", root)
            assertTrue(jsBuild?.endsWith(".securecoder-codeql-js-build.sh") == true)
            assertTrue(java.nio.file.Files.readString(java.nio.file.Path.of(jsBuild)).contains("node --check"))
            val goBuild = guardian.detectBuildCommand("go", root)
            assertTrue(goBuild?.endsWith(".securecoder-codeql-go-build.sh") == true)
            assertTrue(java.nio.file.Files.readString(java.nio.file.Path.of(goBuild)).contains("go build"))
            val cppBuild = guardian.detectBuildCommand("cpp", root)
            assertTrue(cppBuild?.endsWith(".securecoder-codeql-cpp-build.sh") == true)
            val cppScript = java.nio.file.Files.readString(java.nio.file.Path.of(cppBuild))
            assertTrue(cppScript.contains("clang -std=c11 -c"))
            assertTrue(cppScript.contains("clang++ -std=c++17 -c"))
        } finally {
            root.toFile().deleteRecursively()
        }
    }

    @Test
    fun guardian_accepts_custom_query_pack_priority() {
        val guardian = CodeQLGuardian(
            queryPackCandidatesByLanguage = CodeQLGuardian.defaultQueryPackCandidates() + mapOf(
                "python" to listOf(
                    "/tmp/custom-python-sensitive.qls",
                    "codeql/python-queries:codeql-suites/python-code-scanning.qls",
                ),
            ),
        )

        assertEquals("/tmp/custom-python-sensitive.qls", guardian.queryPackForLanguage("python"))
        assertEquals(
            listOf(
                "/tmp/custom-python-sensitive.qls",
                "codeql/python-queries:codeql-suites/python-code-scanning.qls",
            ),
            guardian.queryPacksForLanguage("python"),
        )
    }

    @Test
    fun guardian_treats_known_codeql_internal_npe_as_recoverable() {
        val guardian = CodeQLGuardian()
        val method = guardian.javaClass.getDeclaredMethod("isRecoverableToolFailure", String::class.java)
        method.isAccessible = true
        val message = """
            Oops! A fatal internal error occurred. Details:
            java.lang.NullPointerException
                at com.semmle.inmemory.scheduler.EvaluationSchedule.allocateDfsSeqnums(EvaluationSchedule.java:371)
                at com.semmle.inmemory.scheduler.QueryEvaluator.setPriorityIfNecessary(QueryEvaluator.java:102)
        """.trimIndent()
        val result = method.invoke(guardian, message) as Boolean
        assertTrue(result)
    }
}
