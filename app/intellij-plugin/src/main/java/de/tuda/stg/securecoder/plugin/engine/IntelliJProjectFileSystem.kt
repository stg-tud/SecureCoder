package de.tuda.stg.securecoder.plugin.engine

import com.intellij.openapi.vfs.VfsUtilCore
import com.intellij.openapi.vfs.VirtualFile
import com.intellij.openapi.diagnostic.Logger
import com.intellij.openapi.project.Project
import com.intellij.openapi.roots.ProjectRootManager
import com.intellij.openapi.vfs.VirtualFileManager
import de.tuda.stg.securecoder.engine.file.FileSystem
import java.io.IOException

class IntelliJProjectFileSystem(
    private val project: Project
) : FileSystem {
    private val log = Logger.getInstance(IntelliJProjectFileSystem::class.java)

    override fun iterateAllFiles(): Iterable<FileSystem.File> = sequence {
        val contentRoots = ProjectRootManager.getInstance(project).contentRoots
        val stack = ArrayDeque<VirtualFile>()
        contentRoots.forEach { root -> stack.addLast(root) }
        while (stack.isNotEmpty()) {
            val file = stack.removeLast()

            if (file.isDirectory) {
                for (child in file.children) {
                    stack.addLast(child)
                }
                continue
            } else if (!file.fileType.isBinary && file.length <= 5L * 1024 * 1024) {
                yield(ProjectFile(file, file.url))
            }
        }
    }.asIterable()

    override fun getFile(name: String): FileSystem.File? {
        val vf = VirtualFileManager.getInstance().findFileByUrl(name) ?: return null
        return ProjectFile(vf, name)
    }

    private inner class ProjectFile(
        val vf: VirtualFile,
        val uniqueName: String
    ) : FileSystem.File {
        override fun name(): String = uniqueName

        override fun content(): String {
            return try {
                VfsUtilCore.loadText(vf)
            } catch (e: IOException) {
                log.warn("Could not load text for $uniqueName", e)
                ""
            }
        }
    }
}
