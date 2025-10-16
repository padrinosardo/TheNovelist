"""
User interface module
"""
from .main_window import WritingAssistant
from .pannels import ResultsPanel, TextEditor
from .styles import Colori, Stili

__all__ = [
    'WritingAssistant',
    'ResultsPanel',
    'TextEditor',
    'Colori',
    'Stili'
]