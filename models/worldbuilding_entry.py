"""
Worldbuilding Entry Model - Represents a worldbuilding element
"""
from dataclasses import dataclass, field
from typing import List
import uuid


@dataclass
class WorldbuildingEntry:
    """
    Model for worldbuilding elements (magic systems, geography, politics, etc.)

    Worldbuilding entries represent core elements of a fictional world that need
    to be tracked for consistency and reference during writing.
    """

    # Core fields
    title: str
    category: str = ""              # magic_system, geography, politics, religion, etc.
    description: str = ""           # Detailed description

    # Rules and details
    rules: List[str] = field(default_factory=list)  # Rules governing this element
    notes: str = ""                                  # Additional notes

    # Cross-references to other containers
    related_characters: List[str] = field(default_factory=list)  # Character IDs
    related_locations: List[str] = field(default_factory=list)   # Location IDs
    related_events: List[str] = field(default_factory=list)      # Timeline event IDs

    # Metadata
    tags: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_date: str = ""
    modified_date: str = ""

    # Worldbuilding-specific
    importance: str = "medium"  # low, medium, high, critical

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'description': self.description,
            'rules': self.rules,
            'notes': self.notes,
            'related_characters': self.related_characters,
            'related_locations': self.related_locations,
            'related_events': self.related_events,
            'tags': self.tags,
            'created_date': self.created_date,
            'modified_date': self.modified_date,
            'importance': self.importance
        }

    @staticmethod
    def from_dict(data: dict) -> 'WorldbuildingEntry':
        """Create instance from dictionary"""
        return WorldbuildingEntry(
            id=data['id'],
            title=data['title'],
            category=data.get('category', ''),
            description=data.get('description', ''),
            rules=data.get('rules', []),
            notes=data.get('notes', ''),
            related_characters=data.get('related_characters', []),
            related_locations=data.get('related_locations', []),
            related_events=data.get('related_events', []),
            tags=data.get('tags', []),
            created_date=data.get('created_date', ''),
            modified_date=data.get('modified_date', ''),
            importance=data.get('importance', 'medium')
        )


# Predefined worldbuilding categories
class WorldbuildingCategory:
    """Predefined categories for worldbuilding entries"""

    MAGIC_SYSTEM = "magic_system"
    TECHNOLOGY = "technology"
    GEOGRAPHY = "geography"
    POLITICS = "politics"
    RELIGION = "religion"
    ECONOMY = "economy"
    HISTORY = "history"
    RACES_SPECIES = "races_species"
    CULTURE = "culture"
    FACTIONS = "factions"
    LANGUAGE = "language"
    OTHER = "other"

    @staticmethod
    def get_all_categories() -> List[str]:
        """Get list of all category values"""
        return [
            WorldbuildingCategory.MAGIC_SYSTEM,
            WorldbuildingCategory.TECHNOLOGY,
            WorldbuildingCategory.GEOGRAPHY,
            WorldbuildingCategory.POLITICS,
            WorldbuildingCategory.RELIGION,
            WorldbuildingCategory.ECONOMY,
            WorldbuildingCategory.HISTORY,
            WorldbuildingCategory.RACES_SPECIES,
            WorldbuildingCategory.CULTURE,
            WorldbuildingCategory.FACTIONS,
            WorldbuildingCategory.LANGUAGE,
            WorldbuildingCategory.OTHER
        ]

    @staticmethod
    def get_display_name(category: str, language: str = 'it') -> str:
        """Get localized display name for category"""
        translations = {
            'it': {
                WorldbuildingCategory.MAGIC_SYSTEM: "Sistema Magico",
                WorldbuildingCategory.TECHNOLOGY: "Tecnologia",
                WorldbuildingCategory.GEOGRAPHY: "Geografia",
                WorldbuildingCategory.POLITICS: "Politica",
                WorldbuildingCategory.RELIGION: "Religione",
                WorldbuildingCategory.ECONOMY: "Economia",
                WorldbuildingCategory.HISTORY: "Storia",
                WorldbuildingCategory.RACES_SPECIES: "Razze/Specie",
                WorldbuildingCategory.CULTURE: "Cultura",
                WorldbuildingCategory.FACTIONS: "Fazioni",
                WorldbuildingCategory.LANGUAGE: "Lingue",
                WorldbuildingCategory.OTHER: "Altro"
            },
            'en': {
                WorldbuildingCategory.MAGIC_SYSTEM: "Magic System",
                WorldbuildingCategory.TECHNOLOGY: "Technology",
                WorldbuildingCategory.GEOGRAPHY: "Geography",
                WorldbuildingCategory.POLITICS: "Politics",
                WorldbuildingCategory.RELIGION: "Religion",
                WorldbuildingCategory.ECONOMY: "Economy",
                WorldbuildingCategory.HISTORY: "History",
                WorldbuildingCategory.RACES_SPECIES: "Races/Species",
                WorldbuildingCategory.CULTURE: "Culture",
                WorldbuildingCategory.FACTIONS: "Factions",
                WorldbuildingCategory.LANGUAGE: "Languages",
                WorldbuildingCategory.OTHER: "Other"
            }
        }

        lang_dict = translations.get(language, translations['en'])
        return lang_dict.get(category, category)

    @staticmethod
    def get_icon(category: str) -> str:
        """Get emoji icon for category"""
        icons = {
            WorldbuildingCategory.MAGIC_SYSTEM: "✨",
            WorldbuildingCategory.TECHNOLOGY: "🔬",
            WorldbuildingCategory.GEOGRAPHY: "🗺️",
            WorldbuildingCategory.POLITICS: "👑",
            WorldbuildingCategory.RELIGION: "⛪",
            WorldbuildingCategory.ECONOMY: "💰",
            WorldbuildingCategory.HISTORY: "📜",
            WorldbuildingCategory.RACES_SPECIES: "🧬",
            WorldbuildingCategory.CULTURE: "🎭",
            WorldbuildingCategory.FACTIONS: "⚔️",
            WorldbuildingCategory.LANGUAGE: "💬",
            WorldbuildingCategory.OTHER: "📦"
        }
        return icons.get(category, "📄")
