"""
Scenes Preview Widget - Shows scenes in list or card view
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QListWidget, QListWidgetItem, QScrollArea, QFrame, QGridLayout,
    QLineEdit
)
from PySide6.QtCore import Qt, Signal, QMimeData
from PySide6.QtGui import QPalette, QFont, QDrag
from typing import List
from models.manuscript_structure import Scene
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


class SceneCardWidget(QFrame):
    """Card widget for a single scene"""

    clicked = Signal(str)  # scene_id

    def __init__(self, scene: Scene, parent=None):
        super().__init__(parent)
        self.scene = scene
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
            SceneCardWidget {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 12px;
            }}
            SceneCardWidget:hover {{
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
        title_label = QLabel(f"📝 {self.scene.title}")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {text_color};")
        layout.addWidget(title_label)

        # Word count
        count_label = QLabel(f"{self.scene.word_count:,} words")
        count_label.setStyleSheet(f"color: {subtitle_color}; font-size: 11px;")
        layout.addWidget(count_label)

        # Preview text (first 130 chars)
        preview_text = self._get_preview_text()
        if preview_text:
            preview_label = QLabel(preview_text)
            preview_label.setWordWrap(True)
            preview_label.setStyleSheet(f"color: {text_color}; font-size: 12px; margin-top: 4px;")
            preview_label.setMaximumHeight(60)
            layout.addWidget(preview_label)

        layout.addStretch()

    def _get_preview_text(self) -> str:
        """Get preview text (130 chars)"""
        # Remove HTML tags and get plain text
        text = strip_html(self.scene.content)
        if len(text) > 130:
            return text[:130] + "..."
        return text

    def mouseDoubleClickEvent(self, event):
        """Handle double-click to open scene"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.scene.id)
        super().mouseDoubleClickEvent(event)


class ScenesPreviewWidget(QWidget):
    """
    Widget to preview all scenes of a chapter in list or card view
    """

    scene_clicked = Signal(str)  # scene_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scenes: List[Scene] = []
        self.filtered_scenes: List[Scene] = []  # Filtered list for search
        self.chapter_title: str = ""
        self.current_view = "cards"  # Default: cards view
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header
        header_layout = QHBoxLayout()

        # Title (will be updated with chapter name)
        self.title_label = QLabel("📖 Chapter Scenes")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search scenes...")
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

        # Total scenes
        self.total_scenes_label = QLabel("📝 0 scenes")
        self.total_scenes_label.setStyleSheet(f"color: {palette.color(QPalette.ColorRole.Text).name()}; background: transparent; border: none;")
        stats_layout.addWidget(self.total_scenes_label)

        # Separator
        separator1 = QLabel("•")
        separator1.setStyleSheet(f"color: {palette.color(QPalette.ColorRole.Mid).name()}; background: transparent; border: none;")
        stats_layout.addWidget(separator1)

        # Total words
        self.total_words_label = QLabel("📚 0 words")
        self.total_words_label.setStyleSheet(f"color: {palette.color(QPalette.ColorRole.Text).name()}; background: transparent; border: none;")
        stats_layout.addWidget(self.total_words_label)

        # Separator
        separator2 = QLabel("•")
        separator2.setStyleSheet(f"color: {palette.color(QPalette.ColorRole.Mid).name()}; background: transparent; border: none;")
        stats_layout.addWidget(separator2)

        # Average words per scene
        self.avg_words_label = QLabel("📊 0 avg words/scene")
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
        # Use double-click to open scene
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

    def load_scenes(self, chapter_title: str, scenes: List[Scene]):
        """Load scenes into the view"""
        self.chapter_title = chapter_title
        self.scenes = sorted(scenes, key=lambda s: s.order)
        self.filtered_scenes = self.scenes.copy()

        # Update title
        self.title_label.setText(f"📖 {chapter_title}")

        self._update_statistics()
        self._populate_list_view()
        self._populate_cards_view()

    def _on_search_changed(self, search_text: str):
        """Handle search text change"""
        search_text = search_text.lower().strip()

        if not search_text:
            # No search, show all scenes
            self.filtered_scenes = self.scenes.copy()
        else:
            # Filter scenes by title and content
            self.filtered_scenes = []
            for scene in self.scenes:
                # Check if title or content matches
                if search_text in scene.title.lower() or search_text in scene.content.lower():
                    self.filtered_scenes.append(scene)

        # Refresh views
        self._update_statistics()
        self._populate_list_view()
        self._populate_cards_view()

    def _update_statistics(self):
        """Update statistics labels"""
        total_scenes = len(self.filtered_scenes)
        total_words = sum(scene.word_count for scene in self.filtered_scenes)
        avg_words = total_words // total_scenes if total_scenes > 0 else 0

        self.total_scenes_label.setText(f"📝 {total_scenes} scene{'s' if total_scenes != 1 else ''}")
        self.total_words_label.setText(f"📚 {total_words:,} words")
        self.avg_words_label.setText(f"📊 {avg_words:,} avg words/scene")

    def _populate_list_view(self):
        """Populate list view with scenes"""
        self.list_widget.clear()

        for scene in self.filtered_scenes:
            # Create custom item
            item = QListWidgetItem()

            # Get preview text (remove HTML tags)
            text = strip_html(scene.content)
            if len(text) > 130:
                preview_text = text[:130] + "..."
            else:
                preview_text = text

            item_text = f"📝 {scene.title}\n"
            item_text += f"   {scene.word_count:,} words\n"
            if preview_text:
                item_text += f"   {preview_text}"

            item.setText(item_text)
            item.setData(Qt.ItemDataRole.UserRole, scene.id)

            self.list_widget.addItem(item)

    def _populate_cards_view(self):
        """Populate cards grid view with scenes"""
        # Clear existing cards
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add scene cards (3 per row)
        row = 0
        col = 0
        for scene in self.filtered_scenes:
            card = SceneCardWidget(scene)
            card.clicked.connect(self.scene_clicked.emit)
            self.cards_grid.addWidget(card, row, col)

            col += 1
            if col >= 3:  # 3 cards per row
                col = 0
                row += 1

        # Add spacer at the end
        self.cards_grid.setRowStretch(row + 1, 1)

    def _on_list_item_double_clicked(self, item: QListWidgetItem):
        """Handle list item double-click (open scene)"""
        scene_id = item.data(Qt.ItemDataRole.UserRole)
        if scene_id:
            self.scene_clicked.emit(scene_id)
