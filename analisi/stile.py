"""
Module for writing style analysis
"""
import spacy
import textstat
from collections import Counter


class StyleAnalyzer:
    """Class to analyze writing style"""

    # Part of speech mapping in English
    POS_MAPPING = {
        'NOUN': 'Nouns',
        'VERB': 'Verbs',
        'ADJ': 'Adjectives',
        'ADV': 'Adverbs',
        'PRON': 'Pronouns',
        'DET': 'Determiners',
        'ADP': 'Adpositions',
        'CONJ': 'Conjunctions'
    }

    def __init__(self, model='it_core_news_sm', language='it'):
        """
        Initialize the style analyzer

        Args:
            model: spaCy model name
            language: Language code for textstat
        """
        self.model = model
        self.language = language
        self._nlp = None

        # Configure textstat
        textstat.set_lang(self.language)

    def _get_nlp(self):
        """Lazy loading of spaCy model"""
        if self._nlp is None:
            self._nlp = spacy.load(self.model)
        return self._nlp

    def analyze(self, text):
        """
        Analyze text style

        Args:
            text: Text to analyze

        Returns:
            dict: Dictionary with style metrics
        """
        try:
            nlp = self._get_nlp()
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

            # Readability index
            readability = textstat.gulpease_index(text)

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
                'success': True
            }
        except Exception as e:
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
        for pos, count in result['pos_counts'].items():
            name = self.POS_MAPPING.get(pos, pos)
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