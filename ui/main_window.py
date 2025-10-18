"""
Main application window
"""
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QPushButton, QProgressBar, QSplitter,
                               QGroupBox, QMessageBox, QFileDialog)  # Aggiungi QFileDialog

from utils.file_manager import FileManager

import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ui.pannels import ResultsPanel, TextEditor
from ui.styles import (STILE_BTN_GRAMMATICA, STILE_BTN_RIPETIZIONI,
                       STILE_BTN_STILE, STILE_BTN_PULISCI, Stili)

from workers.thread_analysis import AnalysisThread
from analysis.grammar import GrammarAnalyzer
from analysis.repetition import RepetitionAnalyzer
from analysis.style import StyleAnalyzer


class WritingAssistant(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()

        # Current worker thread
        self.analysis_thread = None

        # Analyzers (to format results)
        self.grammar_analyzer = GrammarAnalyzer()
        self.repetitions_analyzer = RepetitionAnalyzer()
        self.style_analyzer = StyleAnalyzer()

        # File manager
        self.file_manager = FileManager()

        # Track if document has unsaved changes
        self.is_modified = False

        self._initialize_ui()

    def _initialize_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("📝 Writing Assistant - The Novelist")
        self.setGeometry(50, 50, 1400, 800)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Header with title and buttons
        header = self._create_header()
        main_layout.addWidget(header)

        # Main splitter (horizontal)
        main_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(main_splitter)

        # Left panel: Editor
        editor_panel = self._create_editor_panel()
        main_splitter.addWidget(editor_panel)

        # Right panel: Analysis
        analysis_panel = self._create_analysis_panel()
        main_splitter.addWidget(analysis_panel)

        # Proportions (60% editor, 40% analysis)
        main_splitter.setStretchFactor(0, 6)
        main_splitter.setStretchFactor(1, 4)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setMaximumHeight(20)
        self.progress.setStyleSheet(Stili.progress_bar())


        main_layout.addWidget(self.progress)

        # Status bar
        self.statusBar().showMessage(
            "Ready - Write your text and analyze it with the buttons"
        )



    def _create_header(self):
        """Create header with title and buttons"""
        header_widget = QWidget()
        header_layout = QHBoxLayout()
        header_widget.setLayout(header_layout)
        header_widget.setStyleSheet(Stili.header())

        # Title
        title = QLabel("📝 The Novelist")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        header_layout.addWidget(title)

        # File name label
        self.filename_label = QLabel("Untitled")
        self.filename_label.setStyleSheet("color: #666; font-size: 12px; margin-left: 10px;")
        header_layout.addWidget(self.filename_label)

        header_layout.addStretch()

        # File buttons
        self.btn_new = QPushButton("📄 New")
        self.btn_new.clicked.connect(self.new_document)
        self.btn_new.setStyleSheet(Stili.bottone("#607D8B"))
        header_layout.addWidget(self.btn_new)

        self.btn_open = QPushButton("📂 Open")
        self.btn_open.clicked.connect(self.open_document)
        self.btn_open.setStyleSheet(Stili.bottone("#607D8B"))
        header_layout.addWidget(self.btn_open)

        self.btn_save = QPushButton("💾 Save")
        self.btn_save.clicked.connect(self.save_document)
        self.btn_save.setStyleSheet(Stili.bottone("#4CAF50"))
        header_layout.addWidget(self.btn_save)

        self.btn_save_as = QPushButton("💾 Save As")
        self.btn_save_as.clicked.connect(self.save_document_as)
        self.btn_save_as.setStyleSheet(Stili.bottone("#4CAF50"))
        header_layout.addWidget(self.btn_save_as)

        # Separator
        separator = QLabel("|")
        separator.setStyleSheet("color: #ccc; margin: 0 10px;")
        header_layout.addWidget(separator)

        # Analysis buttons
        self.btn_grammar = QPushButton("📖 Grammar")
        self.btn_grammar.clicked.connect(self.analyze_grammar)
        self.btn_grammar.setStyleSheet(STILE_BTN_GRAMMATICA)
        header_layout.addWidget(self.btn_grammar)

        self.btn_repetitions = QPushButton("🔄 Repetitions")
        self.btn_repetitions.clicked.connect(self.analyze_repetitions)
        self.btn_repetitions.setStyleSheet(STILE_BTN_RIPETIZIONI)
        header_layout.addWidget(self.btn_repetitions)

        self.btn_style = QPushButton("✍️ Style")
        self.btn_style.clicked.connect(self.analyze_style)
        self.btn_style.setStyleSheet(STILE_BTN_STILE)
        header_layout.addWidget(self.btn_style)

        self.btn_clear = QPushButton("🗑️ Clear")
        self.btn_clear.clicked.connect(self.clear_all)
        self.btn_clear.setStyleSheet(STILE_BTN_PULISCI)
        header_layout.addWidget(self.btn_clear)

        return header_widget

    def _create_editor_panel(self):
        """Create the editor panel"""
        group = QGroupBox("📄 Text Editor")
        group.setStyleSheet(Stili.gruppo())
        layout = QVBoxLayout()
        group.setLayout(layout)

        # Custom editor widget
        self.editor = TextEditor()

        # Track changes
        self.editor.editor.textChanged.connect(self._on_text_changed)

        layout.addWidget(self.editor)

        return group

    def _create_analysis_panel(self):
        """Create the panel with analyses"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        # Vertical splitter for panels
        analysis_splitter = QSplitter(Qt.Vertical)

        # Results panels
        self.grammar_panel = ResultsPanel("Grammar", "📖")
        analysis_splitter.addWidget(self.grammar_panel)

        self.repetitions_panel = ResultsPanel("Repetitions", "🔄")
        analysis_splitter.addWidget(self.repetitions_panel)

        self.style_panel = ResultsPanel("Style", "✍️")
        analysis_splitter.addWidget(self.style_panel)

        # Equal proportions
        for i in range(3):
            analysis_splitter.setStretchFactor(i, 1)

        layout.addWidget(analysis_splitter)

        return widget

    def _get_validated_text(self):
        """
        Get and validate text from editor

        Returns:
            str or None: Validated text or None if empty
        """
        text = self.editor.get_text().strip()
        if not text:
            QMessageBox.warning(
                self,
                "Warning",
                "Write some text before analyzing!"
            )
            return None
        return text

    def _start_analysis(self, analysis_type, panel, analysis_name):
        """
        Start an analysis in background

        Args:
            analysis_type: Type of analysis to perform
            panel: Panel where to show results
            analysis_name: Analysis name for messages
        """
        text = self._get_validated_text()
        if not text:
            return

        # Show feedback
        panel.set_text("⏳ Analysis in progress...")
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)  # Indeterminate
        self.statusBar().showMessage(f"{analysis_name} in progress...")

        # Disable buttons during analysis
        self._set_buttons_enabled(False)

        # Start thread
        self.analysis_thread = AnalysisThread(text, analysis_type)
        self.analysis_thread.finished.connect(
            lambda result: self._handle_result(
                result, panel, analysis_name, analysis_type
            )
        )
        self.analysis_thread.start()

    def _handle_result(self, result, panel, analysis_name, analysis_type):
        """Handle analysis result"""
        # Hide progress and re-enable buttons
        self.progress.setVisible(False)
        self._set_buttons_enabled(True)

        # Format and show result
        if analysis_type == AnalysisThread.TYPE_GRAMMAR:
            formatted_text = self.grammar_analyzer.format_results(result)

            # NUOVO: Highlight errors in editor
            if result.get('success') and result.get('errors'):
                self.editor.highlight_errors(result['errors'])

        elif analysis_type == AnalysisThread.TYPE_REPETITIONS:
            formatted_text = self.repetitions_analyzer.format_results(result)
        elif analysis_type == AnalysisThread.TYPE_STYLE:
            formatted_text = self.style_analyzer.format_results(result)
        else:
            formatted_text = "Error: unknown analysis type"

        panel.set_text(formatted_text)

        # Status message
        if result.get('success'):
            self.statusBar().showMessage(f"{analysis_name} completed", 3000)
        else:
            self.statusBar().showMessage(f"Error in {analysis_name}", 3000)

    def _set_buttons_enabled(self, enabled):
        """Enable/disable buttons"""
        self.btn_grammar.setEnabled(enabled)
        self.btn_repetitions.setEnabled(enabled)
        self.btn_style.setEnabled(enabled)

    def analyze_grammar(self):
        """Start grammar analysis"""
        self._start_analysis(
            AnalysisThread.TYPE_GRAMMAR,
            self.grammar_panel,
            "Grammar analysis"
        )

    def analyze_repetitions(self):
        """Start repetitions analysis"""
        self._start_analysis(
            AnalysisThread.TYPE_REPETITIONS,
            self.repetitions_panel,
            "Repetitions analysis"
        )

    def analyze_style(self):
        """Start style analysis"""
        self._start_analysis(

            AnalysisThread.TYPE_STYLE,
            self.style_panel,
            "Style analysis"
        )

    def clear_all(self):
        """Clear editor and all panels"""
        response = QMessageBox.question(
            self,
            "Confirm",
            "Do you want to clear all text and analyses?",
            QMessageBox.Yes | QMessageBox.No
        )

        if response == QMessageBox.Yes:
            self.editor.clear()
            self.editor.clear_highlights()  # AGGIUNGI QUESTA RIGA
            self.grammar_panel.clear()
            self.repetitions_panel.clear()
            self.style_panel.clear()
            self.statusBar().showMessage("All cleared", 2000)


    def _on_text_changed(self):
        """Called when text is modified"""
        if not self.is_modified:
            self.is_modified = True
            self._update_window_title()


    def _update_window_title(self):
        """Update window title with filename and modified status"""
        filename = self.file_manager.get_filename()
        modified = "*" if self.is_modified else ""
        self.setWindowTitle(f"📝 The Novelist - {filename}{modified}")
        self.filename_label.setText(f"{filename}{modified}")


    def new_document(self):
        """Create a new document"""
        if self.is_modified:
            response = QMessageBox.question(
                self,
                "Unsaved Changes",
                "Do you want to save changes before creating a new document?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if response == QMessageBox.Save:
                if not self.save_document():
                    return  # Cancelled save
            elif response == QMessageBox.Cancel:
                return

        # Clear everything
        self.editor.clear()
        self.grammar_panel.clear()
        self.repetitions_panel.clear()
        self.style_panel.clear()

        # Reset state
        self.file_manager.clear_file()
        self.is_modified = False
        self._update_window_title()

        self.statusBar().showMessage("New document created", 2000)


    def open_document(self):
        """Open an existing document"""
        if self.is_modified:
            response = QMessageBox.question(
                self,
                "Unsaved Changes",
                "Do you want to save changes before opening another document?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if response == QMessageBox.Save:
                if not self.save_document():
                    return
            elif response == QMessageBox.Cancel:
                return

        # Show open dialog
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open Document",
            self.file_manager.last_directory,
            self.file_manager.get_file_filter()
        )

        if not filepath:
            return  # Cancelled

        # Load file
        text = self.file_manager.load_document(filepath)

        if text is not None:
            self.editor.set_text(text)
            self.is_modified = False
            self._update_window_title()
            self.statusBar().showMessage(f"Opened: {self.file_manager.get_filename()}", 3000)
        else:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not open file:\n{filepath}"
            )


    def save_document(self):
        """Save current document"""
        if not self.file_manager.has_file():
            return self.save_document_as()

        text = self.editor.get_text()

        if self.file_manager.save_document(text, self.file_manager.current_file):
            self.is_modified = False
            self._update_window_title()
            self.statusBar().showMessage(f"Saved: {self.file_manager.get_filename()}", 3000)
            return True
        else:
            QMessageBox.critical(
                self,
                "Error",
                "Could not save file"
            )
            return False


    def save_document_as(self):
        """Save current document with a new name"""
        # Show save dialog
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Document As",
            self.file_manager.last_directory,
            self.file_manager.get_file_filter()
        )

        if not filepath:
            return False  # Cancelled

        # Add extension if missing
        if not os.path.splitext(filepath)[1]:
            filepath += ".txt"

        text = self.editor.get_text()

        if self.file_manager.save_document(text, filepath):
            self.is_modified = False
            self._update_window_title()
            self.statusBar().showMessage(f"Saved as: {self.file_manager.get_filename()}", 3000)
            return True
        else:
            QMessageBox.critical(
                self,
                "Error",
                f"Could not save file:\n{filepath}"
            )
            return False