"""
Chapters Preview Widget - Shows chapters in list or card view
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QScrollArea, QFrame, QGridLayout,
    QLineEdit
)
from PySide6.QtCore import Qt, Signal, QTimer, QMimeData
from PySide6.QtGui import QPalette, QFont, QDrag
from typing import List
from models.manuscript_structure import Chapter
import re


def strip_html(text: str) -> str:
    """
    Remove HTML tags from text and convert to plain text

    Args:
        text: Text possibly containing HTML

    Returns:
        Plain text without HTML tags
    """
    # Remove style and script tags and their contents
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    # Remove HTML comments
    text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
    # Remove DOCTYPE and other declarations
    text = re.sub(r'<!DOCTYPE[^>]*>', '', text, flags=re.IGNORECASE)
    # Remove all remaining HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Replace common HTML entities
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    text = text.replace('&quot;', '"')
    text = text.replace('&apos;', "'")
    # Remove multiple spaces and newlines
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


class ChapterCardWidget(QFrame):
    """Card widget for a single chapter"""

    clicked = Signal(str)  # chapter_id

    def __init__(self, chapter: Chapter, parent=None):
        super().__init__(parent)
        self.chapter = chapter
        self._setup_ui()

    def _setup_ui(self):
        """Setup card UI"""
        # Get palette colors
        palette = self.palette()
        bg_color = palette.color(QPalette.ColorRole.Base).name()
        border_color = palette.color(QPalette.ColorRole.Mid).name()
        text_color = palette.color(QPalette.ColorRole.Text).name()
        subtitle_color = palette.color(QPalette.ColorRole.PlaceholderText).name()

        self.setStyleSheet(f"""
            ChapterCardWidget {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 12px;
            }}
            ChapterCardWidget:hover {{
                border: 2px solid {palette.color(QPalette.ColorRole.Highlight).name()};
                background-color: {palette.color(QPalette.ColorRole.AlternateBase).name()};
            }}
        """)

        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(150)
        self.setMinimumWidth(200)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        # Title
        title_label = QLabel(f"📖 {self.chapter.title}")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {text_color};")
        layout.addWidget(title_label)

        # Word count
        word_count = self.chapter.get_total_word_count()
        count_label = QLabel(f"{word_count:,} words • {len(self.chapter.scenes)} scenes")
        count_label.setStyleSheet(f"color: {subtitle_color}; font-size: 11px;")
        layout.addWidget(count_label)

        # Preview text (first 130 chars from first scene)
        preview_text = self._get_preview_text()
        if preview_text:
            preview_label = QLabel(preview_text)
            preview_label.setWordWrap(True)
            preview_label.setStyleSheet(f"color: {text_color}; font-size: 12px; margin-top: 4px;")
            preview_label.setMaximumHeight(60)
            layout.addWidget(preview_label)

        layout.addStretch()

    def _get_preview_text(self) -> str:
        """Get preview text from first scene (130 chars)"""
        if not self.chapter.scenes:
            return ""

        first_scene = sorted(self.chapter.scenes, key=lambda s: s.order)[0]
        # Remove HTML tags and get plain text
        text = strip_html(first_scene.content)
        if len(text) > 130:
            return text[:130] + "..."
        return text

    def mouseDoubleClickEvent(self, event):
        """Handle double-click to open chapter"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.chapter.id)
        super().mouseDoubleClickEvent(event)


class ChaptersPreviewWidget(QWidget):
    """
    Widget to preview all chapters in list or card view
    """

    chapter_clicked = Signal(str)  # chapter_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.chapters: List[Chapter] = []
        self.filtered_chapters: List[Chapter] = []  # Filtered list for search
        self.current_view = "cards"  # Default: cards view
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header
        header_layout = QHBoxLayout()

        # Title
        title_label = QLabel("📚 Chapters")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search chapters...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self._on_search_changed)
        palette = self.palette()
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {palette.color(QPalette.ColorRole.Mid).name()};
                border-radius: 4px;
                padding: 6px 10px;
                background-color: {palette.color(QPalette.ColorRole.Base).name()};
                color: {palette.color(QPalette.ColorRole.Text).name()};
            }}
            QLineEdit:focus {{
                border: 1px solid {palette.color(QPalette.ColorRole.Highlight).name()};
            }}
        """)
        header_layout.addWidget(self.search_input)

        # View toggle buttons
        self.list_btn = QPushButton("☰ List")
        self.list_btn.setCheckable(True)
        self.list_btn.clicked.connect(lambda: self._switch_view("list"))
        self.list_btn.setFixedSize(80, 32)
        header_layout.addWidget(self.list_btn)

        self.cards_btn = QPushButton("▦ Cards")
        self.cards_btn.setCheckable(True)
        self.cards_btn.setChecked(True)  # Default checked
        self.cards_btn.clicked.connect(lambda: self._switch_view("cards"))
        self.cards_btn.setFixedSize(80, 32)
        header_layout.addWidget(self.cards_btn)

        # Style buttons
        palette = self.palette()
        btn_style = f"""
            QPushButton {{
                border: 1px solid {palette.color(QPalette.ColorRole.Mid).name()};
                border-radius: 4px;
                padding: 4px 8px;
                background-color: {palette.color(QPalette.ColorRole.Base).name()};
                color: {palette.color(QPalette.ColorRole.Text).name()};
            }}
            QPushButton:checked {{
                background-color: {palette.color(QPalette.ColorRole.Highlight).name()};
                color: {palette.color(QPalette.ColorRole.HighlightedText).name()};
                border: 1px solid {palette.color(QPalette.ColorRole.Highlight).name()};
            }}
            QPushButton:hover {{
                background-color: {palette.color(QPalette.ColorRole.AlternateBase).name()};
            }}
        """
        self.list_btn.setStyleSheet(btn_style)
        self.cards_btn.setStyleSheet(btn_style)

        layout.addLayout(header_layout)

        # Statistics bar
        stats_widget = QWidget()
        stats_widget.setStyleSheet(f"""
            QWidget {{
                background-color: {palette.color(QPalette.ColorRole.AlternateBase).name()};
                border: 1px solid {palette.color(QPalette.ColorRole.Mid).name()};
                border-radius: 4px;
                padding: 8px;
            }}
        """)
        stats_layout = QHBoxLayout(stats_widget)
        stats_layout.setContentsMargins(10, 5, 10, 5)

        # Total chapters
        self.total_chapters_label = QLabel("📚 0 chapters")
        self.total_chapters_label.setStyleSheet(f"color: {palette.color(QPalette.ColorRole.Text).name()}; background: transparent; border: none;")
        stats_layout.addWidget(self.total_chapters_label)

        # Separator
        separator1 = QLabel("•")
        separator1.setStyleSheet(f"color: {palette.color(QPalette.ColorRole.Mid).name()}; background: transparent; border: none;")
        stats_layout.addWidget(separator1)

        # Total words
        self.total_words_label = QLabel("📝 0 words")
        self.total_words_label.setStyleSheet(f"color: {palette.color(QPalette.ColorRole.Text).name()}; background: transparent; border: none;")
        stats_layout.addWidget(self.total_words_label)

        # Separator
        separator2 = QLabel("•")
        separator2.setStyleSheet(f"color: {palette.color(QPalette.ColorRole.Mid).name()}; background: transparent; border: none;")
        stats_layout.addWidget(separator2)

        # Average words per chapter
        self.avg_words_label = QLabel("📊 0 avg words/chapter")
        self.avg_words_label.setStyleSheet(f"color: {palette.color(QPalette.ColorRole.Text).name()}; background: transparent; border: none;")
        stats_layout.addWidget(self.avg_words_label)

        stats_layout.addStretch()

        layout.addWidget(stats_widget)

        # Content area (will hold list or cards view)
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.content_widget)

        # Create both views (hidden by default)
        self._create_list_view()
        self._create_cards_view()

        # Show default view
        self._switch_view("cards")

    def _create_list_view(self):
        """Create list view"""
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(4)
        # Use double-click to open chapter
        self.list_widget.itemDoubleClicked.connect(self._on_list_item_double_clicked)

        # Style
        palette = self.palette()
        self.list_widget.setStyleSheet(f"""
            QListWidget {{
                background-color: {palette.color(QPalette.ColorRole.Base).name()};
                border: 1px solid {palette.color(QPalette.ColorRole.Mid).name()};
                border-radius: 4px;
                padding: 4px;
            }}
            QListWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {palette.color(QPalette.ColorRole.Mid).name()};
            }}
            QListWidget::item:selected {{
                background-color: {palette.color(QPalette.ColorRole.Highlight).name()};
                color: {palette.color(QPalette.ColorRole.HighlightedText).name()};
            }}
            QListWidget::item:hover {{
                background-color: {palette.color(QPalette.ColorRole.AlternateBase).name()};
            }}
        """)

        self.list_widget.hide()

    def _create_cards_view(self):
        """Create cards grid view"""
        self.cards_scroll = QScrollArea()
        self.cards_scroll.setWidgetResizable(True)
        self.cards_scroll.setFrameShape(QFrame.Shape.NoFrame)

        # Container for cards
        self.cards_container = QWidget()
        self.cards_grid = QGridLayout(self.cards_container)
        self.cards_grid.setSpacing(15)
        self.cards_grid.setContentsMargins(5, 5, 5, 5)
        self.cards_grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.cards_scroll.setWidget(self.cards_container)
        self.cards_scroll.hide()

    def _switch_view(self, view_type: str):
        """Switch between list and cards view"""
        self.current_view = view_type

        # Update button states
        self.list_btn.setChecked(view_type == "list")
        self.cards_btn.setChecked(view_type == "cards")

        # Clear and re-add the appropriate view
        # Remove current widget from layout
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().hide()

        if view_type == "list":
            self.content_layout.addWidget(self.list_widget)
            self.list_widget.show()
        else:
            self.content_layout.addWidget(self.cards_scroll)
            self.cards_scroll.show()

    def load_chapters(self, chapters: List[Chapter]):
        """Load chapters into the view"""
        self.chapters = sorted(chapters, key=lambda c: c.order)
        self.filtered_chapters = self.chapters.copy()
        self._update_statistics()
        self._populate_list_view()
        self._populate_cards_view()

    def _on_search_changed(self, search_text: str):
        """Handle search text change"""
        search_text = search_text.lower().strip()

        if not search_text:
            # No search, show all chapters
            self.filtered_chapters = self.chapters.copy()
        else:
            # Filter chapters by title and content
            self.filtered_chapters = []
            for chapter in self.chapters:
                # Check if title matches
                if search_text in chapter.title.lower():
                    self.filtered_chapters.append(chapter)
                    continue

                # Check if any scene content matches
                for scene in chapter.scenes:
                    if search_text in scene.content.lower() or search_text in scene.title.lower():
                        self.filtered_chapters.append(chapter)
                        break

        # Refresh views
        self._update_statistics()
        self._populate_list_view()
        self._populate_cards_view()

    def _update_statistics(self):
        """Update statistics labels"""
        total_chapters = len(self.filtered_chapters)
        total_words = sum(chapter.get_total_word_count() for chapter in self.filtered_chapters)
        avg_words = total_words // total_chapters if total_chapters > 0 else 0

        self.total_chapters_label.setText(f"📚 {total_chapters} chapter{'s' if total_chapters != 1 else ''}")
        self.total_words_label.setText(f"📝 {total_words:,} words")
        self.avg_words_label.setText(f"📊 {avg_words:,} avg words/chapter")

    def _populate_list_view(self):
        """Populate list view with chapters"""
        self.list_widget.clear()

        for chapter in self.filtered_chapters:
            # Create custom item
            item = QListWidgetItem()

            # Get preview text (remove HTML tags)
            preview_text = ""
            if chapter.scenes:
                first_scene = sorted(chapter.scenes, key=lambda s: s.order)[0]
                text = strip_html(first_scene.content)
                if len(text) > 130:
                    preview_text = text[:130] + "..."
                else:
                    preview_text = text

            word_count = chapter.get_total_word_count()
            item_text = f"📖 {chapter.title}\n"
            item_text += f"   {word_count:,} words • {len(chapter.scenes)} scenes\n"
            if preview_text:
                item_text += f"   {preview_text}"

            item.setText(item_text)
            item.setData(Qt.ItemDataRole.UserRole, chapter.id)

            self.list_widget.addItem(item)

    def _populate_cards_view(self):
        """Populate cards grid view with chapters"""
        # Clear existing cards
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add chapter cards (3 per row)
        row = 0
        col = 0
        for chapter in self.filtered_chapters:
            card = ChapterCardWidget(chapter)
            card.clicked.connect(self.chapter_clicked.emit)
            self.cards_grid.addWidget(card, row, col)

            col += 1
            if col >= 3:  # 3 cards per row
                col = 0
                row += 1

        # Add spacer at the end
        self.cards_grid.setRowStretch(row + 1, 1)

    def _on_list_item_double_clicked(self, item: QListWidgetItem):
        """Handle list item double-click (open chapter)"""
        chapter_id = item.data(Qt.ItemDataRole.UserRole)
        if chapter_id:
            self.chapter_clicked.emit(chapter_id)
