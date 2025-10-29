"""
Markdown Exporter - Export in formato Markdown
"""
from datetime import datetime
from html.parser import HTMLParser
import re
from utils.exporters.base_exporter import BaseExporter
from utils.logger import AppLogger


class HTMLToMarkdownConverter(HTMLParser):
    """Convert HTML to Markdown syntax"""

    def __init__(self):
        super().__init__()
        self.result = []
        self.current_text = ""
        self.format_stack = []
        self.ignore_content = False  # Flag to ignore content in <style>, <head>, etc.

    def handle_starttag(self, tag, attrs):
        # Ignore content in style and head tags
        if tag in ['style', 'head', 'script']:
            self.ignore_content = True
            return

        # Ignore structural tags
        if tag in ['html', 'body']:
            return

        if tag in ['b', 'strong']:
            self.current_text += '**'
            self.format_stack.append('bold')
        elif tag in ['i', 'em']:
            self.current_text += '*'
            self.format_stack.append('italic')
        elif tag == 'u':
            # Markdown doesn't have underline, use HTML tag
            self.current_text += '<u>'
            self.format_stack.append('underline')
        elif tag == 'br':
            self.current_text += '  \n'  # Markdown line break
        elif tag == 'span':
            # Handle Qt-style inline formatting with <span style="...">
            style_dict = dict(attrs)
            style_str = style_dict.get('style', '')

            # Check for bold (font-weight:700 or font-weight:bold)
            if 'font-weight:700' in style_str or 'font-weight:bold' in style_str:
                self.current_text += '**'
                self.format_stack.append('bold')

            # Check for italic
            if 'font-style:italic' in style_str:
                self.current_text += '*'
                self.format_stack.append('italic')

            # Check for underline
            if 'text-decoration: underline' in style_str:
                self.current_text += '<u>'
                self.format_stack.append('underline')

    def handle_endtag(self, tag):
        # Re-enable content after style/head tags
        if tag in ['style', 'head', 'script']:
            self.ignore_content = False
            return

        # Ignore structural tags
        if tag in ['html', 'body']:
            return

        if tag in ['b', 'strong'] and 'bold' in self.format_stack:
            self.current_text += '**'
            self.format_stack.remove('bold')
        elif tag in ['i', 'em'] and 'italic' in self.format_stack:
            self.current_text += '*'
            self.format_stack.remove('italic')
        elif tag == 'u' and 'underline' in self.format_stack:
            self.current_text += '</u>'
            self.format_stack.remove('underline')
        elif tag == 'span':
            # Close any formatting opened by this span (in reverse order)
            while self.format_stack:
                fmt = self.format_stack.pop()
                if fmt == 'bold':
                    self.current_text += '**'
                elif fmt == 'italic':
                    self.current_text += '*'
                elif fmt == 'underline':
                    self.current_text += '</u>'
        elif tag == 'p':
            if self.current_text.strip():
                self.result.append(self.current_text.strip())
                self.current_text = ""

    def handle_data(self, data):
        # Ignore data if we're in a style/head tag
        if self.ignore_content:
            return

        # Always add data to preserve spacing
        if data:
            self.current_text += data

    def get_result(self):
        if self.current_text.strip():
            self.result.append(self.current_text.strip())
        return '\n\n'.join(self.result)


class MarkdownExporter(BaseExporter):
    """
    Export Markdown per web/blog.

    Supporta:
    - Formato plain text
    - Syntax highlighting ready
    - Frontmatter (Jekyll/Hugo)
    """

    def export(self, output_path: str) -> bool:
        """
        Export in Markdown

        Args:
            output_path: Percorso file Markdown destinazione

        Returns:
            bool: True se successo
        """
        try:
            AppLogger.info(f"Markdown Export: Starting export to {output_path}")

            # Prepara contenuto Markdown
            content_parts = []

            # Aggiungi frontmatter YAML
            if self._get_option('include_frontmatter', True):
                content_parts.append(self._generate_frontmatter())
                content_parts.append("\n\n")

            # Aggiungi titolo e info progetto
            if self._get_option('include_header', True):
                content_parts.append(self._generate_header())
                content_parts.append("\n\n")

            # Aggiungi table of contents
            if self._get_option('include_toc', True):
                content_parts.append(self._generate_toc())
                content_parts.append("\n\n")

            # Aggiungi contenuto capitoli e scene
            content_parts.append(self._generate_manuscript_content())

            # Scrivi file
            markdown_content = ''.join(content_parts)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            AppLogger.info(f"Markdown Export completed successfully: {output_path}")
            return True

        except Exception as e:
            AppLogger.error(f"Markdown Export failed: {e}", exc_info=True)
            return False

    def _generate_frontmatter(self) -> str:
        """
        Genera frontmatter YAML per Jekyll/Hugo

        Returns:
            str: Frontmatter YAML
        """
        parts = ["---"]

        # Titolo
        parts.append(f"title: \"{self.project.title}\"")

        # Autore
        if self.project.author:
            parts.append(f"author: \"{self.project.author}\"")

        # Metadata progetto
        if self.project.project_type:
            # Convert ProjectType enum to string
            project_type_str = self.project.project_type.get_display_name(self.project.language) if hasattr(self.project.project_type, 'get_display_name') else str(self.project.project_type.value)
            parts.append(f"type: \"{project_type_str}\"")

        if self.project.genre:
            parts.append(f"genre: \"{self.project.genre}\"")

        if self.project.language:
            parts.append(f"language: \"{self.project.language}\"")

        # Data export
        export_date = datetime.now().strftime("%Y-%m-%d")
        parts.append(f"date: {export_date}")

        # Statistiche
        word_count = self._get_total_word_count()
        chapter_count = self._get_chapter_count()
        parts.append(f"word_count: {word_count}")
        parts.append(f"chapters: {chapter_count}")

        # Tag se presenti
        if hasattr(self.project, 'tags') and self.project.tags:
            tags_str = ', '.join(self.project.tags)
            parts.append(f"tags: [{tags_str}]")

        parts.append("---")

        AppLogger.debug("Generated YAML frontmatter")
        return '\n'.join(parts)

    def _generate_header(self) -> str:
        """
        Genera header del documento con titolo e info

        Returns:
            str: Header Markdown
        """
        parts = []

        # Titolo principale
        parts.append(f"# {self.project.title}")
        parts.append("")

        # Autore
        if self.project.author:
            parts.append(f"**by {self.project.author}**")
            parts.append("")

        # Info progetto
        info_parts = []
        if self.project.project_type:
            # Convert ProjectType enum to string
            project_type_str = self.project.project_type.get_display_name(self.project.language) if hasattr(self.project.project_type, 'get_display_name') else str(self.project.project_type.value)
            info_parts.append(f"*{project_type_str}*")
        if self.project.genre:
            info_parts.append(f"*{self.project.genre}*")

        if info_parts:
            parts.append(" | ".join(info_parts))
            parts.append("")

        # Statistiche
        word_count = self._get_total_word_count()
        chapter_count = self._get_chapter_count()
        parts.append(f"📊 **{word_count:,} words** | **{chapter_count} chapters**")

        # Data export
        export_date = datetime.now().strftime("%B %d, %Y")
        parts.append(f"📅 Exported: {export_date}")

        AppLogger.debug("Generated document header")
        return '\n'.join(parts)

    def _generate_toc(self) -> str:
        """
        Genera table of contents

        Returns:
            str: TOC Markdown
        """
        parts = []
        chapters = self._get_chapters()

        parts.append("## Table of Contents")
        parts.append("")

        for i, chapter in enumerate(chapters, 1):
            chapter_title = chapter.title or f"Chapter {i}"
            scene_count = len(chapter.scenes)

            # Crea link anchor (slug-style)
            anchor = self._create_anchor(f"chapter-{i}-{chapter_title}")

            toc_line = f"{i}. [Chapter {i}: {chapter_title}](#{anchor})"
            if scene_count > 0:
                toc_line += f" *({scene_count} scene{'s' if scene_count != 1 else ''})*"

            parts.append(toc_line)

        parts.append("")
        parts.append("---")

        AppLogger.debug(f"Generated table of contents with {len(chapters)} chapters")
        return '\n'.join(parts)

    def _generate_manuscript_content(self) -> str:
        """
        Genera il contenuto del manoscritto in Markdown

        Returns:
            str: Contenuto Markdown
        """
        parts = []
        chapters = self._get_chapters()
        use_scene_separators = self._get_option('scene_separators', True)
        separator_style = self._get_option('separator_style', '* * *')

        for i, chapter in enumerate(chapters, 1):
            # Titolo capitolo (Heading 2)
            chapter_title = chapter.title or f"Chapter {i}"
            parts.append(f"## Chapter {i}: {chapter_title}")
            parts.append("")

            # Scene del capitolo
            for j, scene in enumerate(chapter.scenes, 1):
                # Titolo scena (Heading 3)
                scene_title = scene.title or f"Scene {j}"
                parts.append(f"### {scene_title}")
                parts.append("")

                # Contenuto scena
                if scene.content:
                    # Check if content is HTML (from rich text editor)
                    if scene.content.strip().startswith('<') or '<html>' in scene.content.lower():
                        # Convert HTML to Markdown
                        converter = HTMLToMarkdownConverter()
                        converter.feed(scene.content)
                        markdown_content = converter.get_result()
                        if markdown_content.strip():
                            parts.append(markdown_content)
                            parts.append("")
                    else:
                        # Plain text - preserve original logic
                        paragraphs = scene.content.split('\n\n')
                        for paragraph in paragraphs:
                            if paragraph.strip():
                                # Preserva newline singoli all'interno dei paragrafi
                                parts.append(paragraph.strip())
                                parts.append("")
                else:
                    # Placeholder se scena vuota
                    parts.append("*[Scene content not yet written]*")
                    parts.append("")

                # Separatore tra scene (se non è l'ultima scena)
                if use_scene_separators and j < len(chapter.scenes):
                    parts.append(separator_style)
                    parts.append("")

            # Separatore tra capitoli (se non è l'ultimo capitolo)
            if i < len(chapters):
                parts.append("\n---\n")

        AppLogger.debug(f"Generated manuscript content: {len(chapters)} chapters")
        return '\n'.join(parts)

    def _create_anchor(self, text: str) -> str:
        """
        Crea un anchor slug per i link TOC

        Args:
            text: Testo da convertire in anchor

        Returns:
            str: Anchor slug
        """
        # Converti in lowercase
        slug = text.lower()

        # Sostituisci spazi con trattini
        slug = slug.replace(' ', '-')

        # Rimuovi caratteri speciali (mantieni solo lettere, numeri e trattini)
        slug = ''.join(c for c in slug if c.isalnum() or c == '-')

        # Rimuovi trattini multipli
        while '--' in slug:
            slug = slug.replace('--', '-')

        # Rimuovi trattini iniziali/finali
        slug = slug.strip('-')

        return slug
