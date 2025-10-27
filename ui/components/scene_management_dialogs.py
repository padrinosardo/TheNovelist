"""
Scene Management Dialogs - Dialogs for managing chapters and scenes
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QMessageBox)
from PySide6.QtCore import Qt


class ChapterDialog(QDialog):
    """
    Dialog for adding or renaming a chapter
    """

    def __init__(self, parent=None, current_title: str = "", mode: str = "add"):
        """
        Initialize the dialog

        Args:
            parent: Parent widget
            current_title: Current title (for rename mode)
            mode: "add" or "rename"
        """
        super().__init__(parent)
        self.mode = mode
        self.title_value = ""
        self._setup_ui(current_title)

    def _setup_ui(self, current_title: str):
        """Setup the user interface"""
        if self.mode == "add":
            self.setWindowTitle("Add New Chapter")
        else:
            self.setWindowTitle("Rename Chapter")

        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title label
        label = QLabel("Chapter Title:")
        label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(label)

        # Title input
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter chapter title...")
        self.title_input.setText(current_title)
        self.title_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 13px;
                border: 2px solid #ddd;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        self.title_input.selectAll()
        layout.addWidget(self.title_input)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                padding: 8px 20px;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        ok_button = QPushButton("Create" if self.mode == "add" else "Rename")
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        ok_button.clicked.connect(self._on_ok)
        ok_button.setDefault(True)
        buttons_layout.addWidget(ok_button)

        layout.addLayout(buttons_layout)

        # Focus on input
        self.title_input.setFocus()

    def _on_ok(self):
        """Handle OK button click"""
        title = self.title_input.text().strip()

        if not title:
            QMessageBox.warning(
                self,
                "Invalid Title",
                "Chapter title cannot be empty."
            )
            return

        if len(title) > 100:
            QMessageBox.warning(
                self,
                "Title Too Long",
                "Chapter title cannot exceed 100 characters."
            )
            return

        self.title_value = title
        self.accept()

    def get_title(self) -> str:
        """
        Get the entered title

        Returns:
            str: Chapter title
        """
        return self.title_value


class SceneDialog(QDialog):
    """
    Dialog for adding or renaming a scene
    """

    def __init__(self, parent=None, current_title: str = "", mode: str = "add"):
        """
        Initialize the dialog

        Args:
            parent: Parent widget
            current_title: Current title (for rename mode)
            mode: "add" or "rename"
        """
        super().__init__(parent)
        self.mode = mode
        self.title_value = ""
        self._setup_ui(current_title)

    def _setup_ui(self, current_title: str):
        """Setup the user interface"""
        if self.mode == "add":
            self.setWindowTitle("Add New Scene")
        else:
            self.setWindowTitle("Rename Scene")

        self.setModal(True)
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title label
        label = QLabel("Scene Title:")
        label.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(label)

        # Title input
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter scene title...")
        self.title_input.setText(current_title)
        self.title_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 13px;
                border: 2px solid #ddd;
                border-radius: 4px;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)
        self.title_input.selectAll()
        layout.addWidget(self.title_input)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                padding: 8px 20px;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_button)

        ok_button = QPushButton("Create" if self.mode == "add" else "Rename")
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        ok_button.clicked.connect(self._on_ok)
        ok_button.setDefault(True)
        buttons_layout.addWidget(ok_button)

        layout.addLayout(buttons_layout)

        # Focus on input
        self.title_input.setFocus()

    def _on_ok(self):
        """Handle OK button click"""
        title = self.title_input.text().strip()

        if not title:
            QMessageBox.warning(
                self,
                "Invalid Title",
                "Scene title cannot be empty."
            )
            return

        if len(title) > 100:
            QMessageBox.warning(
                self,
                "Title Too Long",
                "Scene title cannot exceed 100 characters."
            )
            return

        self.title_value = title
        self.accept()

    def get_title(self) -> str:
        """
        Get the entered title

        Returns:
            str: Scene title
        """
        return self.title_value


def show_delete_chapter_confirmation(parent, chapter_title: str, scene_count: int) -> bool:
    """
    Show confirmation dialog for deleting a chapter

    Args:
        parent: Parent widget
        chapter_title: Title of chapter to delete
        scene_count: Number of scenes in chapter

    Returns:
        bool: True if user confirmed deletion
    """
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle("Delete Chapter")
    msg.setText(f"Are you sure you want to delete '{chapter_title}'?")

    if scene_count > 0:
        msg.setInformativeText(
            f"This chapter contains {scene_count} scene(s).\n"
            "All scenes and their content will be permanently deleted.\n\n"
            "This action cannot be undone."
        )
    else:
        msg.setInformativeText("This action cannot be undone.")

    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg.setDefaultButton(QMessageBox.StandardButton.No)

    return msg.exec() == QMessageBox.StandardButton.Yes


def show_delete_scene_confirmation(parent, scene_title: str, word_count: int) -> bool:
    """
    Show confirmation dialog for deleting a scene

    Args:
        parent: Parent widget
        scene_title: Title of scene to delete
        word_count: Word count in scene

    Returns:
        bool: True if user confirmed deletion
    """
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle("Delete Scene")
    msg.setText(f"Are you sure you want to delete '{scene_title}'?")

    if word_count > 0:
        msg.setInformativeText(
            f"This scene contains {word_count} word(s) that will be permanently deleted.\n\n"
            "This action cannot be undone."
        )
    else:
        msg.setInformativeText("This action cannot be undone.")

    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
    msg.setDefaultButton(QMessageBox.StandardButton.No)

    return msg.exec() == QMessageBox.StandardButton.Yes
