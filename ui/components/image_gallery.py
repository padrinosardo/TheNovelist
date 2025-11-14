"""
Image Gallery Widget - Drag & drop image management
"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QFrame, QFileDialog, QScrollArea,
                               QMessageBox)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap, QDragEnterEvent, QDropEvent
from typing import List
import os


class ImageGalleryWidget(QWidget):
    """
    Image gallery with drag & drop support
    """

    # Signals
    image_added = Signal(str)  # image_source_path
    image_removed = Signal(str)  # image_filename

    def __init__(self, parent=None):
        super().__init__(parent)
        self._image_paths = []
        self._setup_ui()

    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)

        # Header
        header = QHBoxLayout()

        title = QLabel("Character Images")
        title.setStyleSheet("font-size: 14px; font-weight: bold;")
        header.addWidget(title)

        header.addStretch()

        # Add image button
        self.add_btn = QPushButton("+ Add Image")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 13px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #616161;
            }
            QPushButton:pressed {
                background-color: #424242;
            }
        """)
        self.add_btn.clicked.connect(self._select_image)
        header.addWidget(self.add_btn)

        layout.addLayout(header)

        # Scroll area for thumbnails
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(200)
        scroll.setMaximumHeight(300)

        # Container for thumbnails
        self.thumbnails_container = QWidget()
        self.thumbnails_layout = QHBoxLayout(self.thumbnails_container)
        self.thumbnails_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.thumbnails_layout.setSpacing(10)

        scroll.setWidget(self.thumbnails_container)

        # Drop zone
        self.drop_zone = DropZoneWidget()
        self.drop_zone.file_dropped.connect(self._on_file_dropped)

        layout.addWidget(scroll)
        layout.addWidget(self.drop_zone)

    def load_images(self, image_paths: List[str]):
        """
        Load and display images

        Args:
            image_paths: List of full image paths
        """
        self._image_paths = image_paths

        # Clear existing thumbnails
        self._clear_thumbnails()

        # Create thumbnail for each image
        for image_path in image_paths:
            if os.path.exists(image_path):
                thumbnail = ImageThumbnail(image_path)
                thumbnail.remove_requested.connect(self._on_remove_image)
                self.thumbnails_layout.addWidget(thumbnail)

        # Show/hide drop zone based on image count
        self.drop_zone.setVisible(len(image_paths) == 0)

    def _clear_thumbnails(self):
        """Remove all thumbnail widgets"""
        while self.thumbnails_layout.count():
            item = self.thumbnails_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _select_image(self):
        """Open file dialog to select an image"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Select Character Image",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp);;All Files (*.*)"
        )

        if filepath:
            self.image_added.emit(filepath)

    def _on_file_dropped(self, filepath: str):
        """
        Handle file drop

        Args:
            filepath: Dropped file path
        """
        # Validate image file
        valid_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        ext = os.path.splitext(filepath)[1].lower()

        if ext in valid_extensions:
            self.image_added.emit(filepath)
        else:
            QMessageBox.warning(
                self,
                "Invalid File",
                "Please drop an image file (PNG, JPG, GIF, BMP)"
            )

    def _on_remove_image(self, image_path: str):
        """
        Handle image removal request

        Args:
            image_path: Path to image to remove
        """
        filename = os.path.basename(image_path)
        self.image_removed.emit(filename)

    def get_image_count(self) -> int:
        """
        Get number of images

        Returns:
            int: Image count
        """
        return len(self._image_paths)


class ImageThumbnail(QFrame):
    """
    Single image thumbnail with remove button
    """

    remove_requested = Signal(str)  # image_path

    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self._setup_ui()

    def _setup_ui(self):
        """Setup the thumbnail UI"""
        self.setFixedSize(150, 150)
        self.setStyleSheet("""
            QFrame {
                background-color: #f5f5f5;
                border: 2px solid #ddd;
                border-radius: 4px;
            }
            QFrame:hover {
                border: 2px solid #2196F3;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Image
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                150, 120,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            image_label.setPixmap(scaled)
        else:
            image_label.setText("❌")

        layout.addWidget(image_label)

        # Remove button
        remove_btn = QPushButton("Remove")
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #757575;
                color: white;
                border: none;
                padding: 4px;
                font-size: 11px;
                font-weight: bold;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #616161;
            }
            QPushButton:pressed {
                background-color: #424242;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_requested.emit(self.image_path))
        layout.addWidget(remove_btn)


class DropZoneWidget(QFrame):
    """
    Drag & drop zone for images
    """

    file_dropped = Signal(str)  # filepath

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.setAcceptDrops(True)

    def _setup_ui(self):
        """Setup the drop zone UI"""
        self.setMinimumHeight(150)
        self.setStyleSheet("""
            QFrame {
                background-color: #fafafa;
                border: 2px dashed #ccc;
                border-radius: 8px;
            }
            QFrame:hover {
                border: 2px dashed #2196F3;
                background-color: #e3f2fd;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon = QLabel("🖼️")
        icon.setStyleSheet("font-size: 48px;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        text = QLabel("Drag & drop images here\nor click '+ Add Image' button")
        text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text.setStyleSheet("color: #666; font-size: 13px;")
        layout.addWidget(text)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """Handle file drop"""
        urls = event.mimeData().urls()
        if urls:
            filepath = urls[0].toLocalFile()
            self.file_dropped.emit(filepath)
