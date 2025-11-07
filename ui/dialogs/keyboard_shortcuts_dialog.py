"""
Keyboard Shortcuts Dialog - Shows all available keyboard shortcuts
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QTableWidget, QTableWidgetItem,
                               QHeaderView, QTabWidget, QWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class KeyboardShortcutsDialog(QDialog):
    """
    Dialog that displays all available keyboard shortcuts organized by category
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("⌨️ Scorciatoie da Tastiera")
        self.setMinimumSize(700, 600)
        self._initialize_ui()

    def _initialize_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("⌨️ Scorciatoie da Tastiera")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Usa queste combinazioni per velocizzare la scrittura")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #666; margin-bottom: 10px;")
        layout.addWidget(subtitle)

        # Tab widget for categories
        tabs = QTabWidget()
        tabs.addTab(self._create_formatting_tab(), "📝 Formattazione")
        tabs.addTab(self._create_alignment_tab(), "📐 Allineamento")
        tabs.addTab(self._create_quotes_tab(), "💬 Virgolette & Simboli")
        tabs.addTab(self._create_general_tab(), "⚙️ Generale")
        layout.addWidget(tabs)

        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = QPushButton("Chiudi")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

    def _create_formatting_tab(self):
        """Create formatting shortcuts tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        info = QLabel("Formattazione del testo")
        info.setStyleSheet("font-weight: bold; margin: 5px 0;")
        layout.addWidget(info)

        table = self._create_shortcuts_table([
            ("Grassetto", "Ctrl+B", "Applica/rimuovi grassetto al testo selezionato"),
            ("Corsivo", "Ctrl+I", "Applica/rimuovi corsivo al testo selezionato"),
            ("Sottolineato", "Ctrl+U", "Applica/rimuovi sottolineatura al testo selezionato"),
            ("Barrato", "Ctrl+Shift+X", "Applica/rimuovi barrato al testo selezionato"),
            ("Apice", "Ctrl+Shift+=", "Testo in apice (superscript)"),
            ("Pedice", "Ctrl+=", "Testo in pedice (subscript)"),
            ("Maiuscoletto", "Ctrl+Shift+K", "Applica/rimuovi maiuscoletto (small caps)"),
        ])
        layout.addWidget(table)

        return widget

    def _create_alignment_tab(self):
        """Create alignment shortcuts tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        info = QLabel("Allineamento del paragrafo")
        info.setStyleSheet("font-weight: bold; margin: 5px 0;")
        layout.addWidget(info)

        table = self._create_shortcuts_table([
            ("Allinea a Sinistra", "Ctrl+L", "Allinea il paragrafo a sinistra"),
            ("Centra", "Ctrl+E", "Centra il paragrafo"),
            ("Allinea a Destra", "Ctrl+R", "Allinea il paragrafo a destra"),
            ("Giustifica", "Ctrl+J", "Giustifica il paragrafo"),
        ])
        layout.addWidget(table)

        return widget

    def _create_quotes_tab(self):
        """Create quotes and symbols shortcuts tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        info = QLabel("Virgolette, trattini e simboli tipografici")
        info.setStyleSheet("font-weight: bold; margin: 5px 0;")
        layout.addWidget(info)

        table = self._create_shortcuts_table([
            ("Em Dash (—)", "Ctrl+Shift+-", "Inserisce trattino lungo (em dash)"),
            ("En Dash (–)", "Ctrl+-", "Inserisce trattino medio (en dash)"),
            ("Virgolette", "Pulsante « »", "Click sul pulsante o usa il menu a tendina per scegliere il tipo"),
            ("Ellissi (…)", "Pulsante …", "Inserisce ellissi tipografica (tre puntini)"),
        ])
        layout.addWidget(table)

        note = QLabel("💡 Nota: Le virgolette possono essere inserite tramite il pulsante con menu a tendina.\n"
                     "Seleziona il tipo desiderato dal menu: « », " ", ' ', ecc.")
        note.setStyleSheet("background-color: #FFF3CD; padding: 10px; border-radius: 4px; margin-top: 10px;")
        note.setWordWrap(True)
        layout.addWidget(note)

        return widget

    def _create_general_tab(self):
        """Create general shortcuts tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        info = QLabel("Comandi generali")
        info.setStyleSheet("font-weight: bold; margin: 5px 0;")
        layout.addWidget(info)

        table = self._create_shortcuts_table([
            ("Mostra questa guida", "F1", "Apri la finestra delle scorciatoie da tastiera"),
            ("Annulla", "Ctrl+Z", "Annulla l'ultima modifica"),
            ("Ripeti", "Ctrl+Y", "Ripeti l'ultima modifica annullata"),
            ("Seleziona tutto", "Ctrl+A", "Seleziona tutto il testo"),
            ("Taglia", "Ctrl+X", "Taglia il testo selezionato"),
            ("Copia", "Ctrl+C", "Copia il testo selezionato"),
            ("Incolla", "Ctrl+V", "Incolla il testo dagli appunti"),
        ])
        layout.addWidget(table)

        return widget

    def _create_shortcuts_table(self, shortcuts_data):
        """
        Create a table widget with shortcuts

        Args:
            shortcuts_data: List of tuples (command, shortcut, description)

        Returns:
            QTableWidget
        """
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Comando", "Scorciatoia", "Descrizione"])
        table.setRowCount(len(shortcuts_data))

        # Style
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                gridline-color: #f0f0f0;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #ddd;
                font-weight: bold;
            }
        """)

        # Populate table
        for row, (command, shortcut, description) in enumerate(shortcuts_data):
            # Command
            command_item = QTableWidgetItem(command)
            command_font = QFont()
            command_font.setBold(True)
            command_item.setFont(command_font)
            table.setItem(row, 0, command_item)

            # Shortcut
            shortcut_item = QTableWidgetItem(shortcut)
            shortcut_item.setBackground(Qt.GlobalColor.lightGray)
            shortcut_font = QFont("Courier")
            shortcut_font.setBold(True)
            shortcut_item.setFont(shortcut_font)
            shortcut_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            table.setItem(row, 1, shortcut_item)

            # Description
            description_item = QTableWidgetItem(description)
            table.setItem(row, 2, description_item)

        # Set column widths
        table.setColumnWidth(0, 150)
        table.setColumnWidth(1, 150)
        table.horizontalHeader().setStretchLastSection(True)

        # Make read-only
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)

        # Resize rows to content
        table.verticalHeader().setVisible(False)
        for row in range(table.rowCount()):
            table.setRowHeight(row, 40)

        return table
