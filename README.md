# Amalga Doc Parser

A Python library for parsing and managing healthcare platform analysis documents.

## Description

Amalga Doc Parser provides tools to parse, analyze, and manage structured healthcare platform analysis documents. It extracts sections, tables, and references from markdown documents into structured data models that can be easily processed, analyzed, and serialized.

## Installation

Install Amalga Doc Parser using pip:

```bash
pip install amalga_doc_parser
```

## Usage

Basic example of parsing a healthcare platform analysis document:

```python
from amalga_doc_parser import parse_document

# Parse a document
doc = parse_document("path/to/healthcare_platform_analysis.md")

# Access document content
print(f"Document title: {doc.title}")
print(f"Number of sections: {len(doc.sections)}")
print(f"Number of tables: {len(doc.tables)}")

# Extract key sections
for section in doc.sections:
    print(f"Section: {section.name}")
    
# Save document to JSON
doc.save_to_file("parsed_document.json")

# Load document from JSON
from amalga_doc_parser.models import Document
loaded_doc = Document.load_from_file("parsed_document.json")
```

## Features

- **Structured Document Parsing**: Extract sections, subsections, tables, and references from markdown documents
- **Hierarchical Document Model**: Represent healthcare platform analysis documents with proper section hierarchy
- **Table Extraction**: Automatically parse and structure tables from markdown format
- **Reference Management**: Extract and link document references
- **JSON Serialization**: Save and load parsed documents to/from JSON format
- **Content Analysis**: Easily navigate and analyze document content with a structured object model

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

