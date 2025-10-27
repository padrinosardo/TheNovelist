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
    'QuickSceneDialog'
]
