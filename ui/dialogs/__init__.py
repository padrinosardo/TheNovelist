"""
UI Dialogs - Dialogs for creating/editing entities
"""
from .new_project_dialog import NewProjectDialog
from .timeline_event_dialog import TimelineEventDialog
from .source_detail_dialog import SourceDetailDialog
from .note_detail_dialog import NoteDetailDialog
from .export_dialog import ExportDialog
from .character_ai_assistant_dialog import CharacterAIAssistantDialog
from .ai_settings_dialog import AISettingsDialog
from .upgrade_dialog import UpgradeDialog
from .keyboard_shortcuts_dialog import KeyboardShortcutsDialog
from .insert_table_dialog import InsertTableDialog

__all__ = [
    'NewProjectDialog',
    'TimelineEventDialog',
    'SourceDetailDialog',
    'NoteDetailDialog',
    'ExportDialog',
    'CharacterAIAssistantDialog',
    'AISettingsDialog',
    'UpgradeDialog',
    'KeyboardShortcutsDialog',
    'InsertTableDialog',
]
