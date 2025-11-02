"""
Chapter Detail Widget - Shows chapter details with tabs for scenes, synopsis, and notes
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTextEdit,
    QLabel, QPushButton
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPalette, QFont
from models.manuscript_structure import Chapter
from ui.components.scenes_preview_widget import ScenesPreviewWidget


class ChapterDetailWidget(QWidget):
    """
    Widget to show chapter details with tabs:
    - Scenes: Preview of all scenes in the chapter
    - Synopsis: Chapter synopsis/summary
    - Notes: Chapter notes
    """

    # Signals
    scene_clicked = Signal(str)  # scene_id
    chapter_updated = Signal(str)  # chapter_id
    back_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_chapter = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Header with back button and title
        header_layout = QHBoxLayout()

        # Back button
        self.back_btn = QPushButton("← Back to Chapters")
        self.back_btn.setFixedWidth(150)
        self.back_btn.clicked.connect(self.back_requested.emit)
        header_layout.addWidget(self.back_btn)

        # Chapter title
        self.title_label = QLabel("Chapter Details")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        self.title_label.setFont(title_font)
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Tab widget
        self.tabs = QTabWidget()

        # Tab 1: Scenes Preview
        self.scenes_preview = ScenesPreviewWidget()
        self.scenes_preview.scene_clicked.connect(self.scene_clicked.emit)
        self.tabs.addTab(self.scenes_preview, "📝 Scenes")

        # Tab 2: Synopsis
        self.synopsis_widget = QWidget()
        synopsis_layout = QVBoxLayout(self.synopsis_widget)
        synopsis_layout.setContentsMargins(10, 10, 10, 10)

        synopsis_label = QLabel("Chapter Synopsis")
        synopsis_font = QFont()
        synopsis_font.setPointSize(12)
        synopsis_font.setBold(True)
        synopsis_label.setFont(synopsis_font)
        synopsis_layout.addWidget(synopsis_label)

        self.synopsis_edit = QTextEdit()
        self.synopsis_edit.setPlaceholderText("Write a synopsis or summary of this chapter...")
        self.synopsis_edit.textChanged.connect(self._on_synopsis_changed)
        synopsis_layout.addWidget(self.synopsis_edit)

        self.tabs.addTab(self.synopsis_widget, "📄 Synopsis")

        # Tab 3: Notes
        self.notes_widget = QWidget()
        notes_layout = QVBoxLayout(self.notes_widget)
        notes_layout.setContentsMargins(10, 10, 10, 10)

        notes_label = QLabel("Chapter Notes")
        notes_font = QFont()
        notes_font.setPointSize(12)
        notes_font.setBold(True)
        notes_label.setFont(notes_font)
        notes_layout.addWidget(notes_label)

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Write notes about this chapter...")
        self.notes_edit.textChanged.connect(self._on_notes_changed)
        notes_layout.addWidget(self.notes_edit)

        self.tabs.addTab(self.notes_widget, "📝 Notes")

        # Style tabs
        palette = self.palette()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {palette.color(QPalette.ColorRole.Mid).name()};
                border-radius: 4px;
                background-color: {palette.color(QPalette.ColorRole.Base).name()};
            }}
            QTabBar::tab {{
                background-color: {palette.color(QPalette.ColorRole.AlternateBase).name()};
                color: {palette.color(QPalette.ColorRole.Text).name()};
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {palette.color(QPalette.ColorRole.Base).name()};
                border: 1px solid {palette.color(QPalette.ColorRole.Mid).name()};
                border-bottom: none;
            }}
            QTabBar::tab:hover {{
                background-color: {palette.color(QPalette.ColorRole.Light).name()};
            }}
        """)

        layout.addWidget(self.tabs)

    def load_chapter(self, chapter: Chapter):
        """
        Load chapter data into the widget

        Args:
            chapter: Chapter object to display
        """
        self.current_chapter = chapter

        # Update title
        self.title_label.setText(f"📖 {chapter.title}")

        # Load scenes into preview
        self.scenes_preview.load_scenes(chapter.title, chapter.scenes)

        # Load synopsis and notes (block signals to avoid triggering save)
        self.synopsis_edit.blockSignals(True)
        self.synopsis_edit.setPlainText(chapter.synopsis)
        self.synopsis_edit.blockSignals(False)

        self.notes_edit.blockSignals(True)
        self.notes_edit.setPlainText(chapter.notes)
        self.notes_edit.blockSignals(False)

    def _on_synopsis_changed(self):
        """Handle synopsis text change"""
        if self.current_chapter:
            self.current_chapter.synopsis = self.synopsis_edit.toPlainText()
            self.chapter_updated.emit(self.current_chapter.id)

    def _on_notes_changed(self):
        """Handle notes text change"""
        if self.current_chapter:
            self.current_chapter.notes = self.notes_edit.toPlainText()
            self.chapter_updated.emit(self.current_chapter.id)

    def save_current_data(self):
        """
        Save current synopsis and notes to chapter object

        Returns:
            tuple: (chapter_id, synopsis, notes) or None if no chapter loaded
        """
        if self.current_chapter:
            synopsis = self.synopsis_edit.toPlainText()
            notes = self.notes_edit.toPlainText()
            self.current_chapter.synopsis = synopsis
            self.current_chapter.notes = notes
            return (self.current_chapter.id, synopsis, notes)
        return None
