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

__all__ = [
    'MenuBar',
    'ProjectTree',
    'WorkspaceContainer',
    'ManuscriptView',
    'CharactersListView',
    'CharacterDetailView',
    'ImageGalleryWidget'
]
