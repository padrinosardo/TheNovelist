"""
Module for writing style analysis - MULTI-LANGUAGE VERSION
"""
import textstat
from collections import Counter
from typing import Optional, Dict, List
from analysis.nlp_manager import nlp_manager
from models.project_type import ProjectType
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

    def analyze(self, text, project_type: Optional[ProjectType] = None):
        """
        Analyze text style

        Args:
            text: Text to analyze
            project_type: Optional project type for context-aware analysis

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
                'project_type': project_type,
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

        # Type-specific suggestions
        project_type = result.get('project_type')
        if project_type:
            suggestions = self._get_type_specific_suggestions(result, project_type)
            if suggestions:
                output += "\n💡 TYPE-SPECIFIC SUGGESTIONS\n\n"
                for suggestion in suggestions:
                    output += f"  {suggestion}\n"

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

    def _get_type_specific_suggestions(self, stats: Dict, project_type: Optional[ProjectType]) -> List[str]:
        """
        Generate type-specific writing suggestions based on project type.

        Args:
            stats: Analysis statistics dictionary
            project_type: Project type for context-aware suggestions

        Returns:
            List of suggestion strings
        """
        if not project_type:
            return []

        suggestions = []
        avg_length = stats.get('avg_sentence_length', 0)
        num_words = stats.get('num_words', 0)
        diversity = stats.get('lexical_diversity', 0)

        # Translations for suggestions
        labels = self._get_suggestion_labels()

        if project_type == ProjectType.NOVEL:
            # Novels: More flexible, focus on rhythm and variety
            if avg_length > 30:
                suggestions.append(labels['novel_long_sentences'])
            if avg_length < 12:
                suggestions.append(labels['novel_short_sentences'])
            if diversity < 50:
                suggestions.append(labels['novel_diversity'])

        elif project_type == ProjectType.SHORT_STORY:
            # Short stories: Tight, focused narrative
            if avg_length > 25:
                suggestions.append(labels['short_story_length'])
            if num_words > 15000:
                suggestions.append(labels['short_story_words'])

        elif project_type == ProjectType.ARTICLE_MAGAZINE:
            # Magazine articles: Clear, professional
            if avg_length > 22:
                suggestions.append(labels['magazine_length'])
            if avg_length < 12:
                suggestions.append(labels['magazine_short'])

        elif project_type == ProjectType.ARTICLE_SOCIAL:
            # Social media: Short and punchy
            if avg_length > 15:
                suggestions.append(labels['social_length'])
            if num_words > 250:
                suggestions.append(labels['social_words'])
            if num_words < 50:
                suggestions.append(labels['social_too_short'])

        elif project_type == ProjectType.SCREENPLAY:
            # Screenplay: Action-oriented, visual
            if avg_length > 18:
                suggestions.append(labels['screenplay_length'])
            if diversity < 40:
                suggestions.append(labels['screenplay_diversity'])

        elif project_type == ProjectType.ESSAY:
            # Essay: Logical, argumentative
            if avg_length < 15:
                suggestions.append(labels['essay_short'])
            if diversity < 55:
                suggestions.append(labels['essay_diversity'])

        elif project_type == ProjectType.RESEARCH_PAPER:
            # Research: Formal, precise
            if avg_length > 28:
                suggestions.append(labels['research_length'])
            if diversity < 60:
                suggestions.append(labels['research_diversity'])

        elif project_type == ProjectType.POETRY:
            # Poetry: Highly individual, minimal suggestions
            if num_words > 8000:
                suggestions.append(labels['poetry_words'])

        return suggestions

    def _get_suggestion_labels(self) -> Dict[str, str]:
        """Get localized labels for type-specific suggestions"""
        labels = {
            'it': {
                'novel_long_sentences': "⚠️ Per un romanzo, frasi molto lunghe possono stancare. Varia il ritmo.",
                'novel_short_sentences': "💡 Stile telegrafico. Per un romanzo, prova a variare con frasi più complesse.",
                'novel_diversity': "💡 Arricchisci il lessico per un romanzo più coinvolgente.",
                'short_story_length': "⚠️ Per un racconto breve, preferisci frasi più concise.",
                'short_story_words': "💡 Un racconto oltre 15k parole potrebbe essere considerato una novella.",
                'magazine_length': "⚠️ Per articoli, mantieni le frasi sotto le 22 parole per chiarezza.",
                'magazine_short': "💡 Per articoli professionali, puoi usare frasi più articolate.",
                'social_length': "⚠️ Per i social, frasi brevi (max 15 parole) mantengono l'attenzione.",
                'social_words': "⚠️ Post troppo lungo per social media. Considera di ridurre sotto 250 parole.",
                'social_too_short': "💡 Post molto breve. Assicurati di comunicare il messaggio completo.",
                'screenplay_length': "⚠️ Per sceneggiature, usa frasi brevi e visive (max 18 parole).",
                'screenplay_diversity': "💡 Arricchisci il vocabolario per rendere le scene più vivide.",
                'essay_short': "💡 Per un saggio, puoi sviluppare periodi più articolati.",
                'essay_diversity': "💡 Un saggio richiede un lessico più vario e preciso.",
                'research_length': "⚠️ Paper di ricerca: frasi troppo lunghe riducono la chiarezza scientifica.",
                'research_diversity': "💡 Paper di ricerca: usa terminologia precisa e varia.",
                'poetry_words': "💡 Raccolta di poesie molto estesa. Considera di dividere in volumi."
            },
            'en': {
                'novel_long_sentences': "⚠️ For a novel, very long sentences can tire readers. Vary the rhythm.",
                'novel_short_sentences': "💡 Telegraphic style. For a novel, try varying with more complex sentences.",
                'novel_diversity': "💡 Enrich vocabulary for a more engaging novel.",
                'short_story_length': "⚠️ For short stories, prefer more concise sentences.",
                'short_story_words': "💡 A short story over 15k words might be considered a novella.",
                'magazine_length': "⚠️ For articles, keep sentences under 22 words for clarity.",
                'magazine_short': "💡 For professional articles, you can use more articulated sentences.",
                'social_length': "⚠️ For social media, short sentences (max 15 words) maintain attention.",
                'social_words': "⚠️ Post too long for social media. Consider reducing under 250 words.",
                'social_too_short': "💡 Very short post. Make sure you communicate the complete message.",
                'screenplay_length': "⚠️ For screenplays, use short, visual sentences (max 18 words).",
                'screenplay_diversity': "💡 Enrich vocabulary to make scenes more vivid.",
                'essay_short': "💡 For an essay, you can develop more articulated periods.",
                'essay_diversity': "💡 An essay requires more varied and precise vocabulary.",
                'research_length': "⚠️ Research paper: sentences too long reduce scientific clarity.",
                'research_diversity': "💡 Research paper: use precise and varied terminology.",
                'poetry_words': "💡 Very extensive poetry collection. Consider dividing into volumes."
            },
            'es': {
                'novel_long_sentences': "⚠️ Para una novela, frases muy largas pueden cansar. Varía el ritmo.",
                'novel_short_sentences': "💡 Estilo telegráfico. Para una novela, prueba variar con frases más complejas.",
                'novel_diversity': "💡 Enriquece el léxico para una novela más atractiva.",
                'short_story_length': "⚠️ Para cuentos, prefiere frases más concisas.",
                'short_story_words': "💡 Un cuento de más de 15k palabras podría considerarse novela corta.",
                'magazine_length': "⚠️ Para artículos, mantén las frases bajo 22 palabras para claridad.",
                'magazine_short': "💡 Para artículos profesionales, puedes usar frases más articuladas.",
                'social_length': "⚠️ Para redes sociales, frases breves (máx 15 palabras) mantienen atención.",
                'social_words': "⚠️ Post demasiado largo para redes sociales. Considera reducir bajo 250 palabras.",
                'social_too_short': "💡 Post muy breve. Asegúrate de comunicar el mensaje completo.",
                'screenplay_length': "⚠️ Para guiones, usa frases breves y visuales (máx 18 palabras).",
                'screenplay_diversity': "💡 Enriquece el vocabulario para hacer las escenas más vívidas.",
                'essay_short': "💡 Para un ensayo, puedes desarrollar períodos más articulados.",
                'essay_diversity': "💡 Un ensayo requiere léxico más variado y preciso.",
                'research_length': "⚠️ Artículo de investigación: frases muy largas reducen claridad científica.",
                'research_diversity': "💡 Artículo de investigación: usa terminología precisa y variada.",
                'poetry_words': "💡 Colección de poesía muy extensa. Considera dividir en volúmenes."
            },
            'fr': {
                'novel_long_sentences': "⚠️ Pour un roman, des phrases très longues peuvent fatiguer. Variez le rythme.",
                'novel_short_sentences': "💡 Style télégraphique. Pour un roman, essayez de varier avec des phrases plus complexes.",
                'novel_diversity': "💡 Enrichissez le lexique pour un roman plus captivant.",
                'short_story_length': "⚠️ Pour les nouvelles, préférez des phrases plus concises.",
                'short_story_words': "💡 Une nouvelle de plus de 15k mots pourrait être considérée comme roman court.",
                'magazine_length': "⚠️ Pour les articles, gardez les phrases sous 22 mots pour la clarté.",
                'magazine_short': "💡 Pour les articles professionnels, vous pouvez utiliser des phrases plus articulées.",
                'social_length': "⚠️ Pour les réseaux sociaux, phrases courtes (max 15 mots) maintiennent l'attention.",
                'social_words': "⚠️ Post trop long pour les réseaux sociaux. Considérez réduire sous 250 mots.",
                'social_too_short': "💡 Post très court. Assurez-vous de communiquer le message complet.",
                'screenplay_length': "⚠️ Pour les scénarios, utilisez des phrases courtes et visuelles (max 18 mots).",
                'screenplay_diversity': "💡 Enrichissez le vocabulaire pour rendre les scènes plus vivantes.",
                'essay_short': "💡 Pour un essai, vous pouvez développer des périodes plus articulées.",
                'essay_diversity': "💡 Un essai nécessite un lexique plus varié et précis.",
                'research_length': "⚠️ Article de recherche: phrases trop longues réduisent la clarté scientifique.",
                'research_diversity': "💡 Article de recherche: utilisez une terminologie précise et variée.",
                'poetry_words': "💡 Collection de poésie très étendue. Considérez diviser en volumes."
            },
            'de': {
                'novel_long_sentences': "⚠️ Für einen Roman können sehr lange Sätze ermüdend sein. Variieren Sie den Rhythmus.",
                'novel_short_sentences': "💡 Telegrafischer Stil. Für einen Roman versuchen Sie komplexere Sätze.",
                'novel_diversity': "💡 Bereichern Sie den Wortschatz für einen fesselnderen Roman.",
                'short_story_length': "⚠️ Für Kurzgeschichten bevorzugen Sie prägnantere Sätze.",
                'short_story_words': "💡 Eine Kurzgeschichte über 15k Wörter könnte als Novelle gelten.",
                'magazine_length': "⚠️ Für Artikel halten Sie Sätze unter 22 Wörtern für Klarheit.",
                'magazine_short': "💡 Für professionelle Artikel können Sie artikuliertere Sätze verwenden.",
                'social_length': "⚠️ Für Social Media, kurze Sätze (max 15 Wörter) halten Aufmerksamkeit.",
                'social_words': "⚠️ Post zu lang für Social Media. Erwägen Sie Reduzierung unter 250 Wörter.",
                'social_too_short': "💡 Sehr kurzer Post. Stellen Sie sicher, die vollständige Nachricht zu kommunizieren.",
                'screenplay_length': "⚠️ Für Drehbücher verwenden Sie kurze, visuelle Sätze (max 18 Wörter).",
                'screenplay_diversity': "💡 Bereichern Sie den Wortschatz um Szenen lebendiger zu machen.",
                'essay_short': "💡 Für einen Essay können Sie artikuliertere Perioden entwickeln.",
                'essay_diversity': "💡 Ein Essay erfordert vielfältigeren und präziseren Wortschatz.",
                'research_length': "⚠️ Forschungsarbeit: zu lange Sätze reduzieren wissenschaftliche Klarheit.",
                'research_diversity': "💡 Forschungsarbeit: verwenden Sie präzise und vielfältige Terminologie.",
                'poetry_words': "💡 Sehr umfangreiche Gedichtsammlung. Erwägen Sie Aufteilung in Bände."
            }
        }

        return labels.get(self.language, labels['en'])