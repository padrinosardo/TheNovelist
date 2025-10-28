"""
Source data model - For citations and references (articles, research papers)
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import uuid


@dataclass
class Source:
    """
    Represents a source, citation, or reference.

    Sources are used primarily in journalistic articles, essays, and research papers
    to track references, citations, and bibliographic information.

    Attributes:
        title: Source title
        author: Author name(s)
        url: URL for web sources
        citation: Formatted citation string (APA, MLA, Chicago, etc.)
        notes: Additional notes about the source
        id: Unique identifier
        created_date: ISO format creation timestamp
        modified_date: ISO format last modification timestamp
        source_type: Type of source (web, book, journal, interview, etc.)
        access_date: Date when web source was accessed (ISO format)
        publication_date: Publication date of the source
        publisher: Publisher name (for books, journals)
        doi: Digital Object Identifier (for academic papers)
    """
    title: str
    author: str = ""
    url: str = ""
    citation: str = ""
    notes: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_date: str = ""
    modified_date: str = ""

    # Metadata
    source_type: str = "web"  # web, book, journal, interview, video, podcast, etc.
    access_date: str = ""  # For web sources
    publication_date: str = ""  # Original publication date
    publisher: str = ""  # Publisher name
    doi: str = ""  # Digital Object Identifier

    def __post_init__(self):
        """Initialize timestamps if not provided"""
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        if not self.modified_date:
            self.modified_date = datetime.now().isoformat()
        # Set access_date to now if it's a web source and not provided
        if self.source_type == "web" and not self.access_date and self.url:
            self.access_date = datetime.now().isoformat()

    def update_modified_date(self):
        """Update the modified_date to current time"""
        self.modified_date = datetime.now().isoformat()

    def generate_apa_citation(self) -> str:
        """
        Generate a basic APA-style citation.

        Returns:
            str: APA-formatted citation
        """
        parts = []

        # Author (Year).
        if self.author:
            parts.append(f"{self.author}")
        if self.publication_date:
            year = self.publication_date[:4] if len(self.publication_date) >= 4 else self.publication_date
            parts.append(f"({year}).")

        # Title.
        if self.title:
            parts.append(f"{self.title}.")

        # Publisher or URL
        if self.source_type == "web" and self.url:
            parts.append(f"Retrieved from {self.url}")
        elif self.publisher:
            parts.append(f"{self.publisher}.")

        return " ".join(parts)

    def generate_mla_citation(self) -> str:
        """
        Generate a basic MLA-style citation.

        Returns:
            str: MLA-formatted citation
        """
        parts = []

        # Author.
        if self.author:
            parts.append(f"{self.author}.")

        # Title.
        if self.title:
            # Italicize title (represented with quotes here)
            parts.append(f'"{self.title}."')

        # Publisher, Publication Date
        if self.publisher:
            parts.append(f"{self.publisher},")
        if self.publication_date:
            parts.append(f"{self.publication_date}.")

        # URL
        if self.url:
            parts.append(f"{self.url}.")

        return " ".join(parts)

    def is_web_source(self) -> bool:
        """Check if this is a web source"""
        return self.source_type == "web" or bool(self.url)

    def is_academic_source(self) -> bool:
        """Check if this is an academic source"""
        return self.source_type in ["journal", "book"] or bool(self.doi)

    def to_dict(self) -> dict:
        """
        Convert source to dictionary for JSON serialization.

        Returns:
            dict: Source data as dictionary
        """
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'url': self.url,
            'citation': self.citation,
            'notes': self.notes,
            'created_date': self.created_date,
            'modified_date': self.modified_date,
            'source_type': self.source_type,
            'access_date': self.access_date,
            'publication_date': self.publication_date,
            'publisher': self.publisher,
            'doi': self.doi
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Source':
        """
        Create Source instance from dictionary.

        Args:
            data: Dictionary containing source data

        Returns:
            Source: New Source instance
        """
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            title=data.get('title', 'Untitled Source'),
            author=data.get('author', ''),
            url=data.get('url', ''),
            citation=data.get('citation', ''),
            notes=data.get('notes', ''),
            created_date=data.get('created_date', datetime.now().isoformat()),
            modified_date=data.get('modified_date', datetime.now().isoformat()),
            source_type=data.get('source_type', 'web'),
            access_date=data.get('access_date', ''),
            publication_date=data.get('publication_date', ''),
            publisher=data.get('publisher', ''),
            doi=data.get('doi', '')
        )
