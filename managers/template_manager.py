"""
Template Manager - Pre-configured project structures for different project types
"""
from models.project_type import ProjectType
from models.manuscript_structure import ManuscriptStructureManager, Chapter, Scene
from models.character import Character
from typing import Dict, List
import uuid


class TemplateManager:
    """
    Manages project templates for different writing project types.
    Provides pre-configured structures to help users get started quickly.
    """

    def __init__(self):
        """Initialize the template manager"""
        pass

    def get_template(self, project_type: ProjectType, language: str = 'it') -> Dict:
        """
        Get a pre-configured template for the specified project type.

        Args:
            project_type: Type of project
            language: Language for template content

        Returns:
            dict: Template data with chapters, scenes, characters
        """
        templates = {
            ProjectType.NOVEL: self._get_novel_template,
            ProjectType.SHORT_STORY: self._get_short_story_template,
            ProjectType.ARTICLE_MAGAZINE: self._get_article_magazine_template,
            ProjectType.ARTICLE_SOCIAL: self._get_article_social_template,
            ProjectType.POETRY: self._get_poetry_template,
            ProjectType.SCREENPLAY: self._get_screenplay_template,
            ProjectType.ESSAY: self._get_essay_template,
            ProjectType.RESEARCH_PAPER: self._get_research_paper_template
        }

        template_func = templates.get(project_type, self._get_default_template)
        return template_func(language)

    def _get_novel_template(self, language: str) -> Dict:
        """Template for novel projects"""
        labels = self._get_labels(language)

        chapters = []
        scenes = []

        # Chapter 1
        ch1_id = str(uuid.uuid4())
        scene1_id = str(uuid.uuid4())

        chapters.append({
            'id': ch1_id,
            'title': labels['novel_ch1_title'],
            'description': labels['novel_ch1_desc'],
            'order': 0,
            'scenes': [scene1_id]
        })

        scenes.append({
            'id': scene1_id,
            'title': labels['novel_scene1_title'],
            'content': labels['novel_scene1_content'],
            'order': 0,
            'chapter_id': ch1_id
        })

        # Chapter 2
        ch2_id = str(uuid.uuid4())
        scene2_id = str(uuid.uuid4())

        chapters.append({
            'id': ch2_id,
            'title': labels['novel_ch2_title'],
            'description': labels['novel_ch2_desc'],
            'order': 1,
            'scenes': [scene2_id]
        })

        scenes.append({
            'id': scene2_id,
            'title': labels['novel_scene2_title'],
            'content': labels['novel_scene2_content'],
            'order': 0,
            'chapter_id': ch2_id
        })

        # Chapter 3
        ch3_id = str(uuid.uuid4())
        scene3_id = str(uuid.uuid4())

        chapters.append({
            'id': ch3_id,
            'title': labels['novel_ch3_title'],
            'description': labels['novel_ch3_desc'],
            'order': 2,
            'scenes': [scene3_id]
        })

        scenes.append({
            'id': scene3_id,
            'title': labels['novel_scene3_title'],
            'content': labels['novel_scene3_content'],
            'order': 0,
            'chapter_id': ch3_id
        })

        # Characters
        characters = [
            {
                'name': labels['novel_char1_name'],
                'role': labels['novel_char1_role'],
                'description': labels['novel_char1_desc'],
                'age': '',
                'appearance': '',
                'personality': labels['novel_char1_personality'],
                'background': '',
                'goals': labels['novel_char1_goals'],
                'relationships': ''
            },
            {
                'name': labels['novel_char2_name'],
                'role': labels['novel_char2_role'],
                'description': labels['novel_char2_desc'],
                'age': '',
                'appearance': '',
                'personality': labels['novel_char2_personality'],
                'background': '',
                'goals': labels['novel_char2_goals'],
                'relationships': ''
            }
        ]

        return {
            'chapters': chapters,
            'scenes': scenes,
            'characters': characters,
            'has_chapters': True
        }

    def _get_short_story_template(self, language: str) -> Dict:
        """Template for short story projects"""
        labels = self._get_labels(language)

        scene_id = str(uuid.uuid4())
        scenes = [{
            'id': scene_id,
            'title': labels['short_story_title'],
            'content': labels['short_story_content'],
            'order': 0,
            'chapter_id': None
        }]

        characters = [{
            'name': labels['short_story_char_name'],
            'role': labels['short_story_char_role'],
            'description': labels['short_story_char_desc'],
            'age': '',
            'appearance': '',
            'personality': '',
            'background': '',
            'goals': '',
            'relationships': ''
        }]

        return {
            'chapters': [],
            'scenes': scenes,
            'characters': characters,
            'has_chapters': False
        }

    def _get_article_magazine_template(self, language: str) -> Dict:
        """Template for magazine article projects"""
        labels = self._get_labels(language)

        scene_id = str(uuid.uuid4())
        scenes = [{
            'id': scene_id,
            'title': labels['article_title'],
            'content': labels['article_content'],
            'order': 0,
            'chapter_id': None
        }]

        return {
            'chapters': [],
            'scenes': scenes,
            'characters': [],
            'has_chapters': False
        }

    def _get_article_social_template(self, language: str) -> Dict:
        """Template for social media post projects"""
        labels = self._get_labels(language)

        scene_id = str(uuid.uuid4())
        scenes = [{
            'id': scene_id,
            'title': labels['social_title'],
            'content': labels['social_content'],
            'order': 0,
            'chapter_id': None
        }]

        return {
            'chapters': [],
            'scenes': scenes,
            'characters': [],
            'has_chapters': False
        }

    def _get_poetry_template(self, language: str) -> Dict:
        """Template for poetry projects"""
        labels = self._get_labels(language)

        scene_id = str(uuid.uuid4())
        scenes = [{
            'id': scene_id,
            'title': labels['poetry_title'],
            'content': labels['poetry_content'],
            'order': 0,
            'chapter_id': None
        }]

        return {
            'chapters': [],
            'scenes': scenes,
            'characters': [],
            'has_chapters': False
        }

    def _get_screenplay_template(self, language: str) -> Dict:
        """Template for screenplay projects"""
        labels = self._get_labels(language)

        chapters = []
        scenes = []

        # Act I
        act1_id = str(uuid.uuid4())
        scene1_id = str(uuid.uuid4())

        chapters.append({
            'id': act1_id,
            'title': labels['screenplay_act1_title'],
            'description': labels['screenplay_act1_desc'],
            'order': 0,
            'scenes': [scene1_id]
        })

        scenes.append({
            'id': scene1_id,
            'title': labels['screenplay_scene1_title'],
            'content': labels['screenplay_scene1_content'],
            'order': 0,
            'chapter_id': act1_id
        })

        # Act II
        act2_id = str(uuid.uuid4())
        scene2_id = str(uuid.uuid4())

        chapters.append({
            'id': act2_id,
            'title': labels['screenplay_act2_title'],
            'description': labels['screenplay_act2_desc'],
            'order': 1,
            'scenes': [scene2_id]
        })

        scenes.append({
            'id': scene2_id,
            'title': labels['screenplay_scene2_title'],
            'content': labels['screenplay_scene2_content'],
            'order': 0,
            'chapter_id': act2_id
        })

        characters = [{
            'name': labels['screenplay_char_name'],
            'role': labels['screenplay_char_role'],
            'description': labels['screenplay_char_desc'],
            'age': '',
            'appearance': '',
            'personality': '',
            'background': '',
            'goals': '',
            'relationships': ''
        }]

        return {
            'chapters': chapters,
            'scenes': scenes,
            'characters': characters,
            'has_chapters': True
        }

    def _get_essay_template(self, language: str) -> Dict:
        """Template for essay projects"""
        labels = self._get_labels(language)

        scene_id = str(uuid.uuid4())
        scenes = [{
            'id': scene_id,
            'title': labels['essay_title'],
            'content': labels['essay_content'],
            'order': 0,
            'chapter_id': None
        }]

        return {
            'chapters': [],
            'scenes': scenes,
            'characters': [],
            'has_chapters': False
        }

    def _get_research_paper_template(self, language: str) -> Dict:
        """Template for research paper projects"""
        labels = self._get_labels(language)

        chapters = []
        scenes = []

        # Abstract
        ch1_id = str(uuid.uuid4())
        scene1_id = str(uuid.uuid4())

        chapters.append({
            'id': ch1_id,
            'title': labels['research_ch1_title'],
            'description': labels['research_ch1_desc'],
            'order': 0,
            'scenes': [scene1_id]
        })

        scenes.append({
            'id': scene1_id,
            'title': labels['research_ch1_title'],
            'content': labels['research_ch1_content'],
            'order': 0,
            'chapter_id': ch1_id
        })

        # Introduction
        ch2_id = str(uuid.uuid4())
        scene2_id = str(uuid.uuid4())

        chapters.append({
            'id': ch2_id,
            'title': labels['research_ch2_title'],
            'description': labels['research_ch2_desc'],
            'order': 1,
            'scenes': [scene2_id]
        })

        scenes.append({
            'id': scene2_id,
            'title': labels['research_ch2_title'],
            'content': labels['research_ch2_content'],
            'order': 0,
            'chapter_id': ch2_id
        })

        # Methods
        ch3_id = str(uuid.uuid4())
        scene3_id = str(uuid.uuid4())

        chapters.append({
            'id': ch3_id,
            'title': labels['research_ch3_title'],
            'description': labels['research_ch3_desc'],
            'order': 2,
            'scenes': [scene3_id]
        })

        scenes.append({
            'id': scene3_id,
            'title': labels['research_ch3_title'],
            'content': labels['research_ch3_content'],
            'order': 0,
            'chapter_id': ch3_id
        })

        return {
            'chapters': chapters,
            'scenes': scenes,
            'characters': [],
            'has_chapters': True
        }

    def _get_default_template(self, language: str) -> Dict:
        """Default empty template"""
        scene_id = str(uuid.uuid4())
        scenes = [{
            'id': scene_id,
            'title': 'Scene 1',
            'content': '',
            'order': 0,
            'chapter_id': None
        }]

        return {
            'chapters': [],
            'scenes': scenes,
            'characters': [],
            'has_chapters': False
        }

    def _get_labels(self, language: str) -> Dict[str, str]:
        """Get localized labels for templates"""
        labels = {
            'it': {
                # Novel
                'novel_ch1_title': 'Capitolo 1 - Inizio',
                'novel_ch1_desc': 'Introduzione del protagonista e del contesto',
                'novel_scene1_title': 'Scena di apertura',
                'novel_scene1_content': 'Inizia qui la tua storia...',
                'novel_ch2_title': 'Capitolo 2 - Sviluppo',
                'novel_ch2_desc': 'Sviluppo della trama e dei conflitti',
                'novel_scene2_title': 'Complicazioni',
                'novel_scene2_content': 'La storia si complica...',
                'novel_ch3_title': 'Capitolo 3 - Climax',
                'novel_ch3_desc': 'Punto culminante della storia',
                'novel_scene3_title': 'Momento decisivo',
                'novel_scene3_content': 'Il momento più importante...',
                'novel_char1_name': 'Protagonista',
                'novel_char1_role': 'Protagonista',
                'novel_char1_desc': 'Personaggio principale della storia',
                'novel_char1_personality': 'Coraggioso, determinato',
                'novel_char1_goals': 'Raggiungere il suo obiettivo',
                'novel_char2_name': 'Antagonista',
                'novel_char2_role': 'Antagonista',
                'novel_char2_desc': 'Personaggio che si oppone al protagonista',
                'novel_char2_personality': 'Astuto, spietato',
                'novel_char2_goals': 'Fermare il protagonista',
                # Short Story
                'short_story_title': 'Il racconto',
                'short_story_content': 'Scrivi qui il tuo racconto breve...',
                'short_story_char_name': 'Personaggio principale',
                'short_story_char_role': 'Protagonista',
                'short_story_char_desc': 'Personaggio centrale del racconto',
                # Article
                'article_title': 'Articolo',
                'article_content': '# Titolo\n\n## Introduzione\nScrivi qui l\'introduzione...\n\n## Corpo dell\'articolo\nSviluppa i punti principali...\n\n## Conclusione\nConclusioni e call-to-action...',
                # Social
                'social_title': 'Post',
                'social_content': 'Scrivi qui il tuo post per i social media...\n\nRicorda: breve, coinvolgente, con call-to-action!',
                # Poetry
                'poetry_title': 'Poesia 1',
                'poetry_content': 'Scrivi qui la tua poesia...',
                # Screenplay
                'screenplay_act1_title': 'Atto I - Setup',
                'screenplay_act1_desc': 'Presentazione di personaggi e mondo',
                'screenplay_scene1_title': 'INT. LOCATION - GIORNO',
                'screenplay_scene1_content': 'PERSONAGGIO\nDialogo qui...',
                'screenplay_act2_title': 'Atto II - Confrontation',
                'screenplay_act2_desc': 'Sviluppo del conflitto',
                'screenplay_scene2_title': 'EST. LOCATION - NOTTE',
                'screenplay_scene2_content': 'PERSONAGGIO\nDialogo qui...',
                'screenplay_char_name': 'PROTAGONISTA',
                'screenplay_char_role': 'Protagonista',
                'screenplay_char_desc': 'Personaggio principale',
                # Essay
                'essay_title': 'Saggio',
                'essay_content': '# Tesi\nPresenta la tua tesi...\n\n# Argomenti\n## Primo argomento\nSviluppa qui...\n\n## Secondo argomento\nSviluppa qui...\n\n# Conclusione\nRiassumi e concludi...',
                # Research Paper
                'research_ch1_title': 'Abstract',
                'research_ch1_desc': 'Sintesi della ricerca',
                'research_ch1_content': 'Sintesi di obiettivi, metodi, risultati...',
                'research_ch2_title': 'Introduction',
                'research_ch2_desc': 'Contesto e obiettivi',
                'research_ch2_content': 'Background, research question, hypotheses...',
                'research_ch3_title': 'Methods',
                'research_ch3_desc': 'Metodologia della ricerca',
                'research_ch3_content': 'Participants, procedure, materials, analysis...',
            },
            'en': {
                # Novel
                'novel_ch1_title': 'Chapter 1 - Beginning',
                'novel_ch1_desc': 'Introduction of protagonist and setting',
                'novel_scene1_title': 'Opening scene',
                'novel_scene1_content': 'Start your story here...',
                'novel_ch2_title': 'Chapter 2 - Development',
                'novel_ch2_desc': 'Plot and conflict development',
                'novel_scene2_title': 'Complications',
                'novel_scene2_content': 'The story gets complicated...',
                'novel_ch3_title': 'Chapter 3 - Climax',
                'novel_ch3_desc': 'Story climax',
                'novel_scene3_title': 'Decisive moment',
                'novel_scene3_content': 'The most important moment...',
                'novel_char1_name': 'Protagonist',
                'novel_char1_role': 'Protagonist',
                'novel_char1_desc': 'Main character of the story',
                'novel_char1_personality': 'Brave, determined',
                'novel_char1_goals': 'Achieve their goal',
                'novel_char2_name': 'Antagonist',
                'novel_char2_role': 'Antagonist',
                'novel_char2_desc': 'Character opposing the protagonist',
                'novel_char2_personality': 'Cunning, ruthless',
                'novel_char2_goals': 'Stop the protagonist',
                # Short Story
                'short_story_title': 'The Story',
                'short_story_content': 'Write your short story here...',
                'short_story_char_name': 'Main Character',
                'short_story_char_role': 'Protagonist',
                'short_story_char_desc': 'Central character of the story',
                # Article
                'article_title': 'Article',
                'article_content': '# Title\n\n## Introduction\nWrite the introduction here...\n\n## Main Body\nDevelop main points...\n\n## Conclusion\nConclusions and call-to-action...',
                # Social
                'social_title': 'Post',
                'social_content': 'Write your social media post here...\n\nRemember: short, engaging, with call-to-action!',
                # Poetry
                'poetry_title': 'Poem 1',
                'poetry_content': 'Write your poem here...',
                # Screenplay
                'screenplay_act1_title': 'Act I - Setup',
                'screenplay_act1_desc': 'Introduction of characters and world',
                'screenplay_scene1_title': 'INT. LOCATION - DAY',
                'screenplay_scene1_content': 'CHARACTER\nDialogue here...',
                'screenplay_act2_title': 'Act II - Confrontation',
                'screenplay_act2_desc': 'Conflict development',
                'screenplay_scene2_title': 'EXT. LOCATION - NIGHT',
                'screenplay_scene2_content': 'CHARACTER\nDialogue here...',
                'screenplay_char_name': 'PROTAGONIST',
                'screenplay_char_role': 'Protagonist',
                'screenplay_char_desc': 'Main character',
                # Essay
                'essay_title': 'Essay',
                'essay_content': '# Thesis\nPresent your thesis...\n\n# Arguments\n## First argument\nDevelop here...\n\n## Second argument\nDevelop here...\n\n# Conclusion\nSummarize and conclude...',
                # Research Paper
                'research_ch1_title': 'Abstract',
                'research_ch1_desc': 'Research summary',
                'research_ch1_content': 'Summary of objectives, methods, results...',
                'research_ch2_title': 'Introduction',
                'research_ch2_desc': 'Context and objectives',
                'research_ch2_content': 'Background, research question, hypotheses...',
                'research_ch3_title': 'Methods',
                'research_ch3_desc': 'Research methodology',
                'research_ch3_content': 'Participants, procedure, materials, analysis...',
            }
        }

        return labels.get(language, labels['en'])
