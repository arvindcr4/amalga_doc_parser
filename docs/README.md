# Amalga Doc Parser Documentation

## Overview

The Amalga Doc Parser is a specialized Python library designed for parsing and structuring healthcare platform analysis documents. It provides a robust framework for extracting structured information from markdown-formatted healthcare documents, including sections, tables, and references.

## Key Components

The package consists of two main modules:

1. **Models** (`models.py`): Defines the core data structures:
   - `Document`: The top-level container for a parsed document
   - `Section`: Represents document sections with hierarchical structure
   - `Table`: Represents tabular data with headers and rows
   - `Reference`: Stores document references/citations

2. **Parser** (`parser.py`): Contains functionality to parse markdown documents:
   - `DocumentParser`: The main parser class that processes markdown files
   - `parse_document`: Helper function for simple document parsing

## Installation

```bash
pip install amalga_doc_parser
```

## Basic Usage

```python
from amalga_doc_parser import parse_document

# Parse a document
doc = parse_document("healthcare_platform_analysis.md")

# Access document structure
print(f"Document title: {doc.title}")
print(f"Number of sections: {len(doc.sections)}")

# Save parsed document to JSON
doc.save_to_file("parsed_document.json")
```

For more detailed usage examples, see the [Usage Guide](usage.md).

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

