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
from models.character import Character
from managers.character_manager import CharacterManager


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
        self._temp_dir: Optional[str] = None

    def create_new_project(self, title: str, author: str, filepath: str) -> bool:
        """
        Create a new project and save it as a ZIP file

        Args:
            title: Project title
            author: Author name
            filepath: Path where to save the .tnp file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure .tnp extension
            if not filepath.endswith('.tnp'):
                filepath += '.tnp'

            # Create project instance
            project = Project.create_new(title, author)

            # Create temporary directory for project structure
            temp_dir = tempfile.mkdtemp()

            # Create project structure
            manifest_path = os.path.join(temp_dir, 'manifest.json')
            manuscript_path = os.path.join(temp_dir, 'manuscript.txt')
            characters_path = os.path.join(temp_dir, 'characters.json')
            images_dir = os.path.join(temp_dir, 'images')

            # Create images directory
            os.makedirs(images_dir, exist_ok=True)

            # Write manifest.json
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(project.to_dict(), f, indent=2)

            # Write empty manuscript.txt
            with open(manuscript_path, 'w', encoding='utf-8') as f:
                f.write('')

            # Write empty characters.json
            with open(characters_path, 'w', encoding='utf-8') as f:
                json.dump({'characters': []}, f, indent=2)

            # Create ZIP file
            with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(manifest_path, 'manifest.json')
                zipf.write(manuscript_path, 'manuscript.txt')
                zipf.write(characters_path, 'characters.json')
                # Add empty images directory
                zipf.writestr('images/', '')

            # Clean up temp directory
            shutil.rmtree(temp_dir)

            # Set current project
            self.current_project = project
            self.current_filepath = filepath
            self.character_manager = CharacterManager()

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
            if not os.path.exists(filepath):
                print(f"Error: Project file not found: {filepath}")
                return None, None, None

            # Extract to temporary directory
            self._temp_dir = tempfile.mkdtemp()

            with zipfile.ZipFile(filepath, 'r') as zipf:
                zipf.extractall(self._temp_dir)

            # Read manifest.json
            manifest_path = os.path.join(self._temp_dir, 'manifest.json')
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)

            # Read manuscript.txt
            manuscript_path = os.path.join(self._temp_dir, 'manuscript.txt')
            with open(manuscript_path, 'r', encoding='utf-8') as f:
                manuscript_text = f.read()

            # Create Project instance
            project = Project.from_dict(manifest_data, manuscript_text)

            # Read characters.json
            characters_path = os.path.join(self._temp_dir, 'characters.json')
            with open(characters_path, 'r', encoding='utf-8') as f:
                characters_data = json.load(f)

            # Setup character manager
            images_dir = os.path.join(self._temp_dir, 'images')
            self.character_manager = CharacterManager(images_dir)
            self.character_manager.load_characters(characters_data.get('characters', []))

            # Set current project
            self.current_project = project
            self.current_filepath = filepath

            characters = self.character_manager.get_all_characters()
            return project, manuscript_text, characters

        except Exception as e:
            print(f"Error opening project: {e}")
            if self._temp_dir and os.path.exists(self._temp_dir):
                shutil.rmtree(self._temp_dir)
                self._temp_dir = None
            return None, None, None

    def save_project(self, manuscript_text: str = None) -> bool:
        """
        Save the current project to its file

        Args:
            manuscript_text: Updated manuscript text (optional)

        Returns:
            bool: True if successful, False otherwise
        """
        if not self.current_project or not self.current_filepath:
            print("Error: No project currently open")
            return False

        try:
            # Update manuscript text if provided
            if manuscript_text is not None:
                self.current_project.manuscript_text = manuscript_text

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
            manuscript_path = os.path.join(self._temp_dir, 'manuscript.txt')
            characters_path = os.path.join(self._temp_dir, 'characters.json')

            # Write manifest.json
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_project.to_dict(), f, indent=2)

            # Write manuscript.txt
            with open(manuscript_path, 'w', encoding='utf-8') as f:
                f.write(self.current_project.manuscript_text)

            # Write characters.json
            characters_data = {
                'characters': self.character_manager.get_characters_data()
            }
            with open(characters_path, 'w', encoding='utf-8') as f:
                json.dump(characters_data, f, indent=2)

            # Create new ZIP file
            temp_zip = self.current_filepath + '.tmp'
            with zipfile.ZipFile(temp_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add manifest, manuscript, and characters
                zipf.write(manifest_path, 'manifest.json')
                zipf.write(manuscript_path, 'manuscript.txt')
                zipf.write(characters_path, 'characters.json')

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

            return True

        except Exception as e:
            print(f"Error saving project: {e}")
            # Clean up temp zip if it exists
            temp_zip = self.current_filepath + '.tmp'
            if os.path.exists(temp_zip):
                os.remove(temp_zip)
            return False

    def save_project_as(self, filepath: str, manuscript_text: str = None) -> bool:
        """
        Save the current project to a new file

        Args:
            filepath: New path where to save the .tnp file
            manuscript_text: Updated manuscript text (optional)

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

        success = self.save_project(manuscript_text)

        if not success:
            self.current_filepath = old_filepath

        return success

    def close_project(self):
        """
        Close the current project and clean up temporary files
        """
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
