"""
Insert Table Dialog - Dialog for configuring and inserting a table
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QSpinBox, QGroupBox, QFormLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class InsertTableDialog(QDialog):
    """
    Dialog for inserting a table with configurable rows and columns
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Inserisci Tabella")
        self.setMinimumWidth(350)
        self._initialize_ui()

    def _initialize_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("📊 Inserisci Tabella")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Dimensions group
        dimensions_group = QGroupBox("Dimensioni Tabella")
        dimensions_layout = QFormLayout()

        # Rows spinbox
        self.rows_spin = QSpinBox()
        self.rows_spin.setMinimum(1)
        self.rows_spin.setMaximum(50)
        self.rows_spin.setValue(3)
        self.rows_spin.setSuffix(" righe")
        dimensions_layout.addRow("Righe:", self.rows_spin)

        # Columns spinbox
        self.cols_spin = QSpinBox()
        self.cols_spin.setMinimum(1)
        self.cols_spin.setMaximum(20)
        self.cols_spin.setValue(3)
        self.cols_spin.setSuffix(" colonne")
        dimensions_layout.addRow("Colonne:", self.cols_spin)

        dimensions_group.setLayout(dimensions_layout)
        layout.addWidget(dimensions_group)

        # Info label
        info = QLabel(
            "💡 Dopo aver inserito la tabella, puoi:\n"
            "  • Aggiungere o rimuovere righe e colonne\n"
            "  • Modificare il contenuto delle celle\n"
            "  • Eliminare l'intera tabella"
        )
        info.setStyleSheet("""
            QLabel {
                background-color: #E3F2FD;
                padding: 10px;
                border-radius: 4px;
                color: #1976D2;
            }
        """)
        info.setWordWrap(True)
        layout.addWidget(info)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_btn = QPushButton("Annulla")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        buttons_layout.addWidget(cancel_btn)

        insert_btn = QPushButton("Inserisci")
        insert_btn.clicked.connect(self.accept)
        insert_btn.setDefault(True)
        insert_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        buttons_layout.addWidget(insert_btn)

        layout.addLayout(buttons_layout)

    def get_rows(self):
        """
        Get the number of rows selected

        Returns:
            int: Number of rows
        """
        return self.rows_spin.value()

    def get_columns(self):
        """
        Get the number of columns selected

        Returns:
            int: Number of columns
        """
        return self.cols_spin.value()
