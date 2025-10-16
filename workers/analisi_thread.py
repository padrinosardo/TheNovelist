"""
Worker thread to execute analysis in background
"""
from PySide6.QtCore import QThread, Signal

from analisi.grammatica import GrammarAnalyzer
from analisi.ripetizioni import RepetitionAnalyzer
from analisi.stile import StyleAnalyzer


class AnalysisThread(QThread):
    """
    Thread to execute heavy analysis without blocking the UI
    """

    # Signal emitted when analysis is completed
    finished = Signal(dict)

    # Supported analysis types
    TYPE_GRAMMAR = "grammar"
    TYPE_REPETITIONS = "repetitions"
    TYPE_STYLE = "style"

    def __init__(self, text, analysis_type):
        """
        Initialize the analysis thread

        Args:
            text: Text to analyze
            analysis_type: Type of analysis (grammar, repetitions, style)
        """
        super().__init__()
        self.text = text
        self.analysis_type = analysis_type

        # Initialize analyzers (lazy loading)
        self._grammar_analyzer = None
        self._repetitions_analyzer = None
        self._style_analyzer = None

    def run(self):
        """
        Execute the requested analysis
        This method is executed in a separate thread
        """
        result = {}

        try:
            if self.analysis_type == self.TYPE_GRAMMAR:
                result = self._execute_grammar_analysis()
            elif self.analysis_type == self.TYPE_REPETITIONS:
                result = self._execute_repetitions_analysis()
            elif self.analysis_type == self.TYPE_STYLE:
                result = self._execute_style_analysis()
            else:
                result = {
                    'error': f"Unknown analysis type: {self.analysis_type}",
                    'success': False
                }
        except Exception as e:
            result = {
                'error': f"Error during analysis: {str(e)}",
                'success': False
            }

        # Emit signal with results
        self.finished.emit(result)

    def _execute_grammar_analysis(self):
        """Execute grammar analysis"""
        if self._grammar_analyzer is None:
            self._grammar_analyzer = GrammarAnalyzer()

        return self._grammar_analyzer.analyze(self.text)

    def _execute_repetitions_analysis(self):
        """Execute repetitions analysis"""
        if self._repetitions_analyzer is None:
            self._repetitions_analyzer = RepetitionAnalyzer()

        return self._repetitions_analyzer.analyze(self.text)

    def _execute_style_analysis(self):
        """Execute style analysis"""
        if self._style_analyzer is None:
            self._style_analyzer = StyleAnalyzer()

        return self._style_analyzer.analyze(self.text)