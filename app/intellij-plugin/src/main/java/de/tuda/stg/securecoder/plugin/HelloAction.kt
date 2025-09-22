package de.tuda.stg.securecoder.plugin

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.ui.Messages

class HelloAction : AnAction("Say Hello") {
    override fun actionPerformed(e: AnActionEvent) {
        Messages.showInfoMessage("Hello from SecureCoder plugin!", "SecureCoder")
    }
}
