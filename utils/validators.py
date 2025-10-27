"""
Input Validators - Validation utilities for user input
"""
import os
import re
from pathlib import Path
from typing import Tuple


class Validators:
    """
    Collection of validation functions for user input

    Returns format: (is_valid: bool, error_message: str)
    """

    # Invalid filename characters (Windows + Unix)
    INVALID_FILENAME_CHARS = r'[<>:"/\\|?*\x00-\x1f]'

    # Max filename length (most filesystems)
    MAX_FILENAME_LENGTH = 255

    # Max path length
    MAX_PATH_LENGTH = 4096

    @staticmethod
    def validate_filename(filename: str) -> Tuple[bool, str]:
        """
        Validate a filename

        Args:
            filename: Filename to validate

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not filename:
            return False, "Filename cannot be empty"

        if not filename.strip():
            return False, "Filename cannot be only whitespace"

        # Check for invalid characters
        if re.search(Validators.INVALID_FILENAME_CHARS, filename):
            return False, "Filename contains invalid characters (< > : \" / \\ | ? *)"

        # Check length
        if len(filename) > Validators.MAX_FILENAME_LENGTH:
            return False, f"Filename too long (max {Validators.MAX_FILENAME_LENGTH} characters)"

        # Check for reserved names (Windows)
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL',
            'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
        ]
        name_without_ext = filename.rsplit('.', 1)[0].upper()
        if name_without_ext in reserved_names:
            return False, f"'{filename}' is a reserved system name"

        # Check for trailing dots or spaces (Windows)
        if filename.endswith(('.', ' ')):
            return False, "Filename cannot end with a dot or space"

        return True, ""

    @staticmethod
    def validate_filepath(path: str, check_writable: bool = True) -> Tuple[bool, str]:
        """
        Validate a file path

        Args:
            path: File path to validate
            check_writable: Check if directory is writable

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not path:
            return False, "File path cannot be empty"

        if len(path) > Validators.MAX_PATH_LENGTH:
            return False, f"File path too long (max {Validators.MAX_PATH_LENGTH} characters)"

        # Get directory part
        directory = os.path.dirname(path)

        # If no directory specified, use current directory
        if not directory:
            directory = os.getcwd()

        # Check if directory exists
        if not os.path.exists(directory):
            return False, f"Directory does not exist: {directory}"

        # Check if it's actually a directory
        if not os.path.isdir(directory):
            return False, f"Not a directory: {directory}"

        # Check if writable (optional)
        if check_writable:
            if not os.access(directory, os.W_OK):
                return False, f"No write permission for directory: {directory}"

            # Check available disk space (at least 10MB)
            try:
                stat = os.statvfs(directory)
                available_space = stat.f_bavail * stat.f_frsize
                min_space = 10 * 1024 * 1024  # 10MB

                if available_space < min_space:
                    return False, f"Insufficient disk space (less than 10MB available)"
            except:
                # statvfs not available on all platforms (e.g., Windows)
                pass

        return True, ""

    @staticmethod
    def validate_text_input(
        text: str,
        min_length: int = 0,
        max_length: int = None,
        allow_empty: bool = False,
        field_name: str = "Input"
    ) -> Tuple[bool, str]:
        """
        Validate text input

        Args:
            text: Text to validate
            min_length: Minimum length (default 0)
            max_length: Maximum length (None for no limit)
            allow_empty: Allow empty strings
            field_name: Name of field for error messages

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if text is None:
            return False, f"{field_name} cannot be None"

        text_stripped = text.strip()

        # Check empty
        if not allow_empty and not text_stripped:
            return False, f"{field_name} cannot be empty"

        # Check minimum length
        if len(text_stripped) < min_length:
            return False, f"{field_name} must be at least {min_length} characters"

        # Check maximum length
        if max_length and len(text_stripped) > max_length:
            return False, f"{field_name} cannot exceed {max_length} characters"

        return True, ""

    @staticmethod
    def validate_project_name(name: str) -> Tuple[bool, str]:
        """
        Validate project name

        Args:
            name: Project name to validate

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # Use text validation
        is_valid, error = Validators.validate_text_input(
            name,
            min_length=1,
            max_length=100,
            allow_empty=False,
            field_name="Project name"
        )

        if not is_valid:
            return is_valid, error

        # Check for special characters that might cause issues
        if re.search(r'[<>:"/\\|?*]', name):
            return False, "Project name contains invalid characters (< > : \" / \\ | ? *)"

        return True, ""

    @staticmethod
    def validate_character_name(name: str) -> Tuple[bool, str]:
        """
        Validate character name

        Args:
            name: Character name to validate

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # Use text validation
        is_valid, error = Validators.validate_text_input(
            name,
            min_length=1,
            max_length=100,
            allow_empty=False,
            field_name="Character name"
        )

        if not is_valid:
            return is_valid, error

        # Character names can have more freedom, but check for obviously bad input
        if name.strip() != name:
            return False, "Character name cannot start or end with whitespace"

        return True, ""

    @staticmethod
    def validate_integer(
        value: any,
        min_value: int = None,
        max_value: int = None,
        field_name: str = "Value"
    ) -> Tuple[bool, str]:
        """
        Validate integer value

        Args:
            value: Value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            field_name: Name of field for error messages

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        try:
            int_value = int(value)
        except (ValueError, TypeError):
            return False, f"{field_name} must be a valid integer"

        if min_value is not None and int_value < min_value:
            return False, f"{field_name} must be at least {min_value}"

        if max_value is not None and int_value > max_value:
            return False, f"{field_name} cannot exceed {max_value}"

        return True, ""

    @staticmethod
    def validate_file_exists(filepath: str) -> Tuple[bool, str]:
        """
        Validate that a file exists

        Args:
            filepath: Path to file

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        if not filepath:
            return False, "File path cannot be empty"

        if not os.path.exists(filepath):
            return False, f"File does not exist: {filepath}"

        if not os.path.isfile(filepath):
            return False, f"Path is not a file: {filepath}"

        if not os.access(filepath, os.R_OK):
            return False, f"No read permission for file: {filepath}"

        return True, ""

    @staticmethod
    def validate_image_file(filepath: str) -> Tuple[bool, str]:
        """
        Validate that a file is a supported image

        Args:
            filepath: Path to image file

        Returns:
            Tuple[bool, str]: (is_valid, error_message)
        """
        # First check file exists
        is_valid, error = Validators.validate_file_exists(filepath)
        if not is_valid:
            return is_valid, error

        # Check extension
        valid_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
        ext = os.path.splitext(filepath)[1].lower()

        if ext not in valid_extensions:
            return False, f"Unsupported image format. Supported: {', '.join(valid_extensions)}"

        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        file_size = os.path.getsize(filepath)

        if file_size > max_size:
            size_mb = file_size / (1024 * 1024)
            return False, f"Image too large ({size_mb:.1f}MB). Maximum size is 10MB"

        return True, ""

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize a filename by removing/replacing invalid characters

        Args:
            filename: Filename to sanitize

        Returns:
            str: Sanitized filename
        """
        # Remove invalid characters
        sanitized = re.sub(Validators.INVALID_FILENAME_CHARS, '_', filename)

        # Remove leading/trailing whitespace and dots
        sanitized = sanitized.strip('. ')

        # Ensure not empty
        if not sanitized:
            sanitized = "unnamed"

        # Truncate if too long
        if len(sanitized) > Validators.MAX_FILENAME_LENGTH:
            name, ext = os.path.splitext(sanitized)
            max_name_length = Validators.MAX_FILENAME_LENGTH - len(ext)
            sanitized = name[:max_name_length] + ext

        return sanitized
