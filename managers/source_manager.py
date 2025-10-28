"""
Source Manager - Specialized manager for sources and citations
"""
from typing import List, Optional
from models.source import Source
from models.container_type import ContainerType
from managers.container_manager import ContainerManager
from utils.logger import logger


class SourceManager:
    """
    Specialized manager for handling sources and citations.

    Provides methods for organizing references, generating citations,
    and filtering sources by type.

    Attributes:
        container_manager: The underlying container manager
        container_type: Always SOURCES
    """

    def __init__(self, container_manager: ContainerManager):
        """
        Initialize the source manager.

        Args:
            container_manager: The container manager instance
        """
        self.container_manager = container_manager
        self.container_type = ContainerType.SOURCES

    def add_source(self, title: str, author: str = "", url: str = "",
                   source_type: str = "web", **kwargs) -> str:
        """
        Create a new source.

        Args:
            title: Source title
            author: Author name(s)
            url: URL for web sources
            source_type: Type of source (web, book, journal, etc.)
            **kwargs: Additional fields (publisher, doi, publication_date, etc.)

        Returns:
            str: ID of the created source
        """
        source = Source(
            title=title,
            author=author,
            url=url,
            source_type=source_type,
            citation=kwargs.get('citation', ''),
            notes=kwargs.get('notes', ''),
            access_date=kwargs.get('access_date', ''),
            publication_date=kwargs.get('publication_date', ''),
            publisher=kwargs.get('publisher', ''),
            doi=kwargs.get('doi', '')
        )

        source_id = self.container_manager.add_item(self.container_type, source)
        logger.info(f"Created source: {title} (ID: {source_id})")
        return source_id

    def add_source_object(self, source: Source) -> str:
        """
        Add a source object directly.

        Args:
            source: Source object to add

        Returns:
            str: ID of the created source
        """
        source_id = self.container_manager.add_item(self.container_type, source)
        logger.info(f"Created source: {source.title} (ID: {source_id})")
        return source_id

    def get_source(self, source_id: str) -> Optional[Source]:
        """
        Get a source by ID.

        Args:
            source_id: ID of the source

        Returns:
            Optional[Source]: The source if found, None otherwise
        """
        return self.container_manager.get_item(self.container_type, source_id)

    def get_all_sources(self) -> List[Source]:
        """
        Get all sources.

        Returns:
            List[Source]: List of all sources
        """
        return self.container_manager.get_all_items(self.container_type)

    def update_source(self, source: Source) -> bool:
        """
        Update an existing source.

        Args:
            source: Updated source object

        Returns:
            bool: True if update was successful
        """
        source.update_modified_date()
        return self.container_manager.update_item(
            self.container_type,
            source.id,
            source
        )

    def delete_source(self, source_id: str) -> bool:
        """
        Delete a source.

        Args:
            source_id: ID of the source to delete

        Returns:
            bool: True if deletion was successful
        """
        source = self.get_source(source_id)
        success = self.container_manager.delete_item(self.container_type, source_id)

        if success and source:
            logger.info(f"Deleted source: {source.title} (ID: {source_id})")

        return success

    def get_sources_by_type(self, source_type: str) -> List[Source]:
        """
        Get all sources of a specific type.

        Args:
            source_type: Type to filter by (web, book, journal, etc.)

        Returns:
            List[Source]: List of matching sources
        """
        all_sources = self.get_all_sources()
        return [source for source in all_sources if source.source_type == source_type]

    def get_web_sources(self) -> List[Source]:
        """
        Get all web sources.

        Returns:
            List[Source]: List of web sources
        """
        all_sources = self.get_all_sources()
        return [source for source in all_sources if source.is_web_source()]

    def get_academic_sources(self) -> List[Source]:
        """
        Get all academic sources (journals, books, papers with DOI).

        Returns:
            List[Source]: List of academic sources
        """
        all_sources = self.get_all_sources()
        return [source for source in all_sources if source.is_academic_source()]

    def get_sources_by_author(self, author: str) -> List[Source]:
        """
        Get all sources by a specific author.

        Args:
            author: Author name to search for (case-insensitive)

        Returns:
            List[Source]: List of matching sources
        """
        author_lower = author.lower()
        all_sources = self.get_all_sources()
        return [source for source in all_sources if author_lower in source.author.lower()]

    def search_sources(self, query: str) -> List[Source]:
        """
        Search sources by title, author, or URL.

        Args:
            query: Search query string

        Returns:
            List[Source]: List of matching sources
        """
        query = query.lower()
        all_sources = self.get_all_sources()

        return [
            source for source in all_sources
            if (query in source.title.lower() or
                query in source.author.lower() or
                query in source.url.lower())
        ]

    def get_all_source_types(self) -> List[str]:
        """
        Get a list of all unique source types used.

        Returns:
            List[str]: List of source type names
        """
        all_sources = self.get_all_sources()
        types = set(source.source_type for source in all_sources if source.source_type)
        return sorted(list(types))

    def generate_bibliography(self, citation_style: str = "apa") -> str:
        """
        Generate a formatted bibliography for all sources.

        Args:
            citation_style: Citation style ("apa" or "mla")

        Returns:
            str: Formatted bibliography
        """
        all_sources = self.get_all_sources()

        # Sort sources alphabetically by title
        sorted_sources = sorted(all_sources, key=lambda s: s.title.lower())

        bibliography_lines = []

        for source in sorted_sources:
            if citation_style.lower() == "apa":
                citation = source.generate_apa_citation()
            elif citation_style.lower() == "mla":
                citation = source.generate_mla_citation()
            else:
                # Use custom citation if provided, otherwise generate APA
                citation = source.citation if source.citation else source.generate_apa_citation()

            if citation:
                bibliography_lines.append(citation)

        return "\n\n".join(bibliography_lines)

    def export_sources_to_bibtex(self) -> str:
        """
        Export sources in BibTeX format (basic implementation).

        Returns:
            str: BibTeX formatted string
        """
        all_sources = self.get_all_sources()
        bibtex_entries = []

        for source in all_sources:
            # Determine BibTeX entry type
            if source.source_type == "book":
                entry_type = "book"
            elif source.source_type == "journal":
                entry_type = "article"
            elif source.source_type == "web":
                entry_type = "misc"
            else:
                entry_type = "misc"

            # Create citation key
            author_part = source.author.split(",")[0].replace(" ", "") if source.author else "Unknown"
            year = source.publication_date[:4] if source.publication_date else "n.d."
            citation_key = f"{author_part}{year}"

            # Build BibTeX entry
            entry = f"@{entry_type}{{{citation_key},\n"
            entry += f"  title = {{{source.title}}},\n"

            if source.author:
                entry += f"  author = {{{source.author}}},\n"
            if source.publication_date:
                entry += f"  year = {{{year}}},\n"
            if source.publisher:
                entry += f"  publisher = {{{source.publisher}}},\n"
            if source.url:
                entry += f"  url = {{{source.url}}},\n"
            if source.doi:
                entry += f"  doi = {{{source.doi}}},\n"

            entry += "}\n"
            bibtex_entries.append(entry)

        return "\n".join(bibtex_entries)

    def save(self) -> bool:
        """
        Save all sources to disk.

        Returns:
            bool: True if save was successful
        """
        return self.container_manager.save_container(self.container_type)
