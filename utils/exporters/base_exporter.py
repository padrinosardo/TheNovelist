"""
Base Exporter - Classe astratta per tutti gli exporter
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from managers.project_manager import ProjectManager
from models.project_type import ProjectType


class BaseExporter(ABC):
    """
    Classe base astratta per tutti gli exporter.

    Ogni exporter specifico (PDF, DOCX, Markdown) deve ereditare da questa classe
    e implementare il metodo export().
    """

    def __init__(self, project_manager: ProjectManager, options: Dict[str, Any]):
        """
        Inizializza l'exporter

        Args:
            project_manager: ProjectManager con progetto caricato
            options: Dizionario con opzioni di export
        """
        self.project_manager = project_manager
        self.project = project_manager.current_project
        self.options = options

        # Valida che ci sia un progetto
        if not self.project:
            raise ValueError("No project loaded in ProjectManager")

    @abstractmethod
    def export(self, output_path: str) -> bool:
        """
        Metodo astratto per export - deve essere implementato dalle sottoclassi

        Args:
            output_path: Percorso file destinazione

        Returns:
            bool: True se export riuscito, False altrimenti
        """
        pass

    def _get_manuscript_content(self) -> str:
        """
        Ottiene tutto il contenuto del manoscritto come testo unico

        Returns:
            str: Contenuto completo del manoscritto
        """
        return self.project_manager.manuscript_structure_manager.get_full_manuscript_text()

    def _get_chapters(self):
        """
        Ottiene lista di tutti i capitoli con le loro scene

        Returns:
            List[Chapter]: Lista di capitoli dal manuscript structure
        """
        manuscript_structure = self.project_manager.manuscript_structure_manager.structure
        return manuscript_structure.chapters

    def _get_chapter_count(self) -> int:
        """
        Ottiene numero di capitoli

        Returns:
            int: Numero di capitoli
        """
        return len(self._get_chapters())

    def _get_total_word_count(self) -> int:
        """
        Ottiene conteggio parole totale del manoscritto

        Returns:
            int: Numero totale di parole
        """
        manuscript_structure = self.project_manager.manuscript_structure_manager.structure
        return manuscript_structure.get_total_word_count()

    def _get_option(self, key: str, default=None):
        """
        Ottiene opzione con valore di default

        Args:
            key: Chiave opzione
            default: Valore default se chiave non esiste

        Returns:
            Valore dell'opzione o default
        """
        return self.options.get(key, default)

    def get_type_specific_formatting(self) -> Dict[str, Any]:
        """
        Get formatting options specific to the project type

        Returns:
            dict: Type-specific formatting options
        """
        project_type = self.project.project_type

        # Default options for all types
        formatting = {
            'font_family': 'Times-Roman',
            'font_size': 11,
            'line_spacing': 1.5,
            'paragraph_spacing': 12,
            'chapter_starts_new_page': True,
            'include_page_numbers': True,
            'align_text': 'justify'
        }

        # Type-specific overrides
        if project_type == ProjectType.NOVEL:
            formatting.update({
                'font_family': 'Times-Roman',
                'font_size': 12,
                'line_spacing': 2.0,  # Double spacing for novels
                'paragraph_spacing': 0,  # Minimal paragraph spacing, rely on line spacing
                'first_line_indent': True,
                'chapter_starts_new_page': True,
                'chapter_numbering_style': 'Chapter {n}',
                'scene_separator': '* * *'
            })

        elif project_type == ProjectType.SHORT_STORY:
            formatting.update({
                'font_family': 'Times-Roman',
                'font_size': 12,
                'line_spacing': 2.0,
                'chapter_starts_new_page': False,  # Short stories don't need page breaks
                'scene_separator': '# # #'
            })

        elif project_type == ProjectType.SCREENPLAY:
            formatting.update({
                'font_family': 'Courier',  # Screenplays use Courier
                'font_size': 12,
                'line_spacing': 1.0,  # Single spacing
                'margin_left': 1.5,  # Specific margins for screenplay format
                'margin_right': 1.0,
                'align_text': 'left',  # Left-aligned for screenplays
                'scene_heading_uppercase': True,
                'dialogue_indent': 2.5,
                'character_name_indent': 3.7,
                'parenthetical_indent': 3.1
            })

        elif project_type in [ProjectType.ARTICLE_MAGAZINE, ProjectType.ARTICLE_SOCIAL]:
            formatting.update({
                'font_family': 'Helvetica',  # Modern font for articles
                'font_size': 11,
                'line_spacing': 1.3,
                'paragraph_spacing': 15,
                'chapter_starts_new_page': False,
                'include_byline': True,
                'include_date': True,
                'align_text': 'left' if project_type == ProjectType.ARTICLE_SOCIAL else 'justify'
            })

        elif project_type == ProjectType.ESSAY:
            formatting.update({
                'font_family': 'Times-Roman',
                'font_size': 12,
                'line_spacing': 2.0,  # Double spacing for academic
                'paragraph_spacing': 0,
                'first_line_indent': True,
                'include_word_count': True,
                'chapter_starts_new_page': False
            })

        elif project_type == ProjectType.RESEARCH_PAPER:
            formatting.update({
                'font_family': 'Times-Roman',
                'font_size': 12,
                'line_spacing': 2.0,  # Double spacing for academic
                'paragraph_spacing': 0,
                'include_abstract': True,
                'include_references': True,
                'include_page_numbers': True,
                'section_numbering': True,
                'chapter_starts_new_page': False
            })

        elif project_type == ProjectType.POETRY:
            formatting.update({
                'font_family': 'Times-Roman',
                'font_size': 11,
                'line_spacing': 1.5,
                'align_text': 'left',  # Poetry is usually left-aligned
                'preserve_line_breaks': True,
                'center_titles': True,
                'chapter_starts_new_page': True,  # Each poem on new page
                'stanza_spacing': 20
            })

        return formatting
