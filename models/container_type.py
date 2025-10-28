"""
Container Type System - Dynamic containers based on project type
"""
from enum import Enum
from typing import List, Dict, Tuple


class ContainerType(Enum):
    """
    Enum representing different types of content containers available in projects.

    Containers are dynamically available based on the project type:
    - Universal containers: Available in all projects
    - Narrative containers: For novels, short stories, screenplays
    - Article containers: For magazine articles and social media posts
    - Poetry containers: For poetry collections
    - Research containers: For academic papers and essays
    """

    # ==================== Universal Containers ====================
    MANUSCRIPT = "manuscript"
    NOTES = "notes"

    # ==================== Narrative Containers ====================
    CHARACTERS = "characters"
    LOCATIONS = "locations"
    RESEARCH = "research"
    TIMELINE = "timeline"
    WORLDBUILDING = "worldbuilding"

    # ==================== Article Containers ====================
    SOURCES = "sources"
    KEYWORDS = "keywords"
    MEDIA = "media"

    # ==================== Poetry Containers ====================
    POEMS_COLLECTION = "poems_collection"
    THEMES = "themes"

    # ==================== Screenplay Containers ====================
    SCENES_DB = "scenes_db"

    # ==================== Research/Academic Containers ====================
    REFERENCES = "references"
    DATA = "data"

    @staticmethod
    def get_available_for_project_type(project_type) -> List['ContainerType']:
        """
        Get list of available containers for a specific project type.

        Args:
            project_type: ProjectType enum value

        Returns:
            List[ContainerType]: List of available container types
        """
        # Import here to avoid circular dependency
        from models.project_type import ProjectType

        # Mapping of project types to their available containers
        container_mapping = {
            ProjectType.NOVEL: [
                ContainerType.MANUSCRIPT,
                ContainerType.CHARACTERS,
                ContainerType.LOCATIONS,
                ContainerType.RESEARCH,
                ContainerType.TIMELINE,
                ContainerType.WORLDBUILDING,
                ContainerType.NOTES
            ],

            ProjectType.SHORT_STORY: [
                ContainerType.MANUSCRIPT,
                ContainerType.CHARACTERS,
                ContainerType.LOCATIONS,
                ContainerType.NOTES
            ],

            ProjectType.ARTICLE_MAGAZINE: [
                ContainerType.MANUSCRIPT,
                ContainerType.SOURCES,
                ContainerType.KEYWORDS,
                ContainerType.NOTES
            ],

            ProjectType.ARTICLE_SOCIAL: [
                ContainerType.MANUSCRIPT,
                ContainerType.KEYWORDS,
                ContainerType.MEDIA,
                ContainerType.NOTES
            ],

            ProjectType.POETRY: [
                ContainerType.POEMS_COLLECTION,
                ContainerType.THEMES,
                ContainerType.NOTES
            ],

            ProjectType.SCREENPLAY: [
                ContainerType.MANUSCRIPT,
                ContainerType.CHARACTERS,
                ContainerType.LOCATIONS,
                ContainerType.SCENES_DB,
                ContainerType.NOTES
            ],

            ProjectType.ESSAY: [
                ContainerType.MANUSCRIPT,
                ContainerType.SOURCES,
                ContainerType.NOTES
            ],

            ProjectType.RESEARCH_PAPER: [
                ContainerType.MANUSCRIPT,
                ContainerType.SOURCES,
                ContainerType.REFERENCES,
                ContainerType.DATA,
                ContainerType.NOTES
            ]
        }

        # Return containers for the project type, or default minimal set
        return container_mapping.get(
            project_type,
            [ContainerType.MANUSCRIPT, ContainerType.NOTES]
        )

    @staticmethod
    def get_display_info(container_type: 'ContainerType', language: str = 'it') -> Tuple[str, str]:
        """
        Get display information (icon and name) for a container type.

        Args:
            container_type: The container type
            language: Language code for localization

        Returns:
            Tuple[str, str]: (icon, localized_name)
        """
        # Icon and name mappings
        display_data = {
            ContainerType.MANUSCRIPT: {
                'icon': '📄',
                'names': {
                    'it': 'Manoscritto',
                    'en': 'Manuscript',
                    'es': 'Manuscrito',
                    'fr': 'Manuscrit',
                    'de': 'Manuskript'
                }
            },
            ContainerType.CHARACTERS: {
                'icon': '👤',
                'names': {
                    'it': 'Personaggi',
                    'en': 'Characters',
                    'es': 'Personajes',
                    'fr': 'Personnages',
                    'de': 'Charaktere'
                }
            },
            ContainerType.LOCATIONS: {
                'icon': '🗺️',
                'names': {
                    'it': 'Luoghi',
                    'en': 'Locations',
                    'es': 'Lugares',
                    'fr': 'Lieux',
                    'de': 'Orte'
                }
            },
            ContainerType.RESEARCH: {
                'icon': '🔍',
                'names': {
                    'it': 'Ricerche',
                    'en': 'Research',
                    'es': 'Investigación',
                    'fr': 'Recherche',
                    'de': 'Forschung'
                }
            },
            ContainerType.TIMELINE: {
                'icon': '⏱️',
                'names': {
                    'it': 'Timeline',
                    'en': 'Timeline',
                    'es': 'Cronología',
                    'fr': 'Chronologie',
                    'de': 'Zeitlinie'
                }
            },
            ContainerType.WORLDBUILDING: {
                'icon': '🌍',
                'names': {
                    'it': 'Worldbuilding',
                    'en': 'Worldbuilding',
                    'es': 'Construcción de Mundo',
                    'fr': 'Univers',
                    'de': 'Weltenbau'
                }
            },
            ContainerType.NOTES: {
                'icon': '📝',
                'names': {
                    'it': 'Note',
                    'en': 'Notes',
                    'es': 'Notas',
                    'fr': 'Notes',
                    'de': 'Notizen'
                }
            },
            ContainerType.SOURCES: {
                'icon': '🔗',
                'names': {
                    'it': 'Fonti',
                    'en': 'Sources',
                    'es': 'Fuentes',
                    'fr': 'Sources',
                    'de': 'Quellen'
                }
            },
            ContainerType.KEYWORDS: {
                'icon': '#️⃣',
                'names': {
                    'it': 'Keywords',
                    'en': 'Keywords',
                    'es': 'Palabras Clave',
                    'fr': 'Mots-clés',
                    'de': 'Schlüsselwörter'
                }
            },
            ContainerType.MEDIA: {
                'icon': '🖼️',
                'names': {
                    'it': 'Media',
                    'en': 'Media',
                    'es': 'Medios',
                    'fr': 'Médias',
                    'de': 'Medien'
                }
            },
            ContainerType.THEMES: {
                'icon': '🎭',
                'names': {
                    'it': 'Temi',
                    'en': 'Themes',
                    'es': 'Temas',
                    'fr': 'Thèmes',
                    'de': 'Themen'
                }
            },
            ContainerType.POEMS_COLLECTION: {
                'icon': '📖',
                'names': {
                    'it': 'Raccolta Poesie',
                    'en': 'Poetry Collection',
                    'es': 'Colección de Poesía',
                    'fr': 'Recueil de Poésie',
                    'de': 'Gedichtsammlung'
                }
            },
            ContainerType.SCENES_DB: {
                'icon': '🎬',
                'names': {
                    'it': 'Database Scene',
                    'en': 'Scenes Database',
                    'es': 'Base de Escenas',
                    'fr': 'Base de Scènes',
                    'de': 'Szenen-Datenbank'
                }
            },
            ContainerType.REFERENCES: {
                'icon': '📚',
                'names': {
                    'it': 'Riferimenti',
                    'en': 'References',
                    'es': 'Referencias',
                    'fr': 'Références',
                    'de': 'Referenzen'
                }
            },
            ContainerType.DATA: {
                'icon': '📊',
                'names': {
                    'it': 'Dati',
                    'en': 'Data',
                    'es': 'Datos',
                    'fr': 'Données',
                    'de': 'Daten'
                }
            }
        }

        info = display_data.get(container_type)
        if not info:
            return ('📦', container_type.value.title())

        icon = info['icon']
        name = info['names'].get(language, info['names']['en'])

        return (icon, name)

    @staticmethod
    def get_filename(container_type: 'ContainerType') -> str:
        """
        Get the JSON filename for a container type.

        Args:
            container_type: The container type

        Returns:
            str: Filename (e.g., 'locations.json')
        """
        filename_map = {
            ContainerType.CHARACTERS: 'characters.json',
            ContainerType.LOCATIONS: 'locations.json',
            ContainerType.RESEARCH: 'research.json',
            ContainerType.TIMELINE: 'timeline.json',
            ContainerType.WORLDBUILDING: 'worldbuilding.json',
            ContainerType.NOTES: 'notes.json',
            ContainerType.SOURCES: 'sources.json',
            ContainerType.KEYWORDS: 'keywords.json',
            ContainerType.MEDIA: 'media.json',
            ContainerType.THEMES: 'themes.json',
            ContainerType.POEMS_COLLECTION: 'poems.json',
            ContainerType.SCENES_DB: 'scenes_db.json',
            ContainerType.REFERENCES: 'references.json',
            ContainerType.DATA: 'data.json'
        }

        return filename_map.get(container_type, f'{container_type.value}.json')
