"""
Character management system
"""
import os
import shutil
from typing import List, Optional
from models.character import Character


class CharacterManager:
    """
    Manages CRUD operations for characters in a project
    """

    def __init__(self, images_dir: str = None):
        """
        Initialize the character manager

        Args:
            images_dir: Directory where character images are stored
        """
        self.characters: List[Character] = []
        self.images_dir = images_dir

    def set_images_directory(self, images_dir: str):
        """
        Set the images directory path

        Args:
            images_dir: Path to images directory
        """
        self.images_dir = images_dir
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)

    def load_characters(self, characters_data: List[dict]):
        """
        Load characters from dictionary data

        Args:
            characters_data: List of character dictionaries
        """
        self.characters = [Character.from_dict(data) for data in characters_data]

    def get_characters_data(self) -> List[dict]:
        """
        Get all characters as dictionary data for serialization

        Returns:
            List[dict]: List of character dictionaries
        """
        return [char.to_dict() for char in self.characters]

    def add_character(self, name: str, description: str = "") -> Character:
        """
        Add a new character

        Args:
            name: Character name
            description: Character description

        Returns:
            Character: The newly created character
        """
        character = Character(
            name=name,
            description=description,
            images=[]
        )
        self.characters.append(character)
        return character

    def get_character(self, character_id: str) -> Optional[Character]:
        """
        Get a character by ID

        Args:
            character_id: The character's unique ID

        Returns:
            Character or None: The character if found, None otherwise
        """
        for char in self.characters:
            if char.id == character_id:
                return char
        return None

    def get_all_characters(self) -> List[Character]:
        """
        Get all characters

        Returns:
            List[Character]: List of all characters
        """
        return self.characters.copy()

    def update_character(self, character_id: str, name: str = None,
                        description: str = None) -> Optional[Character]:
        """
        Update a character's information

        Args:
            character_id: The character's unique ID
            name: New name (optional)
            description: New description (optional)

        Returns:
            Character or None: Updated character if found, None otherwise
        """
        character = self.get_character(character_id)
        if not character:
            return None

        if name is not None:
            character.name = name
        if description is not None:
            character.description = description

        return character

    def delete_character(self, character_id: str) -> bool:
        """
        Delete a character and its associated images

        Args:
            character_id: The character's unique ID

        Returns:
            bool: True if deleted, False if not found
        """
        character = self.get_character(character_id)
        if not character:
            return False

        # Delete associated images
        if self.images_dir:
            for image_filename in character.images:
                image_path = os.path.join(self.images_dir, image_filename)
                if os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                    except Exception as e:
                        print(f"Error deleting image {image_path}: {e}")

        # Remove from list
        self.characters = [c for c in self.characters if c.id != character_id]
        return True

    def add_image_to_character(self, character_id: str,
                              image_source_path: str) -> Optional[str]:
        """
        Add an image to a character

        Args:
            character_id: The character's unique ID
            image_source_path: Path to the source image file

        Returns:
            str or None: The saved image filename if successful, None otherwise
        """
        character = self.get_character(character_id)
        if not character:
            return None

        if not self.images_dir:
            print("Error: images directory not set")
            return None

        if not os.path.exists(image_source_path):
            print(f"Error: source image not found: {image_source_path}")
            return None

        # Generate unique filename
        file_ext = os.path.splitext(image_source_path)[1]
        image_index = len(character.images)
        image_filename = f"char_{character.id}_{image_index}{file_ext}"
        image_dest_path = os.path.join(self.images_dir, image_filename)

        try:
            # Copy image to project directory
            shutil.copy2(image_source_path, image_dest_path)

            # Add to character's image list
            character.images.append(image_filename)

            return image_filename
        except Exception as e:
            print(f"Error copying image: {e}")
            return None

    def remove_image_from_character(self, character_id: str,
                                   image_filename: str) -> bool:
        """
        Remove an image from a character

        Args:
            character_id: The character's unique ID
            image_filename: The filename to remove

        Returns:
            bool: True if removed, False otherwise
        """
        character = self.get_character(character_id)
        if not character:
            return False

        if image_filename not in character.images:
            return False

        # Remove from character's list
        character.images.remove(image_filename)

        # Delete physical file
        if self.images_dir:
            image_path = os.path.join(self.images_dir, image_filename)
            if os.path.exists(image_path):
                try:
                    os.remove(image_path)
                except Exception as e:
                    print(f"Error deleting image file: {e}")

        return True

    def get_character_image_paths(self, character_id: str) -> List[str]:
        """
        Get full paths to all images for a character

        Args:
            character_id: The character's unique ID

        Returns:
            List[str]: List of full image paths
        """
        character = self.get_character(character_id)
        if not character or not self.images_dir:
            return []

        paths = []
        for image_filename in character.images:
            image_path = os.path.join(self.images_dir, image_filename)
            if os.path.exists(image_path):
                paths.append(image_path)

        return paths
