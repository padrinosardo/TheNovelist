"""
Project Type System - Different types of writing projects
"""
from enum import Enum
from typing import Dict


class ProjectType(Enum):
    """
    Enum representing different types of writing projects.

    Each project type has specific characteristics:
    - Expected structure (chapters, single document, etc.)
    - Target word count ranges
    - Available containers
    - Analysis focus
    """

    NOVEL = "novel"
    SHORT_STORY = "short_story"
    ARTICLE_MAGAZINE = "article_magazine"
    ARTICLE_SOCIAL = "article_social"
    POETRY = "poetry"
    SCREENPLAY = "screenplay"
    ESSAY = "essay"
    RESEARCH_PAPER = "research_paper"

    def get_display_name(self, language: str = 'it') -> str:
        """
        Get localized display name for the project type.

        Args:
            language: Language code ('it', 'en', 'es', 'fr', 'de')

        Returns:
            str: Localized project type name
        """
        translations = {
            'it': {
                'novel': 'Romanzo',
                'short_story': 'Racconto',
                'article_magazine': 'Articolo per Rivista',
                'article_social': 'Post Social Media',
                'poetry': 'Poesia',
                'screenplay': 'Sceneggiatura',
                'essay': 'Saggio',
                'research_paper': 'Paper di Ricerca'
            },
            'en': {
                'novel': 'Novel',
                'short_story': 'Short Story',
                'article_magazine': 'Magazine Article',
                'article_social': 'Social Media Post',
                'poetry': 'Poetry',
                'screenplay': 'Screenplay',
                'essay': 'Essay',
                'research_paper': 'Research Paper'
            },
            'es': {
                'novel': 'Novela',
                'short_story': 'Cuento',
                'article_magazine': 'Artículo de Revista',
                'article_social': 'Publicación en Redes',
                'poetry': 'Poesía',
                'screenplay': 'Guión',
                'essay': 'Ensayo',
                'research_paper': 'Artículo de Investigación'
            },
            'fr': {
                'novel': 'Roman',
                'short_story': 'Nouvelle',
                'article_magazine': 'Article de Magazine',
                'article_social': 'Publication Réseaux Sociaux',
                'poetry': 'Poésie',
                'screenplay': 'Scénario',
                'essay': 'Essai',
                'research_paper': 'Article de Recherche'
            },
            'de': {
                'novel': 'Roman',
                'short_story': 'Kurzgeschichte',
                'article_magazine': 'Zeitschriftenartikel',
                'article_social': 'Social Media Post',
                'poetry': 'Poesie',
                'screenplay': 'Drehbuch',
                'essay': 'Essay',
                'research_paper': 'Forschungsarbeit'
            }
        }

        lang_dict = translations.get(language, translations['en'])
        return lang_dict.get(self.value, self.value.replace('_', ' ').title())

    def get_target_word_count_range(self) -> tuple:
        """
        Get typical word count range for this project type.

        Returns:
            tuple: (min_words, max_words)
        """
        ranges = {
            ProjectType.NOVEL: (50000, 120000),
            ProjectType.SHORT_STORY: (1000, 20000),
            ProjectType.ARTICLE_MAGAZINE: (500, 5000),
            ProjectType.ARTICLE_SOCIAL: (50, 300),
            ProjectType.POETRY: (0, 10000),  # Variable
            ProjectType.SCREENPLAY: (15000, 30000),
            ProjectType.ESSAY: (2000, 10000),
            ProjectType.RESEARCH_PAPER: (5000, 15000)
        }
        return ranges.get(self, (0, 0))

    def get_icon(self) -> str:
        """
        Get emoji icon for the project type.

        Returns:
            str: Emoji icon
        """
        icons = {
            ProjectType.NOVEL: '📚',
            ProjectType.SHORT_STORY: '📖',
            ProjectType.ARTICLE_MAGAZINE: '📰',
            ProjectType.ARTICLE_SOCIAL: '📱',
            ProjectType.POETRY: '✍️',
            ProjectType.SCREENPLAY: '🎬',
            ProjectType.ESSAY: '📝',
            ProjectType.RESEARCH_PAPER: '🔬'
        }
        return icons.get(self, '📄')

    def get_description(self, language: str = 'it') -> str:
        """
        Get a brief description of the project type.

        Args:
            language: Language code

        Returns:
            str: Description
        """
        descriptions = {
            'it': {
                'novel': 'Opera narrativa lunga con capitoli e scene complesse',
                'short_story': 'Racconto breve con trama concentrata',
                'article_magazine': 'Articolo giornalistico per pubblicazione',
                'article_social': 'Post breve per social media',
                'poetry': 'Raccolta di componimenti poetici',
                'screenplay': 'Sceneggiatura per film o serie TV',
                'essay': 'Saggio argomentativo o espositivo',
                'research_paper': 'Paper accademico con metodologia scientifica'
            },
            'en': {
                'novel': 'Long narrative work with complex chapters and scenes',
                'short_story': 'Short narrative with focused plot',
                'article_magazine': 'Journalistic article for publication',
                'article_social': 'Short post for social media',
                'poetry': 'Collection of poems',
                'screenplay': 'Script for film or TV series',
                'essay': 'Argumentative or expository essay',
                'research_paper': 'Academic paper with scientific methodology'
            }
        }

        lang_dict = descriptions.get(language, descriptions['en'])
        return lang_dict.get(self.value, '')
