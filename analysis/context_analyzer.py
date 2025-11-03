"""
Context Analyzer - Project health checks and contextual suggestions
"""
from typing import Dict, List, Optional
from models.project_type import ProjectType
from models.project import Project
from utils.logger import AppLogger


class ContextAnalyzer:
    """
    Analyzes project context and provides health warnings/suggestions
    based on project type, progress, and completeness.
    """

    def __init__(self, language: str = 'it'):
        """
        Initialize the context analyzer

        Args:
            language: Language code for localized messages
        """
        self.language = language
        AppLogger.info(f"ContextAnalyzer initialized for language: {language}")

    def set_language(self, language: str):
        """
        Change the analyzer language

        Args:
            language: New language code
        """
        if language != self.language:
            AppLogger.info(f"Changing ContextAnalyzer language: {self.language} -> {language}")
            self.language = language

    def analyze_project_health(self, project: Project, word_count: int,
                               character_count: int, scene_count: int) -> Dict:
        """
        Analyze project health and generate contextual suggestions

        Args:
            project: Project instance
            word_count: Current manuscript word count
            character_count: Number of characters defined
            scene_count: Number of scenes/chapters

        Returns:
            dict: Analysis results with warnings and suggestions
        """
        try:
            warnings = []
            suggestions = []
            info = []

            # Get project type
            project_type = project.project_type

            # Get localized messages
            labels = self._get_labels()

            # Check word count against target range
            min_words, max_words = project_type.get_target_word_count_range()

            if min_words > 0 and max_words > 0:
                if word_count < min_words * 0.1:
                    warnings.append(labels['early_stage'].format(
                        type=project_type.get_display_name(self.language)
                    ))
                elif word_count < min_words:
                    info.append(labels['below_target'].format(
                        current=word_count,
                        target=min_words
                    ))
                elif word_count > max_words * 1.5:
                    warnings.append(labels['exceeds_target'].format(
                        current=word_count,
                        max=max_words
                    ))
                elif word_count >= min_words and word_count <= max_words:
                    info.append(labels['good_progress'].format(
                        current=word_count,
                        target=f"{min_words}-{max_words}"
                    ))

            # Type-specific checks
            type_checks = self._get_type_specific_checks(
                project_type, word_count, character_count, scene_count, labels
            )
            warnings.extend(type_checks['warnings'])
            suggestions.extend(type_checks['suggestions'])
            info.extend(type_checks['info'])

            # Character checks for narrative projects
            if project_type in [ProjectType.NOVEL, ProjectType.SHORT_STORY, ProjectType.SCREENPLAY]:
                if character_count == 0 and word_count > 500:
                    suggestions.append(labels['add_characters'])
                elif character_count == 1 and word_count > 2000:
                    suggestions.append(labels['add_more_characters'])

            # Scene/Chapter structure checks
            if project_type in [ProjectType.NOVEL, ProjectType.SCREENPLAY]:
                if scene_count == 0 and word_count > 1000:
                    warnings.append(labels['no_scenes'])
                elif scene_count == 1 and word_count > 5000:
                    suggestions.append(labels['consider_chapters'])

            return {
                'warnings': warnings,
                'suggestions': suggestions,
                'info': info,
                'word_count': word_count,
                'target_range': (min_words, max_words),
                'project_type': project_type,
                'success': True
            }

        except Exception as e:
            AppLogger.error(f"Error in ContextAnalyzer.analyze_project_health: {e}")
            return {
                'error': str(e),
                'success': False
            }

    def _get_type_specific_checks(self, project_type: ProjectType, word_count: int,
                                  character_count: int, scene_count: int,
                                  labels: Dict) -> Dict:
        """
        Get type-specific health checks

        Args:
            project_type: Type of project
            word_count: Current word count
            character_count: Number of characters
            scene_count: Number of scenes
            labels: Localized label dictionary

        Returns:
            dict: Dictionary with warnings, suggestions, and info lists
        """
        warnings = []
        suggestions = []
        info = []

        if project_type == ProjectType.NOVEL:
            if word_count > 150000:
                warnings.append(labels['novel_very_long'])
            if word_count > 20000 and character_count < 3:
                suggestions.append(labels['novel_few_characters'])
            if scene_count > 0 and word_count / scene_count > 5000:
                suggestions.append(labels['novel_long_scenes'])

        elif project_type == ProjectType.SHORT_STORY:
            if word_count > 20000:
                info.append(labels['short_story_novella'])
            if character_count > 5:
                suggestions.append(labels['short_story_many_characters'])

        elif project_type == ProjectType.ARTICLE_MAGAZINE:
            if word_count > 5000:
                warnings.append(labels['article_too_long'])
            if word_count < 500 and word_count > 100:
                suggestions.append(labels['article_too_short'])

        elif project_type == ProjectType.ARTICLE_SOCIAL:
            if word_count > 300:
                warnings.append(labels['social_too_long'])
            if word_count < 50 and word_count > 10:
                warnings.append(labels['social_too_short'])
            if word_count >= 50 and word_count <= 250:
                info.append(labels['social_good_length'])

        elif project_type == ProjectType.SCREENPLAY:
            # Typical screenplay: 90-120 pages, ~250 words/page = 22500-30000 words
            if word_count > 35000:
                warnings.append(labels['screenplay_too_long'])
            if word_count < 15000 and word_count > 5000:
                info.append(labels['screenplay_short_film'])
            if scene_count > 0 and word_count / scene_count < 200:
                suggestions.append(labels['screenplay_short_scenes'])

        elif project_type == ProjectType.ESSAY:
            if word_count > 15000:
                warnings.append(labels['essay_too_long'])
            if word_count < 2000 and word_count > 500:
                suggestions.append(labels['essay_expand'])

        elif project_type == ProjectType.RESEARCH_PAPER:
            if word_count > 20000:
                warnings.append(labels['research_too_long'])
            if word_count < 5000 and word_count > 1000:
                suggestions.append(labels['research_too_short'])
            if word_count >= 5000 and word_count <= 15000:
                info.append(labels['research_good_length'])

        elif project_type == ProjectType.POETRY:
            if word_count > 10000:
                suggestions.append(labels['poetry_collection'])

        return {
            'warnings': warnings,
            'suggestions': suggestions,
            'info': info
        }

    def _get_labels(self) -> Dict[str, str]:
        """Get localized labels for messages"""
        labels = {
            'it': {
                'early_stage': "📝 {type} in fase iniziale. Continua a scrivere!",
                'below_target': "📊 Progresso: {current} parole. Obiettivo: {target} parole",
                'exceeds_target': "⚠️ Il testo supera l'obiettivo ({current} > {max} parole). Considera di rivedere o dividere",
                'good_progress': "✅ Ottimo progresso! {current} parole (obiettivo: {target})",
                'add_characters': "💡 Considera di aggiungere personaggi alla tua storia",
                'add_more_characters': "💡 Storia con un solo personaggio. Considera di aggiungere comprimari",
                'no_scenes': "⚠️ Nessuna scena/capitolo definito. Struttura il manoscritto per migliorare l'organizzazione",
                'consider_chapters': "💡 Testo lungo con una sola scena. Considera di dividere in capitoli",
                'novel_very_long': "⚠️ Romanzo molto lungo (>150k parole). Valuta se dividere in volumi",
                'novel_few_characters': "💡 Romanzo con pochi personaggi. Considera di arricchire il cast",
                'novel_long_scenes': "💡 Scene molto lunghe (media >5k parole). Considera di suddividerle",
                'short_story_novella': "📚 Con oltre 20k parole, questo potrebbe essere considerato una novella",
                'short_story_many_characters': "💡 Molti personaggi per un racconto breve. Mantieni il focus",
                'article_too_long': "⚠️ Articolo molto lungo (>5k parole). Considera di ridurre o dividere",
                'article_too_short': "💡 Articolo breve. Considera di approfondire i contenuti",
                'social_too_long': "⚠️ Post social troppo lungo (>300 parole). Riduci per maggiore impatto",
                'social_too_short': "⚠️ Post social molto breve (<50 parole). Assicurati di comunicare il messaggio",
                'social_good_length': "✅ Lunghezza ideale per post social (50-250 parole)",
                'screenplay_too_long': "⚠️ Sceneggiatura molto lunga (>35k parole ~140 pagine). Standard: 90-120 pagine",
                'screenplay_short_film': "🎬 Lunghezza tipica per cortometraggio o episodio TV",
                'screenplay_short_scenes': "💡 Scene molto brevi. Assicurati di sviluppare adeguatamente",
                'essay_too_long': "⚠️ Saggio molto lungo (>15k parole). Considera di focalizzare l'argomento",
                'essay_expand': "💡 Saggio breve. Considera di espandere l'argomentazione",
                'research_too_long': "⚠️ Paper molto lungo (>20k parole). Verifica i limiti della rivista target",
                'research_too_short': "💡 Paper breve. Assicurati di coprire adeguatamente metodologia e risultati",
                'research_good_length': "✅ Lunghezza standard per paper di ricerca (5-15k parole)",
                'poetry_collection': "📖 Raccolta di poesie estesa. Considera di organizzare in sezioni o volumi",
            },
            'en': {
                'early_stage': "📝 {type} in early stage. Keep writing!",
                'below_target': "📊 Progress: {current} words. Target: {target} words",
                'exceeds_target': "⚠️ Text exceeds target ({current} > {max} words). Consider reviewing or splitting",
                'good_progress': "✅ Great progress! {current} words (target: {target})",
                'add_characters': "💡 Consider adding characters to your story",
                'add_more_characters': "💡 Story with single character. Consider adding supporting cast",
                'no_scenes': "⚠️ No scenes/chapters defined. Structure manuscript for better organization",
                'consider_chapters': "💡 Long text with single scene. Consider dividing into chapters",
                'novel_very_long': "⚠️ Very long novel (>150k words). Consider splitting into volumes",
                'novel_few_characters': "💡 Novel with few characters. Consider enriching the cast",
                'novel_long_scenes': "💡 Very long scenes (avg >5k words). Consider subdividing",
                'short_story_novella': "📚 With over 20k words, this could be considered a novella",
                'short_story_many_characters': "💡 Many characters for short story. Keep focused",
                'article_too_long': "⚠️ Very long article (>5k words). Consider reducing or splitting",
                'article_too_short': "💡 Short article. Consider expanding content",
                'social_too_long': "⚠️ Social post too long (>300 words). Reduce for greater impact",
                'social_too_short': "⚠️ Very short social post (<50 words). Ensure message is communicated",
                'social_good_length': "✅ Ideal length for social post (50-250 words)",
                'screenplay_too_long': "⚠️ Very long screenplay (>35k words ~140 pages). Standard: 90-120 pages",
                'screenplay_short_film': "🎬 Typical length for short film or TV episode",
                'screenplay_short_scenes': "💡 Very short scenes. Ensure adequate development",
                'essay_too_long': "⚠️ Very long essay (>15k words). Consider focusing topic",
                'essay_expand': "💡 Short essay. Consider expanding argumentation",
                'research_too_long': "⚠️ Very long paper (>20k words). Check target journal limits",
                'research_too_short': "💡 Short paper. Ensure adequate coverage of methodology and results",
                'research_good_length': "✅ Standard length for research paper (5-15k words)",
                'poetry_collection': "📖 Extensive poetry collection. Consider organizing into sections or volumes",
            }
        }

        return labels.get(self.language, labels['en'])

    def format_results(self, result: Dict) -> str:
        """
        Format health check results for display

        Args:
            result: Analysis result dictionary

        Returns:
            str: Formatted text for UI
        """
        if not result.get('success'):
            return f"❌ Error: {result.get('error', 'Unknown error')}"

        output = "═" * 50 + "\n"
        output += "PROJECT HEALTH CHECK\n"
        output += "═" * 50 + "\n\n"

        # Project info
        project_type = result.get('project_type')
        if project_type:
            output += f"📋 Type: {project_type.get_display_name(self.language)}\n"
            output += f"📊 Word count: {result.get('word_count', 0)}\n"

            min_words, max_words = result.get('target_range', (0, 0))
            if min_words > 0:
                output += f"🎯 Target range: {min_words}-{max_words} words\n"
            output += "\n"

        # Warnings
        warnings = result.get('warnings', [])
        if warnings:
            output += "⚠️  WARNINGS\n\n"
            for warning in warnings:
                output += f"  {warning}\n"
            output += "\n"

        # Suggestions
        suggestions = result.get('suggestions', [])
        if suggestions:
            output += "💡 SUGGESTIONS\n\n"
            for suggestion in suggestions:
                output += f"  {suggestion}\n"
            output += "\n"

        # Info
        info = result.get('info', [])
        if info:
            output += "ℹ️  INFO\n\n"
            for item in info:
                output += f"  {item}\n"
            output += "\n"

        if not warnings and not suggestions and not info:
            labels = self._get_labels()
            output += "✅ No issues detected. Project looks healthy!\n"

        return output
