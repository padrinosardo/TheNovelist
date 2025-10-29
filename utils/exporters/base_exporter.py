"""
Base Exporter - Classe astratta per tutti gli exporter
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from managers.project_manager import ProjectManager


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
