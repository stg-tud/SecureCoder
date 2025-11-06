package de.tuda.stg.securecoder.plugin.engine

import com.intellij.openapi.application.readAction
import com.intellij.openapi.vfs.VfsUtilCore
import com.intellij.openapi.vfs.VirtualFile
import com.intellij.openapi.diagnostic.Logger
import com.intellij.openapi.project.Project
import com.intellij.openapi.roots.ProjectFileIndex
import com.intellij.openapi.roots.ProjectRootManager
import com.intellij.openapi.vfs.VirtualFileManager
import de.tuda.stg.securecoder.filesystem.FileSystem
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import java.io.IOException

class IntelliJProjectFileSystem(
    private val project: Project,
    private val maxFileSize: Long = 5L * 1024 * 1024
) : FileSystem {
    private val log = Logger.getInstance(IntelliJProjectFileSystem::class.java)

    override fun allFiles(): Flow<FileSystem.File> = flow {
        val contentRoots = ProjectRootManager.getInstance(project).contentRoots
        val index = ProjectFileIndex.getInstance(project)
        val stack = ArrayDeque<VirtualFile>()
        contentRoots.forEach { root -> stack.addLast(root) }
        while (stack.isNotEmpty()) {
            val step = readAction {
                val virtualFile = stack.removeLast()
                if (index.isExcluded(virtualFile) || index.isUnderIgnored(virtualFile)) return@readAction Unit
                if (virtualFile.isDirectory) {
                    virtualFile.children.forEach { child -> stack.addLast(child) }
                } else {
                    val ok = !virtualFile.fileType.isBinary && virtualFile.length <= maxFileSize
                    if (ok) ProjectFile(virtualFile, virtualFile.url) else Unit
                }
            }
            if (step !is ProjectFile) continue
            emit(step)
        }
    }

    override fun getFile(name: String): FileSystem.File? {
        val vf = VirtualFileManager.getInstance().findFileByUrl(name) ?: return null
        return ProjectFile(vf, name)
    }

    private inner class ProjectFile(
        val vf: VirtualFile,
        val uniqueName: String
    ) : FileSystem.File {
        override fun name(): String = uniqueName

        override suspend fun content(): String = readAction {
            try {
                VfsUtilCore.loadText(vf)
            } catch (e: IOException) {
                log.warn("Could not load text for $uniqueName", e)
                ""
            }
        }
    }
}
