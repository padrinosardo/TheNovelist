"""
Worldbuilding Detail View - Form for editing a single worldbuilding entry
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QScrollArea, QFrame, QComboBox, QListWidget,
    QListWidgetItem, QMessageBox, QInputDialog
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont
from models.worldbuilding_entry import WorldbuildingEntry, WorldbuildingCategory
from models.container_type import ContainerType
from ui.components.unified_text_editor import UnifiedTextEditor
from datetime import datetime
import uuid


class WorldbuildingDetailView(QWidget):
    """
    Detailed form for viewing and editing a single worldbuilding entry
    """

    # Signals
    entry_saved = Signal()
    entry_deleted = Signal(str)  # entry_id
    back_requested = Signal()

    # Categories with icons and labels
    CATEGORIES = {
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

    IMPORTANCE_LEVELS = {
        'low': 'Bassa',
        'medium': 'Media',
        'high': 'Alta',
        'critical': 'Critica'
    }

    def __init__(self, container_manager=None, worldbuilding_manager=None, parent=None):
        super().__init__(parent)
        self.container_manager = container_manager
        self.worldbuilding_manager = worldbuilding_manager
        self._current_entry = None
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
            }
        """)

        # Form container
        form_container = QWidget()
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 20, 30, 20)
        form_layout.setSpacing(20)

        # Back button
        back_btn = QPushButton("← Back to Worldbuilding")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: palette(link);
                border: none;
                text-align: left;
                padding: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                color: palette(link);
                text-decoration: underline;
            }
        """)
        back_btn.clicked.connect(self.back_requested.emit)
        form_layout.addWidget(back_btn)

        # Title
        title = QLabel("Worldbuilding Entry")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        form_layout.addWidget(title)

        # Entry Title field
        title_label = QLabel("Titolo*")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        form_layout.addWidget(title_label)

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Es: Sistema Magico Elementale...")
        self.title_input.setStyleSheet(self._get_input_style())
        form_layout.addWidget(self.title_input)

        # Category and Importance row
        meta_layout = QHBoxLayout()

        # Category
        cat_container = QWidget()
        cat_layout = QVBoxLayout(cat_container)
        cat_layout.setContentsMargins(0, 0, 0, 0)

        cat_label = QLabel("Categoria*")
        cat_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        cat_layout.addWidget(cat_label)

        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet(self._get_combo_style())
        for cat_key, (icon, label) in self.CATEGORIES.items():
            self.category_combo.addItem(f"{icon} {label}", cat_key)
        cat_layout.addWidget(self.category_combo)

        meta_layout.addWidget(cat_container)

        # Importance
        imp_container = QWidget()
        imp_layout = QVBoxLayout(imp_container)
        imp_layout.setContentsMargins(0, 0, 0, 0)

        imp_label = QLabel("Importanza")
        imp_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        imp_layout.addWidget(imp_label)

        self.importance_combo = QComboBox()
        self.importance_combo.setStyleSheet(self._get_combo_style())
        for imp_key, imp_label in self.IMPORTANCE_LEVELS.items():
            self.importance_combo.addItem(imp_label, imp_key)
        self.importance_combo.setCurrentIndex(1)  # Default: medium
        imp_layout.addWidget(self.importance_combo)

        meta_layout.addWidget(imp_container)

        form_layout.addLayout(meta_layout)

        # Description
        desc_label = QLabel("Descrizione")
        desc_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        form_layout.addWidget(desc_label)

        desc_hint = QLabel("Descrizione dettagliata dell'elemento worldbuilding")
        desc_hint.setStyleSheet("font-size: 12px; margin-bottom: 5px;")
        form_layout.addWidget(desc_hint)

        self.description_edit = UnifiedTextEditor()
        self.description_edit.setPlaceholderText(
            "Esempio per Sistema Magico:\n"
            "- Come funziona la magia in questo mondo\n"
            "- Chi può usarla e perché\n"
            "- Limitazioni e conseguenze\n"
            "- Effetti collaterali o costi"
        )
        self.description_edit.setStyleSheet(self._get_textedit_style())
        self.description_edit.setMinimumHeight(200)

        form_layout.addWidget(self.description_edit)

        # Rules section
        rules_frame = self._create_rules_section()
        form_layout.addWidget(rules_frame)

        # Tags section
        tags_frame = self._create_tags_section()
        form_layout.addWidget(tags_frame)

        # Notes
        notes_label = QLabel("Note Aggiuntive")
        notes_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        form_layout.addWidget(notes_label)

        self.notes_edit = UnifiedTextEditor()
        self.notes_edit.setPlaceholderText("Note libere, riflessioni, idee...")
        self.notes_edit.setStyleSheet(self._get_textedit_style())
        self.notes_edit.setMaximumHeight(120)

        form_layout.addWidget(self.notes_edit)

        # Action buttons
        buttons_layout = QHBoxLayout()

        # Delete button
        self.delete_btn = QPushButton("🗑️ Elimina")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 12px 20px;
                font-size: 14px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.delete_btn.clicked.connect(self._on_delete)
        buttons_layout.addWidget(self.delete_btn)

        buttons_layout.addStretch()

        # Save button
        save_btn = QPushButton("💾 Salva Entry")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px 30px;
                font-size: 14px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_btn.clicked.connect(self._on_save)
        buttons_layout.addWidget(save_btn)

        form_layout.addLayout(buttons_layout)

        form_layout.addStretch()

        scroll.setWidget(form_container)
        layout.addWidget(scroll)

    def _create_rules_section(self) -> QFrame:
        """Create the rules section"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                border: 1px solid palette(mid);
                border-radius: 4px;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout(frame)

        # Header
        header_layout = QHBoxLayout()

        rules_label = QLabel("Regole e Leggi")
        rules_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(rules_label)

        header_layout.addStretch()

        add_rule_btn = QPushButton("+ Aggiungi Regola")
        add_rule_btn.setStyleSheet(self._get_small_button_style())
        add_rule_btn.clicked.connect(self._on_add_rule)
        header_layout.addWidget(add_rule_btn)

        layout.addLayout(header_layout)

        # Hint
        hint = QLabel("Regole che governano questo elemento del mondo")
        hint.setStyleSheet("font-size: 12px;")
        layout.addWidget(hint)

        # List
        self.rules_list = QListWidget()
        self.rules_list.setMaximumHeight(150)
        self.rules_list.setStyleSheet("""
            QListWidget {
                border: 1px solid palette(mid);
                border-radius: 4px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.rules_list)

        # Remove button
        remove_rule_btn = QPushButton("- Rimuovi Selezionata")
        remove_rule_btn.setStyleSheet(self._get_small_button_style())
        remove_rule_btn.clicked.connect(self._on_remove_rule)
        layout.addWidget(remove_rule_btn)

        return frame

    def _create_tags_section(self) -> QFrame:
        """Create the tags section"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                border: 1px solid palette(mid);
                border-radius: 4px;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout(frame)

        # Header
        tags_label = QLabel("Tags")
        tags_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(tags_label)

        hint = QLabel("Aggiungi tags per organizzare e cercare rapidamente")
        hint.setStyleSheet("font-size: 12px;")
        layout.addWidget(hint)

        # Input row
        input_layout = QHBoxLayout()

        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Nuovo tag...")
        self.tag_input.setStyleSheet(self._get_input_style())
        self.tag_input.returnPressed.connect(self._on_add_tag)
        input_layout.addWidget(self.tag_input)

        add_tag_btn = QPushButton("+ Aggiungi")
        add_tag_btn.setStyleSheet(self._get_small_button_style())
        add_tag_btn.clicked.connect(self._on_add_tag)
        input_layout.addWidget(add_tag_btn)

        layout.addLayout(input_layout)

        # Tags list
        self.tags_list = QListWidget()
        self.tags_list.setMaximumHeight(100)
        self.tags_list.setStyleSheet("""
            QListWidget {
                border: 1px solid palette(mid);
                border-radius: 4px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.tags_list)

        return frame

    def set_managers(self, container_manager, worldbuilding_manager):
        """Set the manager instances"""
        self.container_manager = container_manager
        self.worldbuilding_manager = worldbuilding_manager

    def load_entry(self, entry_id: str):
        """Load an entry for editing"""
        if not self.worldbuilding_manager:
            return

        entry = self.worldbuilding_manager.get_entry(entry_id)
        if not entry:
            return

        self._current_entry = entry

        # Populate fields
        self.title_input.setText(entry.title)

        # Set category
        cat_index = self.category_combo.findData(entry.category)
        if cat_index >= 0:
            self.category_combo.setCurrentIndex(cat_index)

        # Set importance
        imp_index = self.importance_combo.findData(entry.importance)
        if imp_index >= 0:
            self.importance_combo.setCurrentIndex(imp_index)

        self.description_edit.setPlainText(entry.description)
        self.notes_edit.setPlainText(entry.notes)

        # Populate rules
        self.rules_list.clear()
        for rule in entry.rules:
            self.rules_list.addItem(rule)

        # Populate tags
        self.tags_list.clear()
        for tag in entry.tags:
            item = QListWidgetItem(f"#{tag}")
            self.tags_list.addItem(item)

        # Show delete button
        self.delete_btn.setVisible(True)

    def new_entry(self):
        """Prepare form for a new entry"""
        self._current_entry = None

        # Clear fields
        self.title_input.clear()
        self.category_combo.setCurrentIndex(0)
        self.importance_combo.setCurrentIndex(1)  # Medium
        self.description_edit.clear()
        self.notes_edit.clear()
        self.rules_list.clear()
        self.tags_list.clear()
        self.tag_input.clear()

        # Hide delete button
        self.delete_btn.setVisible(False)

    def _on_add_rule(self):
        """Add a new rule"""
        rule, ok = QInputDialog.getText(
            self,
            "Nuova Regola",
            "Inserisci una regola o legge per questo elemento:"
        )

        if ok and rule.strip():
            self.rules_list.addItem(rule.strip())

    def _on_remove_rule(self):
        """Remove selected rule"""
        current_item = self.rules_list.currentItem()
        if current_item:
            self.rules_list.takeItem(self.rules_list.row(current_item))

    def _on_add_tag(self):
        """Add a new tag"""
        tag = self.tag_input.text().strip().replace('#', '')
        if tag:
            # Check for duplicates
            existing_tags = [self.tags_list.item(i).text().replace('#', '')
                           for i in range(self.tags_list.count())]
            if tag not in existing_tags:
                item = QListWidgetItem(f"#{tag}")
                self.tags_list.addItem(item)
            self.tag_input.clear()

    def _on_save(self):
        """Save the entry"""
        title = self.title_input.text().strip()
        if not title:
            QMessageBox.warning(self, "Errore", "Il titolo è obbligatorio!")
            return

        category = self.category_combo.currentData()
        importance = self.importance_combo.currentData()
        description = self.description_edit.toPlainText()
        notes = self.notes_edit.toPlainText()

        # Collect rules
        rules = []
        for i in range(self.rules_list.count()):
            rules.append(self.rules_list.item(i).text())

        # Collect tags
        tags = []
        for i in range(self.tags_list.count()):
            tag_text = self.tags_list.item(i).text().replace('#', '')
            tags.append(tag_text)

        if self._current_entry:
            # Update existing entry
            self._current_entry.title = title
            self._current_entry.category = category
            self._current_entry.importance = importance
            self._current_entry.description = description
            self._current_entry.notes = notes
            self._current_entry.rules = rules
            self._current_entry.tags = tags
            self._current_entry.modified_date = datetime.now().isoformat()

            self.worldbuilding_manager.update_entry(self._current_entry)
        else:
            # Create new entry
            entry = WorldbuildingEntry(
                title=title,
                category=category,
                importance=importance,
                description=description,
                notes=notes,
                rules=rules,
                tags=tags,
                created_date=datetime.now().isoformat(),
                modified_date=datetime.now().isoformat()
            )

            self.container_manager.add_item(ContainerType.WORLDBUILDING, entry)
            self._current_entry = entry

        # Save to disk
        self.worldbuilding_manager.save()

        # Show success message
        QMessageBox.information(self, "Salvato", "Entry salvata con successo!")

        # Emit signal
        self.entry_saved.emit()

    def _on_delete(self):
        """Delete the current entry"""
        if not self._current_entry:
            return

        reply = QMessageBox.question(
            self,
            "Conferma Eliminazione",
            f"Sei sicuro di voler eliminare '{self._current_entry.title}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            entry_id = self._current_entry.id
            if self.worldbuilding_manager.delete_entry(entry_id):
                self.worldbuilding_manager.save()
                self.entry_deleted.emit(entry_id)
                self.back_requested.emit()

    def _get_input_style(self) -> str:
        """Get QLineEdit style"""
        return """
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                border: 2px solid palette(mid);
                border-radius: 4px;
            }
            QLineEdit:focus {
                border-color: palette(highlight);
            }
        """

    def _get_combo_style(self) -> str:
        """Get QComboBox style"""
        return """
            QComboBox {
                padding: 10px;
                font-size: 14px;
                border: 2px solid palette(mid);
                border-radius: 4px;
            }
        """

    def _get_textedit_style(self) -> str:
        """Get QTextEdit style"""
        return """
            QTextEdit {
                padding: 10px;
                font-size: 14px;
                border: 2px solid palette(mid);
                border-radius: 4px;
                line-height: 1.5;
            }
            QTextEdit:focus {
                border-color: palette(highlight);
            }
        """

    def _get_small_button_style(self) -> str:
        """Get small button style"""
        return """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 6px 12px;
                font-size: 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """
