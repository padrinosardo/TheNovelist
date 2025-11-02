"""
Worldbuilding List View - Categorized list of worldbuilding entries
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLineEdit, QLabel, QComboBox, QMenu, QMessageBox, QFrame
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from models.container_type import ContainerType
from models.worldbuilding_entry import WorldbuildingCategory
import uuid


class WorldbuildingListView(QWidget):
    """
    List view showing worldbuilding entries with category filtering
    """

    # Signals
    entry_selected = Signal(str)  # entry_id
    entry_added = Signal()
    entry_deleted = Signal(str)  # entry_id

    # Categories with icons and labels
    CATEGORIES = {
        'all': ('🌍', 'Tutti'),
        'magic_system': ('✨', 'Sistema Magico'),
        'technology': ('🔬', 'Tecnologia'),
        'geography': ('🗺️', 'Geografia'),
        'politics': ('👑', 'Politica'),
        'religion': ('⛪', 'Religione'),
        'economy': ('💰', 'Economia'),
        'history': ('📜', 'Storia'),
        'races_species': ('🧬', 'Razze/Specie'),
        'culture': ('🎭', 'Cultura'),
        'factions': ('⚔️', 'Fazioni'),
        'language': ('💬', 'Lingue'),
        'other': ('📦', 'Altro')
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.container_manager = None
        self.worldbuilding_manager = None
        self.current_filter = 'all'
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)

        # Header
        header = self._create_header()
        layout.addWidget(header)

        # Filter bar
        filter_bar = self._create_filter_bar()
        layout.addWidget(filter_bar)

        # Search bar
        search_bar = self._create_search_bar()
        layout.addWidget(search_bar)

        # Entries list
        self.entries_list = QListWidget()
        self.entries_list.itemClicked.connect(self._on_entry_clicked)
        self.entries_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.entries_list.customContextMenuRequested.connect(self._show_context_menu)
        self.entries_list.setStyleSheet("""
            QListWidget {
                border: none;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid palette(mid);
                margin-bottom: 2px;
            }
            QListWidget::item:hover {
                background-color: palette(midlight);
            }
            QListWidget::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
        """)
        layout.addWidget(self.entries_list)

        # Status bar
        self.status_label = QLabel("No entries")
        self.status_label.setStyleSheet("padding: 10px;")
        layout.addWidget(self.status_label)

    def _create_header(self):
        """Create the header with title and buttons"""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                border-bottom: 2px solid palette(mid);
                padding: 15px;
            }
        """)

        layout = QHBoxLayout(header)

        # Title
        title = QLabel("🌍 Worldbuilding")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        layout.addStretch()

        # Add Entry button
        self.add_btn = QPushButton("+ New Entry")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.add_btn.clicked.connect(self._on_add_entry)
        layout.addWidget(self.add_btn)

        return header

    def _create_filter_bar(self):
        """Create category filter bar"""
        frame = QFrame()
        frame.setStyleSheet("padding: 10px;")

        layout = QHBoxLayout(frame)

        layout.addWidget(QLabel("Categoria:"))

        self.category_filter = QComboBox()
        self.category_filter.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                min-width: 200px;
            }
        """)

        for cat_key, (icon, label) in self.CATEGORIES.items():
            self.category_filter.addItem(f"{icon} {label}", cat_key)

        self.category_filter.currentIndexChanged.connect(self._on_category_changed)
        layout.addWidget(self.category_filter)

        layout.addStretch()

        return frame

    def _create_search_bar(self):
        """Create search bar"""
        frame = QFrame()
        frame.setStyleSheet("padding: 10px; border-bottom: 1px solid palette(mid);")

        layout = QHBoxLayout(frame)

        layout.addWidget(QLabel("🔍"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cerca per titolo, tag o contenuto...")
        self.search_input.textChanged.connect(self._on_search_changed)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.search_input)

        return frame

    def load_worldbuilding(self, container_manager, worldbuilding_manager):
        """
        Load worldbuilding entries

        Args:
            container_manager: ContainerManager instance
            worldbuilding_manager: WorldbuildingManager instance
        """
        self.container_manager = container_manager
        self.worldbuilding_manager = worldbuilding_manager

        # Load entries from storage
        container_manager.load_container(ContainerType.WORLDBUILDING)

        self._refresh_list()

    def _refresh_list(self):
        """Refresh the entries list"""
        if not self.worldbuilding_manager:
            return

        self.entries_list.clear()

        # Get entries filtered by category
        if self.current_filter == 'all':
            entries = self.worldbuilding_manager.get_all_entries()
        else:
            entries = self.worldbuilding_manager.get_entries_by_category(self.current_filter)

        # Apply search filter
        search_text = self.search_input.text().lower()
        if search_text:
            entries = [e for e in entries if
                      search_text in e.title.lower() or
                      search_text in e.description.lower() or
                      any(search_text in tag.lower() for tag in e.tags)]

        # Sort by importance and title
        importance_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        entries.sort(key=lambda e: (importance_order.get(e.importance, 2), e.title.lower()))

        # Populate list
        for entry in entries:
            # Get category icon
            cat_icon, _ = self.CATEGORIES.get(entry.category, ('📄', 'Unknown'))

            # Importance badge
            importance_badge = ''
            if entry.importance == 'critical':
                importance_badge = '🔴 '
            elif entry.importance == 'high':
                importance_badge = '🟠 '

            # Item text
            item_text = f"{cat_icon} {importance_badge}{entry.title}"

            # Subtitle with tags if present
            if entry.tags:
                tags_str = ', '.join([f"#{tag}" for tag in entry.tags[:3]])  # Max 3 tags
                item_text += f"\n    {tags_str}"

            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, entry.id)

            # Tooltip with info
            tooltip = f"{entry.title}\nCategoria: {entry.category}"
            if entry.tags:
                tooltip += f"\nTags: {', '.join(['#' + t for t in entry.tags])}"
            if entry.description:
                # First 100 chars of description
                desc_preview = entry.description[:100]
                if len(entry.description) > 100:
                    desc_preview += "..."
                tooltip += f"\n\n{desc_preview}"
            item.setToolTip(tooltip)

            self.entries_list.addItem(item)

        # Update status
        count_text = f"{len(entries)} {'entry' if len(entries) == 1 else 'entries'}"
        if self.current_filter != 'all':
            _, category_name = self.CATEGORIES.get(self.current_filter, ('', self.current_filter))
            count_text += f" in {category_name}"
        self.status_label.setText(count_text)

    def _on_category_changed(self, index):
        """Handler for category filter change"""
        self.current_filter = self.category_filter.currentData()
        self._refresh_list()

    def _on_search_changed(self):
        """Handler for search text change"""
        self._refresh_list()

    def _on_entry_clicked(self, item):
        """Handler for entry click"""
        entry_id = item.data(Qt.ItemDataRole.UserRole)
        self.entry_selected.emit(entry_id)

    def _on_add_entry(self):
        """Handler for add entry button"""
        self.entry_added.emit()

    def _show_context_menu(self, position):
        """Show context menu for entry"""
        item = self.entries_list.itemAt(position)
        if not item:
            return

        entry_id = item.data(Qt.ItemDataRole.UserRole)

        menu = QMenu(self)

        edit_action = menu.addAction("✏️ Modifica")
        duplicate_action = menu.addAction("📋 Duplica")
        menu.addSeparator()
        delete_action = menu.addAction("🗑️ Elimina")

        action = menu.exec(self.entries_list.mapToGlobal(position))

        if action == delete_action:
            self._delete_entry(entry_id)
        elif action == edit_action:
            self.entry_selected.emit(entry_id)
        elif action == duplicate_action:
            self._duplicate_entry(entry_id)

    def _delete_entry(self, entry_id: str):
        """Delete an entry"""
        entry = self.worldbuilding_manager.get_entry(entry_id)
        if not entry:
            return

        reply = QMessageBox.question(
            self,
            "Conferma Eliminazione",
            f"Sei sicuro di voler eliminare '{entry.title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.worldbuilding_manager.delete_entry(entry_id):
                self.worldbuilding_manager.save()
                self._refresh_list()
                self.entry_deleted.emit(entry_id)

    def _duplicate_entry(self, entry_id: str):
        """Duplicate an entry"""
        new_id = self.worldbuilding_manager.duplicate_entry(entry_id)
        if new_id:
            self.worldbuilding_manager.save()
            self._refresh_list()
