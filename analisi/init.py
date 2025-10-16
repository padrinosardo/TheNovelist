"""
Modulo per le analisi linguistiche e AI
"""
from .grammatica import AnalizzatoreGrammatica
from .ripetizioni import AnalizzatoreRipetizioni
from .stile import AnalizzatoreStile

__all__ = [
    'AnalizzatoreGrammatica',
    'AnalizzatoreRipetizioni',
    'AnalizzatoreStile'
]