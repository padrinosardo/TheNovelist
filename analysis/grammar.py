"""
Module for grammatical text analysis - SIMPLE VERSION
"""
from analysis.grammar_rules import SimpleGrammarChecker


class GrammarAnalyzer:
    """Class to manage grammatical analysis"""

    def __init__(self):
        """Initialize the grammar analyzer"""
        self.checker = SimpleGrammarChecker()

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
            errors = self.checker.check(text)

            # Group by category
            by_category = {}
            for error in errors:
                cat = error['category']
                by_category[cat] = by_category.get(cat, 0) + 1

            return {
                'errors': errors[:max_errors],
                'total_errors': len(errors),
                'by_category': by_category,
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

        output = f"📊 Found {result['total_errors']} possible issues\n"

        # Show category breakdown
        if 'by_category' in result and result['by_category']:
            output += "\n📋 By category:\n"
            category_names = {
                'accent': 'Accenti',
                'apostrophe': 'Apostrofi',
                'preposition': 'Preposizioni',
                'h_verb': 'Verbo avere (H)',
                'verb': 'Verbi',
                'punctuation': 'Punteggiatura',
                'double': 'Doppie consonanti',
                'custom': 'Altro'
            }
            for cat, count in result['by_category'].items():
                cat_name = category_names.get(cat, cat)
                output += f"  • {cat_name}: {count}\n"

        output += "\n"

        errors = result.get('errors', [])
        if errors:
            output += "═" * 50 + "\n"
            output += "ERRORS AND SUGGESTIONS:\n"
            output += "═" * 50 + "\n\n"

            for i, error in enumerate(errors[:max_displayed], 1):
                # Category icon
                category_icons = {
                    'accent': '📝',
                    'apostrophe': '✏️',
                    'preposition': '🔗',
                    'h_verb': '🅷',
                    'verb': '⚡',
                    'punctuation': '📍',
                    'double': '✖️✖️',
                    'custom': '❓'
                }
                icon = category_icons.get(error.get('category', 'custom'), '📝')

                output += f"{icon} Issue #{i}\n"
                output += f"  {error['message']}\n"
                output += f"  Found: '{error['original']}'\n"
                output += f"  💡 Suggestion: '{error['suggestion']}'\n"
                output += f"  Context: {error['context']}\n"
                output += "\n"

            if result['total_errors'] > max_displayed:
                remaining = result['total_errors'] - max_displayed
                output += f"\n... and {remaining} more issues not shown.\n"
        else:
            output += "✅ No errors found! Great job!"

        return output