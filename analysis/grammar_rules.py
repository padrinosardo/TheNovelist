"""
Simple Italian grammar rules - NO external dependencies
"""
import re


class SimpleGrammarChecker:
    """Simple grammar checker using regex rules"""

    def __init__(self):
        """Initialize with common Italian grammar rules"""
        self.rules = self._load_rules()

    def _load_rules(self):
        """Load grammar rules"""
        return [
            # ===== ACCENTI =====
            {
                'pattern': r'\bperche\b',
                'replacement': 'perché',
                'message': "Manca l'accento: 'perché'",
                'category': 'accent'
            },
            {
                'pattern': r'\bpiu\b',
                'replacement': 'più',
                'message': "Manca l'accento: 'più'",
                'category': 'accent'
            },
            {
                'pattern': r'\bcosi\b',
                'replacement': 'così',
                'message': "Manca l'accento: 'così'",
                'category': 'accent'
            },
            {
                'pattern': r'\bcioe\b',
                'replacement': 'cioè',
                'message': "Manca l'accento: 'cioè'",
                'category': 'accent'
            },
            {
                'pattern': r'\bla\b(?=\s+mattina|sera|notte)',
                'replacement': 'là',
                'message': "Avverbio di luogo: usa 'là' con accento",
                'category': 'accent'
            },

            # ===== APOSTROFI =====
            {
                'pattern': r'\bun amica\b',
                'replacement': "un'amica",
                'message': "Apostrofo mancante prima di vocale femminile",
                'category': 'apostrophe'
            },
            {
                'pattern': r'\bun altra\b',
                'replacement': "un'altra",
                'message': "Apostrofo mancante: 'un'altra'",
                'category': 'apostrophe'
            },
            {
                'pattern': r'\bun idea\b',
                'replacement': "un'idea",
                'message': "Apostrofo mancante: 'un'idea'",
                'category': 'apostrophe'
            },
            {
                'pattern': r'\bun ora\b',
                'replacement': "un'ora",
                'message': "Apostrofo mancante: 'un'ora'",
                'category': 'apostrophe'
            },
            {
                'pattern': r'\bun ombra\b',
                'replacement': "un'ombra",
                'message': "Apostrofo mancante: 'un'ombra'",
                'category': 'apostrophe'
            },
            {
                'pattern': r"\bqual'è\b",
                'replacement': "qual è",
                'message': "'qual è' si scrive SENZA apostrofo",
                'category': 'apostrophe'
            },

            # ===== PREPOSIZIONI ARTICOLATE =====
            {
                'pattern': r'\bdi il\b',
                'replacement': 'del',
                'message': "Usa la preposizione articolata 'del'",
                'category': 'preposition'
            },
            {
                'pattern': r'\ba il\b',
                'replacement': 'al',
                'message': "Usa la preposizione articolata 'al'",
                'category': 'preposition'
            },
            {
                'pattern': r'\bda il\b',
                'replacement': 'dal',
                'message': "Usa la preposizione articolata 'dal'",
                'category': 'preposition'
            },
            {
                'pattern': r'\bin il\b',
                'replacement': 'nel',
                'message': "Usa la preposizione articolata 'nel'",
                'category': 'preposition'
            },
            {
                'pattern': r'\bsu il\b',
                'replacement': 'sul',
                'message': "Usa la preposizione articolata 'sul'",
                'category': 'preposition'
            },

            # ===== VERBO AVERE (H) =====
            {
                'pattern': r'\bo\s+fatto\b',
                'replacement': 'ho fatto',
                'message': "Verbo avere: 'ho' con H",
                'category': 'h_verb'
            },
            {
                'pattern': r'\bo\s+detto\b',
                'replacement': 'ho detto',
                'message': "Verbo avere: 'ho' con H",
                'category': 'h_verb'
            },
            {
                'pattern': r'\bo\s+visto\b',
                'replacement': 'ho visto',
                'message': "Verbo avere: 'ho' con H",
                'category': 'h_verb'
            },

            # ===== C'È vs CE =====
            {
                'pattern': r'\bce\s+(sono|era|sarà)\b',
                'replacement': r"c'è \1",
                'message': "Verbo esserci: usa 'c'è' con apostrofo",
                'category': 'verb'
            },

            # ===== PUNTEGGIATURA =====
            {
                'pattern': r'\s+([.,;:!?])',
                'replacement': r'\1',
                'message': "Elimina spazio prima della punteggiatura",
                'category': 'punctuation'
            },
            {
                'pattern': r'([.,;:])([^\s\d\)])',
                'replacement': r'\1 \2',
                'message': "Aggiungi spazio dopo la punteggiatura",
                'category': 'punctuation'
            },
            {
                'pattern': r'  +',
                'replacement': ' ',
                'message': "Elimina spazi doppi",
                'category': 'punctuation'
            },

            # ===== DOPPIE COMUNI =====
            {
                'pattern': r'\bacelera',
                'replacement': 'accelera',
                'message': "Doppia consonante: 'accelerare'",
                'category': 'double'
            },
            {
                'pattern': r'\bacompagna',
                'replacement': 'accompagna',
                'message': "Doppia consonante: 'accompagnare'",
                'category': 'double'
            },
            {
                'pattern': r'\bacuisi',
                'replacement': 'acquisì',
                'message': "Doppia consonante: 'acquisire'",
                'category': 'double'
            },
        ]

    def check(self, text):
        """
        Check text against rules

        Args:
            text: Text to check

        Returns:
            list: List of errors found
        """
        errors = []

        for rule in self.rules:
            pattern = rule['pattern']
            replacement = rule['replacement']
            message = rule['message']
            category = rule['category']

            for match in re.finditer(pattern, text, re.IGNORECASE):
                errors.append({
                    'start': match.start(),
                    'end': match.end(),
                    'message': message,
                    'original': match.group(),
                    'suggestion': replacement,
                    'category': category,
                    'context': self._get_context(text, match.start(), match.end())
                })

        return errors

    def _get_context(self, text, start, end, window=40):
        """Get context around error"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        context = text[context_start:context_end]

        # Add ellipsis
        if context_start > 0:
            context = "..." + context
        if context_end < len(text):
            context = context + "..."

        return context

    def add_custom_rule(self, pattern, replacement, message, category='custom'):
        """
        Add a custom rule

        Args:
            pattern: Regex pattern
            replacement: Suggested replacement
            message: Error message
            category: Rule category
        """
        self.rules.append({
            'pattern': pattern,
            'replacement': replacement,
            'message': message,
            'category': category
        })