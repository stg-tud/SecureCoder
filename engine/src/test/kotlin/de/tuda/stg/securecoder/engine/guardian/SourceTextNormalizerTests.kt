package de.tuda.stg.securecoder.engine.guardian

import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class SourceTextNormalizerTests {
    @Test
    fun decodes_escaped_source_blob_for_c_like_files() {
        val escaped =
            "#include <stdio.h>\\n#include <stdlib.h>\\n\\nint main(void) {\\n    return 0;\\n}\\n"

        val normalized = SourceTextNormalizer.normalize("sample.c", escaped)

        assertTrue(normalized.contains("#include <stdio.h>\n#include <stdlib.h>"))
        assertTrue(normalized.contains("int main(void) {\n    return 0;\n}"))
    }

    @Test
    fun keeps_normal_multiline_source_unchanged() {
        val source = """
            package main

            import "fmt"

            func main() {
                fmt.Println("ok")
            }
        """.trimIndent()

        val normalized = SourceTextNormalizer.normalize("main.go", source)

        assertEquals(source, normalized)
    }

    @Test
    fun trims_transport_artifact_suffix_from_source() {
        val corrupted = """
            #include <string>
            bool ok() {
                return true;
            }"}]}{#include <string>
            bool ok() {
                return true;
            }
        """.trimIndent()

        val normalized = SourceTextNormalizer.normalize("sample.cpp", corrupted)

        assertEquals(
            """
            #include <string>
            bool ok() {
                return true;
            }
            """.trimIndent(),
            normalized
        )
    }

    @Test
    fun detects_placeholder_and_escaped_output_problems() {
        val placeholderProblems = SourceTextNormalizer.detectProblems("index.js", "...")
        val retryProblems = SourceTextNormalizer.detectProblems(
            "index.py",
            "I failed to generate valid code. Retries exceeded."
        )
        val internalErrorProblems = SourceTextNormalizer.detectProblems(
            "index.go",
            "I encountered an internal generation error."
        )
        val escapedProblems = SourceTextNormalizer.detectProblems(
            "index.js",
            "const x = 1;\\nfunction main() {\\n  return x;\\n}\\nmodule.exports = main;\\n"
        )
        val transportProblems = SourceTextNormalizer.detectProblems(
            "sample.cpp",
            "#include <string>\\nbool ok(){return true;} }]}{#include <string>"
        )

        assertTrue(placeholderProblems.any { it.ruleId == "source-placeholder-output" })
        assertTrue(retryProblems.any { it.ruleId == "source-failure-output" })
        assertTrue(internalErrorProblems.any { it.ruleId == "source-failure-output" })
        assertTrue(escapedProblems.any { it.ruleId == "source-escaped-output" })
        assertTrue(transportProblems.any { it.ruleId == "source-transport-artifact" })
    }
}
