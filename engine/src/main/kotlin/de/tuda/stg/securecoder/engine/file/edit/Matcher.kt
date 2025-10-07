package de.tuda.stg.securecoder.engine.file.edit

import de.tuda.stg.securecoder.engine.file.edit.Matcher.MatchResult.Error
import de.tuda.stg.securecoder.engine.file.edit.Matcher.MatchResult.Success

interface Matcher {
    sealed interface MatchResult {
        sealed interface Error : MatchResult {
            object ReplaceOnEmpty : Error
            object NoMatch : Error
            data class MultipleMatch (val matches: List<Int>) : Error
        }
        sealed interface Success : MatchResult {
            object Append : Success
            class Match (val start: Int, val end: Int) : Success
        }
    }

    fun match(text: String, search: Changes.SearchedText): MatchResult

    object RootMatcher : Matcher {
        override fun match(text: String, search: Changes.SearchedText): MatchResult {
            if (search.isAppend()) {
                return Success.Append
            }
            if (text.isEmpty()) {
                return Error.ReplaceOnEmpty
            }
            val matchers = listOf(IndexOfMatcher, TrimmedLinesMatcher)
            matchers.forEach {
                val result = it.match(text, search)
                if (result is Success) return result
            }
            return Error.NoMatch
        }
    }

    object IndexOfMatcher : Matcher {
        override fun match(
            text: String,
            search: Changes.SearchedText
        ): MatchResult {
            val idx = text.indexesOf(search.text)
            return when (idx.size) {
                1 -> Success.Match(idx.first(), idx.first() + search.text.length)
                0 -> Error.NoMatch
                else -> Error.MultipleMatch(idx)
            }
        }

        private fun String.indexesOf(needle: String): List<Int> {
            require(needle.isNotEmpty()) { "needle must not be empty" }
            val result = mutableListOf<Int>()
            var start = 0
            while (true) {
                val i = indexOf(needle, start)
                if (i < 0) break
                result += i
                start = i + 1
            }
            return result
        }
    }

    object TrimmedLinesMatcher : Matcher {
        override fun match(text: String, search: Changes.SearchedText): MatchResult {
            val searchedTrimmed = splitToLinesAndTrimLast(search.text).map { it.trim() }
            val documentLines = text.split("\n")
            val documentLinesTrimmed = documentLines.map { it.trim() }

            if (searchedTrimmed.isEmpty() || searchedTrimmed.size > documentLinesTrimmed.size) return Error.NoMatch

            val matchedIndices = (0..documentLinesTrimmed.size - searchedTrimmed.size)
                .filter { i -> documentLinesTrimmed.subList(i, i + searchedTrimmed.size) == searchedTrimmed }

            if (matchedIndices.isEmpty()) return Error.NoMatch
            if (matchedIndices.size > 1) return Error.MultipleMatch(matchedIndices)

            val firstLine = matchedIndices.first()
            val lineCount = searchedTrimmed.size

            val lineStarts = IntArray(documentLines.size + 1)
            for (i in documentLines.indices) {
                lineStarts[i + 1] = lineStarts[i] + documentLines[i].length + 1
            }

            val startOffset = lineStarts[firstLine]
            val endOffset   = lineStarts[firstLine + lineCount]

            return Success.Match(startOffset, endOffset)
        }

        private fun splitToLinesAndTrimLast(text: String): List<String> {
            val lines = text.split("\n")
            if (lines.isEmpty()) return emptyList()
            val lastNonBlankIndex = lines.indexOfLast { it.trim().isNotEmpty() }
            return if (lastNonBlankIndex >= 0) lines.take(lastNonBlankIndex + 1) else emptyList()
        }
    }
}
