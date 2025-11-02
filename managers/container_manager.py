"""
Container Manager - Generic manager for all container types
"""
import json
import os
from typing import List, Any, Type, Dict, Optional
from pathlib import Path
from models.container_type import ContainerType
from models.location import Location
from models.research_note import ResearchNote
from models.timeline_event import TimelineEvent
from models.source import Source
from models.note import Note
from models.character import Character
from models.worldbuilding_entry import WorldbuildingEntry
from utils.logger import logger
from datetime import datetime


class ContainerManager:
    """
    Generic manager for handling all types of content containers.

    This manager provides a unified interface for loading, saving, and
    managing items across different container types. Each container type
    maps to a specific data model class.

    Attributes:
        project_dir: Directory where project files are stored
        _containers: Dictionary mapping container types to their items
        _loaded: Set of container types that have been loaded
    """

    # Mapping of container types to their model classes
    MODEL_CLASSES = {
        ContainerType.CHARACTERS: Character,
        ContainerType.LOCATIONS: Location,
        ContainerType.RESEARCH: ResearchNote,
        ContainerType.TIMELINE: TimelineEvent,
        ContainerType.WORLDBUILDING: WorldbuildingEntry,
        ContainerType.SOURCES: Source,
        ContainerType.NOTES: Note
    }

    def __init__(self, project_dir: str):
        """
        Initialize the container manager.

        Args:
            project_dir: Directory where project files are stored
        """
        self.project_dir = project_dir
        self._containers: Dict[ContainerType, List[Any]] = {}
        self._loaded: set = set()

    def load_container(self, container_type: ContainerType) -> List[Any]:
        """
        Load items from a specific container.

        Args:
            container_type: Type of container to load

        Returns:
            List[Any]: List of items in the container
        """
        # Check if already loaded
        if container_type in self._loaded:
            return self._containers.get(container_type, [])

        file_path = self._get_container_file_path(container_type)

        # If file doesn't exist, return empty list
        if not os.path.exists(file_path):
            logger.info(f"Container {container_type.value} not found, initializing empty")
            self._containers[container_type] = []
            self._loaded.add(container_type)
            return []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Get the model class for this container type
            model_class = self.MODEL_CLASSES.get(container_type)
            if not model_class:
                logger.error(f"No model class found for container type {container_type.value}")
                self._containers[container_type] = []
                self._loaded.add(container_type)
                return []

            # Deserialize each item
            items = [model_class.from_dict(item_data) for item_data in data]
            self._containers[container_type] = items
            self._loaded.add(container_type)

            logger.info(f"Loaded {len(items)} items from {container_type.value}")
            return items

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error loading {container_type.value}: {e}")
            self._containers[container_type] = []
            self._loaded.add(container_type)
            return []
        except Exception as e:
            logger.error(f"Error loading container {container_type.value}: {e}")
            self._containers[container_type] = []
            self._loaded.add(container_type)
            return []

    def save_container(self, container_type: ContainerType) -> bool:
        """
        Save items from a specific container to disk.

        Args:
            container_type: Type of container to save

        Returns:
            bool: True if save was successful, False otherwise
        """
        if container_type not in self._containers:
            logger.warning(f"Container {container_type.value} not loaded, nothing to save")
            return False

        file_path = self._get_container_file_path(container_type)

        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Serialize all items
            items_data = [item.to_dict() for item in self._containers[container_type]]

            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(items_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Saved {len(items_data)} items to {container_type.value}")
            return True

        except Exception as e:
            logger.error(f"Error saving container {container_type.value}: {e}")
            return False

    def add_item(self, container_type: ContainerType, item: Any) -> str:
        """
        Add an item to a container.

        Args:
            container_type: Type of container
            item: Item to add

        Returns:
            str: ID of the added item
        """
        # Ensure container is loaded
        if container_type not in self._loaded:
            self.load_container(container_type)

        if container_type not in self._containers:
            self._containers[container_type] = []

        # Update timestamps
        if hasattr(item, 'created_date') and not item.created_date:
            item.created_date = datetime.now().isoformat()
        if hasattr(item, 'modified_date'):
            item.modified_date = datetime.now().isoformat()

        # Add item
        self._containers[container_type].append(item)
        logger.info(f"Added item {item.id} to {container_type.value}")

        return item.id

    def get_item(self, container_type: ContainerType, item_id: str) -> Optional[Any]:
        """
        Get a specific item from a container.

        Args:
            container_type: Type of container
            item_id: ID of the item to retrieve

        Returns:
            Optional[Any]: The item if found, None otherwise
        """
        # Ensure container is loaded
        if container_type not in self._loaded:
            self.load_container(container_type)

        if container_type not in self._containers:
            return None

        for item in self._containers[container_type]:
            if item.id == item_id:
                return item

        return None

    def get_all_items(self, container_type: ContainerType) -> List[Any]:
        """
        Get all items from a container.

        Args:
            container_type: Type of container

        Returns:
            List[Any]: List of all items in the container
        """
        # Ensure container is loaded
        if container_type not in self._loaded:
            self.load_container(container_type)

        return self._containers.get(container_type, [])

    def update_item(self, container_type: ContainerType, item_id: str, updated_item: Any) -> bool:
        """
        Update an existing item in a container.

        Args:
            container_type: Type of container
            item_id: ID of the item to update
            updated_item: Updated item data

        Returns:
            bool: True if update was successful, False otherwise
        """
        # Ensure container is loaded
        if container_type not in self._loaded:
            self.load_container(container_type)

        if container_type not in self._containers:
            return False

        for i, item in enumerate(self._containers[container_type]):
            if item.id == item_id:
                # Update modified timestamp
                if hasattr(updated_item, 'modified_date'):
                    updated_item.modified_date = datetime.now().isoformat()

                self._containers[container_type][i] = updated_item
                logger.info(f"Updated item {item_id} in {container_type.value}")
                return True

        logger.warning(f"Item {item_id} not found in {container_type.value}")
        return False

    def delete_item(self, container_type: ContainerType, item_id: str) -> bool:
        """
        Delete an item from a container.

        Args:
            container_type: Type of container
            item_id: ID of the item to delete

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        # Ensure container is loaded
        if container_type not in self._loaded:
            self.load_container(container_type)

        if container_type not in self._containers:
            return False

        for i, item in enumerate(self._containers[container_type]):
            if item.id == item_id:
                del self._containers[container_type][i]
                logger.info(f"Deleted item {item_id} from {container_type.value}")
                return True

        logger.warning(f"Item {item_id} not found in {container_type.value}")
        return False

    def get_item_count(self, container_type: ContainerType) -> int:
        """
        Get the number of items in a container.

        Args:
            container_type: Type of container

        Returns:
            int: Number of items
        """
        # Ensure container is loaded
        if container_type not in self._loaded:
            self.load_container(container_type)

        return len(self._containers.get(container_type, []))

    def clear_container(self, container_type: ContainerType):
        """
        Clear all items from a container (in memory only, doesn't save).

        Args:
            container_type: Type of container to clear
        """
        if container_type in self._containers:
            self._containers[container_type] = []
            logger.info(f"Cleared container {container_type.value}")

    def save_all(self) -> bool:
        """
        Save all loaded containers to disk.

        Returns:
            bool: True if all saves were successful, False otherwise
        """
        success = True
        for container_type in self._loaded:
            if container_type in self._containers:
                if not self.save_container(container_type):
                    success = False

        return success

    def _get_container_file_path(self, container_type: ContainerType) -> str:
        """
        Get the file path for a container type.

        Args:
            container_type: Type of container

        Returns:
            str: Absolute path to the container file
        """
        filename = ContainerType.get_filename(container_type)
        return os.path.join(self.project_dir, filename)
