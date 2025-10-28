# 🗺️ ROADMAP: Sistema Multi-Lingua e Multi-Tipologia

**The Novelist - Feature Planning Document**
**Versione**: 1.0
**Data Creazione**: 2025-10-27
**Obiettivo**: Trasformare The Novelist in uno strumento internazionale e versatile per diverse tipologie di scrittura

---

## 📋 Panoramica

Questo documento descrive il piano completo per implementare un sistema multi-lingua e multi-tipologia in The Novelist, permettendo agli utenti di:

1. **Selezionare la lingua** del progetto (Italiano, English, Español, Français, Deutsch)
2. **Scegliere la tipologia** di progetto (Romanzo, Racconto, Articolo, Poesia, etc.)
3. **Utilizzare contenitori dinamici** specifici per tipologia (Personaggi, Luoghi, Ricerche, Timeline, Note, Fonti, etc.)
4. **Ricevere analisi adattative** basate su lingua e tipologia
5. **Esportare con formattazione** appropriata per il tipo di contenuto

---

## 🎯 Stato Attuale del Progetto

### ✅ Feature Implementate

| Feature | Status | Note |
|---------|--------|-------|
| Project Management | ✅ Completo | Sistema ZIP-based con formato `.tnp` |
| Manuscript Structure | ✅ Completo | Gerarchia Chapters > Scenes |
| Characters Manager | ✅ Completo | CRUD + gestione immagini |
| Writing Statistics | ✅ Completo | Sessioni, obiettivi, dashboard |
| Modern UI | ✅ Completo | IDE-style con sidebar, workspace dinamico |
| Analysis Tools | ✅ Completo | Grammatica, Ripetizioni, Stile |
| Auto-save & Backup | ✅ Completo | Salvataggio automatico e backup |

### ❌ Feature Mancanti

| Feature | Status | Priorità |
|---------|--------|----------|
| Multi-Language Support | ❌ Non implementato | **ALTA** |
| Project Type System | ❌ Non implementato | **ALTA** |
| Dynamic Containers | ❌ Non implementato | **ALTA** |
| Locations Manager | ❌ Non implementato | Media |
| Research Notes | ❌ Non implementato | Media |
| Timeline System | ❌ Non implementato | Bassa |
| Template System | ❌ Non implementato | Media |
| Adaptive Analysis | ❌ Non implementato | Media |

---

## 🏗️ FASE 1: Sistema di Configurazione Lingua 🌍

**Obiettivo**: Permettere a ogni progetto di avere una lingua specifica e supportare analisi multi-lingua.

### Feature 1.1: Infrastruttura Multi-Lingua

**Modifiche al Data Model**:
```python
# models/project.py
@dataclass
class Project:
    title: str
    author: str
    language: str  # NEW: 'it', 'en', 'es', 'fr', 'de'
    created_date: str
    modified_date: str
    manuscript_text: str = ""
```

**Lingue Supportate**:
- `it` - Italiano (default attuale)
- `en` - English
- `es` - Español
- `fr` - Français
- `de` - Deutsch

**Modifiche a ProjectManager**:
- Aggiungere campo `language` al `manifest.json`
- Validare lingua all'apertura progetto
- Migrare progetti vecchi con `language = "it"` di default

**Caricamento Dinamico NLP**:
```python
# Mappatura lingua -> spaCy model
LANGUAGE_MODELS = {
    'it': 'it_core_news_sm',
    'en': 'en_core_web_sm',
    'es': 'es_core_news_sm',
    'fr': 'fr_core_news_sm',
    'de': 'de_core_news_sm'
}

# Caricamento dinamico in base a project.language
nlp = spacy.load(LANGUAGE_MODELS[project.language])
```

**LanguageTool Configuration**:
```python
# analisi/grammatica.py
def analizza_grammatica(text: str, language: str):
    tool = language_tool_python.LanguageTool(language)
    # ... analisi
```

**Settings Manager**:
```python
# utils/settings.py
class Settings:
    # ... existing fields
    preferred_ui_language: str = "it"  # Lingua UI (separata da lingua progetto)
```

**Complessità**: Media
**Tempo Stimato**: 2-3 giorni
**File Coinvolti**:
- `models/project.py`
- `managers/project_manager.py`
- `analisi/grammatica.py`
- `analisi/stile.py`
- `utils/settings.py`

---

### Feature 1.2: UI Selezione Lingua

**New Project Dialog Enhancement**:
```
┌─────────────────────────────────────────┐
│  Nuovo Progetto                         │
├─────────────────────────────────────────┤
│  Titolo:     [________________]         │
│  Autore:     [________________]         │
│  Lingua:     [🇮🇹 Italiano    ▼]       │  ← NEW
│                                         │
│         [Annulla]  [Crea Progetto]      │
└─────────────────────────────────────────┘
```

**Language Dropdown Options**:
- 🇮🇹 Italiano
- 🇬🇧 English
- 🇪🇸 Español
- 🇫🇷 Français
- 🇩🇪 Deutsch

**Project Properties Dialog**:
- Permettere modifica lingua progetto esistente
- Warning: "Cambio lingua richiederà ricaricamento modelli NLP"

**Status Bar Indicator**:
```
┌────────────────────────────────────────────────┐
│ [Documento non salvato] │ 🌍 IT │ 1250 parole │
└────────────────────────────────────────────────┘
                              ↑
                         Badge lingua
```

**Validation**:
- Verificare disponibilità modello spaCy prima di confermare
- Mostrare dialog download se modello mancante
- Fallback a italiano se modello non disponibile

**Complessità**: Bassa
**Tempo Stimato**: 1 giorno
**File Coinvolti**:
- `ui/components/new_project_dialog.py` (nuovo)
- `ui/components/project_properties_dialog.py` (nuovo)
- `ui/new_main_window.py` (status bar)

---

## 🏗️ FASE 2: Sistema Tipologie Progetto 📚

**Obiettivo**: Permettere agli utenti di specificare il tipo di progetto e adattare la struttura di conseguenza.

### Feature 2.1: Definizione Tipologie

**Enum ProjectType**:
```python
# models/project_type.py
from enum import Enum

class ProjectType(Enum):
    NOVEL = "novel"                    # Romanzo
    SHORT_STORY = "short_story"        # Racconto
    ARTICLE_MAGAZINE = "article_magazine"  # Articolo Rivista
    ARTICLE_SOCIAL = "article_social"   # Post Social Media
    POETRY = "poetry"                   # Poesia/Raccolta
    SCREENPLAY = "screenplay"           # Sceneggiatura
    ESSAY = "essay"                     # Saggio
    RESEARCH_PAPER = "research_paper"   # Paper Ricerca

    def get_display_name(self, language: str) -> str:
        """Ritorna nome localizzato della tipologia"""
        translations = {
            'it': {
                'novel': 'Romanzo',
                'short_story': 'Racconto',
                'article_magazine': 'Articolo per Rivista',
                'article_social': 'Post Social Media',
                'poetry': 'Poesia',
                'screenplay': 'Sceneggiatura',
                'essay': 'Saggio',
                'research_paper': 'Paper di Ricerca'
            },
            'en': {
                'novel': 'Novel',
                'short_story': 'Short Story',
                'article_magazine': 'Magazine Article',
                'article_social': 'Social Media Post',
                'poetry': 'Poetry',
                'screenplay': 'Screenplay',
                'essay': 'Essay',
                'research_paper': 'Research Paper'
            }
            # ... altre lingue
        }
        return translations.get(language, translations['en'])[self.value]
```

**Caratteristiche per Tipologia**:

| Tipologia | Struttura Manuscript | Target Word Count | Containers Principali |
|-----------|---------------------|-------------------|----------------------|
| Novel | Chapters + Scenes | 50k-120k | Characters, Locations, Research, Timeline |
| Short Story | Single Document o Scenes | 1k-20k | Characters, Locations, Notes |
| Article Magazine | Single Document | 500-5k | Sources, Keywords, Notes |
| Article Social | Single Document | 50-300 | Keywords, Media, Hashtags |
| Poetry | Collection of Poems | Variabile | Themes, Notes |
| Screenplay | Acts + Scenes | 15k-30k | Characters, Locations, Scenes |
| Essay | Single Document + Sections | 2k-10k | Sources, Notes, References |
| Research Paper | Sections (Intro/Methods/etc) | 5k-15k | Sources, Data, References |

**Complessità**: Bassa
**Tempo Stimato**: 0.5 giorni
**File Coinvolti**:
- `models/project_type.py` (nuovo)

---

### Feature 2.2: Modello Dati Tipologia

**Estensione Project Model**:
```python
# models/project.py
from models.project_type import ProjectType

@dataclass
class Project:
    title: str
    author: str
    language: str
    project_type: ProjectType  # NEW
    created_date: str
    modified_date: str
    manuscript_text: str = ""

    # Metadata specifici per tipologia (opzionali)
    genre: str = ""  # Per Novel, Short Story
    target_word_count: int = 0  # Target generale
    publication_date: str = ""  # Per articoli
    tags: List[str] = field(default_factory=list)  # Tag generali
```

**Serialization**:
```python
def to_dict(self) -> dict:
    return {
        'title': self.title,
        'author': self.author,
        'language': self.language,
        'project_type': self.project_type.value,  # Salva come stringa
        'created_date': self.created_date,
        'modified_date': self.modified_date,
        'manuscript_text': self.manuscript_text,
        'genre': self.genre,
        'target_word_count': self.target_word_count,
        'publication_date': self.publication_date,
        'tags': self.tags
    }

@staticmethod
def from_dict(data: dict) -> 'Project':
    return Project(
        title=data['title'],
        author=data['author'],
        language=data.get('language', 'it'),
        project_type=ProjectType(data.get('project_type', 'novel')),
        # ... altri campi
    )
```

**Migrazione Progetti Esistenti**:
```python
# managers/project_manager.py
def _migrate_old_project(self, manifest_data: dict) -> dict:
    """Migra progetti vecchi al nuovo formato"""
    if 'project_type' not in manifest_data:
        manifest_data['project_type'] = 'novel'  # Default
        manifest_data['language'] = 'it'  # Default
        logger.info("Migrated old project to new format")
    return manifest_data
```

**Complessità**: Bassa
**Tempo Stimato**: 0.5 giorni
**File Coinvolti**:
- `models/project.py`
- `managers/project_manager.py`

---

## 🏗️ FASE 3: Sistema Contenitori Dinamici 📦

**Obiettivo**: Creare un sistema flessibile di contenitori che si adattano alla tipologia di progetto.

### Feature 3.1: Architettura Contenitori

**Container Types Enum**:
```python
# models/container_type.py
from enum import Enum
from typing import List
from models.project_type import ProjectType

class ContainerType(Enum):
    # Contenitori Universali
    MANUSCRIPT = "manuscript"
    NOTES = "notes"

    # Contenitori Narrativa
    CHARACTERS = "characters"
    LOCATIONS = "locations"
    RESEARCH = "research"
    TIMELINE = "timeline"
    WORLDBUILDING = "worldbuilding"

    # Contenitori Articoli
    SOURCES = "sources"
    KEYWORDS = "keywords"
    MEDIA = "media"

    # Contenitori Poesia
    POEMS_COLLECTION = "poems_collection"
    THEMES = "themes"

    # Contenitori Sceneggiatura
    SCENES_DB = "scenes_db"

    # Contenitori Ricerca
    REFERENCES = "references"
    DATA = "data"

    @staticmethod
    def get_available_for_project_type(project_type: ProjectType) -> List['ContainerType']:
        """Ritorna i contenitori disponibili per una data tipologia"""
        mapping = {
            ProjectType.NOVEL: [
                ContainerType.MANUSCRIPT,
                ContainerType.CHARACTERS,
                ContainerType.LOCATIONS,
                ContainerType.RESEARCH,
                ContainerType.TIMELINE,
                ContainerType.WORLDBUILDING,
                ContainerType.NOTES
            ],
            ProjectType.SHORT_STORY: [
                ContainerType.MANUSCRIPT,
                ContainerType.CHARACTERS,
                ContainerType.LOCATIONS,
                ContainerType.NOTES
            ],
            ProjectType.ARTICLE_MAGAZINE: [
                ContainerType.MANUSCRIPT,
                ContainerType.SOURCES,
                ContainerType.KEYWORDS,
                ContainerType.NOTES
            ],
            ProjectType.ARTICLE_SOCIAL: [
                ContainerType.MANUSCRIPT,
                ContainerType.KEYWORDS,
                ContainerType.MEDIA,
                ContainerType.NOTES
            ],
            ProjectType.POETRY: [
                ContainerType.POEMS_COLLECTION,
                ContainerType.THEMES,
                ContainerType.NOTES
            ],
            ProjectType.SCREENPLAY: [
                ContainerType.MANUSCRIPT,
                ContainerType.CHARACTERS,
                ContainerType.LOCATIONS,
                ContainerType.SCENES_DB,
                ContainerType.NOTES
            ],
            ProjectType.ESSAY: [
                ContainerType.MANUSCRIPT,
                ContainerType.SOURCES,
                ContainerType.NOTES
            ],
            ProjectType.RESEARCH_PAPER: [
                ContainerType.MANUSCRIPT,
                ContainerType.SOURCES,
                ContainerType.REFERENCES,
                ContainerType.DATA,
                ContainerType.NOTES
            ]
        }
        return mapping.get(project_type, [ContainerType.MANUSCRIPT, ContainerType.NOTES])
```

**Complessità**: Media
**Tempo Stimato**: 1 giorno
**File Coinvolti**:
- `models/container_type.py` (nuovo)

---

### Feature 3.2: Data Models Nuovi Contenitori

**Location Model**:
```python
# models/location.py
from dataclasses import dataclass, field
from typing import List
import uuid

@dataclass
class Location:
    """Modello per rappresentare un luogo nella narrativa"""
    name: str
    description: str = ""
    images: List[str] = field(default_factory=list)
    characters_present: List[str] = field(default_factory=list)  # IDs personaggi
    notes: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_date: str = ""
    modified_date: str = ""

    # Metadata opzionali
    location_type: str = ""  # Es: "città", "stanza", "pianeta"
    parent_location_id: str = ""  # Per gerarchia (es: stanza -> casa -> città)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'images': self.images,
            'characters_present': self.characters_present,
            'notes': self.notes,
            'created_date': self.created_date,
            'modified_date': self.modified_date,
            'location_type': self.location_type,
            'parent_location_id': self.parent_location_id
        }

    @staticmethod
    def from_dict(data: dict) -> 'Location':
        return Location(
            id=data['id'],
            name=data['name'],
            description=data.get('description', ''),
            images=data.get('images', []),
            characters_present=data.get('characters_present', []),
            notes=data.get('notes', ''),
            created_date=data.get('created_date', ''),
            modified_date=data.get('modified_date', ''),
            location_type=data.get('location_type', ''),
            parent_location_id=data.get('parent_location_id', '')
        )
```

**Research Note Model**:
```python
# models/research_note.py
from dataclasses import dataclass, field
from typing import List
import uuid

@dataclass
class ResearchNote:
    """Modello per note di ricerca"""
    title: str
    content: str = ""
    sources: List[str] = field(default_factory=list)  # URLs o citazioni
    tags: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_date: str = ""
    modified_date: str = ""

    # Metadata
    category: str = ""  # Es: "storia", "tecnologia", "cultura"

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'sources': self.sources,
            'tags': self.tags,
            'created_date': self.created_date,
            'modified_date': self.modified_date,
            'category': self.category
        }

    @staticmethod
    def from_dict(data: dict) -> 'ResearchNote':
        return ResearchNote(
            id=data['id'],
            title=data['title'],
            content=data.get('content', ''),
            sources=data.get('sources', []),
            tags=data.get('tags', []),
            created_date=data.get('created_date', ''),
            modified_date=data.get('modified_date', ''),
            category=data.get('category', '')
        )
```

**Timeline Event Model**:
```python
# models/timeline_event.py
from dataclasses import dataclass, field
from typing import List
import uuid

@dataclass
class TimelineEvent:
    """Modello per eventi nella timeline narrativa"""
    title: str
    date: str = ""  # Data in-story (può essere "Anno 2145" o "3 Maggio")
    description: str = ""
    characters: List[str] = field(default_factory=list)  # IDs personaggi coinvolti
    locations: List[str] = field(default_factory=list)  # IDs luoghi
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_date: str = ""

    # Per ordinamento
    sort_order: int = 0  # Ordine cronologico manuale

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'date': self.date,
            'description': self.description,
            'characters': self.characters,
            'locations': self.locations,
            'created_date': self.created_date,
            'sort_order': self.sort_order
        }

    @staticmethod
    def from_dict(data: dict) -> 'TimelineEvent':
        return TimelineEvent(
            id=data['id'],
            title=data['title'],
            date=data.get('date', ''),
            description=data.get('description', ''),
            characters=data.get('characters', []),
            locations=data.get('locations', []),
            created_date=data.get('created_date', ''),
            sort_order=data.get('sort_order', 0)
        )
```

**Source Model** (per articoli/ricerca):
```python
# models/source.py
from dataclasses import dataclass, field
import uuid

@dataclass
class Source:
    """Modello per fonti e citazioni"""
    title: str
    author: str = ""
    url: str = ""
    citation: str = ""  # Citazione formattata
    notes: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_date: str = ""

    # Metadata
    source_type: str = "web"  # web, book, journal, interview
    access_date: str = ""  # Per fonti web

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'url': self.url,
            'citation': self.citation,
            'notes': self.notes,
            'created_date': self.created_date,
            'source_type': self.source_type,
            'access_date': self.access_date
        }

    @staticmethod
    def from_dict(data: dict) -> 'Source':
        return Source(
            id=data['id'],
            title=data['title'],
            author=data.get('author', ''),
            url=data.get('url', ''),
            citation=data.get('citation', ''),
            notes=data.get('notes', ''),
            created_date=data.get('created_date', ''),
            source_type=data.get('source_type', 'web'),
            access_date=data.get('access_date', '')
        )
```

**Generic Note Model**:
```python
# models/note.py
from dataclasses import dataclass, field
from typing import List
import uuid

@dataclass
class Note:
    """Modello per note generiche"""
    title: str
    content: str = ""
    tags: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_date: str = ""
    modified_date: str = ""

    # Collegamenti
    linked_to_scene: str = ""  # ID scena (se applicabile)
    linked_to_character: str = ""  # ID personaggio (se applicabile)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'tags': self.tags,
            'created_date': self.created_date,
            'modified_date': self.modified_date,
            'linked_to_scene': self.linked_to_scene,
            'linked_to_character': self.linked_to_character
        }

    @staticmethod
    def from_dict(data: dict) -> 'Note':
        return Note(
            id=data['id'],
            title=data['title'],
            content=data.get('content', ''),
            tags=data.get('tags', []),
            created_date=data.get('created_date', ''),
            modified_date=data.get('modified_date', ''),
            linked_to_scene=data.get('linked_to_scene', ''),
            linked_to_character=data.get('linked_to_character', '')
        )
```

**Complessità**: Media
**Tempo Stimato**: 2 giorni
**File Coinvolti**:
- `models/location.py` (nuovo)
- `models/research_note.py` (nuovo)
- `models/timeline_event.py` (nuovo)
- `models/source.py` (nuovo)
- `models/note.py` (nuovo)

---

### Feature 3.3: Container Manager Generico

**Base Container Manager**:
```python
# managers/container_manager.py
from typing import List, Any, Type, Dict
from models.container_type import ContainerType
from models.location import Location
from models.research_note import ResearchNote
from models.timeline_event import TimelineEvent
from models.source import Source
from models.note import Note
from models.character import Character
from utils.logger import logger
from datetime import datetime

class ContainerManager:
    """Manager generico per gestire tutti i tipi di contenitori"""

    # Mappatura tipo -> classe modello
    MODEL_CLASSES = {
        ContainerType.CHARACTERS: Character,
        ContainerType.LOCATIONS: Location,
        ContainerType.RESEARCH: ResearchNote,
        ContainerType.TIMELINE: TimelineEvent,
        ContainerType.SOURCES: Source,
        ContainerType.NOTES: Note
    }

    def __init__(self, project_dir: str):
        self.project_dir = project_dir
        self._containers: Dict[ContainerType, List[Any]] = {}

    def load_container(self, container_type: ContainerType) -> List[Any]:
        """Carica items da un contenitore specifico"""
        file_path = self._get_container_file_path(container_type)

        if not os.path.exists(file_path):
            logger.info(f"Container {container_type.value} not found, returning empty list")
            return []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            model_class = self.MODEL_CLASSES.get(container_type)
            if not model_class:
                logger.error(f"No model class for container type {container_type}")
                return []

            items = [model_class.from_dict(item_data) for item_data in data]
            self._containers[container_type] = items
            logger.info(f"Loaded {len(items)} items from {container_type.value}")
            return items

        except Exception as e:
            logger.error(f"Error loading container {container_type}: {e}")
            return []

    def save_container(self, container_type: ContainerType) -> bool:
        """Salva items di un contenitore specifico"""
        if container_type not in self._containers:
            logger.warning(f"Container {container_type.value} not loaded, nothing to save")
            return False

        file_path = self._get_container_file_path(container_type)

        try:
            items_data = [item.to_dict() for item in self._containers[container_type]]

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(items_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Saved {len(items_data)} items to {container_type.value}")
            return True

        except Exception as e:
            logger.error(f"Error saving container {container_type}: {e}")
            return False

    def add_item(self, container_type: ContainerType, item: Any) -> str:
        """Aggiunge un item a un contenitore"""
        if container_type not in self._containers:
            self._containers[container_type] = []

        # Aggiungi timestamp
        if hasattr(item, 'created_date') and not item.created_date:
            item.created_date = datetime.now().isoformat()
        if hasattr(item, 'modified_date'):
            item.modified_date = datetime.now().isoformat()

        self._containers[container_type].append(item)
        logger.info(f"Added item {item.id} to {container_type.value}")
        return item.id

    def get_item(self, container_type: ContainerType, item_id: str) -> Any:
        """Recupera un item specifico"""
        if container_type not in self._containers:
            return None

        for item in self._containers[container_type]:
            if item.id == item_id:
                return item
        return None

    def get_all_items(self, container_type: ContainerType) -> List[Any]:
        """Recupera tutti gli items di un contenitore"""
        return self._containers.get(container_type, [])

    def update_item(self, container_type: ContainerType, item_id: str, updated_item: Any) -> bool:
        """Aggiorna un item esistente"""
        if container_type not in self._containers:
            return False

        for i, item in enumerate(self._containers[container_type]):
            if item.id == item_id:
                # Aggiorna timestamp modifica
                if hasattr(updated_item, 'modified_date'):
                    updated_item.modified_date = datetime.now().isoformat()

                self._containers[container_type][i] = updated_item
                logger.info(f"Updated item {item_id} in {container_type.value}")
                return True

        logger.warning(f"Item {item_id} not found in {container_type.value}")
        return False

    def delete_item(self, container_type: ContainerType, item_id: str) -> bool:
        """Elimina un item"""
        if container_type not in self._containers:
            return False

        for i, item in enumerate(self._containers[container_type]):
            if item.id == item_id:
                del self._containers[container_type][i]
                logger.info(f"Deleted item {item_id} from {container_type.value}")
                return True

        logger.warning(f"Item {item_id} not found in {container_type.value}")
        return False

    def _get_container_file_path(self, container_type: ContainerType) -> str:
        """Ritorna il path del file per un contenitore"""
        filename_map = {
            ContainerType.CHARACTERS: 'characters.json',
            ContainerType.LOCATIONS: 'locations.json',
            ContainerType.RESEARCH: 'research.json',
            ContainerType.TIMELINE: 'timeline.json',
            ContainerType.SOURCES: 'sources.json',
            ContainerType.NOTES: 'notes.json'
        }
        filename = filename_map.get(container_type, f'{container_type.value}.json')
        return os.path.join(self.project_dir, filename)
```

**Location Manager** (specializzato):
```python
# managers/location_manager.py
from managers.container_manager import ContainerManager
from models.container_type import ContainerType
from models.location import Location
from typing import List
import shutil
import os

class LocationManager:
    """Manager specializzato per gestione luoghi con immagini"""

    def __init__(self, container_manager: ContainerManager, images_dir: str):
        self.container_manager = container_manager
        self.images_dir = images_dir
        self.container_type = ContainerType.LOCATIONS

    def add_location(self, name: str, description: str = "") -> str:
        """Crea un nuovo luogo"""
        location = Location(name=name, description=description)
        return self.container_manager.add_item(self.container_type, location)

    def get_location(self, location_id: str) -> Location:
        """Recupera un luogo per ID"""
        return self.container_manager.get_item(self.container_type, location_id)

    def get_all_locations(self) -> List[Location]:
        """Recupera tutti i luoghi"""
        return self.container_manager.get_all_items(self.container_type)

    def update_location(self, location: Location) -> bool:
        """Aggiorna un luogo"""
        return self.container_manager.update_item(self.container_type, location.id, location)

    def delete_location(self, location_id: str) -> bool:
        """Elimina un luogo e le sue immagini"""
        location = self.get_location(location_id)
        if not location:
            return False

        # Elimina immagini fisiche
        for image_filename in location.images:
            image_path = os.path.join(self.images_dir, image_filename)
            if os.path.exists(image_path):
                os.remove(image_path)

        return self.container_manager.delete_item(self.container_type, location_id)

    def add_image_to_location(self, location_id: str, image_path: str) -> bool:
        """Aggiunge un'immagine a un luogo"""
        location = self.get_location(location_id)
        if not location:
            return False

        # Copia immagine nella directory del progetto
        filename = f"loc_{location_id}_{len(location.images)}{os.path.splitext(image_path)[1]}"
        dest_path = os.path.join(self.images_dir, filename)
        shutil.copy(image_path, dest_path)

        location.images.append(filename)
        return self.update_location(location)

    def remove_image_from_location(self, location_id: str, image_filename: str) -> bool:
        """Rimuove un'immagine da un luogo"""
        location = self.get_location(location_id)
        if not location or image_filename not in location.images:
            return False

        # Elimina file fisico
        image_path = os.path.join(self.images_dir, image_filename)
        if os.path.exists(image_path):
            os.remove(image_path)

        location.images.remove(image_filename)
        return self.update_location(location)
```

**Complessità**: Alta
**Tempo Stimato**: 3 giorni
**File Coinvolti**:
- `managers/container_manager.py` (nuovo)
- `managers/location_manager.py` (nuovo)
- `managers/research_manager.py` (nuovo)
- `managers/timeline_manager.py` (nuovo)
- `managers/source_manager.py` (nuovo)
- `managers/note_manager.py` (nuovo)

---

## 🏗️ FASE 4: Struttura File Progetto Estesa 🗂️

**Obiettivo**: Estendere il formato `.tnp` per supportare i nuovi contenitori.

### Feature 4.1: Nuovo Formato `.tnp`

**Struttura File Estesa**:
```
my_novel.tnp (ZIP Archive)
├── manifest.json                      # Metadata progetto
│   ├── title
│   ├── author
│   ├── language                       # NEW
│   ├── project_type                   # NEW
│   ├── created_date
│   ├── modified_date
│   ├── genre                          # NEW
│   ├── target_word_count              # NEW
│   └── tags                           # NEW
│
├── manuscript_structure.json          # Struttura capitoli/scene (esistente)
├── statistics.json                    # Statistiche scrittura (esistente)
│
├── characters.json                    # Personaggi (esistente)
├── locations.json                     # NEW - Luoghi
├── research.json                      # NEW - Note ricerca
├── timeline.json                      # NEW - Eventi timeline
├── sources.json                       # NEW - Fonti/citazioni
├── notes.json                         # NEW - Note generiche
│
└── images/                            # Directory immagini (estesa)
    ├── char_<uuid>_0.jpg             # Immagini personaggi
    ├── char_<uuid>_1.png
    ├── loc_<uuid>_0.jpg              # NEW - Immagini luoghi
    └── loc_<uuid>_1.png
```

**Esempio manifest.json Esteso**:
```json
{
  "title": "Il Viaggio dell'Eroe",
  "author": "Mario Rossi",
  "language": "it",
  "project_type": "novel",
  "created_date": "2025-01-15T10:30:00",
  "modified_date": "2025-10-27T14:22:00",
  "genre": "Fantasy",
  "target_word_count": 80000,
  "tags": ["epic", "magic", "adventure"],
  "manuscript_text": ""
}
```

**Modifiche a ProjectManager**:
```python
# managers/project_manager.py

class ProjectManager:
    # ... existing code

    def _load_project_data(self):
        """Carica tutti i dati del progetto dal ZIP"""
        try:
            # Carica manifest
            manifest_path = os.path.join(self.temp_dir, 'manifest.json')
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)

            # Migra progetti vecchi
            manifest_data = self._migrate_old_project(manifest_data)

            self.project = Project.from_dict(manifest_data)

            # Carica manuscript structure
            self.manuscript_manager = ManuscriptStructureManager(self.temp_dir)
            self.manuscript_manager.load_manuscript_structure()

            # Carica characters (esistente)
            self.character_manager = CharacterManager(self.temp_dir, self._get_images_dir())
            self.character_manager.load_characters()

            # Carica statistics (esistente)
            self.statistics_manager = StatisticsManager(self.temp_dir)
            self.statistics_manager.load_statistics()

            # NEW: Carica contenitori dinamici
            self.container_manager = ContainerManager(self.temp_dir)
            available_containers = ContainerType.get_available_for_project_type(
                self.project.project_type
            )
            for container_type in available_containers:
                if container_type not in [ContainerType.MANUSCRIPT, ContainerType.CHARACTERS]:
                    self.container_manager.load_container(container_type)

            # NEW: Inizializza manager specializzati
            self.location_manager = LocationManager(
                self.container_manager,
                self._get_images_dir()
            )

            logger.info(f"Loaded project: {self.project.title} (Type: {self.project.project_type.value})")

        except Exception as e:
            logger.error(f"Error loading project data: {e}")
            raise

    def _save_project_data(self):
        """Salva tutti i dati del progetto nel ZIP"""
        try:
            # Salva manifest
            self.project.update_modified_date()
            manifest_path = os.path.join(self.temp_dir, 'manifest.json')
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(self.project.to_dict(), f, ensure_ascii=False, indent=2)

            # Salva manuscript structure
            self.manuscript_manager.save_manuscript_structure()

            # Salva characters
            self.character_manager.save_characters()

            # Salva statistics
            self.statistics_manager.save_statistics()

            # NEW: Salva contenitori dinamici
            available_containers = ContainerType.get_available_for_project_type(
                self.project.project_type
            )
            for container_type in available_containers:
                if container_type not in [ContainerType.MANUSCRIPT, ContainerType.CHARACTERS]:
                    self.container_manager.save_container(container_type)

            logger.info(f"Saved project: {self.project.title}")

        except Exception as e:
            logger.error(f"Error saving project data: {e}")
            raise
```

**Complessità**: Media
**Tempo Stimato**: 2 giorni
**File Coinvolti**:
- `managers/project_manager.py`

---

### Feature 4.2: Migrazione e Retrocompatibilità

**Migration Strategy**:
```python
# managers/project_manager.py

def _migrate_old_project(self, manifest_data: dict) -> dict:
    """Migra progetti vecchi al nuovo formato con logging"""
    migrations_applied = []

    # Migrazione 1: Aggiungi language se mancante
    if 'language' not in manifest_data:
        manifest_data['language'] = 'it'
        migrations_applied.append("Added default language: Italian")

    # Migrazione 2: Aggiungi project_type se mancante
    if 'project_type' not in manifest_data:
        manifest_data['project_type'] = 'novel'
        migrations_applied.append("Added default project type: Novel")

    # Migrazione 3: Aggiungi nuovi campi opzionali
    if 'genre' not in manifest_data:
        manifest_data['genre'] = ""
    if 'target_word_count' not in manifest_data:
        manifest_data['target_word_count'] = 0
    if 'tags' not in manifest_data:
        manifest_data['tags'] = []

    # Migrazione 4: Converti manuscript_text a manuscript_structure se necessario
    if 'manuscript_text' in manifest_data and manifest_data['manuscript_text']:
        # Se esiste testo ma non struttura, crea struttura da testo
        structure_path = os.path.join(self.temp_dir, 'manuscript_structure.json')
        if not os.path.exists(structure_path):
            self._convert_text_to_structure(manifest_data['manuscript_text'])
            manifest_data['manuscript_text'] = ""  # Svuota dopo migrazione
            migrations_applied.append("Converted manuscript text to structure")

    if migrations_applied:
        logger.info(f"Applied migrations: {', '.join(migrations_applied)}")
        # Mostra dialogo all'utente (opzionale)
        self._show_migration_dialog(migrations_applied)

    return manifest_data

def _show_migration_dialog(self, migrations: List[str]):
    """Mostra dialogo all'utente sulle migrazioni applicate"""
    from PySide6.QtWidgets import QMessageBox

    message = "Questo progetto è stato aggiornato al nuovo formato:\n\n"
    message += "\n".join([f"• {m}" for m in migrations])
    message += "\n\nIl progetto funzionerà normalmente. Si consiglia di salvare per confermare le modifiche."

    QMessageBox.information(None, "Progetto Aggiornato", message)
```

**Complessità**: Bassa
**Tempo Stimato**: 1 giorno
**File Coinvolti**:
- `managers/project_manager.py`

---

## 🏗️ FASE 5: UI Progetto Multi-Tipologia 🎨

**Obiettivo**: Adattare l'interfaccia utente per supportare tipologie e contenitori dinamici.

### Feature 5.1: Dialog Creazione Progetto Avanzato

**NewProjectDialog**:
```python
# ui/components/new_project_dialog.py
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit,
                                QComboBox, QPushButton, QGroupBox, QSpinBox)
from models.project_type import ProjectType

class NewProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuovo Progetto")
        self.setMinimumWidth(500)

        # Main layout
        main_layout = QVBoxLayout()

        # Basic info form
        form_layout = QFormLayout()

        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Es: Il Viaggio dell'Eroe")
        form_layout.addRow("Titolo:", self.title_input)

        self.author_input = QLineEdit()
        self.author_input.setPlaceholderText("Il tuo nome")
        form_layout.addRow("Autore:", self.author_input)

        # Language selector
        self.language_combo = QComboBox()
        self.language_combo.addItem("🇮🇹 Italiano", "it")
        self.language_combo.addItem("🇬🇧 English", "en")
        self.language_combo.addItem("🇪🇸 Español", "es")
        self.language_combo.addItem("🇫🇷 Français", "fr")
        self.language_combo.addItem("🇩🇪 Deutsch", "de")
        form_layout.addRow("Lingua:", self.language_combo)

        # Project type selector
        self.type_combo = QComboBox()
        for proj_type in ProjectType:
            display_name = proj_type.get_display_name('it')  # TODO: use UI language
            self.type_combo.addItem(display_name, proj_type)
        form_layout.addRow("Tipologia:", self.type_combo)

        main_layout.addLayout(form_layout)

        # Advanced options (collapsible)
        advanced_group = QGroupBox("Opzioni Avanzate")
        advanced_layout = QFormLayout()

        self.genre_input = QLineEdit()
        self.genre_input.setPlaceholderText("Es: Fantasy, Giallo, Romantico...")
        advanced_layout.addRow("Genere:", self.genre_input)

        self.target_words = QSpinBox()
        self.target_words.setRange(0, 1000000)
        self.target_words.setValue(80000)
        self.target_words.setSuffix(" parole")
        advanced_layout.addRow("Obiettivo Parole:", self.target_words)

        advanced_group.setLayout(advanced_layout)
        advanced_group.setCheckable(True)
        advanced_group.setChecked(False)  # Collapsed by default
        main_layout.addWidget(advanced_group)

        # Buttons
        button_layout = QHBoxLayout()
        cancel_btn = QPushButton("Annulla")
        cancel_btn.clicked.connect(self.reject)
        create_btn = QPushButton("Crea Progetto")
        create_btn.clicked.connect(self.accept)
        create_btn.setDefault(True)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(create_btn)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def get_project_data(self) -> dict:
        """Ritorna i dati del progetto inseriti"""
        return {
            'title': self.title_input.text(),
            'author': self.author_input.text(),
            'language': self.language_combo.currentData(),
            'project_type': self.type_combo.currentData(),
            'genre': self.genre_input.text(),
            'target_word_count': self.target_words.value()
        }
```

**Usage in Main Window**:
```python
# ui/new_main_window.py

def _create_new_project(self):
    """Mostra dialog creazione nuovo progetto"""
    dialog = NewProjectDialog(self)

    if dialog.exec() == QDialog.Accepted:
        project_data = dialog.get_project_data()

        # Valida dati
        if not project_data['title'] or not project_data['author']:
            QMessageBox.warning(self, "Dati Mancanti", "Inserisci titolo e autore.")
            return

        # Chiedi dove salvare
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Salva Nuovo Progetto",
            os.path.expanduser("~/Documents"),
            "The Novelist Projects (*.tnp)"
        )

        if file_path:
            # Crea progetto
            self.project_manager.create_new_project(
                title=project_data['title'],
                author=project_data['author'],
                language=project_data['language'],
                project_type=project_data['project_type'],
                file_path=file_path,
                genre=project_data['genre'],
                target_word_count=project_data['target_word_count']
            )

            # Aggiorna UI
            self._on_project_loaded()
```

**Complessità**: Media
**Tempo Stimato**: 2 giorni
**File Coinvolti**:
- `ui/components/new_project_dialog.py` (nuovo)
- `ui/new_main_window.py`

---

### Feature 5.2: Sidebar Dinamica per Tipologia

**Dynamic ProjectTree**:
```python
# ui/components/project_tree.py

class ProjectTree(QTreeWidget):
    # ... existing code

    def load_project_structure(self, project_manager):
        """Carica la struttura del progetto in base alla tipologia"""
        self.clear()

        if not project_manager or not project_manager.project:
            return

        project = project_manager.project

        # Root item
        root_item = QTreeWidgetItem(self)
        root_item.setText(0, f"📁 {project.title}")
        root_item.setData(0, Qt.UserRole, {'type': 'project'})

        # Aggiungi badge lingua
        language_badge = QLabel(f"🌍 {project.language.upper()}")
        language_badge.setStyleSheet("color: #666; font-size: 10px;")
        self.setItemWidget(root_item, 1, language_badge)

        # Ottieni contenitori disponibili per la tipologia
        available_containers = ContainerType.get_available_for_project_type(project.project_type)

        # Aggiungi contenitori dinamicamente
        for container_type in available_containers:
            self._add_container_node(root_item, container_type, project_manager)

        root_item.setExpanded(True)

    def _add_container_node(self, parent_item, container_type, project_manager):
        """Aggiunge un nodo per un contenitore specifico"""
        # Mappatura icone e nomi
        container_info = {
            ContainerType.MANUSCRIPT: ("📄", "Manoscritto"),
            ContainerType.CHARACTERS: ("👤", "Personaggi"),
            ContainerType.LOCATIONS: ("🗺️", "Luoghi"),
            ContainerType.RESEARCH: ("🔍", "Ricerche"),
            ContainerType.TIMELINE: ("⏱️", "Timeline"),
            ContainerType.NOTES: ("📝", "Note"),
            ContainerType.SOURCES: ("🔗", "Fonti"),
            ContainerType.KEYWORDS: ("#️⃣", "Keywords"),
            ContainerType.MEDIA: ("🖼️", "Media"),
            ContainerType.THEMES: ("🎭", "Temi"),
        }

        icon, name = container_info.get(container_type, ("📦", container_type.value))

        container_item = QTreeWidgetItem(parent_item)
        container_item.setText(0, f"{icon} {name}")
        container_item.setData(0, Qt.UserRole, {
            'type': 'container',
            'container_type': container_type
        })

        # Aggiungi items specifici del contenitore
        if container_type == ContainerType.MANUSCRIPT:
            self._add_manuscript_structure(container_item, project_manager)
        elif container_type == ContainerType.CHARACTERS:
            self._add_characters(container_item, project_manager)
        elif container_type == ContainerType.LOCATIONS:
            self._add_locations(container_item, project_manager)
        # ... altri contenitori

    def _add_locations(self, parent_item, project_manager):
        """Aggiunge i luoghi alla tree"""
        locations = project_manager.location_manager.get_all_locations()

        # Aggiorna conteggio nel parent
        parent_item.setText(0, f"🗺️ Luoghi ({len(locations)})")

        for location in locations:
            loc_item = QTreeWidgetItem(parent_item)
            loc_item.setText(0, f"📍 {location.name}")
            loc_item.setData(0, Qt.UserRole, {
                'type': 'location',
                'id': location.id
            })
```

**Context Menus Dinamici**:
```python
def _show_context_menu(self, position):
    """Mostra menu contestuale in base al tipo di nodo"""
    item = self.itemAt(position)
    if not item:
        return

    data = item.data(0, Qt.UserRole)
    menu = QMenu(self)

    if data['type'] == 'container':
        container_type = data['container_type']

        # Menu per contenitore
        if container_type == ContainerType.LOCATIONS:
            add_action = menu.addAction("➕ Aggiungi Luogo")
            add_action.triggered.connect(self._on_add_location)

        elif container_type == ContainerType.RESEARCH:
            add_action = menu.addAction("➕ Aggiungi Nota Ricerca")
            add_action.triggered.connect(self._on_add_research)

    elif data['type'] == 'location':
        edit_action = menu.addAction("✏️ Modifica")
        edit_action.triggered.connect(lambda: self._on_edit_location(data['id']))

        delete_action = menu.addAction("🗑️ Elimina")
        delete_action.triggered.connect(lambda: self._on_delete_location(data['id']))

    menu.exec_(self.viewport().mapToGlobal(position))
```

**Complessità**: Alta
**Tempo Stimato**: 3 giorni
**File Coinvolti**:
- `ui/components/project_tree.py`

---

### Feature 5.3: Viste Dettaglio Contenitori

**LocationDetailView** (simile a CharacterDetailView):
```python
# ui/components/location_detail_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                                QTextEdit, QPushButton, QLabel, QScrollArea)
from ui.components.image_gallery import ImageGallery

class LocationDetailView(QWidget):
    """Vista dettaglio per un luogo"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_location = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()

        # Header
        header = QLabel("Dettagli Luogo")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(header)

        # Nome
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Nome:"))
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Tipo luogo
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Tipo:"))
        self.type_input = QLineEdit()
        self.type_input.setPlaceholderText("Es: città, stanza, pianeta...")
        type_layout.addWidget(self.type_input)
        layout.addLayout(type_layout)

        # Descrizione
        layout.addWidget(QLabel("Descrizione:"))
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Descrivi il luogo...")
        layout.addWidget(self.description_edit)

        # Note
        layout.addWidget(QLabel("Note:"))
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(100)
        layout.addWidget(self.notes_edit)

        # Galleria immagini
        layout.addWidget(QLabel("Immagini:"))
        self.image_gallery = ImageGallery()
        self.image_gallery.image_added.connect(self._on_image_added)
        self.image_gallery.image_removed.connect(self._on_image_removed)
        layout.addWidget(self.image_gallery)

        # Pulsante salva
        save_btn = QPushButton("Salva Modifiche")
        save_btn.clicked.connect(self._save_location)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def load_location(self, location, location_manager):
        """Carica un luogo nella vista"""
        self.current_location = location
        self.location_manager = location_manager

        self.name_input.setText(location.name)
        self.type_input.setText(location.location_type)
        self.description_edit.setText(location.description)
        self.notes_edit.setText(location.notes)

        # Carica immagini
        self.image_gallery.clear()
        for image_filename in location.images:
            image_path = os.path.join(
                self.location_manager.images_dir,
                image_filename
            )
            self.image_gallery.add_image(image_path)

    def _save_location(self):
        """Salva le modifiche al luogo"""
        if not self.current_location:
            return

        self.current_location.name = self.name_input.text()
        self.current_location.location_type = self.type_input.text()
        self.current_location.description = self.description_edit.toPlainText()
        self.current_location.notes = self.notes_edit.toPlainText()

        self.location_manager.update_location(self.current_location)

        QMessageBox.information(self, "Salvato", "Modifiche salvate con successo!")
```

**ResearchListView**:
```python
# ui/components/research_list_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                                QPushButton, QLineEdit, QLabel)

class ResearchListView(QWidget):
    """Vista lista note di ricerca"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()

        # Header con ricerca
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("🔍 Note di Ricerca"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cerca per titolo o tag...")
        self.search_input.textChanged.connect(self._filter_notes)
        header_layout.addWidget(self.search_input)

        add_btn = QPushButton("➕ Nuova Nota")
        add_btn.clicked.connect(self._add_note)
        header_layout.addWidget(add_btn)

        layout.addLayout(header_layout)

        # Lista note
        self.notes_list = QListWidget()
        self.notes_list.itemClicked.connect(self._on_note_selected)
        layout.addWidget(self.notes_list)

        self.setLayout(layout)

    def load_research_notes(self, container_manager):
        """Carica le note di ricerca"""
        self.container_manager = container_manager
        notes = container_manager.get_all_items(ContainerType.RESEARCH)

        self.notes_list.clear()
        for note in notes:
            item = QListWidgetItem(f"📄 {note.title}")
            item.setData(Qt.UserRole, note.id)

            # Sottotitolo con tags
            if note.tags:
                tags_str = ", ".join([f"#{tag}" for tag in note.tags])
                item.setToolTip(tags_str)

            self.notes_list.addItem(item)
```

**TimelineView**:
```python
# ui/components/timeline_view.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QFrame,
                                QLabel, QPushButton)

class TimelineView(QWidget):
    """Vista cronologica eventi"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("⏱️ Timeline Eventi"))
        add_btn = QPushButton("➕ Nuovo Evento")
        add_btn.clicked.connect(self._add_event)
        header_layout.addWidget(add_btn)
        layout.addLayout(header_layout)

        # Scroll area per timeline
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        self.timeline_container = QWidget()
        self.timeline_layout = QVBoxLayout()
        self.timeline_container.setLayout(self.timeline_layout)

        scroll.setWidget(self.timeline_container)
        layout.addWidget(scroll)

        self.setLayout(layout)

    def load_timeline(self, container_manager):
        """Carica eventi timeline"""
        self.container_manager = container_manager
        events = container_manager.get_all_items(ContainerType.TIMELINE)

        # Ordina per sort_order
        events.sort(key=lambda e: e.sort_order)

        # Pulisci timeline
        while self.timeline_layout.count():
            item = self.timeline_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Aggiungi eventi
        for event in events:
            event_widget = self._create_event_widget(event)
            self.timeline_layout.addWidget(event_widget)

    def _create_event_widget(self, event):
        """Crea widget per un evento"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)

        layout = QVBoxLayout()

        # Titolo ed data
        title_label = QLabel(f"<b>{event.title}</b>")
        layout.addWidget(title_label)

        if event.date:
            date_label = QLabel(f"📅 {event.date}")
            date_label.setStyleSheet("color: #666;")
            layout.addWidget(date_label)

        # Descrizione
        if event.description:
            desc_label = QLabel(event.description)
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        frame.setLayout(layout)
        return frame
```

**Complessità**: Alta
**Tempo Stimato**: 4 giorni
**File Coinvolti**:
- `ui/components/location_detail_view.py` (nuovo)
- `ui/components/research_list_view.py` (nuovo)
- `ui/components/timeline_view.py` (nuovo)
- `ui/components/workspace_container.py` (modifiche per nuove viste)

---

## 🏗️ FASE 6: Analisi Adattativa per Lingua/Tipologia 🔍

**Obiettivo**: Adattare gli strumenti di analisi in base alla lingua e tipologia di progetto.

### Feature 6.1: Analisi Grammatica Multi-Lingua

**Modifiche a GrammaticaAnalyzer**:
```python
# analisi/grammatica.py
import language_tool_python
from typing import List, Dict

class GrammaticaAnalyzer:
    def __init__(self):
        self.tool = None
        self.current_language = None

    def set_language(self, language_code: str):
        """Imposta la lingua per l'analisi"""
        if self.current_language != language_code:
            if self.tool:
                self.tool.close()

            # Mappatura codici lingua
            lang_map = {
                'it': 'it',
                'en': 'en-US',
                'es': 'es',
                'fr': 'fr',
                'de': 'de'
            }

            lt_language = lang_map.get(language_code, 'en-US')
            self.tool = language_tool_python.LanguageTool(lt_language)
            self.current_language = language_code
            logger.info(f"LanguageTool initialized for language: {lt_language}")

    def analizza(self, text: str, language: str) -> List[Dict]:
        """Analizza grammatica nel testo"""
        self.set_language(language)

        if not self.tool:
            return []

        matches = self.tool.check(text)

        errori = []
        for match in matches:
            errori.append({
                'message': match.message,
                'context': match.context,
                'offset': match.offset,
                'length': match.errorLength,
                'replacements': match.replacements[:3],  # Top 3 suggerimenti
                'rule_id': match.ruleId,
                'category': match.category
            })

        return errori
```

**Complessità**: Bassa
**Tempo Stimato**: 1 giorno
**File Coinvolti**:
- `analisi/grammatica.py`

---

### Feature 6.2: Analisi Stile per Tipologia

**Adaptive Style Analyzer**:
```python
# analisi/stile.py
from models.project_type import ProjectType
from typing import Dict

class StileAnalyzer:
    # ... existing code

    def analizza(self, text: str, project_type: ProjectType, language: str) -> Dict:
        """Analizza stile adattato alla tipologia"""

        # Analisi base
        risultati = self._analizza_base(text, language)

        # Aggiungi metriche specifiche per tipologia
        risultati['suggestions'] = self._get_type_specific_suggestions(
            risultati, project_type
        )

        return risultati

    def _get_type_specific_suggestions(self, stats: Dict, project_type: ProjectType) -> List[str]:
        """Genera suggerimenti basati sulla tipologia"""
        suggestions = []

        avg_sentence_length = stats.get('avg_sentence_length', 0)
        lexical_diversity = stats.get('lexical_diversity', 0)

        if project_type == ProjectType.NOVEL:
            # Romanzo: varietà e fluidità
            if avg_sentence_length > 25:
                suggestions.append("⚠️ Frasi molto lunghe (media: {:.1f} parole). Considera di spezzarle.".format(avg_sentence_length))

            if lexical_diversity < 0.4:
                suggestions.append("⚠️ Varietà lessicale bassa ({:.1%}). Usa sinonimi per arricchire il testo.".format(lexical_diversity))

        elif project_type == ProjectType.ARTICLE_SOCIAL:
            # Social: brevità e impatto
            if avg_sentence_length > 15:
                suggestions.append("💡 Per i social, preferisci frasi brevi (max 15 parole). Attuale: {:.1f}".format(avg_sentence_length))

            total_words = stats.get('total_words', 0)
            if total_words > 300:
                suggestions.append("⚠️ Post molto lungo ({} parole). Target social: 50-300 parole.".format(total_words))

            # Controlla presenza hashtags
            if '#' not in stats.get('text', ''):
                suggestions.append("💡 Considera di aggiungere hashtags per visibilità.")

        elif project_type == ProjectType.ARTICLE_MAGAZINE:
            # Articolo rivista: formalità e struttura
            if avg_sentence_length < 12:
                suggestions.append("💡 Frasi troppo brevi per un articolo ({:.1f} parole). Target: 15-20.".format(avg_sentence_length))

            # Controlla paragrafi
            num_paragraphs = stats.get('num_paragraphs', 0)
            if num_paragraphs < 3:
                suggestions.append("💡 Articolo con pochi paragrafi. Struttura consigliata: Intro, Corpo, Conclusione.")

        elif project_type == ProjectType.POETRY:
            # Poesia: libertà espressiva, ma coerenza
            suggestions.append("✨ Per la poesia, le regole sono flessibili. Segui il tuo stile!")

        elif project_type == ProjectType.RESEARCH_PAPER:
            # Paper: precisione e formalità
            if lexical_diversity < 0.5:
                suggestions.append("⚠️ Varietà lessicale bassa per un paper accademico ({:.1%}).".format(lexical_diversity))

            # TODO: Check for citations
            suggestions.append("💡 Verifica che tutte le affermazioni siano supportate da citazioni.")

        return suggestions
```

**Complessità**: Media
**Tempo Stimato**: 2 giorni
**File Coinvolti**:
- `analisi/stile.py`

---

### Feature 6.3: Suggerimenti Contestuali

**Contextual Warnings System**:
```python
# analisi/context_analyzer.py
from models.project_type import ProjectType
from typing import List, Dict

class ContextAnalyzer:
    """Analizzatore di contesto per warnings e suggerimenti"""

    @staticmethod
    def check_project_health(project_manager) -> List[Dict]:
        """Controlla lo stato generale del progetto e ritorna warnings"""
        warnings = []

        project = project_manager.project
        stats = project_manager.statistics_manager.get_stats()

        # Check word count vs target
        current_words = stats.total_words
        target_words = project.target_word_count

        if target_words > 0:
            progress = current_words / target_words

            if project.project_type == ProjectType.NOVEL:
                if current_words < 20000:
                    warnings.append({
                        'level': 'info',
                        'message': f"Romanzo in fase iniziale ({current_words:,} / {target_words:,} parole, {progress:.1%})"
                    })
                elif current_words > 150000:
                    warnings.append({
                        'level': 'warning',
                        'message': f"Romanzo molto lungo ({current_words:,} parole). Considera di dividere in volumi."
                    })

            elif project.project_type == ProjectType.SHORT_STORY:
                if current_words > 20000:
                    warnings.append({
                        'level': 'warning',
                        'message': f"Troppo lungo per un racconto ({current_words:,} parole). Considera di farne un romanzo breve."
                    })

            elif project.project_type == ProjectType.ARTICLE_SOCIAL:
                if current_words > 300:
                    warnings.append({
                        'level': 'warning',
                        'message': f"Post social troppo lungo ({current_words} parole). Target: 50-300."
                    })

        # Check characters
        if project.project_type in [ProjectType.NOVEL, ProjectType.SHORT_STORY]:
            characters = project_manager.character_manager.get_all_characters()
            if len(characters) == 0:
                warnings.append({
                    'level': 'info',
                    'message': "Nessun personaggio creato. Aggiungi personaggi per organizzare meglio la narrativa."
                })

        # Check sources for academic/journalistic content
        if project.project_type in [ProjectType.ARTICLE_MAGAZINE, ProjectType.RESEARCH_PAPER]:
            sources = project_manager.container_manager.get_all_items(ContainerType.SOURCES)
            if len(sources) < 3:
                warnings.append({
                    'level': 'warning',
                    'message': "Poche fonti citate. Un buon articolo/paper richiede fonti solide."
                })

        return warnings
```

**Display Warnings in UI**:
```python
# ui/components/project_health_panel.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame

class ProjectHealthPanel(QWidget):
    """Pannello che mostra lo stato del progetto"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout()

        header = QLabel("📊 Stato Progetto")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)

        self.warnings_container = QVBoxLayout()
        layout.addLayout(self.warnings_container)

        layout.addStretch()
        self.setLayout(layout)

    def update_warnings(self, warnings: List[Dict]):
        """Aggiorna i warnings visualizzati"""
        # Pulisci
        while self.warnings_container.count():
            item = self.warnings_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Aggiungi warnings
        for warning in warnings:
            self._add_warning_widget(warning)

    def _add_warning_widget(self, warning: Dict):
        """Aggiunge un widget warning"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)

        level = warning['level']
        icon = "⚠️" if level == 'warning' else "ℹ️"
        color = "#ff9800" if level == 'warning' else "#2196f3"

        label = QLabel(f"{icon} {warning['message']}")
        label.setWordWrap(True)
        label.setStyleSheet(f"color: {color}; padding: 8px;")

        layout = QVBoxLayout()
        layout.addWidget(label)
        frame.setLayout(layout)

        self.warnings_container.addWidget(frame)
```

**Complessità**: Media
**Tempo Stimato**: 2 giorni
**File Coinvolti**:
- `analisi/context_analyzer.py` (nuovo)
- `ui/components/project_health_panel.py` (nuovo)
- `ui/new_main_window.py` (integrazione pannello)

---

## 🏗️ FASE 7: Export e Template 📤

**Obiettivo**: Fornire template pre-configurati e export formattato per tipologia.

### Feature 7.1: Template per Tipologia

**Template System**:
```python
# utils/templates.py
from models.project_type import ProjectType
from models.project import Project
from models.manuscript_structure import Chapter, Scene, ManuscriptStructure
from typing import Dict

class TemplateManager:
    """Gestisce i template per diverse tipologie di progetto"""

    @staticmethod
    def create_from_template(project_type: ProjectType, title: str, author: str, language: str) -> Dict:
        """Crea struttura iniziale da template"""

        if project_type == ProjectType.NOVEL:
            return TemplateManager._create_novel_template(title, author, language)

        elif project_type == ProjectType.SHORT_STORY:
            return TemplateManager._create_short_story_template(title, author, language)

        elif project_type == ProjectType.ARTICLE_MAGAZINE:
            return TemplateManager._create_article_template(title, author, language)

        elif project_type == ProjectType.SCREENPLAY:
            return TemplateManager._create_screenplay_template(title, author, language)

        # Default: struttura minima
        return {
            'manuscript_structure': ManuscriptStructure(),
            'initial_characters': [],
            'initial_locations': [],
            'initial_notes': []
        }

    @staticmethod
    def _create_novel_template(title: str, author: str, language: str) -> Dict:
        """Template per romanzo"""
        # Crea struttura base: 3 capitoli con 1 scena ciascuno
        chapters = [
            Chapter(
                title=f"Capitolo {i+1}",
                scenes=[
                    Scene(
                        title=f"Scena 1",
                        content="",
                        order=0
                    )
                ],
                order=i
            )
            for i in range(3)
        ]

        manuscript = ManuscriptStructure(chapters=chapters)

        # Personaggi esempio
        from models.character import Character
        initial_characters = [
            Character(name="Protagonista", description="Il personaggio principale della storia."),
            Character(name="Antagonista", description="Il personaggio che si oppone al protagonista.")
        ]

        # Luoghi esempio
        from models.location import Location
        initial_locations = [
            Location(name="Luogo Principale", description="Il luogo dove si svolge gran parte della storia.")
        ]

        # Note iniziali
        from models.note import Note
        initial_notes = [
            Note(
                title="Note sulla Trama",
                content="Usa questa nota per tenere traccia delle idee sulla trama principale."
            )
        ]

        return {
            'manuscript_structure': manuscript,
            'initial_characters': initial_characters,
            'initial_locations': initial_locations,
            'initial_notes': initial_notes
        }

    @staticmethod
    def _create_article_template(title: str, author: str, language: str) -> Dict:
        """Template per articolo"""
        # Singola "scena" con struttura suggerita
        scene_content = """[TITOLO ACCATTIVANTE]

[INTRODUZIONE - cattura l'attenzione del lettore]

[CORPO PRINCIPALE - sviluppa l'argomento]

[CONCLUSIONE - riassumi e chiama all'azione]

[FONTI E RIFERIMENTI]
"""

        chapter = Chapter(
            title="Articolo",
            scenes=[Scene(title="Bozza", content=scene_content, order=0)],
            order=0
        )

        manuscript = ManuscriptStructure(chapters=[chapter])

        return {
            'manuscript_structure': manuscript,
            'initial_characters': [],
            'initial_locations': [],
            'initial_notes': []
        }
```

**Usage in Project Creation**:
```python
# managers/project_manager.py

def create_new_project(self, title: str, author: str, language: str,
                       project_type: ProjectType, file_path: str, **kwargs):
    """Crea un nuovo progetto con template"""
    # ... existing code ...

    # Applica template
    template_data = TemplateManager.create_from_template(
        project_type, title, author, language
    )

    # Imposta manuscript structure
    self.manuscript_manager.set_manuscript_structure(
        template_data['manuscript_structure']
    )

    # Aggiungi contenuti iniziali
    for character in template_data.get('initial_characters', []):
        self.character_manager.add_character(character)

    for location in template_data.get('initial_locations', []):
        self.location_manager.add_location(location.name, location.description)

    # ... save project
```

**Complessità**: Media
**Tempo Stimato**: 2 giorni
**File Coinvolti**:
- `utils/templates.py` (nuovo)
- `managers/project_manager.py`

---

### Feature 7.2: Export Formattato

**Export Manager**:
```python
# utils/export_manager.py
from models.project_type import ProjectType
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class ExportManager:
    """Gestisce l'export in vari formati"""

    @staticmethod
    def export_to_pdf(project_manager, output_path: str):
        """Esporta progetto in PDF con formattazione per tipologia"""

        project = project_manager.project
        project_type = project.project_type

        if project_type == ProjectType.NOVEL:
            ExportManager._export_novel_pdf(project_manager, output_path)

        elif project_type == ProjectType.ARTICLE_MAGAZINE:
            ExportManager._export_article_pdf(project_manager, output_path)

        elif project_type == ProjectType.SCREENPLAY:
            ExportManager._export_screenplay_pdf(project_manager, output_path)

        else:
            ExportManager._export_generic_pdf(project_manager, output_path)

    @staticmethod
    def _export_novel_pdf(project_manager, output_path: str):
        """Export romanzo in formato standard manuscript"""
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []
        styles = getSampleStyleSheet()

        # Stile personalizzato per romanzi
        chapter_style = ParagraphStyle(
            'ChapterHeading',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=0.5*inch,
            alignment=1  # Center
        )

        body_style = ParagraphStyle(
            'NovelBody',
            parent=styles['BodyText'],
            fontSize=12,
            leading=14,
            firstLineIndent=0.5*inch
        )

        # Frontespizio
        story.append(Paragraph(project_manager.project.title, chapter_style))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(f"di {project_manager.project.author}", styles['Normal']))
        story.append(PageBreak())

        # Capitoli
        manuscript = project_manager.manuscript_manager.get_manuscript_structure()
        for chapter in manuscript.chapters:
            # Titolo capitolo
            story.append(Paragraph(chapter.title, chapter_style))
            story.append(Spacer(1, 0.3*inch))

            # Scene del capitolo
            for scene in chapter.scenes:
                # Aggiungi contenuto scena
                for paragraph in scene.content.split('\n\n'):
                    if paragraph.strip():
                        story.append(Paragraph(paragraph, body_style))
                        story.append(Spacer(1, 0.2*inch))

            story.append(PageBreak())

        doc.build(story)

    @staticmethod
    def _export_article_pdf(project_manager, output_path: str):
        """Export articolo in formato pubblicazione"""
        # Formato più compatto, con citazioni evidenziate
        # ... implementazione simile con stili diversi
        pass

    @staticmethod
    def _export_screenplay_pdf(project_manager, output_path: str):
        """Export sceneggiatura in formato standard (Courier, margini specifici)"""
        # Formato sceneggiatura: Courier 12pt, margini standard industria
        # ... implementazione con formattazione Courier New
        pass
```

**Export Menu Integration**:
```python
# ui/components/menu_bar.py

def _create_file_menu(self):
    file_menu = self.addMenu("File")

    # ... existing actions

    # Export submenu
    export_menu = file_menu.addMenu("Esporta")

    export_pdf = QAction("Esporta PDF...", self)
    export_pdf.triggered.connect(self.export_pdf_requested.emit)
    export_menu.addAction(export_pdf)

    export_docx = QAction("Esporta Word (DOCX)...", self)
    export_docx.triggered.connect(self.export_docx_requested.emit)
    export_menu.addAction(export_docx)
```

**Complessità**: Media
**Tempo Stimato**: 3 giorni
**File Coinvolti**:
- `utils/export_manager.py` (nuovo)
- `ui/components/menu_bar.py`
- `ui/new_main_window.py` (gestione segnali export)

---

## 📊 PRIORITÀ DI IMPLEMENTAZIONE

### **Milestone 1: Fondamenta Multi-Lingua e Tipologie (v1.5)**
**Tempo Stimato**: 4-5 giorni
**Priorità**: ALTA ⭐⭐⭐

**Feature Incluse**:
- ✅ Feature 1.1: Infrastruttura Multi-Lingua (2-3 giorni)
- ✅ Feature 1.2: UI Selezione Lingua (1 giorno)
- ✅ Feature 2.1: Definizione Tipologie (0.5 giorni)
- ✅ Feature 2.2: Modello Dati Tipologia (0.5 giorni)

**Deliverables**:
- Sistema selezione lingua per progetto
- Definizione enum tipologie progetto
- Dialog creazione progetto base con lingua/tipologia
- Migrazione progetti esistenti

---

### **Milestone 2: Contenitori Dinamici Base (v1.6)**
**Tempo Stimato**: 7-8 giorni
**Priorità**: ALTA ⭐⭐⭐

**Feature Incluse**:
- ✅ Feature 3.1: Architettura Contenitori (1 giorno)
- ✅ Feature 3.2: Data Models - Locations e Research (2 giorni)
- ✅ Feature 3.3: Container Manager + Location Manager (3 giorni)
- ✅ Feature 4.1: Estensione formato .tnp (2 giorni)
- ✅ Feature 4.2: Migrazione (1 giorno)

**Deliverables**:
- Sistema contenitori generico
- Implementazione Locations e Research Notes
- Manager per gestione contenitori
- Formato .tnp esteso

---

### **Milestone 3: UI Completa e Contenitori Avanzati (v1.7)**
**Tempo Stimato**: 8-10 giorni
**Priorità**: MEDIA ⭐⭐

**Feature Incluse**:
- ✅ Feature 5.1: Dialog Creazione Avanzato (2 giorni)
- ✅ Feature 5.2: Sidebar Dinamica (3 giorni)
- ✅ Feature 5.3: Viste Dettaglio (LocationDetailView, ResearchListView, TimelineView) (4 giorni)
- ✅ Feature 3.2 completamento: Timeline, Sources, Notes models (1 giorno)

**Deliverables**:
- Dialog creazione progetto completo
- Sidebar che si adatta alla tipologia
- Viste dettaglio per tutti i contenitori
- Timeline, Sources, Notes completi

---

### **Milestone 4: Intelligenza Adattativa e Template (v2.0)**
**Tempo Stimato**: 7-8 giorni
**Priorità**: MEDIA ⭐

**Feature Incluse**:
- ✅ Feature 6.1: Analisi Grammatica Multi-Lingua (1 giorno)
- ✅ Feature 6.2: Analisi Stile per Tipologia (2 giorni)
- ✅ Feature 6.3: Suggerimenti Contestuali (2 giorni)
- ✅ Feature 7.1: Template per Tipologia (2 giorni)
- ✅ Feature 7.2: Export Formattato (3 giorni)

**Deliverables**:
- Analisi adattativa lingua/tipologia
- Sistema suggerimenti contestuali
- Template pre-configurati
- Export PDF/DOCX formattato

---

## 📈 STIMA COMPLESSITÀ TOTALE

| Fase | Complessità | Tempo Stimato | Priorità |
|------|-------------|---------------|----------|
| **Fase 1** - Multi-Lingua | Media | 3 giorni | ⭐⭐⭐ ALTA |
| **Fase 2** - Tipologie | Bassa | 1 giorno | ⭐⭐⭐ ALTA |
| **Fase 3** - Contenitori | Alta | 6 giorni | ⭐⭐⭐ ALTA |
| **Fase 4** - Formato File | Media | 3 giorni | ⭐⭐⭐ ALTA |
| **Fase 5** - UI Dinamica | Alta | 9 giorni | ⭐⭐ MEDIA |
| **Fase 6** - Analisi Adattativa | Media | 5 giorni | ⭐ MEDIA |
| **Fase 7** - Template/Export | Media | 5 giorni | ⭐ MEDIA |
| **TOTALE** | - | **~32 giorni** | - |

---

## 🎯 PERCORSO CONSIGLIATO

### **Sprint 1 (1 settimana)**: Milestone 1 - Fondamenta
Focus su lingua e tipologie base. Alla fine dello sprint, l'utente può creare progetti con lingua e tipologia specifiche.

### **Sprint 2 (1.5 settimane)**: Milestone 2 - Contenitori Base
Implementa sistema contenitori e aggiunge Locations/Research. Formato file esteso.

### **Sprint 3 (2 settimane)**: Milestone 3 - UI Completa
UI dinamica, sidebar adattiva, viste dettaglio per tutti i contenitori.

### **Sprint 4 (1.5 settimane)**: Milestone 4 - Intelligenza
Analisi adattativa, template, export formattato.

---

## 🔄 DIPENDENZE TRA FEATURE

```
Fase 1 (Multi-Lingua)
    ↓
Fase 2 (Tipologie) ──→ Fase 6 (Analisi Adattativa)
    ↓                       ↓
Fase 3 (Contenitori) ──→ Fase 7 (Template)
    ↓
Fase 4 (Formato File)
    ↓
Fase 5 (UI Dinamica)
```

---

## 📝 NOTE IMPLEMENTATIVE

### **Testing Requirements**
- Test unitari per ogni nuovo model
- Test integrazione ProjectManager con contenitori
- Test UI per dialog e viste
- Test export PDF/DOCX
- Test migrazione progetti vecchi

### **Documentation Updates**
- README.md: Aggiornare feature list
- MANUAL_TESTING_GUIDE.md: Aggiungere test per nuove feature
- Creare USER_GUIDE.md con istruzioni multi-lingua/tipologia

### **Performance Considerations**
- Caricamento lazy dei contenitori (solo quelli usati)
- Cache per spaCy models caricati
- Ottimizzazione export PDF per progetti grandi

### **Internationalization (i18n)**
- Preparare infrastruttura per UI multilingua
- File di traduzione per UI (it, en, es, fr, de)
- Localizzazione messaggi errore

---

## 🚀 PROSSIMI PASSI

1. **Review del Piano**: Valutare se ci sono aggiunte/modifiche
2. **Setup Environment**: Installare dipendenze aggiuntive (reportlab per PDF)
3. **Iniziare Milestone 1**: Feature 1.1 - Infrastruttura Multi-Lingua
4. **Iterare**: Completare milestone incrementalmente

---

**Documento Creato**: 2025-10-27
**Ultima Modifica**: 2025-10-27
**Versione**: 1.0
**Autore**: The Novelist Development Team
