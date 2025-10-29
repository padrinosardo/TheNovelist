"""
Export Dialog - Export project in various formats (PDF, DOCX, Markdown)
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QComboBox, QPushButton, QLabel, QCheckBox,
    QSpinBox, QDoubleSpinBox, QFileDialog, QMessageBox,
    QProgressDialog, QWidget, QFrame
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QFont
from typing import Optional
import os

from managers.project_manager import ProjectManager
from utils.export_manager import ExportManager
from utils.logger import AppLogger


class ExportWorker(QThread):
    """Worker thread for export operations"""
    finished = Signal(bool, str)  # success, message
    progress = Signal(int)  # progress percentage

    def __init__(self, project_manager, format_type, options, output_path):
        super().__init__()
        self.project_manager = project_manager
        self.format_type = format_type
        self.options = options
        self.output_path = output_path

    def run(self):
        """Execute export in background"""
        try:
            self.progress.emit(10)
            success = ExportManager.export(
                self.project_manager,
                self.format_type,
                self.options,
                self.output_path
            )
            self.progress.emit(100)

            if success:
                self.finished.emit(True, f"Export completed successfully!\n\nFile saved to:\n{self.output_path}")
            else:
                self.finished.emit(False, "Export failed. Check the logs for details.")

        except Exception as e:
            AppLogger.error(f"Export worker error: {e}", exc_info=True)
            self.finished.emit(False, f"Export failed with error:\n{str(e)}")


class ExportDialog(QDialog):
    """
    Dialog for exporting projects in various formats.

    Features:
    - Format selection (PDF, DOCX, Markdown)
    - Format-specific options
    - File path selection
    - Export progress feedback
    """

    def __init__(self, project_manager: ProjectManager, parent=None):
        super().__init__(parent)
        self.project_manager = project_manager
        self.setWindowTitle("Export Project")
        self.setMinimumWidth(600)
        self.setMinimumHeight(650)

        # Worker thread
        self.worker = None

        self._setup_ui()
        self._connect_signals()
        self._update_format_options()

    def _setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # Title
        title_label = QLabel("Export Your Project")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Subtitle with project name
        if self.project_manager.current_project:
            subtitle = QLabel(f"Project: {self.project_manager.current_project.title}")
            subtitle.setStyleSheet("color: #666; font-size: 12px;")
            layout.addWidget(subtitle)

        # === FORMAT SELECTION GROUP ===
        format_group = QGroupBox("Export Format")
        format_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2196F3;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        format_layout = QFormLayout()
        format_layout.setSpacing(10)

        # Format combo
        self.format_combo = QComboBox()
        self.format_combo.addItem("📄 PDF (Portable Document Format)", "pdf")
        self.format_combo.addItem("📝 DOCX (Microsoft Word)", "docx")
        self.format_combo.addItem("📋 Markdown (Web/Blog)", "markdown")
        self.format_combo.setToolTip("Select the export format")
        format_layout.addRow("Format:", self.format_combo)

        # Format description
        self.format_description = QLabel()
        self.format_description.setWordWrap(True)
        self.format_description.setStyleSheet("color: #666; font-size: 11px; padding: 5px;")
        format_layout.addRow(self.format_description)

        format_group.setLayout(format_layout)
        layout.addWidget(format_group)

        # === OPTIONS GROUP ===
        self.options_group = QGroupBox("Export Options")
        self.options_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        self.options_layout = QFormLayout()
        self.options_layout.setSpacing(10)

        # Common options
        self.include_cover_check = QCheckBox("Include cover page")
        self.include_cover_check.setChecked(True)
        self.include_cover_check.setToolTip("Include a cover page with project information")
        self.options_layout.addRow(self.include_cover_check)

        self.include_toc_check = QCheckBox("Include table of contents")
        self.include_toc_check.setChecked(True)
        self.include_toc_check.setToolTip("Include a table of contents listing all chapters")
        self.options_layout.addRow(self.include_toc_check)

        self.chapter_page_break_check = QCheckBox("Page break between chapters")
        self.chapter_page_break_check.setChecked(True)
        self.chapter_page_break_check.setToolTip("Start each chapter on a new page")
        self.options_layout.addRow(self.chapter_page_break_check)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.options_layout.addRow(line)

        # Font sizes
        font_label = QLabel("Font Sizes")
        font_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        self.options_layout.addRow(font_label)

        self.chapter_font_spin = QSpinBox()
        self.chapter_font_spin.setRange(12, 36)
        self.chapter_font_spin.setValue(20)
        self.chapter_font_spin.setSuffix(" pt")
        self.chapter_font_spin.setToolTip("Font size for chapter titles")
        self.options_layout.addRow("Chapter Title:", self.chapter_font_spin)

        self.scene_font_spin = QSpinBox()
        self.scene_font_spin.setRange(10, 24)
        self.scene_font_spin.setValue(14)
        self.scene_font_spin.setSuffix(" pt")
        self.scene_font_spin.setToolTip("Font size for scene titles")
        self.options_layout.addRow("Scene Title:", self.scene_font_spin)

        self.content_font_spin = QSpinBox()
        self.content_font_spin.setRange(8, 18)
        self.content_font_spin.setValue(11)
        self.content_font_spin.setSuffix(" pt")
        self.content_font_spin.setToolTip("Font size for content text")
        self.options_layout.addRow("Content Text:", self.content_font_spin)

        # Separator
        line2 = QFrame()
        line2.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        self.options_layout.addRow(line2)

        # Margins (for PDF/DOCX)
        self.margin_label = QLabel("Margins (cm)")
        self.margin_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        self.options_layout.addRow(self.margin_label)

        self.margin_top_spin = QDoubleSpinBox()
        self.margin_top_spin.setRange(0.5, 10.0)
        self.margin_top_spin.setValue(2.5)
        self.margin_top_spin.setSingleStep(0.5)
        self.margin_top_spin.setSuffix(" cm")
        self.options_layout.addRow("Top:", self.margin_top_spin)

        self.margin_bottom_spin = QDoubleSpinBox()
        self.margin_bottom_spin.setRange(0.5, 10.0)
        self.margin_bottom_spin.setValue(2.5)
        self.margin_bottom_spin.setSingleStep(0.5)
        self.margin_bottom_spin.setSuffix(" cm")
        self.options_layout.addRow("Bottom:", self.margin_bottom_spin)

        self.margin_left_spin = QDoubleSpinBox()
        self.margin_left_spin.setRange(0.5, 10.0)
        self.margin_left_spin.setValue(2.5)
        self.margin_left_spin.setSingleStep(0.5)
        self.margin_left_spin.setSuffix(" cm")
        self.options_layout.addRow("Left:", self.margin_left_spin)

        self.margin_right_spin = QDoubleSpinBox()
        self.margin_right_spin.setRange(0.5, 10.0)
        self.margin_right_spin.setValue(2.5)
        self.margin_right_spin.setSingleStep(0.5)
        self.margin_right_spin.setSuffix(" cm")
        self.options_layout.addRow("Right:", self.margin_right_spin)

        # Markdown-specific options
        self.markdown_options_label = QLabel("Markdown Options")
        self.markdown_options_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        self.options_layout.addRow(self.markdown_options_label)

        self.include_frontmatter_check = QCheckBox("Include YAML frontmatter")
        self.include_frontmatter_check.setChecked(True)
        self.include_frontmatter_check.setToolTip("Include Jekyll/Hugo compatible YAML frontmatter")
        self.options_layout.addRow(self.include_frontmatter_check)

        self.include_header_check = QCheckBox("Include document header")
        self.include_header_check.setChecked(True)
        self.include_header_check.setToolTip("Include header with title and project info")
        self.options_layout.addRow(self.include_header_check)

        self.scene_separators_check = QCheckBox("Use scene separators")
        self.scene_separators_check.setChecked(True)
        self.scene_separators_check.setToolTip("Add visual separators between scenes")
        self.options_layout.addRow(self.scene_separators_check)

        self.options_group.setLayout(self.options_layout)
        layout.addWidget(self.options_group)

        # === OUTPUT FILE GROUP ===
        output_group = QGroupBox("Output File")
        output_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #FF9800;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        output_layout = QVBoxLayout()
        output_layout.setSpacing(10)

        # File path input with browse button
        file_row = QHBoxLayout()
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("Click 'Browse' to select output location...")
        self.file_path_input.setReadOnly(True)
        file_row.addWidget(self.file_path_input, 1)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.setMinimumWidth(100)
        file_row.addWidget(self.browse_button)

        output_layout.addLayout(file_row)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # Spacer
        layout.addStretch()

        # === BUTTONS ===
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setMinimumWidth(100)
        button_layout.addWidget(self.cancel_button)

        self.export_button = QPushButton("Export")
        self.export_button.setMinimumWidth(100)
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        button_layout.addWidget(self.export_button)

        layout.addLayout(button_layout)

    def _connect_signals(self):
        """Connect signals to slots"""
        self.format_combo.currentIndexChanged.connect(self._update_format_options)
        self.browse_button.clicked.connect(self._browse_output_file)
        self.export_button.clicked.connect(self._perform_export)
        self.cancel_button.clicked.connect(self.reject)

    def _update_format_options(self):
        """Update UI based on selected format"""
        format_type = self.format_combo.currentData()

        # Update description
        descriptions = {
            'pdf': "Export as a professional PDF document with formatting, ideal for printing and distribution.",
            'docx': "Export as a Microsoft Word document, editable and compatible with Word processors.",
            'markdown': "Export as plain text Markdown, perfect for web publishing and version control."
        }
        self.format_description.setText(descriptions.get(format_type, ""))

        # Show/hide format-specific options
        is_markdown = format_type == 'markdown'

        # Margins only for PDF/DOCX
        self.margin_label.setVisible(not is_markdown)
        self.margin_top_spin.setVisible(not is_markdown)
        self.margin_bottom_spin.setVisible(not is_markdown)
        self.margin_left_spin.setVisible(not is_markdown)
        self.margin_right_spin.setVisible(not is_markdown)

        # Find the rows to hide/show
        for i in range(self.options_layout.rowCount()):
            item = self.options_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            if item and item.widget():
                if item.widget() == self.margin_label:
                    # Hide the label and next 4 rows (top, bottom, left, right)
                    for j in range(5):
                        if i + j < self.options_layout.rowCount():
                            label_item = self.options_layout.itemAt(i + j, QFormLayout.ItemRole.LabelRole)
                            field_item = self.options_layout.itemAt(i + j, QFormLayout.ItemRole.FieldRole)
                            if label_item and label_item.widget():
                                label_item.widget().setVisible(not is_markdown)
                            if field_item and field_item.widget():
                                field_item.widget().setVisible(not is_markdown)

        # Markdown-specific options
        self.markdown_options_label.setVisible(is_markdown)
        self.include_frontmatter_check.setVisible(is_markdown)
        self.include_header_check.setVisible(is_markdown)
        self.scene_separators_check.setVisible(is_markdown)

        # Update suggested file path if one exists
        if self.file_path_input.text():
            current_path = self.file_path_input.text()
            # Change extension
            base_path = os.path.splitext(current_path)[0]
            extensions = {'pdf': '.pdf', 'docx': '.docx', 'markdown': '.md'}
            new_path = base_path + extensions[format_type]
            self.file_path_input.setText(new_path)

    def _browse_output_file(self):
        """Open file dialog to select output location"""
        format_type = self.format_combo.currentData()

        # File filters
        filters = {
            'pdf': "PDF Files (*.pdf)",
            'docx': "Word Documents (*.docx)",
            'markdown': "Markdown Files (*.md)"
        }

        # Default filename
        if self.project_manager.current_project:
            default_name = self.project_manager.current_project.title.replace(' ', '_')
        else:
            default_name = "export"

        extensions = {'pdf': '.pdf', 'docx': '.docx', 'markdown': '.md'}
        default_filename = default_name + extensions[format_type]

        # Use project directory as default location
        if self.project_manager.current_filepath:
            project_dir = os.path.dirname(self.project_manager.current_filepath)
            default_path = os.path.join(project_dir, default_filename)
        else:
            default_path = default_filename

        # Open save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Export As",
            default_path,
            filters[format_type]
        )

        if file_path:
            self.file_path_input.setText(file_path)

    def _collect_options(self) -> dict:
        """Collect export options from UI"""
        format_type = self.format_combo.currentData()

        options = {
            'include_cover': self.include_cover_check.isChecked(),
            'include_toc': self.include_toc_check.isChecked(),
            'chapter_page_break': self.chapter_page_break_check.isChecked(),
            'chapter_font_size': self.chapter_font_spin.value(),
            'scene_font_size': self.scene_font_spin.value(),
            'content_font_size': self.content_font_spin.value(),
        }

        # Add format-specific options
        if format_type in ['pdf', 'docx']:
            options.update({
                'margin_top': self.margin_top_spin.value(),
                'margin_bottom': self.margin_bottom_spin.value(),
                'margin_left': self.margin_left_spin.value(),
                'margin_right': self.margin_right_spin.value(),
            })

        if format_type == 'markdown':
            options.update({
                'include_frontmatter': self.include_frontmatter_check.isChecked(),
                'include_header': self.include_header_check.isChecked(),
                'scene_separators': self.scene_separators_check.isChecked(),
                'separator_style': '* * *'
            })

        return options

    def _perform_export(self):
        """Perform the export operation"""
        # Validate inputs
        output_path = self.file_path_input.text().strip()
        if not output_path:
            QMessageBox.warning(
                self,
                "No Output File",
                "Please select an output file location using the Browse button."
            )
            return

        # Check if project is loaded
        if not self.project_manager.has_project():
            QMessageBox.critical(
                self,
                "No Project",
                "No project is currently loaded. Please open or create a project first."
            )
            return

        # Collect options
        format_type = self.format_combo.currentData()
        options = self._collect_options()

        # Create progress dialog
        progress = QProgressDialog("Exporting project...", "Cancel", 0, 100, self)
        progress.setWindowTitle("Export Progress")
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)

        # Create and start worker thread
        self.worker = ExportWorker(self.project_manager, format_type, options, output_path)
        self.worker.progress.connect(progress.setValue)
        self.worker.finished.connect(lambda success, msg: self._on_export_finished(success, msg, progress))
        self.worker.start()

    def _on_export_finished(self, success: bool, message: str, progress: QProgressDialog):
        """Handle export completion"""
        progress.close()

        if success:
            # Show success message
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.setWindowTitle("Export Successful")
            msg_box.setText(message)
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg_box.exec()

            # Close dialog
            self.accept()
        else:
            # Show error message
            QMessageBox.critical(
                self,
                "Export Failed",
                message
            )
