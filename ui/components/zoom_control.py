"""
Zoom Control Widget - Graphical zoom slider for editor
"""
from PySide6.QtWidgets import QWidget, QHBoxLayout, QSlider, QLabel
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class ZoomControl(QWidget):
    """
    Zoom control widget with slider and percentage display

    Features:
    - Visual slider from 50% to 200%
    - Icons for zoom in/out
    - Percentage label
    - Double-click to reset to 100%
    """

    # Signal emitted when zoom level changes
    zoom_changed = Signal(int)  # Emits percentage (50-200)

    def __init__(self, parent=None):
        """
        Initialize zoom control

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        """Setup the UI components"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(3)

        # Zoom out icon/label
        self.zoom_out_label = QLabel("🔍➖")
        self.zoom_out_label.setToolTip("Zoom Out")
        layout.addWidget(self.zoom_out_label)

        # Slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setMinimum(50)   # 50%
        self.slider.setMaximum(200)  # 200%
        self.slider.setValue(100)    # Default 100%
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.setTickInterval(25)  # Ticks at 50, 75, 100, 125, 150, 175, 200
        self.slider.setFixedWidth(150)
        self.slider.setToolTip("Drag to adjust zoom level\nDouble-click to reset to 100%")

        # Connect slider signals - FORCE CONNECTION
        import sys
        print(f"[DEBUG] ZoomControl.__init__: Connecting valueChanged signal", file=sys.stderr, flush=True)
        try:
            self.slider.valueChanged.connect(self._on_slider_changed)
            print(f"[DEBUG] ZoomControl.__init__: valueChanged signal connected successfully", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"[ERROR] Failed to connect valueChanged: {e}", file=sys.stderr, flush=True)

        try:
            self.slider.sliderReleased.connect(self._on_slider_released)
            print(f"[DEBUG] ZoomControl.__init__: sliderReleased signal connected successfully", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"[ERROR] Failed to connect sliderReleased: {e}", file=sys.stderr, flush=True)

        # Enable double-click detection
        self.slider.mouseDoubleClickEvent = self._on_slider_double_click

        layout.addWidget(self.slider)

        # Zoom in icon/label
        self.zoom_in_label = QLabel("🔍➕")
        self.zoom_in_label.setToolTip("Zoom In")
        layout.addWidget(self.zoom_in_label)

        # Percentage label
        self.percentage_label = QLabel("100%")
        self.percentage_label.setMinimumWidth(40)
        self.percentage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(10)
        self.percentage_label.setFont(font)
        self.percentage_label.setToolTip("Current zoom level")
        layout.addWidget(self.percentage_label)

        # Style the slider
        self.slider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999;
                height: 6px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #B0B0B0, stop:0.5 #2196F3, stop:1 #B0B0B0);
                margin: 2px 0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #2196F3;
                border: 2px solid #1976D2;
                width: 14px;
                height: 14px;
                margin: -5px 0;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: #1976D2;
                border: 2px solid #0D47A1;
            }
            QSlider::sub-page:horizontal {
                background: #2196F3;
                border-radius: 3px;
            }
            QSlider::add-page:horizontal {
                background: #d0d0d0;
                border-radius: 3px;
            }
        """)

    def _on_slider_changed(self, value: int):
        """
        Handle slider value change (updates label and applies zoom immediately)

        Args:
            value: Slider value (50-200)
        """
        import sys
        print(f"[DEBUG] ZoomControl._on_slider_changed: value={value}", file=sys.stderr, flush=True)
        self.percentage_label.setText(f"{value}% CHANGED")  # Aggiungo CHANGED per vedere se viene chiamato
        self.slider.setToolTip(f"Zoom: {value}% - Signal emitted")
        # Emit zoom change immediately for responsive feedback
        print(f"[DEBUG] ZoomControl: emitting zoom_changed signal with value={value}", file=sys.stderr, flush=True)
        self.zoom_changed.emit(value)

    def _on_slider_released(self):
        """Handle slider release (emit signal to apply zoom)"""
        value = self.slider.value()
        print(f"[DEBUG] ZoomControl: slider released, emitting zoom_changed signal with value={value}")
        self.zoom_changed.emit(value)

    def _on_slider_double_click(self, event):
        """
        Handle double-click on slider (reset to 100%)

        Args:
            event: Mouse event
        """
        self.set_zoom_level(100)
        self.zoom_changed.emit(100)

    def set_zoom_level(self, percentage: int):
        """
        Set zoom level programmatically

        Args:
            percentage: Zoom percentage (50-200)
        """
        # Clamp to valid range
        clamped = max(50, min(200, percentage))

        # Block signals to avoid recursive updates
        self.slider.blockSignals(True)
        self.slider.setValue(clamped)
        self.slider.blockSignals(False)

        # Update label
        self.percentage_label.setText(f"{clamped}%")

    def get_zoom_level(self) -> int:
        """
        Get current zoom level

        Returns:
            int: Current zoom percentage
        """
        return self.slider.value()
