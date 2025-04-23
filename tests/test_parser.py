"""
Tests for amalga_doc_parser module.

This module contains tests for the document parser functionality.
"""

import os
import unittest
import json
from pathlib import Path

from amalga_doc_parser import parse_document
from amalga_doc_parser.models import Document, Section, Table, Reference


class TestParser(unittest.TestCase):
    """Test case for the document parser."""

    def setUp(self):
        """Set up the test environment."""
        self.test_data_dir = Path(__file__).parent / "data"
        self.sample_file = self.test_data_dir / "sample.md"

    def test_parse_document(self):
        """Test basic document parsing."""
        # Parse the sample document
        doc = parse_document(str(self.sample_file))
        
        # Test basic document properties
        self.assertEqual(doc.title, "Sample Platform Analysis")
        self.assertGreater(len(doc.sections), 0)
        
        # Verify Executive Summary section exists
        exec_summary = None
        for section in doc.sections:
            if "Executive Summary" in section.name:
                exec_summary = section
                break
        
        self.assertIsNotNone(exec_summary, "Executive Summary section not found")
        self.assertGreater(len(exec_summary.content), 0)

    def test_document_serialization(self):
        """Test JSON serialization and deserialization."""
        # Create a simple document
        doc = Document(title="Test Document")
        doc.add_section(Section(name="Test Section", content="Test content"))
        doc.add_table(Table(id="T1", caption="Test Table", headers=["A", "B"], rows=[["1", "2"]]))
        doc.add_reference(Reference(id="1", text="Test Reference"))
        
        # Serialize to JSON
        json_str = doc.to_json()
        self.assertIsInstance(json_str, str)
        
        # Deserialize from JSON
        loaded_doc = Document.from_json(json_str)
        self.assertEqual(loaded_doc.title, "Test Document")
        self.assertEqual(len(loaded_doc.sections), 1)
        self.assertEqual(len(loaded_doc.tables), 1)
        self.assertEqual(len(loaded_doc.references), 1)

    def test_section_hierarchy(self):
        """Test section hierarchy parsing."""
        # Parse the sample document
        doc = parse_document(str(self.sample_file))
        
        # Find a section with subsections
        section_with_subsections = None
        for section in doc.sections:
            if section.subsections:
                section_with_subsections = section
                break
        
        self.assertIsNotNone(section_with_subsections, "No section with subsections found")
        self.assertGreater(len(section_with_subsections.subsections), 0)


if __name__ == "__main__":
    unittest.main()

"""
Unit tests for the Amalga Doc Parser document parser.
"""

import unittest
import os
import json
from pathlib import Path

# Add parent directory to path to enable imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.amalga_doc_parser.models import Document, Section, Table, Reference
from src.amalga_doc_parser.parser import DocumentParser, parse_document, ParserError


class TestDocumentParser(unittest.TestCase):
    """Test cases for the document parser functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_file = os.path.join(os.path.dirname(__file__), 'data', 'sample.md')
        self.parser = DocumentParser()
        
    def test_file_exists(self):
        """Test that the sample file exists."""
        self.assertTrue(os.path.exists(self.sample_file), 
                       f"Sample file not found: {self.sample_file}")
        
    def test_parse_document(self):
        """Test parsing a complete document."""
        document = parse_document(self.sample_file)
        
        # Basic document structure checks
        self.assertIsInstance(document, Document)
        self.assertEqual(document.title, "Sample")  # Based on filename
        
        # Check sections
        self.assertGreaterEqual(len(document.sections), 4, 
                               "Document should have at least 4 top-level sections")
        
        # Check section names
        section_names = [section.name for section in document.sections]
        self.assertIn("Executive Summary", section_names)
        self.assertIn("Platform Overview: Origins, Evolution, and Market Context", 
                     section_names)
        
        # Check tables
        self.assertGreaterEqual(len(document.tables), 1, 
                               "Document should have at least one table")
        
        # Check references
        self.assertGreaterEqual(len(document.references), 3, 
                               "Document should have at least 3 references")
        
    def test_section_hierarchy(self):
        """Test correct parsing of section hierarchy."""
        document = parse_document(self.sample_file)
        
        # Find Platform Overview section
        platform_section = None
        for section in document.sections:
            if "Platform Overview" in section.name:
                platform_section = section
                break
                
        self.assertIsNotNone(platform_section, 
                            "Platform Overview section should exist")
        
        # Check subsections
        self.assertGreaterEqual(len(platform_section.subsections), 2, 
                               "Platform Overview should have at least 2 subsections")
        
        # Check specific subsection
        subsection_names = [sub.name for sub in platform_section.subsections]
        self.assertIn("From Azyxxi to Microsoft Amalga: The Genesis", 
                     subsection_names)
        
    def test_table_parsing(self):
        """Test table extraction and parsing."""
        document = parse_document(self.sample_file)
        
        # Find the product family table
        product_table = None
        for table in document.tables:
            if "Product Family" in table.caption:
                product_table = table
                break
                
        self.assertIsNotNone(product_table, 
                            "Product Family table should be extracted")
        
        # Check table structure
        self.assertGreaterEqual(len(product_table.headers), 4, 
                               "Table should have at least 4 columns")
        self.assertGreaterEqual(len(product_table.rows), 2, 
                               "Table should have at least 2 data rows")
        
        # Check specific table content
        self.assertIn("Product Name", product_table.headers)
        
        # Check a specific cell value (flattened search)
        found_uis = False
        for row in product_table.rows:
            for cell in row:
                if "UIS" in cell:
                    found_uis = True
                    break
        self.assertTrue(found_uis, "Table should contain UIS reference")
        
    def test_reference_extraction(self):
        """Test extraction of numbered references."""
        document = parse_document(self.sample_file)
        
        # Check we have the expected references
        self.assertGreaterEqual(len(document.references), 3)
        
        # Build a dict of references by ID for easier checking
        refs_by_id = {ref.id: ref.text for ref in document.references}
        
        # Check specific references
        self.assertIn("1", refs_by_id)
        self.assertIn("Microsoft", refs_by_id["1"])  # First reference should mention Microsoft
        
    def test_nonexistent_file(self):
        """Test error handling for non-existent files."""
        with self.assertRaises(ParserError):
            parse_document("nonexistent_file.md")
            
    def test_document_to_json(self):
        """Test serialization of document to JSON."""
        document = parse_document(self.sample_file)
        json_str = document.to_json()
        
        # Verify it's valid JSON
        try:
            json_data = json.loads(json_str)
            self.assertIsInstance(json_data, dict)
            self.assertIn("title", json_data)
            self.assertIn("sections", json_data)
            self.assertIn("metadata", json_data)
        except json.JSONDecodeError:
            self.fail("Document to_json() did not produce valid JSON")
            
    def test_document_roundtrip(self):
        """Test document serialization and deserialization roundtrip."""
        original = parse_document(self.sample_file)
        json_str = original.to_json()
        
        # Deserialize back to document
        roundtrip = Document.from_json(json_str)
        
        # Check key properties match
        self.assertEqual(original.title, roundtrip.title)
        self.assertEqual(len(original.sections), len(roundtrip.sections))
        self.assertEqual(len(original.tables), len(roundtrip.tables))
        self.assertEqual(len(original.references), len(roundtrip.references))
            

if __name__ == '__main__':
    unittest.main()

