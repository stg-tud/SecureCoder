package de.tuda.stg.securecoder.plugin.engine.event

import com.intellij.icons.AllIcons
import de.tuda.stg.securecoder.engine.file.edit.Changes
import de.tuda.stg.securecoder.engine.stream.EventIcon
import javax.swing.Icon

sealed interface UiStreamEvent {
    data class Message(
        val title: String,
        val description: String,
        val icon: Icon,
        val debugText: String? = null
    ) : UiStreamEvent

    data class EditFiles(val changes: Changes) : UiStreamEvent
}

fun EventIcon.toIntellijIcon(): Icon = when (this) {
    EventIcon.Info -> AllIcons.General.Information
    EventIcon.Warning -> AllIcons.General.Warning
    EventIcon.Error -> AllIcons.General.Error
}
