"""
File manager for saving and loading documents
"""
import os
from datetime import datetime


class FileManager:
    """Class to handle document saving and loading"""

    # Supported file formats
    FORMATS = {
        'Text Files': '*.txt',
        'Markdown Files': '*.md',
        'All Files': '*.*'
    }

    def __init__(self):
        """Initialize file manager"""
        self.current_file = None
        self.last_directory = os.path.expanduser("~/Documents")

    def save_document(self, text, filepath):
        """
        Save document to file

        Args:
            text: Text content to save
            filepath: Full path where to save

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            # Save file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)

            # Update state
            self.current_file = filepath
            self.last_directory = directory if directory else self.last_directory

            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False

    def load_document(self, filepath):
        """
        Load document from file

        Args:
            filepath: Full path of file to load

        Returns:
            str or None: File content if successful, None otherwise
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()

            # Update state
            self.current_file = filepath
            self.last_directory = os.path.dirname(filepath)

            return text
        except Exception as e:
            print(f"Error loading file: {e}")
            return None

    def get_file_filter(self):
        """
        Get file filter string for dialogs

        Returns:
            str: Filter string for QFileDialog
        """
        filters = []
        for name, pattern in self.FORMATS.items():
            filters.append(f"{name} ({pattern})")
        return ";;".join(filters)

    def get_filename(self):
        """
        Get current filename without path

        Returns:
            str: Filename or 'Untitled'
        """
        if self.current_file:
            return os.path.basename(self.current_file)
        return "Untitled"

    def has_file(self):
        """
        Check if a file is currently open

        Returns:
            bool: True if file is open
        """
        return self.current_file is not None

    def clear_file(self):
        """Clear current file state"""
        self.current_file = None