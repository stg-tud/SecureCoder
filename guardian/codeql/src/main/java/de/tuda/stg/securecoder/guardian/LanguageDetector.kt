package de.tuda.stg.securecoder.guardian

import java.io.File

fun detectLanguages(files: List<File>): Set<String> {
    val extensions = files.map { it.name.substringAfterLast('.', missingDelimiterValue = "").lowercase() }
    return extensions.mapNotNull { languageFromExtension(it) }.toSet()
}

private fun languageFromExtension(ext: String): String? = when (ext.lowercase()) {
    "kt", "kts", "java" -> "java"
    "js", "jsx", "ts", "tsx" -> "javascript"
    "py" -> "python"
    "rb" -> "ruby"
    "go" -> "go"
    "swift" -> "swift"
    "c", "cc", "cpp", "cxx", "h", "hh", "hpp", "hxx" -> "cpp"
    "cs" -> "csharp"
    else -> null
}
