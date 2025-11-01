"""
Context Builder - Costruisce contesti AI gerarchici per conversazioni

Implementa il pattern Template Method per costruire system prompts dinamici
che includono:
- Info base progetto
- Story context (Milestone 1)
- Info entità specifica (personaggio, location, etc.)
- Relazioni con altre entità
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class ContextBuilder(ABC):
    """
    Base class per costruire contesti AI gerarchici.

    Pattern: Template Method
    - build_full_context() orchestra i vari livelli
    - Sottoclassi implementano _build_entity_context() e _build_relations_context()
    """

    def __init__(self, project):
        """
        Args:
            project: Project model instance
        """
        self.project = project

    def build_full_context(self, entity: Any, **kwargs) -> str:
        """
        Costruisce il contesto completo gerarchico.

        Args:
            entity: Entità specifica (Character, Location, etc.)
            **kwargs: Opzioni aggiuntive (include_relations, max_related, etc.)

        Returns:
            str: System prompt formattato Markdown
        """
        sections = []

        # LIVELLO 1: Info base progetto
        sections.append(self._build_project_base_context())

        # LIVELLO 2: Story Context (dai campi Milestone 1!)
        story_context = self._build_story_context()
        if story_context:
            sections.append(story_context)

        # LIVELLO 3: Contesto specifico entità (es: personaggio)
        sections.append(self._build_entity_context(entity))

        # LIVELLO 4: Relazioni (opzionale)
        if kwargs.get('include_relations', True):
            relations = self._build_relations_context(entity, **kwargs)
            if relations:
                sections.append(relations)

        return "\n\n".join(filter(None, sections))

    def _build_project_base_context(self) -> str:
        """Costruisce il contesto base del progetto"""
        return f"""# PROGETTO

**Titolo**: {self.project.title}
**Autore**: {self.project.author}
**Genere**: {self.project.genre or 'Non specificato'}
**Tipo**: {self.project.project_type.value}
**Lingua**: {self.project.language}
"""

    def _build_story_context(self) -> Optional[str]:
        """
        Costruisce il contesto narrativo.

        🆕 MILESTONE 2: Se AI Writing Guide è abilitato, usa quello invece dei Story Context fields!

        PRIORITÀ:
        1. AI Writing Guide (se enabled) - Milestone 2
        2. Story Context fields (fallback) - Milestone 1

        Returns:
            str: Contesto narrativo formattato, o None se non ci sono dati
        """
        # 🆕 PRIORITÀ 1: AI Writing Guide (Milestone 2)
        if self.project.ai_writing_guide_enabled and self.project.ai_writing_guide_content:
            # Restituisci il Writing Guide custom direttamente
            # L'utente ha pieno controllo sul formato Markdown
            return self.project.ai_writing_guide_content

        # PRIORITÀ 2: Story Context fields (Milestone 1 - fallback)
        # Se non ci sono dati story context, skip questa sezione
        if not any([
            self.project.synopsis,
            self.project.setting_time_period,
            self.project.setting_location,
            self.project.narrative_tone,
            self.project.narrative_pov,
            self.project.themes,
            self.project.target_audience,
            self.project.story_notes
        ]):
            return None

        parts = ["# CONTESTO NARRATIVO"]

        # Synopsis
        if self.project.synopsis:
            parts.append(f"**Sinossi**: {self.project.synopsis}")

        # Ambientazione
        if self.project.setting_time_period or self.project.setting_location:
            parts.append("\n**Ambientazione**:")
            if self.project.setting_time_period:
                parts.append(f"- Periodo: {self.project.setting_time_period}")
            if self.project.setting_location:
                parts.append(f"- Luogo: {self.project.setting_location}")

        # Tono narrativo
        if self.project.narrative_tone:
            parts.append(f"\n**Tono**: {self.project.narrative_tone}")

        # Punto di vista
        if self.project.narrative_pov:
            # Traduci codice in testo leggibile
            pov_labels = {
                'first_person': 'Prima persona',
                'third_limited': 'Terza persona limitata',
                'third_omniscient': 'Terza persona onnisciente',
                'multiple': 'POV multipli'
            }
            pov_text = pov_labels.get(self.project.narrative_pov, self.project.narrative_pov)
            parts.append(f"**Punto di vista**: {pov_text}")

        # Temi
        if self.project.themes:
            parts.append(f"\n**Temi**: {', '.join(self.project.themes)}")

        # Pubblico target
        if self.project.target_audience:
            parts.append(f"**Pubblico target**: {self.project.target_audience}")

        # Note aggiuntive
        if self.project.story_notes:
            parts.append(f"\n**Note aggiuntive**:\n{self.project.story_notes}")

        return "\n".join(parts)

    @abstractmethod
    def _build_entity_context(self, entity: Any) -> str:
        """
        Costruisce il contesto specifico dell'entità.

        Da implementare nelle sottoclassi (CharacterContextBuilder, LocationContextBuilder, etc.)

        Args:
            entity: L'entità specifica (Character, Location, etc.)

        Returns:
            str: Contesto formattato dell'entità
        """
        pass

    @abstractmethod
    def _build_relations_context(self, entity: Any, **kwargs) -> str:
        """
        Costruisce il contesto delle relazioni con altre entità.

        Da implementare nelle sottoclassi.

        Args:
            entity: L'entità di riferimento
            **kwargs: Opzioni (max_related, etc.)

        Returns:
            str: Contesto relazionale formattato, o stringa vuota se non applicabile
        """
        pass


class CharacterContextBuilder(ContextBuilder):
    """
    Context builder specializzato per conversazioni sui personaggi.

    Aggiunge:
    - Informazioni specifiche del personaggio
    - Altri personaggi esistenti per coerenza narrativa
    """

    def __init__(self, project, character_manager):
        """
        Args:
            project: Project model instance
            character_manager: CharacterManager per accedere agli altri personaggi
        """
        super().__init__(project)
        self.character_manager = character_manager

    def _build_entity_context(self, character) -> str:
        """
        Costruisce il contesto specifico del personaggio.

        Args:
            character: Character model instance

        Returns:
            str: Contesto del personaggio formattato
        """
        # Messaggio obiettivo dinamico basato su genre e tone
        objective_parts = ["Aiutami a sviluppare in profondità questo personaggio"]

        if self.project.genre:
            objective_parts.append(f"coerente con il genere \"{self.project.genre}\"")

        if self.project.narrative_tone:
            objective_parts.append(f"e il tono \"{self.project.narrative_tone}\"")

        objective_parts.append("del progetto.")
        objective = ", ".join(objective_parts)

        return f"""# PERSONAGGIO IN SVILUPPO

**Nome**: {character.name}
**Descrizione attuale**:
{character.description if character.description else '[Da sviluppare]'}

**Obiettivo**: {objective}
"""

    def _build_relations_context(self, character, **kwargs) -> str:
        """
        Costruisce il contesto relazionale: altri personaggi nel romanzo.

        Args:
            character: Character di riferimento
            **kwargs: max_related_characters (default: 5)

        Returns:
            str: Lista altri personaggi, o stringa vuota se non ce ne sono
        """
        # Ottieni tutti i personaggi tranne quello corrente
        all_characters = self.character_manager.get_all_characters()
        other_characters = [c for c in all_characters if c.id != character.id]

        if not other_characters:
            return ""

        # Limita il numero di personaggi correlati
        max_chars = kwargs.get('max_related_characters', 5)
        other_characters = other_characters[:max_chars]

        context = "# ALTRI PERSONAGGI NEL ROMANZO\n\n"
        context += "Tieni conto di questi personaggi già esistenti per garantire coerenza:\n\n"

        for char in other_characters:
            # Preview della descrizione (primi 150 caratteri)
            if char.description:
                desc_preview = char.description[:150]
                if len(char.description) > 150:
                    desc_preview += "..."
            else:
                desc_preview = "[Nessuna descrizione]"

            context += f"- **{char.name}**: {desc_preview}\n"

        return context


class LocationContextBuilder(ContextBuilder):
    """Context builder per conversazioni sui luoghi"""

    def __init__(self, project, location_manager):
        super().__init__(project)
        self.location_manager = location_manager

    def _build_entity_context(self, location) -> str:
        """Costruisce il contesto specifico del luogo"""
        objective_parts = ["Aiutami a sviluppare in profondità questo luogo"]

        if self.project.genre:
            objective_parts.append(f"coerente con il genere \"{self.project.genre}\"")

        if self.project.narrative_tone:
            objective_parts.append(f"e il tono \"{self.project.narrative_tone}\"")

        objective_parts.append("del progetto.")
        objective = ", ".join(objective_parts)

        parts = [f"""# LUOGO IN SVILUPPO

**Nome**: {location.name}"""]

        if location.location_type:
            parts.append(f"**Tipo**: {location.location_type}")

        parts.append(f"""**Descrizione attuale**:
{location.description if location.description else '[Da sviluppare]'}

**Obiettivo**: {objective}""")

        return "\n".join(parts)

    def _build_relations_context(self, location, **kwargs) -> str:
        """Costruisce il contesto relazionale: altri luoghi nel romanzo"""
        all_locations = self.location_manager.get_all_locations()
        other_locations = [l for l in all_locations if l.id != location.id]

        if not other_locations:
            return ""

        max_locs = kwargs.get('max_related_locations', 5)
        other_locations = other_locations[:max_locs]

        context = "# ALTRI LUOGHI NEL ROMANZO\n\n"
        context += "Tieni conto di questi luoghi già esistenti per garantire coerenza:\n\n"

        for loc in other_locations:
            if loc.description:
                desc_preview = loc.description[:150]
                if len(loc.description) > 150:
                    desc_preview += "..."
            else:
                desc_preview = "[Nessuna descrizione]"

            type_info = f" ({loc.location_type})" if loc.location_type else ""
            context += f"- **{loc.name}{type_info}**: {desc_preview}\n"

        return context


class NoteContextBuilder(ContextBuilder):
    """Context builder per conversazioni sulle note"""

    def __init__(self, project):
        super().__init__(project)

    def _build_entity_context(self, note) -> str:
        """Costruisce il contesto specifico della nota"""
        parts = [f"""# NOTA IN SVILUPPO

**Titolo**: {note.title}
**Contenuto attuale**:
{note.content if note.content else '[Da sviluppare]'}"""]

        if note.tags:
            parts.append(f"\n**Tags**: {', '.join(note.tags)}")

        parts.append("\n**Obiettivo**: Aiutami a espandere, migliorare o chiarire questa nota.")

        return "\n".join(parts)

    def _build_relations_context(self, note, **kwargs) -> str:
        """Note non hanno relazioni complesse"""
        return ""


class SceneContextBuilder(ContextBuilder):
    """Context builder per conversazioni sulle scene"""

    def __init__(self, project, manuscript_manager=None):
        super().__init__(project)
        self.manuscript_manager = manuscript_manager

    def _build_entity_context(self, scene_data: dict) -> str:
        """
        Costruisce il contesto specifico della scena

        Args:
            scene_data: dict con chiavi: scene_title, chapter_title, content
        """
        objective_parts = ["Aiutami a sviluppare questa scena"]

        if self.project.genre:
            objective_parts.append(f"coerente con il genere \"{self.project.genre}\"")

        if self.project.narrative_tone:
            objective_parts.append(f"e il tono \"{self.project.narrative_tone}\"")

        objective_parts.append("del progetto.")
        objective = ", ".join(objective_parts)

        scene_title = scene_data.get('scene_title', 'Senza titolo')
        chapter_title = scene_data.get('chapter_title', 'Senza capitolo')
        content = scene_data.get('content', '')

        word_count = len(content.split()) if content else 0

        return f"""# SCENA IN SVILUPPO

**Capitolo**: {chapter_title}
**Scena**: {scene_title}
**Lunghezza attuale**: {word_count} parole

**Contenuto attuale**:
{content if content else '[Da scrivere]'}

**Obiettivo**: {objective}"""

    def _build_relations_context(self, scene_data: dict, **kwargs) -> str:
        """Contesto delle scene vicine (opzionale)"""
        # Potremmo aggiungere info sulle scene precedenti/successive
        return ""
