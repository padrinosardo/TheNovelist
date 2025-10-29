"""
Export Manager - Coordina export in vari formati
"""
from typing import Dict, Any
from managers.project_manager import ProjectManager
from utils.logger import AppLogger


class ExportManager:
    """
    Manager principale per export progetti in vari formati.

    Supporta:
    - PDF (via ReportLab)
    - DOCX (via python-docx)
    - Markdown (plain text)

    Usage:
        success = ExportManager.export(
            project_manager,
            'pdf',
            {'include_cover': True, 'font_size': 12},
            '/path/to/output.pdf'
        )
    """

    # Mappatura formato -> classe exporter
    # Verrà popolata dopo aver implementato gli exporter specifici
    EXPORTERS = {}

    @staticmethod
    def export(project_manager: ProjectManager,
               format: str,
               options: Dict[str, Any],
               output_path: str) -> bool:
        """
        Export principale - coordina l'export nel formato richiesto

        Args:
            project_manager: ProjectManager con progetto caricato
            format: Formato export ('pdf', 'docx', 'markdown')
            options: Dizionario con opzioni di export
            output_path: Percorso file destinazione

        Returns:
            bool: True se export riuscito, False altrimenti

        Raises:
            ValueError: Se formato non supportato o progetto non caricato
        """
        try:
            # Valida che ci sia un progetto
            if not project_manager.has_project():
                AppLogger.error("Export failed: No project loaded")
                raise ValueError("No project loaded")

            # Valida formato
            format_lower = format.lower()
            if format_lower not in ExportManager.EXPORTERS:
                AppLogger.error(f"Export format not supported: {format}")
                raise ValueError(f"Unsupported export format: {format}")

            # Ottieni classe exporter
            exporter_class = ExportManager.EXPORTERS[format_lower]

            # Log inizio export
            project_title = project_manager.current_project.title
            AppLogger.info(f"Starting export: {project_title} -> {format_lower} -> {output_path}")

            # Crea istanza exporter e esegui export
            exporter = exporter_class(project_manager, options)
            success = exporter.export(output_path)

            # Log risultato
            if success:
                AppLogger.info(f"Export completed successfully: {output_path}")
            else:
                AppLogger.error(f"Export failed for: {output_path}")

            return success

        except ValueError as e:
            AppLogger.error(f"Export validation error: {e}")
            raise

        except Exception as e:
            AppLogger.error(f"Unexpected error during export: {e}", exc_info=True)
            return False

    @staticmethod
    def register_exporter(format: str, exporter_class):
        """
        Registra un nuovo exporter

        Args:
            format: Nome formato (es. 'pdf', 'docx')
            exporter_class: Classe exporter (deve ereditare da BaseExporter)
        """
        ExportManager.EXPORTERS[format.lower()] = exporter_class
        AppLogger.debug(f"Registered exporter: {format}")

    @staticmethod
    def get_supported_formats() -> list:
        """
        Ottiene lista formati supportati

        Returns:
            List[str]: Lista formati disponibili
        """
        return list(ExportManager.EXPORTERS.keys())

    @staticmethod
    def is_format_supported(format: str) -> bool:
        """
        Verifica se un formato è supportato

        Args:
            format: Nome formato da verificare

        Returns:
            bool: True se supportato
        """
        return format.lower() in ExportManager.EXPORTERS


# Importa e registra exporter quando disponibili
# Questi import verranno decommentati quando implementiamo gli exporter
try:
    from utils.exporters.pdf_exporter import PDFExporter
    ExportManager.register_exporter('pdf', PDFExporter)
except ImportError:
    AppLogger.warning("PDFExporter not available yet")

try:
    from utils.exporters.docx_exporter import DOCXExporter
    ExportManager.register_exporter('docx', DOCXExporter)
except ImportError:
    AppLogger.warning("DOCXExporter not available yet")

try:
    from utils.exporters.markdown_exporter import MarkdownExporter
    ExportManager.register_exporter('markdown', MarkdownExporter)
except ImportError:
    AppLogger.warning("MarkdownExporter not available yet")
