"""
Module for text repetition analysis
"""
import spacy
from collections import Counter


class RepetitionAnalyzer:
    """Class to analyze word repetitions"""

    def __init__(self, model='it_core_news_sm'):
        """
        Initialize the repetition analyzer

        Args:
            model: spaCy model name to use
        """
        self.model = model
        self._nlp = None

    def _get_nlp(self):
        """Lazy loading of spaCy model"""
        if self._nlp is None:
            self._nlp = spacy.load(self.model)
        return self._nlp

    def analyze(self, text, top_n=20, min_length=3):
        """
        Analyze text to find repetitions

        Args:
            text: Text to analyze
            top_n: Number of most frequent words to return
            min_length: Minimum word length to consider

        Returns:
            dict: Dictionary with 'repetitions' and other info
        """
        try:
            nlp = self._get_nlp()
            doc = nlp(text)

            # Filter significant words
            words = [
                token.lemma_.lower()
                for token in doc
                if not token.is_stop
                   and not token.is_punct
                   and len(token.text) > min_length
                   and token.is_alpha  # Only alphabetic characters
            ]

            # Count occurrences
            count = Counter(words)
            repetitions = count.most_common(top_n)

            return {
                'repetitions': repetitions,
                'total_words_analyzed': len(words),
                'unique_words': len(set(words)),
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
        output += "MOST USED WORDS\n"
        output += "═" * 50 + "\n\n"
        output += "(Excluding stop words and common words)\n\n"

        repetitions = result.get('repetitions', [])

        if not repetitions:
            output += "No significant repetitions found."
            return output

        for word, count in repetitions:
            # Create visual bar
            bar_length = min(count, 30)
            bar = "█" * bar_length

            # Evaluation based on frequency
            rating = self._evaluate_frequency(count)

            output += f"{word:20} {bar} {count}x{rating}\n"

        # Additional statistics
        output += "\n" + "─" * 50 + "\n"
        output += f"Words analyzed: {result.get('total_words_analyzed', 0)}\n"
        output += f"Unique words: {result.get('unique_words', 0)}\n"
        output += "\n💡 Tip: Look for synonyms for the most repeated words!"

        return output

    def _evaluate_frequency(self, count):
        """
        Evaluate word frequency

        Args:
            count: Number of occurrences

        Returns:
            str: Rating emoji
        """
        if count > 10:
            return " ⚠️ TOO FREQUENT"
        elif count > 5:
            return " ⚡ Frequent"
        return ""