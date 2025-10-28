"""
Location Manager - Specialized manager for locations with image handling
"""
import os
import shutil
from typing import List, Optional
from pathlib import Path
from models.location import Location
from models.container_type import ContainerType
from managers.container_manager import ContainerManager
from utils.logger import logger


class LocationManager:
    """
    Specialized manager for handling locations with image support.

    This manager wraps the ContainerManager to provide location-specific
    functionality, particularly for managing location images.

    Attributes:
        container_manager: The underlying container manager
        images_dir: Directory where location images are stored
        container_type: Always LOCATIONS
    """

    def __init__(self, container_manager: ContainerManager, images_dir: str):
        """
        Initialize the location manager.

        Args:
            container_manager: The container manager instance
            images_dir: Directory for storing images
        """
        self.container_manager = container_manager
        self.images_dir = images_dir
        self.container_type = ContainerType.LOCATIONS

        # Ensure images directory exists
        os.makedirs(self.images_dir, exist_ok=True)

    def add_location(self, name: str, description: str = "", location_type: str = "") -> str:
        """
        Create a new location.

        Args:
            name: Location name
            description: Location description
            location_type: Type of location (e.g., "city", "room")

        Returns:
            str: ID of the created location
        """
        location = Location(
            name=name,
            description=description,
            location_type=location_type
        )

        location_id = self.container_manager.add_item(self.container_type, location)
        logger.info(f"Created location: {name} (ID: {location_id})")
        return location_id

    def add_location_object(self, location: Location) -> str:
        """
        Add a location object directly.

        Args:
            location: Location object to add

        Returns:
            str: ID of the created location
        """
        location_id = self.container_manager.add_item(self.container_type, location)
        logger.info(f"Created location: {location.name} (ID: {location_id})")
        return location_id

    def get_location(self, location_id: str) -> Optional[Location]:
        """
        Get a location by ID.

        Args:
            location_id: ID of the location

        Returns:
            Optional[Location]: The location if found, None otherwise
        """
        return self.container_manager.get_item(self.container_type, location_id)

    def get_all_locations(self) -> List[Location]:
        """
        Get all locations.

        Returns:
            List[Location]: List of all locations
        """
        return self.container_manager.get_all_items(self.container_type)

    def update_location(self, location: Location) -> bool:
        """
        Update an existing location.

        Args:
            location: Updated location object

        Returns:
            bool: True if update was successful
        """
        location.update_modified_date()
        return self.container_manager.update_item(
            self.container_type,
            location.id,
            location
        )

    def delete_location(self, location_id: str) -> bool:
        """
        Delete a location and all its associated images.

        Args:
            location_id: ID of the location to delete

        Returns:
            bool: True if deletion was successful
        """
        # Get the location first to access its images
        location = self.get_location(location_id)
        if not location:
            logger.warning(f"Location {location_id} not found for deletion")
            return False

        # Delete all associated images
        for image_filename in location.images:
            image_path = os.path.join(self.images_dir, image_filename)
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
                    logger.info(f"Deleted image: {image_filename}")
            except Exception as e:
                logger.error(f"Error deleting image {image_filename}: {e}")

        # Delete the location itself
        success = self.container_manager.delete_item(self.container_type, location_id)
        if success:
            logger.info(f"Deleted location: {location.name} (ID: {location_id})")
        return success

    def add_image_to_location(self, location_id: str, image_path: str) -> bool:
        """
        Add an image to a location.

        The image file will be copied to the project's images directory
        with a standardized filename.

        Args:
            location_id: ID of the location
            image_path: Path to the image file to add

        Returns:
            bool: True if image was added successfully
        """
        location = self.get_location(location_id)
        if not location:
            logger.error(f"Location {location_id} not found")
            return False

        # Verify source image exists
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return False

        # Generate filename: loc_<location_id>_<index>.<ext>
        file_extension = os.path.splitext(image_path)[1]
        image_index = len(location.images)
        filename = f"loc_{location_id}_{image_index}{file_extension}"
        dest_path = os.path.join(self.images_dir, filename)

        try:
            # Copy image to project directory
            shutil.copy2(image_path, dest_path)
            logger.info(f"Copied image to: {dest_path}")

            # Add filename to location
            location.add_image(filename)

            # Update location
            self.update_location(location)

            return True

        except Exception as e:
            logger.error(f"Error adding image to location: {e}")
            return False

    def remove_image_from_location(self, location_id: str, image_filename: str) -> bool:
        """
        Remove an image from a location.

        Args:
            location_id: ID of the location
            image_filename: Filename of the image to remove

        Returns:
            bool: True if image was removed successfully
        """
        location = self.get_location(location_id)
        if not location:
            logger.error(f"Location {location_id} not found")
            return False

        if image_filename not in location.images:
            logger.warning(f"Image {image_filename} not associated with location {location_id}")
            return False

        # Delete physical file
        image_path = os.path.join(self.images_dir, image_filename)
        try:
            if os.path.exists(image_path):
                os.remove(image_path)
                logger.info(f"Deleted image file: {image_path}")
        except Exception as e:
            logger.error(f"Error deleting image file: {e}")
            return False

        # Remove from location
        location.remove_image(image_filename)

        # Update location
        self.update_location(location)

        return True

    def get_image_path(self, image_filename: str) -> str:
        """
        Get the full path to an image file.

        Args:
            image_filename: Name of the image file

        Returns:
            str: Full path to the image
        """
        return os.path.join(self.images_dir, image_filename)

    def get_locations_by_type(self, location_type: str) -> List[Location]:
        """
        Get all locations of a specific type.

        Args:
            location_type: Type of location to filter by

        Returns:
            List[Location]: List of matching locations
        """
        all_locations = self.get_all_locations()
        return [loc for loc in all_locations if loc.location_type == location_type]

    def get_locations_by_character(self, character_id: str) -> List[Location]:
        """
        Get all locations associated with a specific character.

        Args:
            character_id: ID of the character

        Returns:
            List[Location]: List of locations where the character is present
        """
        all_locations = self.get_all_locations()
        return [loc for loc in all_locations if character_id in loc.characters_present]

    def search_locations(self, query: str) -> List[Location]:
        """
        Search locations by name or description.

        Args:
            query: Search query string

        Returns:
            List[Location]: List of matching locations
        """
        query = query.lower()
        all_locations = self.get_all_locations()
        return [
            loc for loc in all_locations
            if query in loc.name.lower() or query in loc.description.lower()
        ]

    def save(self) -> bool:
        """
        Save all locations to disk.

        Returns:
            bool: True if save was successful
        """
        return self.container_manager.save_container(self.container_type)
