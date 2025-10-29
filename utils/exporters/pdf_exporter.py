"""
PDF Exporter - Export in formato PDF con ReportLab
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                PageBreak, Table, TableStyle)
from reportlab.lib import colors
from datetime import datetime
import re
from html.parser import HTMLParser

from utils.exporters.base_exporter import BaseExporter
from utils.logger import AppLogger


class HTMLToReportLabConverter(HTMLParser):
    """Convert HTML to ReportLab-compatible markup"""

    def __init__(self):
        super().__init__()
        self.result = []
        self.current_text = ""
        self.ignore_content = False  # Flag to ignore content in <style>, <head>, etc.
        self.format_stack = []  # Track which formats are active for span tags

    def handle_starttag(self, tag, attrs):
        # Ignore content in style and head tags
        if tag in ['style', 'head', 'script']:
            self.ignore_content = True
            return

        # Ignore structural tags
        if tag in ['html', 'body']:
            return

        # Map HTML tags to ReportLab tags
        if tag in ['b', 'strong']:
            self.current_text += '<b>'
        elif tag in ['i', 'em']:
            self.current_text += '<i>'
        elif tag == 'u':
            self.current_text += '<u>'
        elif tag == 'br':
            self.current_text += '<br/>'
        elif tag == 'span':
            # Handle Qt-style inline formatting with <span style="...">
            style_dict = dict(attrs)
            style_str = style_dict.get('style', '')

            # Check for bold (font-weight:700 or font-weight:bold)
            if 'font-weight:700' in style_str or 'font-weight:bold' in style_str:
                self.current_text += '<b>'
                self.format_stack.append('bold')

            # Check for italic
            if 'font-style:italic' in style_str:
                self.current_text += '<i>'
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

        if tag in ['b', 'strong']:
            self.current_text += '</b>'
        elif tag in ['i', 'em']:
            self.current_text += '</i>'
        elif tag == 'u':
            self.current_text += '</u>'
        elif tag == 'span':
            # Close any formatting opened by this span (in reverse order)
            while self.format_stack:
                fmt = self.format_stack.pop()
                if fmt == 'bold':
                    self.current_text += '</b>'
                elif fmt == 'italic':
                    self.current_text += '</i>'
                elif fmt == 'underline':
                    self.current_text += '</u>'
        elif tag == 'p':
            # Paragraph end
            if self.current_text.strip():
                self.result.append(self.current_text.strip())
                self.current_text = ""

    def handle_data(self, data):
        # Ignore data if we're in a style/head tag
        if self.ignore_content:
            return

        # Always add data to preserve spacing
        if data:
            # Escape special characters for ReportLab (but NOT the formatting tags we add)
            # Note: We escape the text content, not our markup
            escaped = data.replace('&', '&amp;')
            escaped = escaped.replace('<', '&lt;')
            escaped = escaped.replace('>', '&gt;')
            self.current_text += escaped

    def get_result(self):
        # Add any remaining text
        if self.current_text.strip():
            self.result.append(self.current_text.strip())
        return self.result


class PDFExporter(BaseExporter):
    """
    Export PDF con formattazione professionale.

    Supporta:
    - Frontespizio
    - Indice capitoli
    - Formattazione per tipologia progetto
    - Margini e font personalizzabili
    """

    def export(self, output_path: str) -> bool:
        """
        Export in PDF

        Args:
            output_path: Percorso file PDF destinazione

        Returns:
            bool: True se successo
        """
        try:
            AppLogger.info(f"PDF Export: Starting export to {output_path}")

            # Crea documento PDF
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=self._get_option('margin_right', 2.5) * cm,
                leftMargin=self._get_option('margin_left', 2.5) * cm,
                topMargin=self._get_option('margin_top', 2.5) * cm,
                bottomMargin=self._get_option('margin_bottom', 2.5) * cm,
            )

            # Prepara contenuto
            story = []

            # Aggiungi cover page
            if self._get_option('include_cover', True):
                self._add_cover_page(story)
                story.append(PageBreak())

            # Aggiungi table of contents
            if self._get_option('include_toc', True):
                self._add_table_of_contents(story)
                story.append(PageBreak())

            # Aggiungi contenuto capitoli e scene
            self._add_manuscript_content(story)

            # Costruisci PDF
            doc.build(story)

            AppLogger.info(f"PDF Export completed successfully: {output_path}")
            return True

        except Exception as e:
            AppLogger.error(f"PDF Export failed: {e}", exc_info=True)
            return False

    def _get_styles(self):
        """
        Ottiene gli stili personalizzati per il PDF

        Returns:
            dict: Dizionario di stili
        """
        styles = getSampleStyleSheet()

        # Stile titolo cover
        styles.add(ParagraphStyle(
            name='CoverTitle',
            parent=styles['Heading1'],
            fontSize=28,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Stile autore cover
        styles.add(ParagraphStyle(
            name='CoverAuthor',
            parent=styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))

        # Stile info cover
        styles.add(ParagraphStyle(
            name='CoverInfo',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#7f8c8d'),
            spaceAfter=8,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))

        # Stile titolo capitolo
        styles.add(ParagraphStyle(
            name='ChapterTitle',
            parent=styles['Heading1'],
            fontSize=self._get_option('chapter_font_size', 20),
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=20,
            spaceBefore=30,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))

        # Stile titolo scena
        styles.add(ParagraphStyle(
            name='SceneTitle',
            parent=styles['Heading2'],
            fontSize=self._get_option('scene_font_size', 14),
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=20,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))

        # Stile contenuto scena
        styles.add(ParagraphStyle(
            name='SceneContent',
            parent=styles['Normal'],
            fontSize=self._get_option('content_font_size', 11),
            textColor=colors.black,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            fontName='Times-Roman',
            leading=16
        ))

        # Stile TOC
        styles.add(ParagraphStyle(
            name='TOCTitle',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=20,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        styles.add(ParagraphStyle(
            name='TOCEntry',
            parent=styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=8,
            alignment=TA_LEFT,
            fontName='Helvetica'
        ))

        return styles

    def _add_cover_page(self, story):
        """
        Aggiunge la pagina di copertina

        Args:
            story: Lista elementi del documento
        """
        styles = self._get_styles()

        # Spazio iniziale
        story.append(Spacer(1, 5 * cm))

        # Titolo
        title = Paragraph(self.project.title, styles['CoverTitle'])
        story.append(title)
        story.append(Spacer(1, 1 * cm))

        # Autore
        if self.project.author:
            author = Paragraph(f"by {self.project.author}", styles['CoverAuthor'])
            story.append(author)
            story.append(Spacer(1, 2 * cm))

        # Info progetto
        if self.project.project_type:
            # Convert ProjectType enum to string
            project_type_str = self.project.project_type.get_display_name(self.project.language) if hasattr(self.project.project_type, 'get_display_name') else str(self.project.project_type.value)
            project_type = Paragraph(project_type_str, styles['CoverInfo'])
            story.append(project_type)

        if self.project.genre:
            genre = Paragraph(self.project.genre, styles['CoverInfo'])
            story.append(genre)

        # Data
        story.append(Spacer(1, 2 * cm))
        export_date = datetime.now().strftime("%d %B %Y")
        date_para = Paragraph(export_date, styles['CoverInfo'])
        story.append(date_para)

        AppLogger.debug("Added cover page to PDF")

    def _add_table_of_contents(self, story):
        """
        Aggiunge l'indice dei capitoli

        Args:
            story: Lista elementi del documento
        """
        styles = self._get_styles()
        chapters = self._get_chapters()

        # Titolo TOC
        toc_title = Paragraph("Table of Contents", styles['TOCTitle'])
        story.append(toc_title)
        story.append(Spacer(1, 1 * cm))

        # Lista capitoli
        for i, chapter in enumerate(chapters, 1):
            chapter_title = chapter.title or f"Chapter {i}"
            scene_count = len(chapter.scenes)

            toc_text = f"Chapter {i}: {chapter_title}"
            if scene_count > 0:
                toc_text += f" ({scene_count} scene{'s' if scene_count != 1 else ''})"

            toc_entry = Paragraph(toc_text, styles['TOCEntry'])
            story.append(toc_entry)

        AppLogger.debug(f"Added table of contents with {len(chapters)} chapters")

    def _add_manuscript_content(self, story):
        """
        Aggiunge il contenuto del manoscritto (capitoli e scene)

        Args:
            story: Lista elementi del documento
        """
        styles = self._get_styles()
        chapters = self._get_chapters()

        for i, chapter in enumerate(chapters, 1):
            # Titolo capitolo
            chapter_title = chapter.title or f"Chapter {i}"
            chapter_para = Paragraph(f"Chapter {i}: {chapter_title}", styles['ChapterTitle'])
            story.append(chapter_para)

            # Scene del capitolo
            for j, scene in enumerate(chapter.scenes, 1):
                # Titolo scena
                scene_title = scene.title or f"Scene {j}"
                scene_para = Paragraph(scene_title, styles['SceneTitle'])
                story.append(scene_para)

                # Contenuto scena
                if scene.content:
                    # Check if content is HTML (from rich text editor)
                    if scene.content.strip().startswith('<') or '<html>' in scene.content.lower():
                        # Convert HTML to ReportLab-compatible markup
                        converter = HTMLToReportLabConverter()
                        converter.feed(scene.content)
                        paragraphs = converter.get_result()

                        for paragraph_text in paragraphs:
                            if paragraph_text.strip():
                                content_para = Paragraph(paragraph_text, styles['SceneContent'])
                                story.append(content_para)
                    else:
                        # Plain text - preserve original logic
                        paragraphs = scene.content.split('\n\n')
                        for paragraph_text in paragraphs:
                            if paragraph_text.strip():
                                # Escape caratteri speciali per ReportLab
                                clean_text = self._escape_xml(paragraph_text.strip())
                                # Sostituisci newline singoli con <br/> per preservare gli accapo
                                clean_text = clean_text.replace('\n', '<br/>')
                                content_para = Paragraph(clean_text, styles['SceneContent'])
                                story.append(content_para)
                else:
                    # Placeholder se scena vuota
                    story.append(Paragraph("[Scene content not yet written]", styles['SceneContent']))

                # Spazio tra scene
                if j < len(chapter.scenes):
                    story.append(Spacer(1, 0.5 * cm))

            # Page break tra capitoli (se richiesto)
            if self._get_option('chapter_page_break', True) and i < len(chapters):
                story.append(PageBreak())

        AppLogger.debug(f"Added manuscript content: {len(chapters)} chapters")

    def _escape_xml(self, text: str) -> str:
        """
        Escape caratteri speciali per XML/ReportLab

        Args:
            text: Testo da escape

        Returns:
            str: Testo con escape
        """
        if not text:
            return ""

        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        return text
