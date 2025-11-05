"""
TheNovelist - Writing Assistant
Main file (main.py)
"""
import os
import sys
import traceback
import warnings

# PyInstaller compatibility: Get base path
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    BASE_PATH = sys._MEIPASS
else:
    # Running in normal Python
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Enable detailed Qt warnings with traceback
os.environ['QT_LOGGING_RULES'] = ''  # Enable ALL warnings temporarily


# Capture warnings with traceback
def warning_handler(message, category, filename, lineno, file=None, line=None):
    print(f"\n{'=' * 60}")
    print(f"WARNING: {message}")
    print(f"File: {filename}:{lineno}")
    print(f"Category: {category.__name__}")
    print(f"{'=' * 60}")
    traceback.print_stack()
    print(f"{'=' * 60}\n")


warnings.showwarning = warning_handler

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Qt, QEvent

# Import custom modules
from ui.new_main_window import TheNovelistMainWindow


def verify_dependencies():
    """Verify that all necessary dependencies are installed"""
    try:
        import spacy

        # Try to load model - works in both dev and bundled environments
        try:
            # First try standard load (works in dev)
            spacy.load('it_core_news_sm')
        except OSError:
            # If that fails and we're in PyInstaller, try loading from bundle path
            if getattr(sys, 'frozen', False):
                model_path = os.path.join(BASE_PATH, 'it_core_news_sm', 'it_core_news_sm-3.8.0')
                if os.path.exists(model_path):
                    spacy.load(model_path)
                else:
                    raise OSError(f"Model not found in bundle at {model_path}")
            else:
                raise

        return True
    except OSError as e:
        QMessageBox.critical(
            None,
            "Missing Model",
            f"spaCy Italian model not found.\n\n"
            f"Error: {e}\n\n"
            "If running from source, install with:\n"
            "python -m spacy download it_core_news_sm"
        )
        return False
    except ImportError as e:
        QMessageBox.critical(
            None,
            "Missing Dependencies",
            f"Error: {e}\n\n"
            "Install dependencies:\n"
            "pip install -r requirements.txt"
        )
        return False


def apply_adaptive_stylesheet(app: QApplication):
    """Apply stylesheet that adapts to system theme (light/dark mode)"""
    # Get system palette
    palette = app.palette()

    # Force the application to use system colors
    # This ensures widgets respect the system theme
    app.setStyle("Fusion")  # Fusion style works best with dark mode

    # Create adaptive stylesheet using palette colors
    # These will automatically adapt when system theme changes
    stylesheet = """
    /* Use system palette colors - automatically adapts to light/dark mode */
    QWidget {
        background-color: palette(window);
        color: palette(window-text);
    }

    QTextEdit, QPlainTextEdit, QLineEdit {
        background-color: palette(base);
        color: palette(text);
        border: 1px solid palette(mid);
    }

    QPushButton {
        background-color: palette(button);
        color: palette(button-text);
        border: 1px solid palette(mid);
        padding: 5px 15px;
        border-radius: 3px;
    }

    QPushButton:hover {
        background-color: palette(light);
    }

    QPushButton:pressed {
        background-color: palette(mid);
    }

    QLabel {
        color: palette(window-text);
    }

    QComboBox {
        background-color: palette(base);
        color: palette(text);
        border: 1px solid palette(mid);
    }

    QTreeView, QListView {
        background-color: palette(base);
        color: palette(text);
        alternate-background-color: palette(alternate-base);
    }

    QScrollBar:vertical {
        background: palette(window);
        width: 12px;
    }

    QScrollBar::handle:vertical {
        background: palette(mid);
        border-radius: 6px;
    }

    QScrollBar::handle:vertical:hover {
        background: palette(dark);
    }

    QScrollBar:horizontal {
        background: palette(window);
        height: 12px;
    }

    QScrollBar::handle:horizontal {
        background: palette(mid);
        border-radius: 6px;
    }

    QScrollBar::handle:horizontal:hover {
        background: palette(dark);
    }

    QMenuBar {
        background-color: palette(window);
        color: palette(window-text);
    }

    QMenuBar::item:selected {
        background-color: palette(highlight);
        color: palette(highlighted-text);
    }

    QMenu {
        background-color: palette(window);
        color: palette(window-text);
    }

    QMenu::item:selected {
        background-color: palette(highlight);
        color: palette(highlighted-text);
    }

    QTabWidget::pane {
        border: 1px solid palette(mid);
        background-color: palette(window);
    }

    QTabBar::tab {
        background-color: palette(button);
        color: palette(button-text);
        border: 1px solid palette(mid);
        padding: 5px 10px;
    }

    QTabBar::tab:selected {
        background-color: palette(highlight);
        color: palette(highlighted-text);
    }

    QStatusBar {
        background-color: palette(window);
        color: palette(window-text);
    }
    """

    app.setStyleSheet(stylesheet)


def main():
    """Application entry point"""
    app = QApplication(sys.argv)

    # Apply adaptive stylesheet that respects system theme
    apply_adaptive_stylesheet(app)

    # Verify dependencies before starting
    if not verify_dependencies():
        sys.exit(1)

    # Create and show main window
    window = TheNovelistMainWindow()
    window.show()

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()