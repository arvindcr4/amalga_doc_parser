"""
Parser module for the Amalga Doc Parser.

This module contains functionality to parse markdown documents and extract
structured information like sections, subsections, tables, and references.
"""

import re
import logging
from typing import List, Dict, Tuple, Optional, Iterator, Any
import os
from pathlib import Path

from .models import Document, Section, Table, Reference

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Regular expressions for parsing
SECTION_HEADER_PATTERN = re.compile(r"^(#{1,6})\s*((?:\d+\.)*\d*\.?\s*)?(.+)$")
TABLE_ROW_PATTERN = re.compile(r"^\|(.+)\|$")
TABLE_SEPARATOR_PATTERN = re.compile(r"^\|(\s*[-:]+[-:]\s*\|)+$")
TABLE_CAPTION_PATTERN = re.compile(r"^(?:Table|TABLE)\s+[\d\.]+:?\s+(.+)$")
REFERENCE_PATTERN = re.compile(r"^\[(\d+)\]\s+(.+)$")


class ParserError(Exception):
    """Exception raised for errors during document parsing."""
    pass


class DocumentParser:
    """Parser for healthcare platform analysis documents in markdown format."""

    def __init__(self):
        """Initialize the document parser."""
        # Initialize parser state
        self.document = None
        self.current_section = None
        self.section_stack = []
        self.table_buffer = []
        self.is_in_table = False
        self.table_count = 0
        self.seen_document_title = False
        
        # List of expected sections for validation
        self.expected_sections = [
            "Executive Summary",
            "Platform Overview",
            "Core Capabilities",
            "Data Management Architecture",
            "User Experience and Interface Design",
            "Technological Foundations",
            "Competitive Differentiation",
            "Lessons Learned"
        ]

    def parse_file(self, filepath: str, title: Optional[str] = None) -> Document:
        """Parse a markdown file into a Document."""
        if not os.path.exists(filepath):
            raise ParserError(f"File does not exist: {filepath}")
            
        # Initialize document with title from filename
        self.document = Document(title=title if title else Path(filepath).stem.replace("_", " ").title())
        
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                current_content = []
                
                for line in f:
                    line = line.rstrip()
                    
                    # Check for section header
                    header_match = SECTION_HEADER_PATTERN.match(line)
                    if header_match:
                        # Process any buffered content
                        if current_content and self.current_section:
                            self.current_section.content += "\n".join(current_content) + "\n"
                        current_content = []
                        
                        # Process the header
                        hashes, number_part, title_part = header_match.groups()
                        self._process_section_header(title_part, len(hashes), number_part)
                        continue
                    
                    # Check for table
                    if TABLE_ROW_PATTERN.match(line) or TABLE_SEPARATOR_PATTERN.match(line):
                        if current_content and not self.is_in_table:
                            if self.current_section:
                                self.current_section.content += "\n".join(current_content) + "\n"
                            current_content = []
                        self.table_buffer.append(line)
                        self.is_in_table = True
                    elif self.is_in_table and not line.strip():
                        self._process_table_buffer()
                    else:
                        # Check for reference
                        ref_match = REFERENCE_PATTERN.match(line)
                        if ref_match:
                            ref_id, ref_text = ref_match.groups()
                            self.document.add_reference(Reference(id=ref_id, text=ref_text))
                        
                        # Add to current content
                        if self.current_section:
                            current_content.append(line)
                
                # Process any remaining content
                if current_content and self.current_section:
                    self.current_section.content += "\n".join(current_content) + "\n"
                
                self._finalize_parsing()
                
            logger.info(f"Successfully parsed document: {self.document.title}")
            logger.info(f"Found {len(self.document.sections)} top-level sections, "
                       f"{len(self.document.tables)} tables, and "
                       f"{len(self.document.references)} references")
            
            return self.document
            
        except Exception as e:
            error_msg = f"Error parsing file {filepath}: {str(e)}"
            logger.error(error_msg)
            raise ParserError(error_msg) from e
            
    def _clean_section_name(self, section_name: str) -> str:
        """Remove numeric prefixes and extra whitespace from section names."""
        # Remove leading numbers (e.g., "1." or "2.1.") while preserving the rest
        cleaned = re.sub(r"^\d+\.(?:\d+\.)*\s*", "", section_name)
        return cleaned.strip()
        
    def _process_section_header(self, title_part: str, level: int, number_part: Optional[str] = None) -> None:
        """Process a section header and update document structure."""
        # Construct raw section name
        raw_name = f"{number_part} {title_part}" if number_part else title_part
        raw_name = raw_name.strip()
        
        logger.info(f"Processing section: {raw_name} (level {level})")
        
        # Skip first level 1 header for document title
        if level == 1 and not self.seen_document_title:
            self.seen_document_title = True
            return
            
        # Clean section name for matching
        cleaned_name = self._clean_section_name(raw_name)
        
        # Create section with both raw and cleaned names
        section = Section(
            name=cleaned_name,
            raw_name=raw_name,
            level=level
        )
        
        # Handle section hierarchy
        if level == 1:
            # Top-level section
            logger.info(f"Adding top-level section: {raw_name}")
            self.document.add_section(section)
            self.section_stack = [section]
        else:
            # Find appropriate parent by looking for the closest section with a lower level
            parent_found = False
            for i in range(len(self.section_stack) - 1, -1, -1):
                potential_parent = self.section_stack[i]
                if potential_parent.level < level:
                    # Found a valid parent
                    logger.info(f"Adding subsection {raw_name} to parent {potential_parent.raw_name}")
                    potential_parent.add_subsection(section)
                    # Update stack by removing anything after the parent and adding this section
                    self.section_stack = self.section_stack[:i+1] + [section]
                    parent_found = True
                    break
            
            if not parent_found:
                # No parent found, add to root
                logger.warning(f"No parent found for {raw_name}, adding to root")
                self.document.add_section(section)
                self.section_stack = [section]
        
        self.current_section = section
    
    def _process_table_buffer(self, caption: str = "") -> None:
        """Process the buffered table lines and add table to document."""
        if not self.table_buffer:
            self.is_in_table = False
            return
            
        # Parse table structure
        headers = []
        rows = []
        
        # If there's at least 2 rows, first row is likely headers
        if len(self.table_buffer) >= 2:
            # First row should be headers
            header_line = self.table_buffer[0]
            if "|" in header_line:
                headers = [cell.strip() for cell in header_line.strip("|").split("|")]
            
            # Skip the separator line (|---|---|)
            data_rows = self.table_buffer[2:] if len(self.table_buffer) > 2 else []
            
            for row_line in data_rows:
                if row_line and "|" in row_line:
                    row_data = [cell.strip() for cell in row_line.strip("|").split("|")]
                    rows.append(row_data)
        
        # Create and add the table
        self.table_count += 1
        table_id = f"T{self.table_count}"
        
        # Try to extract caption if not provided
        if not caption:
            caption = f"Table {self.table_count}"
            
            # Try to find caption in the current section's content
            if self.current_section:
                lines = self.current_section.content.splitlines()
                for line in lines[-5:]:  # Look at the last few lines
                    caption_match = TABLE_CAPTION_PATTERN.match(line)
                    if caption_match:
                        caption = line.strip()
                        break
        
        table = Table(
            id=table_id,
            caption=caption,
            headers=headers,
            rows=rows
        )
        self.document.add_table(table)
        
        logger.debug(f"Processed table: {table_id} - {caption}")
        
        # Reset table state
        self.table_buffer = []
        self.is_in_table = False
    
    def _finalize_parsing(self) -> None:
        """Finalize the parsing process, handling any incomplete structures."""
        # Handle any unfinished table
        if self.is_in_table and self.table_buffer:
            self._process_table_buffer()
            
        # Validate document structure
        self._validate_document()
    
    def _validate_document(self) -> None:
        """
        Validate the document structure after parsing.
        
        Raises:
            ParserError: If validation fails
        """
        # Check if we have any sections
        if not self.document.sections:
            logger.warning("Document has no sections")
            
        # Get cleaned section names
        found_sections = [section.name for section in self.document.sections]
        if self.document.sections and self.document.sections[0].subsections:
            found_sections.extend([sub.name for sub in self.document.sections[0].subsections])
            
        logger.info(f"Found sections: {found_sections}")
        missing_sections = []
        
        for expected in self.expected_sections:
            if not any(expected.lower() in section.lower() for section in found_sections):
                missing_sections.append(expected)
                
        if missing_sections:
            logger.warning(f"Missing expected sections: {', '.join(missing_sections)}")


def parse_document(filepath: str, title: Optional[str] = None) -> Document:
    """
    Parse a markdown document file into a structured Document object.
    
    Args:
        filepath: Path to the markdown file to parse
        title: Optional document title
        
    Returns:
        Document: The structured document object
        
    Raises:
        ParserError: If parsing fails
    """
    parser = DocumentParser()
    return parser.parse_file(filepath, title)
