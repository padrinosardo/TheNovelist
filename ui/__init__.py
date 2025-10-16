"""
User interface module
"""
from .finestra_principale import WritingAssistant
from .pannelli import ResultsPanel, TextEditor
from .stili import Colori, Stili

__all__ = [
    'WritingAssistant',
    'ResultsPanel',
    'TextEditor',
    'Colori',
    'Stili'
]