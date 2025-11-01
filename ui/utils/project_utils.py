"""
Project Utilities - Helper functions for Project Info View

Includes:
- Export/Import functions for Story Context and Writing Guide
- Quick Actions (copy, swap, reset)
- Performance optimization utilities
"""
import os
from typing import Optional
from datetime import datetime


class ProjectUtils:
    """Utility functions for project operations"""

    @staticmethod
    def export_to_markdown(content: str, title: str, default_filename: str) -> Optional[str]:
        """
        Export content to markdown file

        Args:
            content: Content to export
            title: Title for the header
            default_filename: Default filename

        Returns:
            str: Path to saved file, or None if cancelled
        """
        from PySide6.QtWidgets import QFileDialog

        # Add header with metadata
        export_content = f"# {title}\n\n"
        export_content += f"**Exported**: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        export_content += "---\n\n"
        export_content += content

        # Open save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            f"Export {title}",
            os.path.expanduser(f"~/Documents/{default_filename}.md"),
            "Markdown Files (*.md);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(export_content)
                return file_path
            except Exception as e:
                print(f"Export error: {e}")
                return None

        return None

    @staticmethod
    def import_from_markdown() -> Optional[str]:
        """
        Import content from markdown file

        Returns:
            str: Imported content, or None if cancelled
        """
        from PySide6.QtWidgets import QFileDialog

        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Import Markdown",
            os.path.expanduser("~/Documents"),
            "Markdown Files (*.md);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Strip metadata header if present
                if content.startswith("# ") and "---" in content:
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        content = parts[2].strip()

                return content
            except Exception as e:
                print(f"Import error: {e}")
                return None

        return None

    @staticmethod
    def story_context_to_markdown(project) -> str:
        """
        Convert Story Context fields to Markdown format

        Args:
            project: Project instance

        Returns:
            str: Markdown formatted story context
        """
        md = "# STORY CONTEXT\n\n"

        if project.synopsis:
            md += f"## Synopsis\n\n{project.synopsis}\n\n"

        if project.setting_time_period or project.setting_location:
            md += "## Setting\n\n"
            if project.setting_time_period:
                md += f"**Time Period**: {project.setting_time_period}\n\n"
            if project.setting_location:
                md += f"**Location**: {project.setting_location}\n\n"

        if project.narrative_tone:
            md += f"## Narrative Tone\n\n{project.narrative_tone}\n\n"

        if project.narrative_pov:
            pov_labels = {
                'first_person': 'First Person',
                'third_limited': 'Third Person Limited',
                'third_omniscient': 'Third Person Omniscient',
                'multiple': 'Multiple POVs'
            }
            pov = pov_labels.get(project.narrative_pov, project.narrative_pov)
            md += f"## Point of View\n\n{pov}\n\n"

        if project.themes:
            md += f"## Themes\n\n{', '.join(project.themes)}\n\n"

        if project.target_audience:
            md += f"## Target Audience\n\n{project.target_audience}\n\n"

        if project.story_notes:
            md += f"## Story Notes\n\n{project.story_notes}\n\n"

        return md


class PerformanceUtils:
    """Performance optimization utilities"""

    @staticmethod
    def debounce(wait_ms: int):
        """
        Decorator for debouncing function calls

        Args:
            wait_ms: Milliseconds to wait before executing

        Returns:
            Decorated function
        """
        from PySide6.QtCore import QTimer

        def decorator(func):
            timer = None

            def debounced(*args, **kwargs):
                nonlocal timer
                if timer is not None:
                    timer.stop()

                timer = QTimer()
                timer.setSingleShot(True)
                timer.timeout.connect(lambda: func(*args, **kwargs))
                timer.start(wait_ms)

            return debounced

        return decorator
