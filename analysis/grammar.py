"""
Module for grammatical text analysis - MULTI-LANGUAGE VERSION
"""
from analysis.grammar_rules import SimpleGrammarChecker
from analysis.nlp_manager import nlp_manager
from utils.logger import AppLogger
from typing import Optional


class GrammarAnalyzer:
    """Class to manage grammatical analysis with multi-language support"""

    def __init__(self, language: str = 'it'):
        """
        Initialize the grammar analyzer

        Args:
            language: Language code ('it', 'en', 'es', 'fr', 'de')
        """
        self.language = language
        self.checker = SimpleGrammarChecker()  # Fallback per italiano

        # Imposta lingua nel manager
        nlp_manager.set_language(language)

        AppLogger.info(f"GrammarAnalyzer initialized for language: {language}")

    def set_language(self, language: str):
        """
        Cambia la lingua di analisi

        Args:
            language: Nuovo codice lingua
        """
        if language != self.language:
            AppLogger.info(f"Changing GrammarAnalyzer language: {self.language} -> {language}")
            self.language = language
            nlp_manager.set_language(language)

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
            # Se italiano, usa SimpleGrammarChecker (regole custom)
            if self.language == 'it':
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
                    'language': self.language,
                    'success': True
                }

            # Per altre lingue, usa LanguageTool
            else:
                return self._analyze_with_languagetool(text, max_errors)

        except Exception as e:
            AppLogger.error(f"Error in GrammarAnalyzer.analyze: {e}")
            return {
                'error': str(e),
                'success': False
            }

    def _analyze_with_languagetool(self, text: str, max_errors: int):
        """
        Analizza usando LanguageTool (per lingue diverse dall'italiano)

        Args:
            text: Testo da analizzare
            max_errors: Numero massimo errori da ritornare

        Returns:
            dict: Risultati analisi
        """
        tool = nlp_manager.get_language_tool(self.language)

        if tool is None:
            return {
                'error': f'LanguageTool not available for language: {self.language}',
                'success': False
            }

        matches = tool.check(text)

        errors = []
        by_category = {}

        for match in matches:
            category = match.category or 'other'
            by_category[category] = by_category.get(category, 0) + 1

            errors.append({
                'message': match.message,
                'original': text[match.offset:match.offset + match.errorLength],
                'suggestion': match.replacements[0] if match.replacements else '',
                'context': match.context,
                'category': category,
                'rule_id': match.ruleId
            })

        return {
            'errors': errors[:max_errors],
            'total_errors': len(errors),
            'by_category': by_category,
            'language': self.language,
            'success': True
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