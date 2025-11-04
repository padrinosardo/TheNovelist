"""
UI Components for TheNovelist
"""
from .menu_bar import MenuBar
from .project_tree import ProjectTree
from .workspace_container import WorkspaceContainer
from .manuscript_view import ManuscriptView
from .characters_list_view import CharactersListView
from .character_detail_view import CharacterDetailView
from .image_gallery import ImageGalleryWidget
from .statistics_dashboard import StatisticsDashboard
from .scene_management_dialogs import (ChapterDialog, SceneDialog,
                                       show_delete_chapter_confirmation,
                                       show_delete_scene_confirmation)
from .quick_scene_dialog import QuickSceneDialog
from .chapters_preview_widget import ChaptersPreviewWidget
from .scenes_preview_widget import ScenesPreviewWidget
from .chapter_detail_widget import ChapterDetailWidget
from .worldbuilding_list_view import WorldbuildingListView
from .worldbuilding_detail_view import WorldbuildingDetailView
from .spell_check_highlighter import SpellCheckHighlighter
from .spell_check_text_edit import SpellCheckTextEdit
from .ai_config_widget import AIConfigWidget

__all__ = [
    'MenuBar',
    'ProjectTree',
    'WorkspaceContainer',
    'ManuscriptView',
    'CharactersListView',
    'CharacterDetailView',
    'ImageGalleryWidget',
    'StatisticsDashboard',
    'ChapterDialog',
    'SceneDialog',
    'show_delete_chapter_confirmation',
    'show_delete_scene_confirmation',
    'QuickSceneDialog',
    'ChaptersPreviewWidget',
    'ScenesPreviewWidget',
    'ChapterDetailWidget',
    'WorldbuildingListView',
    'WorldbuildingDetailView',
    'SpellCheckHighlighter',
    'SpellCheckTextEdit',
    'AIConfigWidget'
]
