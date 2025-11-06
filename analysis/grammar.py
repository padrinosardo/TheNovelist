"""
Module for grammatical text analysis - MULTI-LANGUAGE VERSION
"""
from analysis.grammar_rules import SimpleGrammarChecker
from analysis.nlp_manager import nlp_manager
from utils.logger import AppLogger
from typing import Optional
import re

# Import spell checker
try:
    from spellchecker import SpellChecker
    SPELL_CHECKER_AVAILABLE = True
except ImportError:
    SPELL_CHECKER_AVAILABLE = False
    AppLogger.warning("PySpellChecker not available - spelling errors won't be detected in analysis")


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

        # Initialize spell checker if available
        self.spell_checker = None
        if SPELL_CHECKER_AVAILABLE:
            try:
                self.spell_checker = SpellChecker(language=language)
                AppLogger.info(f"Spell checker initialized for language: {language}")
            except Exception as e:
                AppLogger.warning(f"Could not initialize spell checker: {e}")

        # Word pattern for spell checking (same as spell_check_highlighter.py)
        self.word_pattern = re.compile(r'\b[a-zA-ZàèéìòùÀÈÉÌÒÙáéíóúÁÉÍÓÚäëïöüÄËÏÖÜâêîôûÂÊÎÔÛçÇñÑ]+\b')

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

            # Re-initialize spell checker for new language
            if SPELL_CHECKER_AVAILABLE:
                try:
                    self.spell_checker = SpellChecker(language=language)
                    AppLogger.info(f"Spell checker re-initialized for language: {language}")
                except Exception as e:
                    AppLogger.warning(f"Could not re-initialize spell checker: {e}")
                    self.spell_checker = None

    def _check_spelling(self, text: str):
        """
        Check text for spelling errors

        Args:
            text: Text to check

        Returns:
            list: List of spelling errors in same format as grammar errors
        """
        if not self.spell_checker:
            return []

        spelling_errors = []

        # Get exclusion zones from grammar checker to skip HTML/URLs
        _, exclusions = self.checker._preprocess_text(text)

        # Find all words in text
        for match in self.word_pattern.finditer(text):
            word = match.group()
            start_pos = match.start()
            end_pos = match.end()

            # Skip if word is in exclusion zone (HTML, URL, etc.)
            if self.checker._match_overlaps_exclusion(start_pos, end_pos, exclusions):
                continue

            # Skip numbers, single letters, all uppercase (likely acronyms)
            if len(word) <= 1 or word.isupper() or word.isdigit():
                continue

            # Skip capitalized words (likely proper nouns) unless obviously wrong
            if word[0].isupper() and len(word) > 1:
                # Only check if it looks suspicious (e.g., "Torrrrone")
                if not any(c * 3 in word.lower() for c in 'abcdefghilmnopqrstuvz'):
                    continue

            # Check if word is misspelled
            word_lower = word.lower()
            if self.spell_checker.unknown([word_lower]):
                # Get suggestion
                suggestion = self.spell_checker.correction(word_lower)
                if suggestion and suggestion != word_lower:
                    # Get context
                    context = self.checker._get_context(text, start_pos, end_pos)

                    spelling_errors.append({
                        'start': start_pos,
                        'end': end_pos,
                        'message': f"Possibile errore di ortografia",
                        'original': word,
                        'suggestion': suggestion if word[0].isupper() else suggestion,
                        'category': 'spelling',
                        'context': context
                    })

        return spelling_errors

    def analyze(self, text, max_errors=30):
        """
        Analyze text to find grammatical and spelling errors

        Args:
            text: Text to analyze
            max_errors: Maximum number of errors to return

        Returns:
            dict: Dictionary with 'errors' and 'total_errors'
        """
        try:
            # Se italiano, usa SimpleGrammarChecker (regole custom) + spell checker
            if self.language == 'it':
                # Get grammar errors
                grammar_errors = self.checker.check(text)

                # Get spelling errors
                spelling_errors = self._check_spelling(text)

                # Combine all errors
                all_errors = grammar_errors + spelling_errors

                # Sort by position in text
                all_errors.sort(key=lambda e: e.get('start', 0))

                # Group by category
                by_category = {}
                for error in all_errors:
                    cat = error['category']
                    by_category[cat] = by_category.get(cat, 0) + 1

                AppLogger.info(f"Grammar analysis found {len(grammar_errors)} grammar errors and {len(spelling_errors)} spelling errors")

                return {
                    'errors': all_errors[:max_errors],
                    'total_errors': len(all_errors),
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
                'spelling': 'Ortografia',
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
                    'spelling': '🔤',
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