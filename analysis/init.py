"""
Modulo per le analysis linguistiche e AI
"""
from .grammar import AnalizzatoreGrammatica
from .repetition import AnalizzatoreRipetizioni
from .style import AnalizzatoreStile

__all__ = [
    'AnalizzatoreGrammatica',
    'AnalizzatoreRipetizioni',
    'AnalizzatoreStile'
]