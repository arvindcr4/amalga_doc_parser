"""
Data models for the Amalga Doc Parser.

This module defines the core data structures used to represent healthcare platform
analysis documents, including documents, sections, tables, and references.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import json
from datetime import datetime


@dataclass
class Reference:
    """A reference or citation in the document."""
    id: str
    text: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert the reference to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "text": self.text
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Reference':
        """Create a Reference instance from a dictionary."""
        return cls(
            id=data["id"],
            text=data["text"]
        )


@dataclass
class Table:
    """A table in the document."""
    id: str
    caption: str
    headers: List[str] = field(default_factory=list)
    rows: List[List[str]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the table to a dictionary for JSON serialization."""
        return {
            "id": self.id,
            "caption": self.caption,
            "headers": self.headers,
            "rows": self.rows
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Table':
        """Create a Table instance from a dictionary."""
        return cls(
            id=data["id"],
            caption=data["caption"],
            headers=data.get("headers", []),
            rows=data.get("rows", [])
        )


@dataclass
class Section:
    """A section or subsection in the document."""
    name: str
    raw_name: str = ""  # Store the original name with numbers
    content: str = ""
    level: int = 1
    subsections: List['Section'] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the section to a dictionary for JSON serialization."""
        return {
            "name": self.name,
            "raw_name": self.raw_name,
            "content": self.content,
            "level": self.level,
            "subsections": [subsec.to_dict() for subsec in self.subsections]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Section':
        """Create a Section instance from a dictionary."""
        section = cls(
            name=data["name"],
            raw_name=data.get("raw_name", ""),
            content=data["content"],
            level=data["level"]
        )
        section.subsections = [
            Section.from_dict(subsec) for subsec in data.get("subsections", [])
        ]
        return section

    def add_subsection(self, subsection: 'Section') -> None:
        """Add a subsection to this section."""
        self.subsections.append(subsection)


@dataclass
class Document:
    """The top-level document representation."""
    title: str
    sections: List[Section] = field(default_factory=list)
    tables: List[Table] = field(default_factory=list)
    references: List[Reference] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize metadata with creation timestamp if not present."""
        if "created_at" not in self.metadata:
            self.metadata["created_at"] = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the document to a dictionary for JSON serialization."""
        return {
            "title": self.title,
            "sections": [section.to_dict() for section in self.sections],
            "metadata": {
                **self.metadata,
                "tables": [table.to_dict() for table in self.tables],
                "references": [ref.to_dict() for ref in self.references]
            }
        }

    def to_json(self, indent: int = 2) -> str:
        """Serialize the document to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create a Document instance from a dictionary."""
        # Extract tables and references from metadata
        metadata = data.get("metadata", {})
        tables_data = metadata.pop("tables", []) if isinstance(metadata, dict) else []
        refs_data = metadata.pop("references", []) if isinstance(metadata, dict) else []
        
        document = cls(
            title=data["title"],
            sections=[Section.from_dict(section) for section in data.get("sections", [])],
            metadata=metadata if isinstance(metadata, dict) else {}
        )
        
        # Add tables and references
        document.tables = [Table.from_dict(table) for table in tables_data]
        document.references = [Reference.from_dict(ref) for ref in refs_data]
        
        return document

    @classmethod
    def from_json(cls, json_str: str) -> 'Document':
        """Create a Document instance from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def save_to_file(self, filepath: str) -> None:
        """Save the document to a JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.to_json())

    @classmethod
    def load_from_file(cls, filepath: str) -> 'Document':
        """Load a document from a JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            return cls.from_json(f.read())

    def add_section(self, section: Section) -> None:
        """Add a top-level section to the document."""
        self.sections.append(section)

    def add_table(self, table: Table) -> None:
        """Add a table to the document."""
        self.tables.append(table)

    def add_reference(self, reference: Reference) -> None:
        """Add a reference to the document."""
        self.references.append(reference)

