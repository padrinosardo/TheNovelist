"""
Project management system - handles ZIP-based project files
"""
import json
import os
import shutil
import tempfile
import zipfile
from typing import Optional, Tuple, List
from models.project import Project
from models.project_type import ProjectType
from models.character import Character
from models.manuscript_structure import ManuscriptStructure, Chapter, Scene
from models.container_type import ContainerType
from managers.character_manager import CharacterManager
from managers.statistics_manager import StatisticsManager
from managers.manuscript_structure_manager import ManuscriptStructureManager
from managers.container_manager import ContainerManager
from managers.location_manager import LocationManager
from managers.research_manager import ResearchManager
from managers.timeline_manager import TimelineManager
from managers.source_manager import SourceManager
from managers.note_manager import NoteManager
from managers.worldbuilding_manager import WorldbuildingManager
from utils.logger import AppLogger
from utils.error_handler import ErrorHandler
from utils.backup_manager import BackupManager


class ProjectManager:
    """
    Manages project files in ZIP format (.tnp files)

    Project structure inside ZIP:
        manifest.json - Project metadata
        manuscript.txt - Main text content
        characters.json - Character data
        images/ - Character images directory
    """

    def __init__(self):
        """Initialize the project manager"""
        self.current_project: Optional[Project] = None
        self.current_filepath: Optional[str] = None
        self.character_manager = CharacterManager()
        self.statistics_manager = StatisticsManager()
        self.manuscript_structure_manager = ManuscriptStructureManager()
        self._temp_dir: Optional[str] = None

        # New container managers (Milestone 2)
        self.container_manager: Optional[ContainerManager] = None
        self.location_manager: Optional[LocationManager] = None
        self.research_manager: Optional[ResearchManager] = None
        self.timeline_manager: Optional[TimelineManager] = None
        self.worldbuilding_manager: Optional[WorldbuildingManager] = None
        self.source_manager: Optional[SourceManager] = None
        self.note_manager: Optional[NoteManager] = None

    def create_new_project(self, title: str, author: str, filepath: str, language: str = 'it',
                          project_type: ProjectType = ProjectType.NOVEL, genre: str = "",
                          target_word_count: int = 0, tags: List[str] = None) -> bool:
        """
        Create a new project and save it as a ZIP file

        Args:
            title: Project title
            author: Author name
            filepath: Path where to save the .tnp file
            language: Project language code ('it', 'en', 'es', 'fr', 'de')
            project_type: Type of project (Novel, Article, etc.)
            genre: Genre/category (optional)
            target_word_count: Target word count (optional)
            tags: List of tags (optional)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure .tnp extension
            if not filepath.endswith('.tnp'):
                filepath += '.tnp'

            # Create project instance with language and type
            project = Project.create_new(
                title=title,
                author=author,
                language=language,
                project_type=project_type,
                genre=genre,
                target_word_count=target_word_count,
                tags=tags if tags is not None else []
            )

            # Create temporary directory for project structure
            temp_dir = tempfile.mkdtemp()

            # Create project structure
            manifest_path = os.path.join(temp_dir, 'manifest.json')
            manuscript_structure_path = os.path.join(temp_dir, 'manuscript_structure.json')
            characters_path = os.path.join(temp_dir, 'characters.json')
            images_dir = os.path.join(temp_dir, 'images')

            # Create images directory
            os.makedirs(images_dir, exist_ok=True)

            # Write manifest.json
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(project.to_dict(), f, indent=2)

            # Create default manuscript structure (Chapter 1 > Scene 1)
            default_structure = ManuscriptStructure.create_default()
            with open(manuscript_structure_path, 'w', encoding='utf-8') as f:
                json.dump(default_structure.to_dict(), f, indent=2)

            # Write empty characters.json
            with open(characters_path, 'w', encoding='utf-8') as f:
                json.dump({'characters': []}, f, indent=2)

            # Create empty container files for available containers
            available_containers = ContainerType.get_available_for_project_type(project_type)
            container_files = []

            for container_type in available_containers:
                if container_type in [ContainerType.MANUSCRIPT, ContainerType.CHARACTERS]:
                    continue  # These are handled separately

                filename = ContainerType.get_filename(container_type)
                container_path = os.path.join(temp_dir, filename)

                # Write empty array for each container
                with open(container_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, indent=2)

                container_files.append((container_path, filename))
                AppLogger.debug(f"Created empty container: {filename}")

            # Create ZIP file
            with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(manifest_path, 'manifest.json')
                zipf.write(manuscript_structure_path, 'manuscript_structure.json')
                zipf.write(characters_path, 'characters.json')

                # Add all container files
                for container_path, filename in container_files:
                    zipf.write(container_path, filename)

                # Add empty images directory
                zipf.writestr('images/', '')

            # Clean up temp directory
            shutil.rmtree(temp_dir)

            # Open the newly created project to initialize all managers
            project_data, manuscript_text, characters = self.open_project(filepath)

            if project_data is None:
                AppLogger.error(f"Failed to open newly created project: {filepath}")
                return False

            AppLogger.info(f"New project created: {project.title} (type: {project_type.value}, language: {project.language})")
            return True

        except Exception as e:
            print(f"Error creating project: {e}")
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            return False

    def open_project(self, filepath: str) -> Tuple[Optional[Project], Optional[str], Optional[List[Character]]]:
        """
        Open an existing project from a .tnp file

        Args:
            filepath: Path to the .tnp file

        Returns:
            Tuple: (Project, manuscript_text, characters) or (None, None, None) on error
        """
        try:
            AppLogger.info(f"Opening project: {filepath}")

            # Check if file exists
            if not os.path.exists(filepath):
                AppLogger.error(f"Project file not found: {filepath}")
                raise FileNotFoundError(f"Project file not found: {filepath}")

            # Validate file size (max 100MB)
            file_size = os.path.getsize(filepath)
            if file_size > 100 * 1024 * 1024:
                AppLogger.error(f"Project file too large: {file_size / (1024 * 1024):.2f}MB")
                raise ValueError("Project file is too large (max 100MB)")

            # Test ZIP integrity before extracting
            try:
                with zipfile.ZipFile(filepath, 'r') as zipf:
                    # Test all files in archive for corruption
                    corrupt_file = zipf.testzip()
                    if corrupt_file:
                        AppLogger.error(f"Corrupted file in archive: {corrupt_file}")
                        raise zipfile.BadZipFile(f"Archive contains corrupted file: {corrupt_file}")

                    # Check required files exist (manuscript files are optional for migration)
                    required_files = ['manifest.json', 'characters.json']
                    file_list = zipf.namelist()

                    for required in required_files:
                        if required not in file_list:
                            AppLogger.error(f"Missing required file: {required}")
                            raise ValueError(f"Project file is missing required file: {required}")

                    AppLogger.debug("ZIP integrity check passed")

            except zipfile.BadZipFile as e:
                AppLogger.error(f"Bad ZIP file: {e}")
                raise zipfile.BadZipFile("Project file is corrupted or not a valid archive")

            # Extract to temporary directory
            self._temp_dir = tempfile.mkdtemp()

            with zipfile.ZipFile(filepath, 'r') as zipf:
                zipf.extractall(self._temp_dir)

            # Read and validate manifest.json
            manifest_path = os.path.join(self._temp_dir, 'manifest.json')
            try:
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    manifest_data = json.load(f)

                # Validate required fields in manifest
                required_fields = ['title', 'author', 'created_date']
                for field in required_fields:
                    if field not in manifest_data:
                        AppLogger.error(f"Manifest missing required field: {field}")
                        raise ValueError(f"Project manifest is invalid (missing {field})")

                AppLogger.debug("Manifest validation passed")

                # Migrate old project format if needed
                manifest_data, migrations_applied = self._migrate_old_project(manifest_data)
                if migrations_applied:
                    # Save migrated manifest back to temp directory
                    with open(manifest_path, 'w', encoding='utf-8') as f:
                        json.dump(manifest_data, f, indent=2)
                    AppLogger.info(f"Applied {len(migrations_applied)} migrations to project")

            except json.JSONDecodeError as e:
                AppLogger.error(f"Invalid JSON in manifest.json: {e}")
                raise ValueError(f"Project manifest is corrupted (invalid JSON)")

            # Load or migrate manuscript structure
            manuscript_structure_path = os.path.join(self._temp_dir, 'manuscript_structure.json')
            manuscript_structure = None

            if os.path.exists(manuscript_structure_path):
                # New format: load manuscript_structure.json
                AppLogger.debug("Loading manuscript structure from JSON")
                try:
                    with open(manuscript_structure_path, 'r', encoding='utf-8') as f:
                        structure_data = json.load(f)
                    manuscript_structure = ManuscriptStructure.from_dict(structure_data)
                    AppLogger.info("Manuscript structure loaded successfully")
                except json.JSONDecodeError as e:
                    AppLogger.error(f"Invalid JSON in manuscript_structure.json: {e}")
                    raise ValueError(f"Manuscript structure is corrupted (invalid JSON)")
            else:
                # Old format: migrate from manuscript.txt
                AppLogger.info("Old project format detected - migrating to new structure")
                manuscript_path = os.path.join(self._temp_dir, 'manuscript.txt')
                manuscript_text = ""

                if os.path.exists(manuscript_path):
                    with open(manuscript_path, 'r', encoding='utf-8') as f:
                        manuscript_text = f.read()

                # Create structure with migrated content
                manuscript_structure = self._migrate_old_manuscript(manuscript_text)
                AppLogger.info("Migration completed successfully")

            # Get full manuscript text for Project model (for backward compatibility)
            manuscript_text = manuscript_structure.get_full_text()

            # Create Project instance
            project = Project.from_dict(manifest_data, manuscript_text)

            # Read and validate characters.json
            characters_path = os.path.join(self._temp_dir, 'characters.json')
            try:
                with open(characters_path, 'r', encoding='utf-8') as f:
                    characters_data = json.load(f)

                # Validate structure
                if not isinstance(characters_data, dict) or 'characters' not in characters_data:
                    AppLogger.error("Invalid characters.json structure")
                    raise ValueError("Character data is corrupted (invalid structure)")

                AppLogger.debug("Characters validation passed")

            except json.JSONDecodeError as e:
                AppLogger.error(f"Invalid JSON in characters.json: {e}")
                raise ValueError(f"Character data is corrupted (invalid JSON)")

            # Setup character manager
            images_dir = os.path.join(self._temp_dir, 'images')
            self.character_manager = CharacterManager(images_dir)
            self.character_manager.load_characters(characters_data.get('characters', []))

            # Load statistics
            self.statistics_manager.load_statistics(self._temp_dir)

            # Setup manuscript structure manager
            self.manuscript_structure_manager = ManuscriptStructureManager(manuscript_structure)

            # Migrate containers for old projects (Milestone 2 - Step 4.3)
            container_migrations = self._migrate_containers(project.project_type)
            if container_migrations:
                AppLogger.info(f"Container migrations applied: {', '.join(container_migrations)}")

            # Initialize container managers (Milestone 2)
            self.container_manager = ContainerManager(self._temp_dir)
            self.location_manager = LocationManager(self.container_manager, images_dir)
            self.research_manager = ResearchManager(self.container_manager)
            self.timeline_manager = TimelineManager(self.container_manager)
            self.worldbuilding_manager = WorldbuildingManager(self.container_manager)
            self.source_manager = SourceManager(self.container_manager)
            self.note_manager = NoteManager(self.container_manager)

            # Load available containers based on project type
            available_containers = ContainerType.get_available_for_project_type(project.project_type)
            for container_type in available_containers:
                if container_type in [ContainerType.MANUSCRIPT, ContainerType.CHARACTERS]:
                    continue  # Already loaded

                try:
                    items = self.container_manager.load_container(container_type)
                    AppLogger.debug(f"Loaded {len(items)} items from {container_type.value}")
                except Exception as e:
                    AppLogger.warning(f"Could not load container {container_type.value}: {e}")

            # Set current project
            self.current_project = project
            self.current_filepath = filepath

            # Set NLP language for opened project
            self._set_nlp_language(project.language)

            AppLogger.info(f"Project opened successfully: {project.title} (type: {project.project_type.value}, language: {project.language})")
            characters = self.character_manager.get_all_characters()
            return project, manuscript_text, characters

        except FileNotFoundError as e:
            AppLogger.error(f"File not found: {e}")
            # Clean up
            if self._temp_dir and os.path.exists(self._temp_dir):
                shutil.rmtree(self._temp_dir)
                self._temp_dir = None
            return None, None, None

        except (zipfile.BadZipFile, ValueError) as e:
            # File corruption detected - offer recovery
            AppLogger.error(f"File corruption detected: {e}")

            # Clean up temp directory
            if self._temp_dir and os.path.exists(self._temp_dir):
                shutil.rmtree(self._temp_dir)
                self._temp_dir = None

            # Check if backups exist
            try:
                project_filename = os.path.basename(filepath)
                project_name = project_filename.rsplit('.', 1)[0]
                backups = BackupManager().list_backups(project_name)

                if backups:
                    AppLogger.info(f"Found {len(backups)} backup(s) for corrupted project")
                    # User will be prompted to restore from backup in the UI layer
                else:
                    AppLogger.warning("No backups available for corrupted project")

            except Exception as backup_error:
                AppLogger.error(f"Error checking backups: {backup_error}")

            return None, None, None

        except PermissionError as e:
            AppLogger.error(f"Permission denied: {e}")
            # Clean up
            if self._temp_dir and os.path.exists(self._temp_dir):
                shutil.rmtree(self._temp_dir)
                self._temp_dir = None
            return None, None, None

        except Exception as e:
            AppLogger.critical(f"Unexpected error opening project: {e}", exc_info=True)
            # Clean up
            if self._temp_dir and os.path.exists(self._temp_dir):
                shutil.rmtree(self._temp_dir)
                self._temp_dir = None
            return None, None, None

    def _migrate_old_manuscript(self, manuscript_text: str) -> ManuscriptStructure:
        """
        Migrate old manuscript format (single text file) to new structure

        Args:
            manuscript_text: The old manuscript text

        Returns:
            ManuscriptStructure: Migrated structure with Chapter 1 > Scene 1
        """
        structure = ManuscriptStructure()

        # Create Chapter 1
        chapter = Chapter.create_new("Chapter 1", order=0)

        # Create Scene 1 with all the old content
        scene = Scene.create_new("Scene 1", order=0, content=manuscript_text)
        chapter.add_scene(scene)

        structure.add_chapter(chapter)
        structure.current_scene_id = scene.id

        AppLogger.info(f"Migrated manuscript: {scene.word_count} words in Chapter 1 > Scene 1")
        return structure

    def _migrate_old_project(self, manifest_data: dict) -> Tuple[dict, List[str]]:
        """
        Migrate old project format to support new features (language, project_type, etc.)

        Args:
            manifest_data: The manifest dictionary

        Returns:
            Tuple: (updated manifest_data, list of migrations applied)
        """
        migrations_applied = []

        # Migration 1: Add language field if missing
        if 'language' not in manifest_data:
            manifest_data['language'] = 'it'  # Default to Italian
            migrations_applied.append("Added default language: Italian (it)")
            AppLogger.info("Migration applied: Added language field with default 'it'")

        # Migration 2: Add project_type field if missing (Milestone 2)
        if 'project_type' not in manifest_data:
            manifest_data['project_type'] = 'novel'  # Default to Novel
            migrations_applied.append("Added default project type: Novel")
            AppLogger.info("Migration applied: Added project_type field with default 'novel'")

        # Migration 3: Add optional metadata fields if missing (Milestone 2)
        if 'genre' not in manifest_data:
            manifest_data['genre'] = ''
            migrations_applied.append("Added genre field (empty)")

        if 'target_word_count' not in manifest_data:
            manifest_data['target_word_count'] = 0
            migrations_applied.append("Added target_word_count field (0)")

        if 'tags' not in manifest_data:
            manifest_data['tags'] = []
            migrations_applied.append("Added tags field (empty list)")

        # Migration 4: Add containers_version field if missing (Milestone 2 - Step 4.3)
        # This tracks which version of the container system is present
        if 'containers_version' not in manifest_data:
            manifest_data['containers_version'] = '1.0'
            migrations_applied.append("Added containers_version field (1.0)")
            AppLogger.info("Migration applied: Added containers_version field with version '1.0'")

        return manifest_data, migrations_applied

    def _migrate_containers(self, project_type: ProjectType) -> List[str]:
        """
        Migrate old projects to include container files (Milestone 2 - Step 4.3)

        Creates empty container JSON files for projects that don't have them yet.
        This enables old projects to use the new container system (locations,
        research notes, timeline, etc.) without requiring manual conversion.

        Args:
            project_type: The project type to determine which containers are needed

        Returns:
            List[str]: List of migration messages describing what was created
        """
        migrations_applied = []

        # Get containers that should exist for this project type
        available_containers = ContainerType.get_available_for_project_type(project_type)

        for container_type in available_containers:
            # Skip containers that are handled separately
            if container_type in [ContainerType.MANUSCRIPT, ContainerType.CHARACTERS]:
                continue

            # Get the expected file path
            filename = ContainerType.get_filename(container_type)
            container_path = os.path.join(self._temp_dir, filename)

            # If file doesn't exist, create it with an empty array
            if not os.path.exists(container_path):
                try:
                    with open(container_path, 'w', encoding='utf-8') as f:
                        json.dump([], f, indent=2)

                    icon, name = ContainerType.get_display_info(container_type, 'en')
                    migrations_applied.append(f"Created empty container: {name} ({filename})")
                    AppLogger.info(f"Container migration: Created {filename}")

                except Exception as e:
                    AppLogger.error(f"Failed to create container file {filename}: {e}")

        if migrations_applied:
            AppLogger.info(f"Container migration completed: {len(migrations_applied)} containers created")

        return migrations_applied

    def _set_nlp_language(self, language: str):
        """
        Set the NLP language in the nlp_manager

        Args:
            language: Language code to set
        """
        try:
            from analysis.nlp_manager import nlp_manager
            nlp_manager.set_language(language)
            AppLogger.info(f"NLP language set to: {language}")
        except Exception as e:
            AppLogger.warning(f"Failed to set NLP language: {e}")
            # Non-fatal error, continue anyway

    def save_project(self) -> bool:
        """
        Save the current project to its file (with error handling and backup)

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.current_project or not self.current_filepath:
            AppLogger.warning("Attempted to save project but no project is open")
            return False

        try:
            AppLogger.info(f"Saving project: {self.current_project.title}")

            # Create backup before saving
            if os.path.exists(self.current_filepath):
                backup_path = BackupManager().create_backup(
                    self.current_filepath,
                    "auto_save"
                )
                if backup_path:
                    AppLogger.debug(f"Created backup: {backup_path}")

            # Update manuscript text in Project model for backward compatibility
            self.current_project.manuscript_text = self.manuscript_structure_manager.get_full_manuscript_text()

            # Update modified date
            self.current_project.update_modified_date()

            # If we don't have a temp dir, we need to create one
            if not self._temp_dir or not os.path.exists(self._temp_dir):
                self._temp_dir = tempfile.mkdtemp()
                images_dir = os.path.join(self._temp_dir, 'images')
                os.makedirs(images_dir, exist_ok=True)
                self.character_manager.set_images_directory(images_dir)

            # Update files in temp directory
            manifest_path = os.path.join(self._temp_dir, 'manifest.json')
            manuscript_structure_path = os.path.join(self._temp_dir, 'manuscript_structure.json')
            characters_path = os.path.join(self._temp_dir, 'characters.json')

            # Write manifest.json
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_project.to_dict(), f, indent=2)

            # Write manuscript_structure.json
            with open(manuscript_structure_path, 'w', encoding='utf-8') as f:
                json.dump(self.manuscript_structure_manager.to_dict(), f, indent=2)

            # Write characters.json
            characters_data = {
                'characters': self.character_manager.get_characters_data()
            }
            with open(characters_path, 'w', encoding='utf-8') as f:
                json.dump(characters_data, f, indent=2)

            # Write statistics.json
            self.statistics_manager.save_statistics(self._temp_dir)

            # Save all container managers (Milestone 2)
            if self.container_manager:
                self.container_manager.save_all()
                AppLogger.debug("Saved all container managers")

            # Create new ZIP file
            temp_zip = self.current_filepath + '.tmp'
            with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add manifest, manuscript structure, characters, and statistics
                zipf.write(manifest_path, 'manifest.json')
                zipf.write(manuscript_structure_path, 'manuscript_structure.json')
                zipf.write(characters_path, 'characters.json')

                # Add statistics if exists
                statistics_path = os.path.join(self._temp_dir, 'statistics.json')
                if os.path.exists(statistics_path):
                    zipf.write(statistics_path, 'statistics.json')

                # Add all container JSON files (Milestone 2)
                available_containers = ContainerType.get_available_for_project_type(self.current_project.project_type)
                for container_type in available_containers:
                    if container_type in [ContainerType.MANUSCRIPT, ContainerType.CHARACTERS]:
                        continue  # Already handled

                    filename = ContainerType.get_filename(container_type)
                    container_path = os.path.join(self._temp_dir, filename)

                    if os.path.exists(container_path):
                        zipf.write(container_path, filename)
                        AppLogger.debug(f"Added container to ZIP: {filename}")

                # Add images directory and its contents
                images_dir = os.path.join(self._temp_dir, 'images')
                if os.path.exists(images_dir):
                    for filename in os.listdir(images_dir):
                        file_path = os.path.join(images_dir, filename)
                        if os.path.isfile(file_path):
                            zipf.write(file_path, f'images/{filename}')
                else:
                    # Add empty images directory
                    zipf.writestr('images/', '')

            # Replace old file with new one
            if os.path.exists(self.current_filepath):
                os.remove(self.current_filepath)
            os.rename(temp_zip, self.current_filepath)

            AppLogger.info(f"Project saved successfully: {self.current_filepath}")
            return True

        except PermissionError as e:
            AppLogger.error(f"Permission denied while saving project: {e}")
            # Clean up temp zip if it exists
            temp_zip = self.current_filepath + '.tmp'
            if os.path.exists(temp_zip):
                try:
                    os.remove(temp_zip)
                except:
                    pass
            return False

        except IOError as e:
            AppLogger.error(f"IO error while saving project: {e}")
            # Clean up temp zip if it exists
            temp_zip = self.current_filepath + '.tmp'
            if os.path.exists(temp_zip):
                try:
                    os.remove(temp_zip)
                except:
                    pass
            return False

        except Exception as e:
            AppLogger.critical(f"Unexpected error saving project: {e}", exc_info=True)
            # Clean up temp zip if it exists
            temp_zip = self.current_filepath + '.tmp'
            if os.path.exists(temp_zip):
                try:
                    os.remove(temp_zip)
                except:
                    pass
            return False

    def save_project_as(self, filepath: str) -> bool:
        """
        Save the current project to a new file

        Args:
            filepath: New path where to save the .tnp file

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.current_project:
            print("Error: No project currently open")
            return False

        # Ensure .tnp extension
        if not filepath.endswith('.tnp'):
            filepath += '.tnp'

        old_filepath = self.current_filepath
        self.current_filepath = filepath

        success = self.save_project()

        if not success:
            self.current_filepath = old_filepath

        return success

    def close_project(self):
        """
        Close the current project and clean up temporary files
        """
        # End any active writing session
        if self.statistics_manager.is_session_active():
            self.statistics_manager.reset_session()

        # Clean up temporary directory
        if self._temp_dir and os.path.exists(self._temp_dir):
            try:
                shutil.rmtree(self._temp_dir)
            except Exception as e:
                print(f"Error cleaning up temp directory: {e}")

        self._temp_dir = None
        self.current_project = None
        self.current_filepath = None
        self.character_manager = CharacterManager()
        self.manuscript_structure_manager = ManuscriptStructureManager()

        # Reset container managers (Milestone 2)
        self.container_manager = None
        self.location_manager = None
        self.research_manager = None
        self.timeline_manager = None
        self.source_manager = None
        self.note_manager = None

    def get_project_title(self) -> str:
        """
        Get current project title

        Returns:
            str: Project title or 'Untitled'
        """
        if self.current_project:
            return self.current_project.title
        return "Untitled"

    def has_project(self) -> bool:
        """
        Check if a project is currently open

        Returns:
            bool: True if project is open
        """
        return self.current_project is not None

    def get_temp_images_directory(self) -> Optional[str]:
        """
        Get the temporary images directory path

        Returns:
            str or None: Path to images directory if available
        """
        if self._temp_dir:
            return os.path.join(self._temp_dir, 'images')
        return None
