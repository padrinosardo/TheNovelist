"""
Preferences Dialog - Application-level preferences
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QLineEdit, QDialogButtonBox, QFileDialog,
                               QGroupBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from pathlib import Path


class PreferencesDialog(QDialog):
    """Dialog to configure application-level preferences"""

    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings = settings_manager
        self.setWindowTitle("Preferenze")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(200)

        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("Preferenze Applicazione")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        layout.addWidget(header)

        # Description
        desc = QLabel("Configurazione generale dell'applicazione.\n"
                     "Queste impostazioni sono salvate in ~/.thenovelist/settings.json "
                     "e persistono anche quando aggiorni l'applicazione.")
        desc.setStyleSheet("color: #666; margin: 10px 0;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # Projects Folder Section
        projects_group = QGroupBox("Cartella Progetti")
        projects_layout = QVBoxLayout(projects_group)

        folder_desc = QLabel("Specifica la cartella predefinita in cui salvare e aprire i progetti:")
        folder_desc.setWordWrap(True)
        projects_layout.addWidget(folder_desc)

        # Folder input
        folder_input_layout = QHBoxLayout()
        folder_input_layout.setSpacing(10)

        self.folder_input = QLineEdit()
        current_folder = self.settings.get_default_projects_folder()
        self.folder_input.setText(current_folder)
        self.folder_input.setPlaceholderText(str(Path.home() / "Documents"))
        self.folder_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 13px;
            }
        """)
        folder_input_layout.addWidget(self.folder_input)

        browse_btn = QPushButton("Sfoglia...")
        browse_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                font-size: 13px;
            }
        """)
        browse_btn.clicked.connect(self._browse_folder)
        folder_input_layout.addWidget(browse_btn)

        projects_layout.addLayout(folder_input_layout)

        # Info about persistence
        info_label = QLabel("💡 Questa impostazione viene mantenuta anche quando aggiorni l'applicazione "
                           "a una nuova versione.")
        info_label.setStyleSheet("color: #0066cc; font-size: 12px; margin-top: 10px;")
        info_label.setWordWrap(True)
        projects_layout.addWidget(info_label)

        layout.addWidget(projects_group)

        layout.addStretch()

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self._save_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _browse_folder(self):
        """Open folder browser dialog"""
        current_folder = self.folder_input.text() or str(Path.home() / "Documents")

        folder = QFileDialog.getExistingDirectory(
            self,
            "Seleziona Cartella Progetti Predefinita",
            current_folder,
            QFileDialog.Option.ShowDirsOnly
        )

        if folder:
            self.folder_input.setText(folder)

    def _save_and_accept(self):
        """Save settings and close dialog"""
        folder = self.folder_input.text().strip()

        # Validate folder
        if not folder:
            folder = str(Path.home() / "Documents")

        # Save to settings
        self.settings.set_default_projects_folder(folder)

        self.accept()

    def get_default_projects_folder(self) -> str:
        """Get the selected default projects folder"""
        return self.folder_input.text().strip()
