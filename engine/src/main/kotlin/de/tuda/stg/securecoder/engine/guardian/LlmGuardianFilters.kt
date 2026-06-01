package de.tuda.stg.securecoder.engine.guardian

import de.tuda.stg.securecoder.guardian.AnalyzeRequest

internal suspend fun LlmAnalyzeResponse.filteredForRequest(req: AnalyzeRequest): LlmAnalyzeResponse =
    copy(findings = findings.filter { it.isGroundedIn(req) })

private suspend fun LlmAnalyzeResponse.Finding.isGroundedIn(req: AnalyzeRequest): Boolean {
    val text = listOf(shortName, description).joinToString(" ").lowercase()
    if (containsSpeculativeLanguage(text)) return false
    val fileContent = req.files.firstOrNull { it.name == fileName }?.content
        ?: req.fileSystem.getFile(fileName)?.content()
        ?: return true
    val code = fileContent.lowercase()
    return when {
        text.contains("path traversal") || text.contains("path injection") || text.contains("zip slip") || text.contains("tar slip") ->
            hasAnyToken(code, FILESYSTEM_TOKENS)
        text.contains("ssrf") || text.contains("server-side request forgery") || text.contains("open redirect") || text.contains("url redirection") ->
            hasAnyToken(code, URL_REDIRECT_TOKENS)
        text.contains("command injection") || text.contains("shell injection") ->
            hasAnyToken(code, COMMAND_TOKENS)
        text.contains("xpath injection") ->
            hasAnyToken(code, XPATH_TOKENS)
        text.contains("ldap injection") ->
            hasAnyToken(code, LDAP_TOKENS)
        text.contains("xxe") || text.contains("xml bomb") ->
            hasAnyToken(code, XML_TOKENS)
        text.contains("log injection") ->
            hasAnyToken(code, LOG_TOKENS)
        else -> true
    }
}

private fun hasAnyToken(code: String, tokens: Set<String>): Boolean = tokens.any { it in code }

private fun containsSpeculativeLanguage(text: String): Boolean =
    SPECULATIVE_PATTERNS.any { it in text }

private val SPECULATIVE_PATTERNS = setOf(
    "if later used",
    "if this returned value is later used",
    "if the returned value is later used",
    "in a context where",
    "by a downstream",
    "downstream redirect mechanism",
    "downstream consumer",
    "unseen callers",
    "might be interpreted",
    "could potentially",
    "could lead to",
    "would be advisable",
)

private val FILESYSTEM_TOKENS = setOf(
    "open(",
    "os.path",
    "pathlib",
    "filepath.",
    "tarfile",
    "zipfile",
    "extractall",
    "extract(",
    "readfile(",
    "writefile(",
    "fileinputstream",
    "fstream",
    "ifstream",
    "ofstream",
    "fs.readfile",
    "fs.writefile",
    "new file(",
)

private val URL_REDIRECT_TOKENS = setOf(
    "urlparse",
    "location",
    "redirect(",
    "httpresponseredirect",
    "response.redirect",
    "sendredirect",
    "window.location",
    "fetch(",
    "requests.",
    "urllib",
    "http://",
    "https://",
    "net/http",
    "url.",
)

private val COMMAND_TOKENS = setOf(
    "subprocess",
    "os.system",
    "runtime.getruntime().exec",
    "processbuilder",
    "exec(",
    "spawn(",
    "popen(",
    "sh -c",
    "/bin/sh",
)

private val XPATH_TOKENS = setOf(
    "xpath",
    "etree",
    "xmldocument",
    "selectsinglenode",
    "xpathfactory",
)

private val LDAP_TOKENS = setOf(
    "ldap",
    "searchfilter",
    "dircontext",
    "ldapsearch",
)

private val XML_TOKENS = setOf(
    "xml",
    "etree",
    "minidom",
    "documentbuilder",
    "saxparser",
    "lxml",
)

private val LOG_TOKENS = setOf(
    "logging.",
    "logger.",
    "log.",
    "console.log",
    "print(",
)
