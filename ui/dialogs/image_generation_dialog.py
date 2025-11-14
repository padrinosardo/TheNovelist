"""
Image Generation Dialog - Interfaccia per generare immagini AI

Features:
- Preview prompt
- Selezione stile, dimensione, qualità
- Display costo stimato
- Progress indicator
- Preview risultati
"""
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QTextEdit, QComboBox, QPushButton, QSpinBox,
                               QProgressBar, QMessageBox, QScrollArea, QWidget,
                               QGridLayout, QFrame, QCheckBox)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QPixmap, QFont
from typing import Optional, List
from pathlib import Path

from managers.ai.image_generator import AIImageGenerator, ImageGenerationResult
from managers.ai.prompt_builder import ImagePromptBuilder, ImageStyle


class ImageGenerationWorker(QThread):
    """Worker thread per generazione immagini async"""

    finished = Signal(list)  # List[ImageGenerationResult]
    error = Signal(str)

    def __init__(self, generator: AIImageGenerator, prompt: str,
                 model: str, size: str, quality: str, n: int,
                 save_directory: Path, filename_prefix: str):
        super().__init__()
        self.generator = generator
        self.prompt = prompt
        self.model = model
        self.size = size
        self.quality = quality
        self.n = n
        self.save_directory = save_directory
        self.filename_prefix = filename_prefix

    def run(self):
        """Genera immagini in background"""
        try:
            results = self.generator.generate_image(
                prompt=self.prompt,
                model=self.model,
                size=self.size,
                quality=self.quality,
                n=self.n,
                save_directory=self.save_directory,
                filename_prefix=self.filename_prefix
            )
            self.finished.emit(results)
        except Exception as e:
            self.error.emit(str(e))


class ImageGenerationDialog(QDialog):
    """
    Dialog per generare immagini AI

    Features:
    - Personalizzazione prompt
    - Selezione parametri (stile, size, quality)
    - Display costo stimato
    - Preview risultati
    """

    images_generated = Signal(list)  # List[str] - paths delle immagini selezionate

    def __init__(self, api_key: str, entity_type: str, entity_name: str,
                 description: str = "", location_type: str = "",
                 save_directory: Optional[Path] = None, parent=None):
        """
        Initialize dialog

        Args:
            api_key: OpenAI API key
            entity_type: "character" o "location"
            entity_name: Nome entità
            description: Descrizione entità
            location_type: Tipo location (solo per location)
            save_directory: Directory dove salvare immagini
            parent: Parent widget
        """
        super().__init__(parent)

        self.api_key = api_key
        self.entity_type = entity_type
        self.entity_name = entity_name
        self.description = description
        self.location_type = location_type
        self.save_directory = save_directory or Path.cwd() / "generated_images"

        self.generator = AIImageGenerator(api_key)
        self.worker: Optional[ImageGenerationWorker] = None
        self.results: List[ImageGenerationResult] = []

        self._setup_ui()
        self._populate_default_prompt()

    def _setup_ui(self):
        """Setup UI"""
        self.setWindowTitle(f"Genera Immagine - {self.entity_name}")
        self.setMinimumWidth(600)
        self.setMinimumHeight(700)

        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel(f"🎨 Genera Immagine per: {self.entity_name}")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # === PROMPT SECTION ===
        prompt_label = QLabel("Prompt Descrizione:")
        prompt_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(prompt_label)

        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText(
            "Inserisci la descrizione fisica del personaggio...\n"
            "Esempio: donna 25 anni, capelli biondi lunghi, occhi verdi, corporatura atletica, vestito elegante"
        )
        self.prompt_edit.setMaximumHeight(120)
        self.prompt_edit.textChanged.connect(self._update_cost_estimate)
        layout.addWidget(self.prompt_edit)

        # === PARAMETERS SECTION ===
        params_frame = QFrame()
        params_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        params_layout = QVBoxLayout(params_frame)

        # Style
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("Stile:"))
        self.style_combo = QComboBox()
        styles = ImagePromptBuilder.get_all_styles()
        for value, name in styles.items():
            self.style_combo.addItem(name, value)
        # Default: Digital Art for characters, Concept Art for locations
        default_style = "digital_art" if self.entity_type == "character" else "concept_art"
        index = self.style_combo.findData(default_style)
        if index >= 0:
            self.style_combo.setCurrentIndex(index)
        self.style_combo.currentIndexChanged.connect(self._on_style_changed)
        style_layout.addWidget(self.style_combo)
        params_layout.addLayout(style_layout)

        # Model
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Modello:"))
        self.model_combo = QComboBox()
        self.model_combo.addItem("DALL-E 3 (Alta Qualità)", "dall-e-3")
        self.model_combo.addItem("DALL-E 2 (Economico)", "dall-e-2")
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        model_layout.addWidget(self.model_combo)
        params_layout.addLayout(model_layout)

        # Size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Dimensioni:"))
        self.size_combo = QComboBox()
        self._update_size_options()
        self.size_combo.currentIndexChanged.connect(self._update_cost_estimate)
        size_layout.addWidget(self.size_combo)
        params_layout.addLayout(size_layout)

        # Quality (DALL-E 3 only)
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Qualità:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItem("Standard", "standard")
        self.quality_combo.addItem("HD", "hd")
        self.quality_combo.currentIndexChanged.connect(self._update_cost_estimate)
        quality_layout.addWidget(self.quality_combo)
        params_layout.addLayout(quality_layout)

        layout.addWidget(params_frame)

        # === COST ESTIMATE ===
        self.cost_label = QLabel("Costo stimato: $0.00")
        self.cost_label.setStyleSheet("""
            QLabel {
                background-color: #FFF3CD;
                color: #856404;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.cost_label)

        # === PROGRESS BAR ===
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # === RESULTS SECTION ===
        self.results_label = QLabel("Risultati:")
        self.results_label.setStyleSheet("font-weight: bold;")
        self.results_label.setVisible(False)
        layout.addWidget(self.results_label)

        # Results scroll area
        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setMinimumHeight(200)
        self.results_scroll.setVisible(False)

        self.results_widget = QWidget()
        self.results_layout = QGridLayout(self.results_widget)
        self.results_scroll.setWidget(self.results_widget)
        layout.addWidget(self.results_scroll)

        # === BUTTONS ===
        buttons_layout = QHBoxLayout()

        self.generate_btn = QPushButton("🎨 Genera Immagine")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.generate_btn.clicked.connect(self._generate_images)
        buttons_layout.addWidget(self.generate_btn)

        self.save_btn = QPushButton("💾 Salva Selezionate")
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.save_btn.clicked.connect(self._save_selected)
        buttons_layout.addWidget(self.save_btn)

        cancel_btn = QPushButton("Annulla")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

        # Initial cost estimate
        self._update_cost_estimate()

    def _populate_default_prompt(self):
        """
        NON popola automaticamente il prompt.
        L'utente deve inserire manualmente la descrizione fisica.
        Questo evita problemi con contenuti sensibili e dà pieno controllo.
        """
        # Campo lasciato vuoto intenzionalmente
        # L'utente scriverà la propria descrizione fisica
        pass

    def _on_style_changed(self):
        """
        Quando cambia lo stile, non modifichiamo il prompt dell'utente.
        Lo stile viene applicato automaticamente durante la generazione.
        """
        # Non facciamo nulla - preserviamo il testo inserito dall'utente
        pass

    def _on_model_changed(self):
        """Aggiorna opzioni quando cambia modello"""
        self._update_size_options()
        self._update_quality_options()
        self._update_cost_estimate()

    def _update_size_options(self):
        """Aggiorna opzioni dimensioni in base al modello"""
        model = self.model_combo.currentData()
        sizes = AIImageGenerator.get_available_sizes(model)

        self.size_combo.clear()
        for size in sizes:
            self.size_combo.addItem(size, size)

    def _update_quality_options(self):
        """Aggiorna opzioni qualità in base al modello"""
        model = self.model_combo.currentData()
        self.quality_combo.setEnabled(model == "dall-e-3")

    def _update_cost_estimate(self):
        """Aggiorna stima costo"""
        model = self.model_combo.currentData()
        size = self.size_combo.currentData()
        quality = self.quality_combo.currentData()

        if not model or not size:
            return

        cost = self.generator.estimate_cost(
            model=model,
            size=size,
            quality=quality,
            n=1
        )

        self.cost_label.setText(f"Costo stimato: ${cost:.3f}")

    def _generate_images(self):
        """Avvia generazione immagini"""
        user_description = self.prompt_edit.toPlainText().strip()

        if not user_description:
            QMessageBox.warning(self, "Prompt Vuoto",
                              "Inserisci una descrizione fisica del personaggio.")
            return

        # Costruisci prompt finale: nome + descrizione utente + stile
        parts = []

        # Aggiungi nome del personaggio/location
        if self.entity_type == "character":
            parts.append(f"A detailed portrait of {self.entity_name}")
        elif self.entity_type == "location":
            parts.append(f"A detailed view of {self.entity_name}")
        else:
            parts.append(self.entity_name)

        # Aggiungi descrizione inserita dall'utente
        parts.append(user_description)

        # Aggiungi modificatore stile
        style_value = self.style_combo.currentData()
        if style_value:
            style = ImagePromptBuilder.get_style_by_value(style_value)
            if style:
                style_mod = style.get_prompt_modifier()
                if style_mod:
                    parts.append(style_mod)

        prompt = ", ".join(parts)

        # Disable UI during generation
        self.generate_btn.setEnabled(False)
        self.prompt_edit.setEnabled(False)
        self.style_combo.setEnabled(False)
        self.model_combo.setEnabled(False)
        self.size_combo.setEnabled(False)
        self.quality_combo.setEnabled(False)

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate

        # Start worker thread
        model = self.model_combo.currentData()
        size = self.size_combo.currentData()
        quality = self.quality_combo.currentData()

        filename_prefix = self.entity_type + "_" + self.entity_name.replace(" ", "_")

        self.worker = ImageGenerationWorker(
            generator=self.generator,
            prompt=prompt,
            model=model,
            size=size,
            quality=quality,
            n=1,
            save_directory=self.save_directory,
            filename_prefix=filename_prefix
        )

        self.worker.finished.connect(self._on_generation_finished)
        self.worker.error.connect(self._on_generation_error)
        self.worker.start()

    def _on_generation_finished(self, results: List[ImageGenerationResult]):
        """Gestisci completamento generazione"""
        self.progress_bar.setVisible(False)
        self.results = results

        # Re-enable UI
        self.generate_btn.setEnabled(True)
        self.prompt_edit.setEnabled(True)
        self.style_combo.setEnabled(True)
        self.model_combo.setEnabled(True)
        self.size_combo.setEnabled(True)
        self.quality_combo.setEnabled(True)

        # Display results
        self._display_results()

    def _on_generation_error(self, error: str):
        """Gestisci errore generazione"""
        self.progress_bar.setVisible(False)

        # Re-enable UI
        self.generate_btn.setEnabled(True)
        self.prompt_edit.setEnabled(True)
        self.style_combo.setEnabled(True)
        self.model_combo.setEnabled(True)
        self.size_combo.setEnabled(True)
        self.quality_combo.setEnabled(True)

        QMessageBox.critical(self, "Errore Generazione", f"Errore durante la generazione:\n\n{error}")

    def _display_results(self):
        """Visualizza risultati generazione"""
        # Clear previous results
        while self.results_layout.count():
            item = self.results_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.results_label.setVisible(True)
        self.results_scroll.setVisible(True)

        # Display each result
        for i, result in enumerate(self.results):
            if not result.success:
                error_label = QLabel(f"❌ Errore: {result.error}")
                error_label.setStyleSheet("color: red;")
                self.results_layout.addWidget(error_label, i, 0)
                continue

            # Create frame for result
            frame = QFrame()
            frame.setFrameStyle(QFrame.Shape.StyledPanel)
            frame_layout = QVBoxLayout(frame)

            # Checkbox for selection
            checkbox = QCheckBox("Seleziona")
            checkbox.setChecked(True)
            checkbox.setProperty("image_path", result.image_path)
            frame_layout.addWidget(checkbox)

            # Image preview
            if result.image_path:
                pixmap = QPixmap(result.image_path)
                if not pixmap.isNull():
                    # Scale to fit
                    scaled = pixmap.scaled(400, 400, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation)
                    image_label = QLabel()
                    image_label.setPixmap(scaled)
                    image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    frame_layout.addWidget(image_label)

            # Info
            if result.revised_prompt:
                info_label = QLabel(f"Prompt rivisto:\n{result.revised_prompt[:100]}...")
                info_label.setWordWrap(True)
                info_label.setStyleSheet("color: #666; font-size: 11px;")
                frame_layout.addWidget(info_label)

            cost_label = QLabel(f"Costo: ${result.cost_estimate:.3f}")
            cost_label.setStyleSheet("font-weight: bold;")
            frame_layout.addWidget(cost_label)

            self.results_layout.addWidget(frame, i // 2, i % 2)

        # Enable save button
        self.save_btn.setEnabled(True)

    def _save_selected(self):
        """Salva immagini selezionate"""
        selected_paths = []

        # Find all checkboxes
        for i in range(self.results_layout.count()):
            item = self.results_layout.itemAt(i)
            if item and item.widget():
                frame = item.widget()
                # Find checkbox in frame
                for child in frame.findChildren(QCheckBox):
                    if child.isChecked():
                        path = child.property("image_path")
                        if path:
                            selected_paths.append(path)

        if not selected_paths:
            QMessageBox.warning(self, "Nessuna Selezione",
                              "Seleziona almeno un'immagine da salvare.")
            return

        # Emit paths and close
        self.images_generated.emit(selected_paths)
        self.accept()
