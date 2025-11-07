"""
Welcome Screen - Project history and quick access
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QColor
from datetime import datetime
from typing import List, Dict
from models.project_type import ProjectType
import os


class WelcomeScreen(QWidget):
    """
    Welcome screen showing recent projects history

    Features:
    - Table with project list (title, type, dates)
    - Sorted by last opened date (most recent first)
    - Double-click to open project
    - Quick actions: New Project, Open Other
    """

    # Signals
    project_selected = Signal(str)  # filepath
    new_project_requested = Signal()
    open_other_requested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._projects_data: List[Dict] = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        # Reduced margins for smaller screens
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)

        # === HEADER ===
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)

        # Logo/Title - reduced size
        title = QLabel("📚 The Novelist")
        title_font = QFont()
        title_font.setPointSize(24)  # Reduced from 32
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title)

        # Subtitle - reduced size
        subtitle = QLabel("I tuoi Progetti")
        subtitle_font = QFont()
        subtitle_font.setPointSize(14)  # Reduced from 16
        subtitle.setFont(subtitle_font)
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #666;")
        header_layout.addWidget(subtitle)

        layout.addLayout(header_layout)
        layout.addSpacing(10)  # Reduced from 20

        # === PROJECTS TABLE ===
        table_label = QLabel("Progetti Recenti")
        table_label_font = QFont()
        table_label_font.setPointSize(12)  # Reduced from 14
        table_label_font.setBold(True)
        table_label.setFont(table_label_font)
        layout.addWidget(table_label)

        self.projects_table = QTableWidget()
        self.projects_table.setColumnCount(4)
        self.projects_table.setHorizontalHeaderLabels([
            "Titolo",
            "Tipo",
            "Creato",
            "Ultima Modifica"
        ])

        # Table styling
        self.projects_table.setAlternatingRowColors(True)
        self.projects_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.projects_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.projects_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.projects_table.verticalHeader().setVisible(False)
        self.projects_table.setShowGrid(False)
        # Optimized for smaller screens
        self.projects_table.setMinimumHeight(200)
        self.projects_table.setMaximumHeight(400)

        # Header styling - Title column takes most space
        header = self.projects_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Title column - expands
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # Type - fixed small
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Created - fixed small
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Modified - fixed small

        # Set fixed widths for small columns
        self.projects_table.setColumnWidth(1, 150)  # Type column
        self.projects_table.setColumnWidth(2, 180)  # Created column
        self.projects_table.setColumnWidth(3, 180)  # Modified column

        # Row height - reduced for smaller screens
        self.projects_table.verticalHeader().setDefaultSectionSize(45)

        # Double-click to open
        self.projects_table.itemDoubleClicked.connect(self._on_project_double_clicked)

        # Custom styling
        self.projects_table.setStyleSheet("""
            QTableWidget {
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: white;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 10px;
            }
            QTableWidget::item:selected {
                background-color: #2196F3;
                color: white;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #ddd;
                font-weight: bold;
                font-size: 13px;
            }
        """)

        layout.addWidget(self.projects_table)

        # === FOOTER INFO ===
        self.info_label = QLabel("Nessun progetto recente")
        self.info_label.setStyleSheet("color: #999; font-style: italic;")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)

        layout.addSpacing(10)  # Reduced from 15

        # === ACTION BUTTONS (bottom right) ===
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()  # Push buttons to the right

        self.new_project_btn = QPushButton("Nuovo Progetto")
        self.new_project_btn.setFixedSize(140, 35)  # 1/4 of original size
        self.new_project_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 15px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.new_project_btn.clicked.connect(self.new_project_requested.emit)
        buttons_layout.addWidget(self.new_project_btn)

        buttons_layout.addSpacing(10)

        self.open_other_btn = QPushButton("Apri Altro...")
        self.open_other_btn.setFixedSize(140, 35)  # 1/4 of original size
        self.open_other_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 15px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        self.open_other_btn.clicked.connect(self.open_other_requested.emit)
        buttons_layout.addWidget(self.open_other_btn)

        layout.addLayout(buttons_layout)

    def load_projects(self, projects_metadata: List[Dict]):
        """
        Load and display projects

        Args:
            projects_metadata: List of project metadata dicts from SettingsManager
        """
        self._projects_data = projects_metadata
        self._populate_table()

        # Force column widths to be applied
        self.projects_table.setColumnWidth(1, 150)  # Type
        self.projects_table.setColumnWidth(2, 180)  # Created
        self.projects_table.setColumnWidth(3, 180)  # Modified

    def _populate_table(self):
        """Populate the table with projects data"""
        # Clear existing rows
        self.projects_table.setRowCount(0)

        if not self._projects_data:
            self.info_label.setText("Nessun progetto recente. Crea un nuovo progetto per iniziare!")
            self.info_label.setVisible(True)
            return

        # Sort by last_opened_date (most recent first)
        sorted_projects = sorted(
            self._projects_data,
            key=lambda p: p.get('last_opened_date', ''),
            reverse=True
        )

        # Populate rows
        for project in sorted_projects:
            self._add_project_row(project)

        # Update info label
        count = len(sorted_projects)
        self.info_label.setText(f"Progetti Recenti: {count} di 10")
        self.info_label.setVisible(True)

    def _add_project_row(self, project: Dict):
        """
        Add a project row to the table

        Args:
            project: Project metadata dict
        """
        row = self.projects_table.rowCount()
        self.projects_table.insertRow(row)

        # Get project data
        filepath = project.get('filepath', '')
        title = project.get('title', '')
        if not title:
            # Use filename without extension as fallback
            filename = os.path.basename(filepath)
            title = filename.rsplit('.', 1)[0] if '.' in filename else filename
        project_type_str = project.get('project_type', 'novel')
        created_date = project.get('created_date', '')
        modified_date = project.get('modified_date', '')

        # Get ProjectType enum and icon
        try:
            project_type = ProjectType(project_type_str)
            type_icon = project_type.get_icon()
            type_name = project_type.get_display_name('it')
        except ValueError:
            type_icon = '📄'
            type_name = project_type_str.replace('_', ' ').title()

        # Column 0: Title only (no icon)
        title_item = QTableWidgetItem(title)
        title_font = QFont()
        title_font.setPointSize(13)
        title_font.setBold(True)
        title_item.setFont(title_font)
        title_item.setData(Qt.ItemDataRole.UserRole, filepath)  # Store filepath
        self.projects_table.setItem(row, 0, title_item)

        # Column 1: Type (with icon)
        type_item = QTableWidgetItem(f"{type_icon} {type_name}")
        type_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.projects_table.setItem(row, 1, type_item)

        # Column 2: Created Date
        created_formatted = self._format_date(created_date)
        created_item = QTableWidgetItem(created_formatted)
        created_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.projects_table.setItem(row, 2, created_item)

        # Column 3: Modified Date
        modified_formatted = self._format_date(modified_date)
        modified_item = QTableWidgetItem(modified_formatted)
        modified_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        # Highlight recent modifications (within 24 hours)
        if self._is_recent(modified_date):
            modified_item.setForeground(QColor("#4CAF50"))
            modified_font = QFont()
            modified_font.setBold(True)
            modified_item.setFont(modified_font)

        self.projects_table.setItem(row, 3, modified_item)

    def _format_date(self, date_str: str) -> str:
        """
        Format ISO date string to readable format

        Args:
            date_str: ISO format date string

        Returns:
            str: Formatted date (e.g., "15 Gen 2025, 14:30")
        """
        if not date_str:
            return "—"

        try:
            dt = datetime.fromisoformat(date_str)

            # Italian month names
            month_names = [
                "Gen", "Feb", "Mar", "Apr", "Mag", "Giu",
                "Jul", "Ago", "Set", "Ott", "Nov", "Dic"
            ]

            month = month_names[dt.month - 1]

            # Format: "15 Gen 2025, 14:30"
            return f"{dt.day} {month} {dt.year}, {dt.hour:02d}:{dt.minute:02d}"

        except (ValueError, AttributeError):
            return date_str[:10] if len(date_str) >= 10 else date_str

    def _is_recent(self, date_str: str) -> bool:
        """
        Check if date is within last 24 hours

        Args:
            date_str: ISO format date string

        Returns:
            bool: True if within 24 hours
        """
        if not date_str:
            return False

        try:
            dt = datetime.fromisoformat(date_str)
            now = datetime.now()
            delta = now - dt
            return delta.total_seconds() < 24 * 3600
        except (ValueError, AttributeError):
            return False

    def _on_project_double_clicked(self, item: QTableWidgetItem):
        """
        Handle project double-click

        Args:
            item: Clicked table item
        """
        row = item.row()

        # Get filepath from first column
        title_item = self.projects_table.item(row, 0)
        if title_item:
            filepath = title_item.data(Qt.ItemDataRole.UserRole)
            if filepath:
                self.project_selected.emit(filepath)

    def refresh(self, projects_metadata: List[Dict]):
        """
        Refresh the projects list

        Args:
            projects_metadata: Updated list of project metadata
        """
        self.load_projects(projects_metadata)
