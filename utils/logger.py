"""
Application Logger - Centralized logging system
"""
import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime


class AppLogger:
    """
    Centralized logging system for The Novelist application

    Features:
    - Rotating file handler (max 5 files, 5MB each)
    - Console output for debugging
    - Formatted messages with timestamp, level, module, function
    - Stack traces for errors
    """

    _logger = None
    _initialized = False

    @classmethod
    def initialize(cls):
        """Initialize the logging system"""
        if cls._initialized:
            return

        # Create logs directory
        log_dir = Path.home() / '.thenovelist' / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)

        # Log file path
        log_file = log_dir / 'app.log'

        # Create logger
        cls._logger = logging.getLogger('TheNovelist')
        cls._logger.setLevel(logging.DEBUG)

        # Remove existing handlers
        cls._logger.handlers.clear()

        # Create rotating file handler
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        # Create console handler for warnings and above
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        # Create formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(module)s:%(funcName)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        cls._logger.addHandler(file_handler)
        cls._logger.addHandler(console_handler)

        cls._initialized = True
        cls._logger.info("=" * 80)
        cls._logger.info("The Novelist - Application Started")
        cls._logger.info(f"Log file: {log_file}")
        cls._logger.info("=" * 80)

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """
        Get the application logger instance

        Returns:
            logging.Logger: Configured logger
        """
        if not cls._initialized:
            cls.initialize()
        return cls._logger

    @classmethod
    def debug(cls, message: str, exc_info=False):
        """
        Log debug message

        Args:
            message: Message to log
            exc_info: Include exception info
        """
        logger = cls.get_logger()
        logger.debug(message, exc_info=exc_info)

    @classmethod
    def info(cls, message: str):
        """
        Log info message

        Args:
            message: Message to log
        """
        logger = cls.get_logger()
        logger.info(message)

    @classmethod
    def warning(cls, message: str):
        """
        Log warning message

        Args:
            message: Message to log
        """
        logger = cls.get_logger()
        logger.warning(message)

    @classmethod
    def error(cls, message: str, exc_info=True):
        """
        Log error message with stack trace

        Args:
            message: Message to log
            exc_info: Include exception info (default True)
        """
        logger = cls.get_logger()
        logger.error(message, exc_info=exc_info)

    @classmethod
    def critical(cls, message: str, exc_info=True):
        """
        Log critical error message with stack trace

        Args:
            message: Message to log
            exc_info: Include exception info (default True)
        """
        logger = cls.get_logger()
        logger.critical(message, exc_info=exc_info)

    @classmethod
    def get_log_file_path(cls) -> Path:
        """
        Get the path to the log file

        Returns:
            Path: Path to current log file
        """
        return Path.home() / '.thenovelist' / 'logs' / 'app.log'

    @classmethod
    def get_logs_directory(cls) -> Path:
        """
        Get the logs directory path

        Returns:
            Path: Path to logs directory
        """
        return Path.home() / '.thenovelist' / 'logs'


# Initialize logger on module import
AppLogger.initialize()

# Create module-level logger instance for convenience
logger = AppLogger.get_logger()
