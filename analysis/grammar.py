"""
Module for grammatical text analysis
"""
import language_tool_python


class GrammarAnalyzer:
    """Class to manage grammatical analysis"""

    def __init__(self, language='it'):
        """
        Initialize the grammar analyzer

        Args:
            language: Language code (default: 'it' for Italian)
        """
        self.language = language
        self._tool = None

    def _get_tool(self):
        """Lazy loading of LanguageTool"""
        if self._tool is None:
            self._tool = language_tool_python.LanguageToolPublicAPI(self.language)
        return self._tool

    def analyze(self, text, max_errors=30):
        """
        Analyze text to find grammatical errors

        Args:
            text: Text to analyze
            max_errors: Maximum number of errors to return

        Returns:
            dict: Dictionary with 'errors' and 'total_errors'
        """
        try:
            tool = self._get_tool()
            errors = tool.check(text)

            return {
                'errors': errors[:max_errors],
                'total_errors': len(errors),
                'success': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }

    def format_results(self, result, max_displayed=15):
        """
        Format analysis results for display

        Args:
            result: Analysis result
            max_displayed: Maximum number of errors to show

        Returns:
            str: Formatted text for UI
        """
        if not result.get('success'):
            return f"❌ Error: {result.get('error', 'Unknown error')}"

        output = f"📊 Found {result['total_errors']} possible issues\n\n"

        errors = result.get('errors', [])
        if errors:
            output += "═" * 50 + "\n"
            output += "ERRORS AND SUGGESTIONS:\n"
            output += "═" * 50 + "\n\n"

            for i, error in enumerate(errors[:max_displayed], 1):
                output += f"▶ Issue #{i}\n"
                output += f"  {error.message}\n"
                output += f"  Context: ...{error.context}...\n"

                if error.replacements:
                    suggestions = ', '.join(error.replacements[:3])
                    output += f"  💡 Suggestions: {suggestions}\n"

                output += "\n"

            if result['total_errors'] > max_displayed:
                remaining = result['total_errors'] - max_displayed
                output += f"\n... and {remaining} more issues not shown.\n"
        else:
            output += "✅ No errors found! Great job!"

        return output