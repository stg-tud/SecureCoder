package de.tuda.stg.securecoder.filesystem

import java.nio.file.Files
import java.nio.file.Path
import java.nio.file.StandardOpenOption
import java.nio.charset.StandardCharsets
import kotlinx.coroutines.flow.toList

object FileSystemToDiskWriter {
    suspend fun writeFileSystemToTemp(fs: FileSystem): Path {
        val tmpDir = Files.createTempDirectory("vfs-")
        val files = fs.allFiles().toList()
        if (files.isEmpty()) return tmpDir
        val nameComponents: List<List<String>> = files.map { f ->
            val p = Path.of(f.name()).normalize()
            p.iterator().asSequence().map { it.toString() }.toList()
        }
        val commonPrefix: List<String> = longestCommonPrefix(nameComponents)
        for (file in files) {
            val p = Path.of(file.name()).normalize()
            val comps = p.iterator().asSequence().map { it.toString() }.toList()
            val relComps = comps.drop(commonPrefix.size)
            val target = relComps.fold(tmpDir) { acc, segment -> acc.resolve(segment) }

            val parent = target.parent
            if (parent != null) Files.createDirectories(parent)

            val bytes = file.content().toByteArray(StandardCharsets.UTF_8)
            Files.write(
                target,
                bytes,
                StandardOpenOption.CREATE,
                StandardOpenOption.TRUNCATE_EXISTING,
                StandardOpenOption.WRITE
            )
        }
        return tmpDir
    }

    private fun longestCommonPrefix(paths: List<List<String>>): List<String> {
        if (paths.isEmpty()) return emptyList()
        val shortest = paths.minBy { it.size }
        val prefix = mutableListOf<String>()

        for (i in shortest.indices) {
            val candidate = shortest[i]
            if (paths.all { it.size > i && it[i] == candidate }) {
                prefix += candidate
            } else {
                break
            }
        }
        return prefix
    }
}
