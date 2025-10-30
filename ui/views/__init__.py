"""
UI Views - List and detail views for dynamic containers
"""
from .location_list_view import LocationListView
from .location_detail_view import LocationDetailView
from .research_list_view import ResearchListView
from .research_detail_view import ResearchDetailView
from .timeline_view import TimelineView
from .sources_list_view import SourcesListView
from .notes_list_view import NotesListView
from .project_info_detail_view import ProjectInfoDetailView

__all__ = [
    'LocationListView',
    'LocationDetailView',
    'ResearchListView',
    'ResearchDetailView',
    'TimelineView',
    'SourcesListView',
    'NotesListView',
    'ProjectInfoDetailView',
]
