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

    def _preprocess_text(self, text):
        """
        Pre-process text to remove HTML, URLs, emails and other technical content
        that should not be analyzed for grammar errors.

        Args:
            text: Original text

        Returns:
            tuple: (cleaned_text, exclusion_ranges)
                - cleaned_text: Text with placeholders
                - exclusion_ranges: List of (start, end) tuples to skip
        """
        # Store original text for position tracking
        cleaned = text
        exclusions = []

        # Pattern 1: HTML/XML tags (e.g., <html>, <p>, </div>, etc.)
        html_pattern = r'<[^>]+>'
        for match in re.finditer(html_pattern, text):
            exclusions.append((match.start(), match.end()))

        # Pattern 2: URLs (http://, https://, www., ftp://)
        url_pattern = r'(https?://|ftp://|www\.)[^\s<>"{}|\\^`\[\]]+'
        for match in re.finditer(url_pattern, text, re.IGNORECASE):
            exclusions.append((match.start(), match.end()))

        # Pattern 3: Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(email_pattern, text):
            exclusions.append((match.start(), match.end()))

        # Pattern 4: File paths (e.g., /path/to/file.txt, C:\path\to\file)
        filepath_pattern = r'([A-Za-z]:\\|/)[^\s<>"\']+\.[a-z]{2,5}'
        for match in re.finditer(filepath_pattern, text):
            exclusions.append((match.start(), match.end()))

        # Pattern 5: DOCTYPE declarations
        doctype_pattern = r'<!DOCTYPE[^>]+>'
        for match in re.finditer(doctype_pattern, text, re.IGNORECASE):
            exclusions.append((match.start(), match.end()))

        # Pattern 6: CSS content inside <style> tags (entire tag + content)
        style_pattern = r'<style[^>]*>.*?</style>'
        for match in re.finditer(style_pattern, text, re.IGNORECASE | re.DOTALL):
            exclusions.append((match.start(), match.end()))

        # Pattern 7: JavaScript content inside <script> tags (entire tag + content)
        script_pattern = r'<script[^>]*>.*?</script>'
        for match in re.finditer(script_pattern, text, re.IGNORECASE | re.DOTALL):
            exclusions.append((match.start(), match.end()))

        # Merge overlapping exclusions
        exclusions = self._merge_ranges(exclusions)

        return cleaned, exclusions

    def _merge_ranges(self, ranges):
        """Merge overlapping ranges"""
        if not ranges:
            return []

        # Sort by start position
        sorted_ranges = sorted(ranges, key=lambda x: x[0])
        merged = [sorted_ranges[0]]

        for current in sorted_ranges[1:]:
            last = merged[-1]
            # If ranges overlap, merge them
            if current[0] <= last[1]:
                merged[-1] = (last[0], max(last[1], current[1]))
            else:
                merged.append(current)

        return merged

    def _is_in_exclusion(self, pos, exclusions):
        """Check if position is in any exclusion range"""
        for start, end in exclusions:
            if start <= pos < end:
                return True
        return False

    def _match_overlaps_exclusion(self, match_start, match_end, exclusions):
        """
        Check if a match overlaps with any exclusion zone

        This is more robust than checking only the start position,
        as it catches cases like '.<p>' where '.' is real text but '<p>' is HTML.
        """
        for excl_start, excl_end in exclusions:
            # Check if match overlaps with exclusion zone
            if (match_start < excl_end and match_end > excl_start):
                return True
        return False

    def check(self, text):
        """
        Check text against rules

        Args:
            text: Text to check

        Returns:
            list: List of errors found
        """
        # Pre-process text to identify areas to exclude (HTML, URLs, etc.)
        _, exclusions = self._preprocess_text(text)

        errors = []

        for rule in self.rules:
            pattern = rule['pattern']
            replacement = rule['replacement']
            message = rule['message']
            category = rule['category']

            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Skip if match overlaps with an exclusion zone (HTML, URL, CSS, etc.)
                if self._match_overlaps_exclusion(match.start(), match.end(), exclusions):
                    continue

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