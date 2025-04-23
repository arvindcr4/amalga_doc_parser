# Amalga Doc Parser Usage Guide

This guide provides detailed examples of how to use the Amalga Doc Parser library for working with healthcare platform analysis documents.

## Basic Parsing

The simplest way to parse a document is using the `parse_document` function:

```python
from amalga_doc_parser import parse_document

# Parse a document with automatic title derivation from filename
doc = parse_document("path/to/healthcare_platform_analysis.md")

# Parse with a specified title
doc = parse_document("path/to/document.md", title="Healthcare Platform Analysis")
```

## Working with Sections

Once you have a parsed document, you can access its sections:

```python
# Access top-level sections
for section in doc.sections:
    print(f"Section: {section.name}")
    print(f"Content: {section.content[:100]}...")  # First 100 chars
    
    # Access subsections
    for subsection in section.subsections:
        print(f"  Subsection: {subsection.name}")
```

## Working with Tables

Tables are extracted automatically during parsing:

```python
# Access all tables in the document
for table in doc.tables:
    print(f"Table {table.id}: {table.caption}")
    print(f"Headers: {table.headers}")
    print(f"Number of rows: {len(table.rows)}")
    
    # Print first row
    if table.rows:
        print(f"First row: {table.rows[0]}")
```

## Working with References

References are also extracted during parsing:

```python
# Access all references
for ref in doc.references:
    print(f"[{ref.id}] {ref.text}")
```

## Document Serialization

You can save and load documents from JSON:

```python
# Save to JSON
doc.save_to_file("output.json")

# Load from JSON
from amalga_doc_parser.models import Document
loaded_doc = Document.load_from_file("output.json")
```

## Creating Documents Programmatically

You can also create document structures programmatically:

```python
from amalga_doc_parser.models import Document, Section, Table, Reference

# Create a new document
doc = Document(title="Healthcare Platform Analysis")

# Add sections
section = Section(name="Executive Summary", content="This is the executive summary content.")
doc.add_section(section)

# Add a table
table = Table(
    id="T1",
    caption="Key Metrics",
    headers=["Metric", "Value", "Change"],
    rows=[
        ["Users", "10,000", "+15%"],
        ["Response Time", "1.2s", "-10%"]
    ]
)
doc.add_table(table)

# Add a reference
ref = Reference(id="1", text="Smith J. et al. Healthcare Platform Best Practices, 2025")
doc.add_reference(ref)

# Save the document
doc.save_to_file("programmatic_doc.json")
```

## Error Handling

The parser provides error handling through the `ParserError` exception:

```python
from amalga_doc_parser import parse_document, ParserError

try:
    doc = parse_document("nonexistent_file.md")
except ParserError as e:
    print(f"Error parsing document: {e}")
```

