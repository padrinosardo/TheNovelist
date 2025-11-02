"""
Worldbuilding Manager - Specialized manager for worldbuilding entries
"""
from typing import List, Optional
from models.container_type import ContainerType
from models.worldbuilding_entry import WorldbuildingEntry, WorldbuildingCategory
from utils.logger import AppLogger


class WorldbuildingManager:
    """
    Manager specializzato per gestire worldbuilding entries con categorizzazione

    Features:
        - CRUD operations on worldbuilding entries
        - Category-based filtering
        - Tag-based search
        - Importance-based sorting
    """

    def __init__(self, container_manager):
        """
        Initialize WorldbuildingManager

        Args:
            container_manager: The ContainerManager instance for data operations
        """
        self.container_manager = container_manager
        self.container_type = ContainerType.WORLDBUILDING

        AppLogger.info("WorldbuildingManager initialized")

    def add_entry(self, title: str, category: str = "", description: str = "") -> str:
        """
        Create a new worldbuilding entry

        Args:
            title: Entry title
            category: Category (from WorldbuildingCategory)
            description: Entry description

        Returns:
            str: Entry ID
        """
        entry = WorldbuildingEntry(
            title=title,
            category=category,
            description=description
        )

        entry_id = self.container_manager.add_item(self.container_type, entry)
        AppLogger.info(f"Created worldbuilding entry: {title} (category: {category})")

        return entry_id

    def get_entry(self, entry_id: str) -> Optional[WorldbuildingEntry]:
        """
        Get a worldbuilding entry by ID

        Args:
            entry_id: Entry ID

        Returns:
            WorldbuildingEntry or None if not found
        """
        return self.container_manager.get_item(self.container_type, entry_id)

    def get_all_entries(self) -> List[WorldbuildingEntry]:
        """
        Get all worldbuilding entries

        Returns:
            List of WorldbuildingEntry objects
        """
        return self.container_manager.get_all_items(self.container_type)

    def get_entries_by_category(self, category: str) -> List[WorldbuildingEntry]:
        """
        Get entries filtered by category

        Args:
            category: Category to filter by

        Returns:
            List of WorldbuildingEntry objects in that category
        """
        all_entries = self.get_all_entries()
        return [e for e in all_entries if e.category == category]

    def get_entries_by_tag(self, tag: str) -> List[WorldbuildingEntry]:
        """
        Get entries that have a specific tag

        Args:
            tag: Tag to search for

        Returns:
            List of WorldbuildingEntry objects with that tag
        """
        all_entries = self.get_all_entries()
        return [e for e in all_entries if tag in e.tags]

    def get_entries_by_importance(self, importance: str) -> List[WorldbuildingEntry]:
        """
        Get entries filtered by importance level

        Args:
            importance: Importance level (low, medium, high, critical)

        Returns:
            List of WorldbuildingEntry objects with that importance
        """
        all_entries = self.get_all_entries()
        return [e for e in all_entries if e.importance == importance]

    def search_entries(self, search_text: str) -> List[WorldbuildingEntry]:
        """
        Search entries by title, description, or tags

        Args:
            search_text: Text to search for (case-insensitive)

        Returns:
            List of matching WorldbuildingEntry objects
        """
        all_entries = self.get_all_entries()
        search_lower = search_text.lower()

        results = []
        for entry in all_entries:
            # Search in title
            if search_lower in entry.title.lower():
                results.append(entry)
                continue

            # Search in description
            if search_lower in entry.description.lower():
                results.append(entry)
                continue

            # Search in tags
            if any(search_lower in tag.lower() for tag in entry.tags):
                results.append(entry)
                continue

            # Search in notes
            if search_lower in entry.notes.lower():
                results.append(entry)
                continue

        return results

    def update_entry(self, entry: WorldbuildingEntry) -> bool:
        """
        Update an existing worldbuilding entry

        Args:
            entry: Updated WorldbuildingEntry object

        Returns:
            bool: True if successful
        """
        success = self.container_manager.update_item(self.container_type, entry.id, entry)

        if success:
            AppLogger.info(f"Updated worldbuilding entry: {entry.title}")
        else:
            AppLogger.warning(f"Failed to update worldbuilding entry: {entry.id}")

        return success

    def delete_entry(self, entry_id: str) -> bool:
        """
        Delete a worldbuilding entry

        Args:
            entry_id: Entry ID

        Returns:
            bool: True if successful
        """
        entry = self.get_entry(entry_id)
        if entry:
            success = self.container_manager.delete_item(self.container_type, entry_id)

            if success:
                AppLogger.info(f"Deleted worldbuilding entry: {entry.title}")
            else:
                AppLogger.warning(f"Failed to delete worldbuilding entry: {entry_id}")

            return success

        return False

    def get_used_categories(self) -> List[str]:
        """
        Get list of categories currently used in entries

        Returns:
            List of category strings
        """
        all_entries = self.get_all_entries()
        categories = set(e.category for e in all_entries if e.category)
        return sorted(list(categories))

    def get_used_tags(self) -> List[str]:
        """
        Get list of all tags currently used in entries

        Returns:
            List of tag strings
        """
        all_entries = self.get_all_entries()
        tags = set()
        for entry in all_entries:
            tags.update(entry.tags)
        return sorted(list(tags))

    def get_entries_count(self) -> int:
        """
        Get total number of worldbuilding entries

        Returns:
            int: Number of entries
        """
        return len(self.get_all_entries())

    def get_category_counts(self) -> dict:
        """
        Get count of entries per category

        Returns:
            dict: {category: count}
        """
        all_entries = self.get_all_entries()
        counts = {}

        for entry in all_entries:
            category = entry.category or 'uncategorized'
            counts[category] = counts.get(category, 0) + 1

        return counts

    def duplicate_entry(self, entry_id: str) -> Optional[str]:
        """
        Duplicate an existing entry

        Args:
            entry_id: ID of entry to duplicate

        Returns:
            str: New entry ID, or None if failed
        """
        entry = self.get_entry(entry_id)
        if not entry:
            return None

        # Create copy with modified title
        from copy import deepcopy
        import uuid

        new_entry = deepcopy(entry)
        new_entry.id = str(uuid.uuid4())
        new_entry.title = f"{entry.title} (copia)"
        new_entry.created_date = ""  # Will be set by container_manager
        new_entry.modified_date = ""

        new_id = self.container_manager.add_item(self.container_type, new_entry)
        AppLogger.info(f"Duplicated worldbuilding entry: {entry.title}")

        return new_id

    def load(self) -> bool:
        """
        Load worldbuilding entries from storage

        Returns:
            bool: True if successful
        """
        try:
            self.container_manager.load_container(self.container_type)
            count = self.get_entries_count()
            AppLogger.info(f"Loaded {count} worldbuilding entries")
            return True
        except Exception as e:
            AppLogger.error(f"Failed to load worldbuilding entries: {e}")
            return False

    def save(self) -> bool:
        """
        Save worldbuilding entries to storage

        Returns:
            bool: True if successful
        """
        try:
            success = self.container_manager.save_container(self.container_type)
            if success:
                count = self.get_entries_count()
                AppLogger.info(f"Saved {count} worldbuilding entries")
            return success
        except Exception as e:
            AppLogger.error(f"Failed to save worldbuilding entries: {e}")
            return False
