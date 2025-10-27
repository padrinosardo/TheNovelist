"""
Backup Manager - Automatic backup system for projects
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from utils.logger import AppLogger


class BackupManager:
    """
    Manages automatic backups of project files

    Features:
    - Creates backups before risky operations
    - Maintains max N backups per project
    - Provides restore functionality
    - Automatic cleanup of old backups
    """

    def __init__(self, max_backups: int = 5):
        """
        Initialize backup manager

        Args:
            max_backups: Maximum number of backups to keep per project
        """
        self.backup_dir = Path.home() / '.thenovelist' / 'backups'
        self.max_backups = max_backups
        self._ensure_backup_directory()

    def _ensure_backup_directory(self):
        """Ensure backup directory exists"""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            AppLogger.debug(f"Backup directory: {self.backup_dir}")
        except Exception as e:
            AppLogger.error(f"Failed to create backup directory: {e}")

    def create_backup(
        self,
        project_path: str,
        operation: str = "manual"
    ) -> Optional[str]:
        """
        Create a backup of a project file

        Args:
            project_path: Path to the .tnp project file
            operation: Description of operation (save, delete, manual, etc.)

        Returns:
            Optional[str]: Path to created backup file, or None if failed
        """
        try:
            # Validate source file
            if not os.path.exists(project_path):
                AppLogger.warning(f"Cannot backup non-existent file: {project_path}")
                return None

            if not os.path.isfile(project_path):
                AppLogger.warning(f"Cannot backup directory: {project_path}")
                return None

            # Get project name (without extension)
            project_filename = os.path.basename(project_path)
            project_name = project_filename.rsplit('.', 1)[0]

            # Create backup filename
            # Format: projectname_YYYYMMDD_HHMMSS_operation.tnp.bak
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{project_name}_{timestamp}_{operation}.tnp.bak"
            backup_path = self.backup_dir / backup_filename

            # Copy file
            shutil.copy2(project_path, backup_path)

            AppLogger.info(f"Created backup: {backup_filename} (operation: {operation})")

            # Cleanup old backups
            self.cleanup_old_backups(project_name)

            return str(backup_path)

        except Exception as e:
            AppLogger.error(f"Failed to create backup: {e}", exc_info=True)
            return None

    def restore_backup(self, backup_path: str, restore_path: str) -> bool:
        """
        Restore a project from backup

        Args:
            backup_path: Path to backup file
            restore_path: Path where to restore the project

        Returns:
            bool: True if successful
        """
        try:
            # Validate backup file
            if not os.path.exists(backup_path):
                AppLogger.error(f"Backup file not found: {backup_path}")
                return False

            if not backup_path.endswith('.tnp.bak'):
                AppLogger.warning(f"Invalid backup file extension: {backup_path}")

            # Before restoring, backup the current file (if exists)
            if os.path.exists(restore_path):
                current_backup = self.create_backup(restore_path, "before_restore")
                if current_backup:
                    AppLogger.info(f"Backed up current file before restore: {current_backup}")

            # Copy backup to restore location
            shutil.copy2(backup_path, restore_path)

            AppLogger.info(f"Restored from backup: {backup_path} -> {restore_path}")
            return True

        except Exception as e:
            AppLogger.error(f"Failed to restore backup: {e}", exc_info=True)
            return False

    def list_backups(self, project_name: str) -> List[Dict[str, any]]:
        """
        List all backups for a project

        Args:
            project_name: Name of the project (without extension)

        Returns:
            List[Dict]: List of backup info dictionaries, sorted by date (newest first)
        """
        backups = []

        try:
            if not self.backup_dir.exists():
                return backups

            # Find all backup files for this project
            pattern = f"{project_name}_*.tnp.bak"

            for backup_file in self.backup_dir.glob(pattern):
                try:
                    # Parse filename to extract info
                    # Format: projectname_YYYYMMDD_HHMMSS_operation.tnp.bak
                    filename = backup_file.name
                    parts = filename.rsplit('_', 1)

                    if len(parts) < 2:
                        continue

                    operation_part = parts[1].replace('.tnp.bak', '')

                    # Get file stats
                    stat = backup_file.stat()
                    size_mb = stat.st_size / (1024 * 1024)
                    modified_time = datetime.fromtimestamp(stat.st_mtime)

                    backup_info = {
                        'path': str(backup_file),
                        'filename': filename,
                        'operation': operation_part,
                        'size_mb': round(size_mb, 2),
                        'date': modified_time,
                        'date_str': modified_time.strftime('%Y-%m-%d %H:%M:%S')
                    }

                    backups.append(backup_info)

                except Exception as e:
                    AppLogger.warning(f"Error reading backup file {backup_file}: {e}")
                    continue

            # Sort by date (newest first)
            backups.sort(key=lambda x: x['date'], reverse=True)

        except Exception as e:
            AppLogger.error(f"Failed to list backups: {e}")

        return backups

    def cleanup_old_backups(self, project_name: str):
        """
        Remove old backups beyond the maximum limit

        Args:
            project_name: Name of the project
        """
        try:
            backups = self.list_backups(project_name)

            # If we have more than max_backups, delete the oldest ones
            if len(backups) > self.max_backups:
                backups_to_delete = backups[self.max_backups:]

                for backup in backups_to_delete:
                    try:
                        os.remove(backup['path'])
                        AppLogger.info(f"Deleted old backup: {backup['filename']}")
                    except Exception as e:
                        AppLogger.warning(f"Failed to delete backup {backup['filename']}: {e}")

        except Exception as e:
            AppLogger.error(f"Failed to cleanup old backups: {e}")

    def get_backup_info(self, backup_path: str) -> Optional[Dict[str, any]]:
        """
        Get information about a specific backup file

        Args:
            backup_path: Path to backup file

        Returns:
            Optional[Dict]: Backup info dictionary or None
        """
        try:
            backup_file = Path(backup_path)

            if not backup_file.exists():
                return None

            stat = backup_file.stat()
            size_mb = stat.st_size / (1024 * 1024)
            modified_time = datetime.fromtimestamp(stat.st_mtime)

            return {
                'path': str(backup_file),
                'filename': backup_file.name,
                'size_mb': round(size_mb, 2),
                'date': modified_time,
                'date_str': modified_time.strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            AppLogger.error(f"Failed to get backup info: {e}")
            return None

    def delete_backup(self, backup_path: str) -> bool:
        """
        Delete a specific backup file

        Args:
            backup_path: Path to backup file to delete

        Returns:
            bool: True if successful
        """
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
                AppLogger.info(f"Deleted backup: {backup_path}")
                return True
            else:
                AppLogger.warning(f"Backup file not found: {backup_path}")
                return False

        except Exception as e:
            AppLogger.error(f"Failed to delete backup: {e}")
            return False

    def get_total_backup_size(self) -> float:
        """
        Get total size of all backups in MB

        Returns:
            float: Total size in MB
        """
        total_size = 0

        try:
            if self.backup_dir.exists():
                for backup_file in self.backup_dir.glob('*.tnp.bak'):
                    try:
                        total_size += backup_file.stat().st_size
                    except:
                        continue

        except Exception as e:
            AppLogger.error(f"Failed to calculate backup size: {e}")

        return round(total_size / (1024 * 1024), 2)

    def cleanup_all_backups(self) -> int:
        """
        Delete all backup files

        Returns:
            int: Number of backups deleted
        """
        deleted_count = 0

        try:
            if self.backup_dir.exists():
                for backup_file in self.backup_dir.glob('*.tnp.bak'):
                    try:
                        os.remove(backup_file)
                        deleted_count += 1
                    except Exception as e:
                        AppLogger.warning(f"Failed to delete {backup_file}: {e}")

            AppLogger.info(f"Deleted {deleted_count} backup files")

        except Exception as e:
            AppLogger.error(f"Failed to cleanup all backups: {e}")

        return deleted_count
