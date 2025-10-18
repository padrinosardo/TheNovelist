"""
TheNovelist - Writing Assistant
Main file (main.py)
"""
import os
import sys
import traceback
import warnings

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

# Import custom modules
from ui.main_window import WritingAssistant


def verify_dependencies():
    """Verify that all necessary dependencies are installed"""
    try:
        import spacy
        spacy.load('it_core_news_sm')
        return True
    except OSError:
        QMessageBox.critical(
            None,
            "Missing Model",
            "You must install the Italian spaCy model:\n\n"
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


def main():
    """Application entry point"""
    app = QApplication(sys.argv)

    # Verify dependencies before starting
    if not verify_dependencies():
        sys.exit(1)

    # Create and show main window
    window = WritingAssistant()
    window.show()

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()