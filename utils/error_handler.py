"""
Error Handler - Centralized exception handling
"""
from enum import Enum
from typing import Optional, Tuple
import traceback
from utils.logger import AppLogger


class ErrorType(Enum):
    """Types of errors that can occur"""
    FILE_ERROR = "file"
    NETWORK_ERROR = "network"
    VALIDATION_ERROR = "validation"
    SYSTEM_ERROR = "system"
    CORRUPTION_ERROR = "corruption"
    PERMISSION_ERROR = "permission"
    UNKNOWN_ERROR = "unknown"


class ErrorSeverity(Enum):
    """Severity levels for errors"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorHandler:
    """
    Centralized error handling system

    Classifies errors, logs them, and provides user-friendly messages
    """

    @staticmethod
    def classify_error(exception: Exception) -> ErrorType:
        """
        Classify an exception into an error type

        Args:
            exception: The exception to classify

        Returns:
            ErrorType: Classified error type
        """
        exception_type = type(exception).__name__

        # File-related errors
        if isinstance(exception, (FileNotFoundError, IsADirectoryError, NotADirectoryError)):
            return ErrorType.FILE_ERROR

        if isinstance(exception, IOError):
            return ErrorType.FILE_ERROR

        # Permission errors
        if isinstance(exception, PermissionError):
            return ErrorType.PERMISSION_ERROR

        # Network errors
        if 'timeout' in exception_type.lower() or 'connection' in exception_type.lower():
            return ErrorType.NETWORK_ERROR

        # Validation errors
        if isinstance(exception, (ValueError, TypeError)):
            return ErrorType.VALIDATION_ERROR

        # Corruption errors
        if 'corrupt' in str(exception).lower() or 'zip' in exception_type.lower():
            return ErrorType.CORRUPTION_ERROR

        # System errors
        if isinstance(exception, (OSError, MemoryError, SystemError)):
            return ErrorType.SYSTEM_ERROR

        # Unknown
        return ErrorType.UNKNOWN_ERROR

    @staticmethod
    def get_severity(error_type: ErrorType) -> ErrorSeverity:
        """
        Get severity level for error type

        Args:
            error_type: Type of error

        Returns:
            ErrorSeverity: Severity level
        """
        severity_map = {
            ErrorType.VALIDATION_ERROR: ErrorSeverity.WARNING,
            ErrorType.FILE_ERROR: ErrorSeverity.ERROR,
            ErrorType.PERMISSION_ERROR: ErrorSeverity.ERROR,
            ErrorType.NETWORK_ERROR: ErrorSeverity.WARNING,
            ErrorType.CORRUPTION_ERROR: ErrorSeverity.CRITICAL,
            ErrorType.SYSTEM_ERROR: ErrorSeverity.CRITICAL,
            ErrorType.UNKNOWN_ERROR: ErrorSeverity.ERROR,
        }
        return severity_map.get(error_type, ErrorSeverity.ERROR)

    @staticmethod
    def get_user_friendly_message(error_type: ErrorType, exception: Exception) -> str:
        """
        Get user-friendly error message

        Args:
            error_type: Type of error
            exception: The exception

        Returns:
            str: User-friendly message
        """
        messages = {
            ErrorType.FILE_ERROR: (
                "Unable to access the file.\n\n"
                "The file may not exist, may have been moved, or may be in use by another application."
            ),
            ErrorType.PERMISSION_ERROR: (
                "Permission denied.\n\n"
                "You don't have permission to access this file or directory. "
                "Please check file permissions or try a different location."
            ),
            ErrorType.NETWORK_ERROR: (
                "Network connection failed.\n\n"
                "Please check your internet connection and try again. "
                "Some features require an active internet connection."
            ),
            ErrorType.VALIDATION_ERROR: (
                "Invalid input.\n\n"
                "The provided data is not valid. Please check your input and try again."
            ),
            ErrorType.CORRUPTION_ERROR: (
                "File is corrupted or damaged.\n\n"
                "The project file may be corrupted. You can try restoring from a backup."
            ),
            ErrorType.SYSTEM_ERROR: (
                "System error occurred.\n\n"
                "A critical system error has occurred. Please save your work and restart the application."
            ),
            ErrorType.UNKNOWN_ERROR: (
                "An unexpected error occurred.\n\n"
                "Please try again. If the problem persists, check the error log for details."
            ),
        }

        base_message = messages.get(error_type, messages[ErrorType.UNKNOWN_ERROR])

        # Add specific exception message if helpful
        exception_msg = str(exception)
        if exception_msg and len(exception_msg) < 200:
            base_message += f"\n\nDetails: {exception_msg}"

        return base_message

    @staticmethod
    def get_suggestions(error_type: ErrorType) -> list:
        """
        Get suggestions for resolving the error

        Args:
            error_type: Type of error

        Returns:
            list: List of suggestion strings
        """
        suggestions = {
            ErrorType.FILE_ERROR: [
                "Check if the file exists",
                "Make sure the file is not open in another program",
                "Try a different file location",
                "Restore from backup if available"
            ],
            ErrorType.PERMISSION_ERROR: [
                "Check file and folder permissions",
                "Try running the application as administrator",
                "Save to a different location",
                "Close other applications that might be using the file"
            ],
            ErrorType.NETWORK_ERROR: [
                "Check your internet connection",
                "Disable VPN if active",
                "Try again in a few moments",
                "Check firewall settings"
            ],
            ErrorType.VALIDATION_ERROR: [
                "Check for invalid characters",
                "Verify all required fields are filled",
                "Check length limits",
                "Use only allowed characters"
            ],
            ErrorType.CORRUPTION_ERROR: [
                "Restore from backup",
                "Try opening a recent version",
                "Contact support with the error log",
                "Create a new project and copy content manually"
            ],
            ErrorType.SYSTEM_ERROR: [
                "Save your work immediately",
                "Restart the application",
                "Check available disk space",
                "Check available memory"
            ],
            ErrorType.UNKNOWN_ERROR: [
                "Try the operation again",
                "Restart the application",
                "Check the error log for details",
                "Report the issue if it persists"
            ],
        }
        return suggestions.get(error_type, suggestions[ErrorType.UNKNOWN_ERROR])

    @staticmethod
    def is_recoverable(error_type: ErrorType) -> bool:
        """
        Check if error type is potentially recoverable

        Args:
            error_type: Type of error

        Returns:
            bool: True if recoverable
        """
        recoverable_types = {
            ErrorType.FILE_ERROR: True,
            ErrorType.PERMISSION_ERROR: True,
            ErrorType.NETWORK_ERROR: True,
            ErrorType.VALIDATION_ERROR: True,
            ErrorType.CORRUPTION_ERROR: False,
            ErrorType.SYSTEM_ERROR: False,
            ErrorType.UNKNOWN_ERROR: False,
        }
        return recoverable_types.get(error_type, False)

    @staticmethod
    def handle_exception(
        exception: Exception,
        context: str,
        show_dialog: bool = True,
        parent=None
    ) -> Tuple[bool, Optional[str]]:
        """
        Handle an exception with logging and optional user dialog

        Args:
            exception: The exception to handle
            context: Context where error occurred (e.g., "save_project")
            show_dialog: Whether to show error dialog to user
            parent: Parent widget for dialog

        Returns:
            Tuple[bool, Optional[str]]: (retry, backup_path)
                retry: True if user wants to retry operation
                backup_path: Path to backup if available
        """
        # Classify error
        error_type = ErrorHandler.classify_error(exception)
        severity = ErrorHandler.get_severity(error_type)

        # Log the error
        log_message = f"Error in {context}: {type(exception).__name__}: {str(exception)}"

        if severity == ErrorSeverity.CRITICAL:
            AppLogger.critical(log_message, exc_info=True)
        elif severity == ErrorSeverity.ERROR:
            AppLogger.error(log_message, exc_info=True)
        elif severity == ErrorSeverity.WARNING:
            AppLogger.warning(log_message)
        else:
            AppLogger.info(log_message)

        # Get technical details
        technical_details = traceback.format_exc()

        # Show dialog if requested
        retry = False
        backup_path = None

        if show_dialog and parent:
            try:
                from ui.components.error_dialog import ErrorDialog

                user_message = ErrorHandler.get_user_friendly_message(error_type, exception)
                suggestions = ErrorHandler.get_suggestions(error_type)
                recoverable = ErrorHandler.is_recoverable(error_type)

                dialog = ErrorDialog(
                    error_type=error_type,
                    severity=severity,
                    message=user_message,
                    technical_details=technical_details,
                    suggestions=suggestions,
                    recoverable=recoverable,
                    context=context,
                    parent=parent
                )

                result = dialog.exec()
                retry = result == ErrorDialog.DialogCode.Retry
                backup_path = dialog.selected_backup

            except Exception as dialog_error:
                # Fallback if error dialog fails
                AppLogger.error(f"Failed to show error dialog: {dialog_error}", exc_info=True)
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.critical(
                    parent,
                    "Error",
                    f"An error occurred: {str(exception)}"
                )

        return retry, backup_path

    @staticmethod
    def log_operation(operation: str, success: bool, details: str = ""):
        """
        Log an operation result

        Args:
            operation: Operation name
            success: Whether operation succeeded
            details: Additional details
        """
        if success:
            AppLogger.info(f"Operation '{operation}' completed successfully. {details}")
        else:
            AppLogger.warning(f"Operation '{operation}' failed. {details}")
