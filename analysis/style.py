"""
Module for writing style analysis - MULTI-LANGUAGE VERSION
"""
import textstat
from collections import Counter
from typing import Optional
from analysis.nlp_manager import nlp_manager
from utils.logger import AppLogger


class StyleAnalyzer:
    """Class to analyze writing style with multi-language support"""

    # Part of speech mapping (localized for multiple languages)
    POS_MAPPING = {
        'NOUN': {'it': 'Sostantivi', 'en': 'Nouns', 'es': 'Sustantivos', 'fr': 'Noms', 'de': 'Substantive'},
        'VERB': {'it': 'Verbi', 'en': 'Verbs', 'es': 'Verbos', 'fr': 'Verbes', 'de': 'Verben'},
        'ADJ': {'it': 'Aggettivi', 'en': 'Adjectives', 'es': 'Adjetivos', 'fr': 'Adjectifs', 'de': 'Adjektive'},
        'ADV': {'it': 'Avverbi', 'en': 'Adverbs', 'es': 'Adverbios', 'fr': 'Adverbes', 'de': 'Adverbien'},
        'PRON': {'it': 'Pronomi', 'en': 'Pronouns', 'es': 'Pronombres', 'fr': 'Pronoms', 'de': 'Pronomen'},
        'DET': {'it': 'Determinanti', 'en': 'Determiners', 'es': 'Determinantes', 'fr': 'Déterminants', 'de': 'Artikel'},
        'ADP': {'it': 'Preposizioni', 'en': 'Adpositions', 'es': 'Adposiciones', 'fr': 'Adpositions', 'de': 'Präpositionen'},
        'CONJ': {'it': 'Congiunzioni', 'en': 'Conjunctions', 'es': 'Conjunciones', 'fr': 'Conjonctions', 'de': 'Konjunktionen'}
    }

    def __init__(self, language: str = 'it'):
        """
        Initialize the style analyzer

        Args:
            language: Language code ('it', 'en', 'es', 'fr', 'de')
        """
        self.language = language

        # Imposta lingua nel manager
        nlp_manager.set_language(language)

        AppLogger.info(f"StyleAnalyzer initialized for language: {language}")

    def set_language(self, language: str):
        """
        Cambia la lingua di analisi

        Args:
            language: Nuovo codice lingua
        """
        if language != self.language:
            AppLogger.info(f"Changing StyleAnalyzer language: {self.language} -> {language}")
            self.language = language
            nlp_manager.set_language(language)

    def analyze(self, text):
        """
        Analyze text style

        Args:
            text: Text to analyze

        Returns:
            dict: Dictionary with style metrics
        """
        try:
            # Ottieni modello spaCy dal manager
            nlp = nlp_manager.get_spacy_model(self.language)

            if nlp is None:
                return {
                    'error': f'spaCy model not available for language: {self.language}',
                    'success': False
                }

            doc = nlp(text)

            # Basic statistics
            sentences = list(doc.sents)
            words = [token for token in doc if not token.is_punct]
            unique_words = set([token.lemma_.lower() for token in words])

            # Calculations
            num_sentences = len(sentences)
            num_words = len(words)
            num_unique_words = len(unique_words)

            avg_sentence_length = num_words / num_sentences if num_sentences > 0 else 0
            diversity = num_unique_words / num_words if num_words > 0 else 0

            # Readability index (usa metodo appropriato per la lingua)
            if self.language == 'it':
                readability = textstat.gulpease_index(text)
            else:
                readability = textstat.flesch_reading_ease(text)

            # Part of speech analysis
            pos_counts = Counter([token.pos_ for token in doc if not token.is_punct])

            return {
                'num_sentences': num_sentences,
                'num_words': num_words,
                'unique_words': num_unique_words,
                'avg_sentence_length': round(avg_sentence_length, 1),
                'lexical_diversity': round(diversity * 100, 1),
                'readability': round(readability, 1),
                'pos_counts': dict(pos_counts.most_common(5)),
                'language': self.language,
                'success': True
            }
        except Exception as e:
            AppLogger.error(f"Error in StyleAnalyzer.analyze: {e}")
            return {
                'error': str(e),
                'success': False
            }

    def format_results(self, result):
        """
        Format results for display

        Args:
            result: Analysis result

        Returns:
            str: Formatted text for UI
        """
        if not result.get('success'):
            return f"❌ Error: {result.get('error', 'Unknown error')}"

        output = "═" * 50 + "\n"
        output += "WRITING STYLE ANALYSIS\n"
        output += "═" * 50 + "\n\n"

        # General statistics
        output += "📊 GENERAL STATISTICS\n\n"
        output += f"  • Sentences: {result['num_sentences']}\n"
        output += f"  • Words: {result['num_words']}\n"
        output += f"  • Unique words: {result['unique_words']}\n"
        output += f"  • Average sentence length: {result['avg_sentence_length']} words\n\n"

        # Sentence length evaluation
        output += self._evaluate_sentence_length(result['avg_sentence_length'])

        # Text quality
        output += "\n🎯 TEXT QUALITY\n\n"
        output += f"  • Lexical diversity: {result['lexical_diversity']}%\n"
        output += self._evaluate_diversity(result['lexical_diversity'])

        output += f"\n  • Gulpease readability: {result['readability']}\n"
        output += self._evaluate_readability(result['readability'])

        # Text composition
        output += "\n📝 COMPOSITION\n\n"
        lang = result.get('language', self.language)
        for pos, count in result['pos_counts'].items():
            # Usa mapping localizzato
            translations = self.POS_MAPPING.get(pos, {})
            name = translations.get(lang, pos) if isinstance(translations, dict) else pos
            output += f"  • {name}: {count}\n"

        return output

    def _evaluate_sentence_length(self, length):
        """Evaluate average sentence length"""
        if length < 10:
            return "    → Very short sentences (dynamic style)\n"
        elif length < 20:
            return "    → ✅ Ideal sentence length\n"
        else:
            return "    → ⚠️ Long sentences (consider breaking them up)\n"

    def _evaluate_diversity(self, diversity):
        """Evaluate lexical diversity"""
        if diversity > 60:
            return "    → ✅ Excellent! Rich vocabulary\n"
        elif diversity > 40:
            return "    → ⚡ Good, but you can vary more\n"
        else:
            return "    → ⚠️ Too many repetitions\n"

    def _evaluate_readability(self, readability):
        """Evaluate readability index"""
        if readability >= 80:
            return "    → ✅ Very easy to read\n"
        elif readability >= 60:
            return "    → ✅ Easy to read\n"
        elif readability >= 40:
            return "    → ⚡ Medium difficulty\n"
        else:
            return "    → ⚠️ Complex text\n"