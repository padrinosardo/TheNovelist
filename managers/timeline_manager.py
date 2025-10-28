"""
Timeline Manager - Specialized manager for timeline events
"""
from typing import List, Optional
from models.timeline_event import TimelineEvent
from models.container_type import ContainerType
from managers.container_manager import ContainerManager
from utils.logger import logger


class TimelineManager:
    """
    Specialized manager for handling timeline events.

    Provides methods for organizing and managing chronological events
    with support for manual ordering and filtering.

    Attributes:
        container_manager: The underlying container manager
        container_type: Always TIMELINE
    """

    def __init__(self, container_manager: ContainerManager):
        """
        Initialize the timeline manager.

        Args:
            container_manager: The container manager instance
        """
        self.container_manager = container_manager
        self.container_type = ContainerType.TIMELINE

    def add_timeline_event(self, title: str, date: str = "", description: str = "",
                          sort_order: int = 0) -> str:
        """
        Create a new timeline event.

        Args:
            title: Event title
            date: In-story date
            description: Event description
            sort_order: Manual sort order

        Returns:
            str: ID of the created event
        """
        event = TimelineEvent(
            title=title,
            date=date,
            description=description,
            sort_order=sort_order
        )

        event_id = self.container_manager.add_item(self.container_type, event)
        logger.info(f"Created timeline event: {title} (ID: {event_id})")
        return event_id

    def add_timeline_event_object(self, event: TimelineEvent) -> str:
        """
        Add a timeline event object directly.

        Args:
            event: TimelineEvent object to add

        Returns:
            str: ID of the created timeline event
        """
        event_id = self.container_manager.add_item(self.container_type, event)
        logger.info(f"Created timeline event: {event.title} (ID: {event_id})")
        return event_id

    def get_timeline_event(self, event_id: str) -> Optional[TimelineEvent]:
        """
        Get a timeline event by ID.

        Args:
            event_id: ID of the event

        Returns:
            Optional[TimelineEvent]: The event if found, None otherwise
        """
        return self.container_manager.get_item(self.container_type, event_id)

    def get_all_timeline_events(self, sorted: bool = True) -> List[TimelineEvent]:
        """
        Get all timeline events.

        Args:
            sorted: If True, sort by sort_order

        Returns:
            List[TimelineEvent]: List of all timeline events
        """
        events = self.container_manager.get_all_items(self.container_type)

        if sorted:
            events = list(events)  # Make a copy
            events.sort(key=lambda e: e.sort_order)

        return events

    def update_timeline_event(self, event: TimelineEvent) -> bool:
        """
        Update an existing timeline event.

        Args:
            event: Updated event object

        Returns:
            bool: True if update was successful
        """
        event.update_modified_date()
        return self.container_manager.update_item(
            self.container_type,
            event.id,
            event
        )

    def delete_timeline_event(self, event_id: str) -> bool:
        """
        Delete a timeline event.

        Args:
            event_id: ID of the event to delete

        Returns:
            bool: True if deletion was successful
        """
        event = self.get_timeline_event(event_id)
        success = self.container_manager.delete_item(self.container_type, event_id)

        if success and event:
            logger.info(f"Deleted timeline event: {event.title} (ID: {event_id})")

        return success

    def reorder_event(self, event_id: str, new_sort_order: int) -> bool:
        """
        Change the sort order of an event.

        Args:
            event_id: ID of the event to reorder
            new_sort_order: New sort order value

        Returns:
            bool: True if reorder was successful
        """
        event = self.get_timeline_event(event_id)
        if not event:
            return False

        event.sort_order = new_sort_order
        return self.update_timeline_event(event)

    def get_events_by_character(self, character_id: str) -> List[TimelineEvent]:
        """
        Get all events involving a specific character.

        Args:
            character_id: ID of the character

        Returns:
            List[TimelineEvent]: List of matching events
        """
        all_events = self.get_all_timeline_events(sorted=True)
        return [event for event in all_events if character_id in event.characters]

    def get_events_by_location(self, location_id: str) -> List[TimelineEvent]:
        """
        Get all events that take place at a specific location.

        Args:
            location_id: ID of the location

        Returns:
            List[TimelineEvent]: List of matching events
        """
        all_events = self.get_all_timeline_events(sorted=True)
        return [event for event in all_events if location_id in event.locations]

    def search_events(self, query: str) -> List[TimelineEvent]:
        """
        Search events by title, date, or description.

        Args:
            query: Search query string

        Returns:
            List[TimelineEvent]: List of matching events
        """
        query = query.lower()
        all_events = self.get_all_timeline_events(sorted=False)

        return [
            event for event in all_events
            if (query in event.title.lower() or
                query in event.date.lower() or
                query in event.description.lower())
        ]

    def auto_sort_events(self):
        """
        Automatically assign sort_order values based on current order.

        This recalculates sort_order for all events, assigning sequential
        values (0, 10, 20, 30...) to allow easy insertion between events.
        """
        events = self.get_all_timeline_events(sorted=True)

        for i, event in enumerate(events):
            event.sort_order = i * 10
            self.update_timeline_event(event)

        logger.info(f"Auto-sorted {len(events)} timeline events")

    def insert_event_between(self, event_id: str, before_event_id: str, after_event_id: str) -> bool:
        """
        Insert an event between two other events.

        Args:
            event_id: ID of event to insert
            before_event_id: ID of event that should come before
            after_event_id: ID of event that should come after

        Returns:
            bool: True if insertion was successful
        """
        event = self.get_timeline_event(event_id)
        before_event = self.get_timeline_event(before_event_id)
        after_event = self.get_timeline_event(after_event_id)

        if not (event and before_event and after_event):
            return False

        # Calculate new sort order (midpoint)
        new_sort_order = (before_event.sort_order + after_event.sort_order) // 2

        # If there's no room, auto-sort first
        if new_sort_order == before_event.sort_order or new_sort_order == after_event.sort_order:
            self.auto_sort_events()
            # Recalculate
            before_event = self.get_timeline_event(before_event_id)
            after_event = self.get_timeline_event(after_event_id)
            new_sort_order = (before_event.sort_order + after_event.sort_order) // 2

        event.sort_order = new_sort_order
        return self.update_timeline_event(event)

    def save(self) -> bool:
        """
        Save all timeline events to disk.

        Returns:
            bool: True if save was successful
        """
        return self.container_manager.save_container(self.container_type)
