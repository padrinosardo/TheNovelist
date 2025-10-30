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

__all__ = [
    'NewProjectDialog',
    'TimelineEventDialog',
    'SourceDetailDialog',
    'NoteDetailDialog',
    'ExportDialog',
    'CharacterAIAssistantDialog',
    'AISettingsDialog',
]
