# RFP Document RAG System

A comprehensive CLI-based RAG (Retrieval-Augmented Generation) system for searching and retrieving RFP document templates with intelligent metadata extraction and semantic search capabilities.

## Features

- **Intelligent Document Processing**: Extract text and metadata from DOCX files
- **Dynamic RFP Type Categorization**: Automatically classify documents by type (EPC_Project, Supply_Contract, Service_Agreement, etc.)
- **Semantic Versioning**: Handle duplicate documents with smart version tracking
- **AI-Powered Summarization**: Generate comprehensive document summaries using OpenAI
- **Advanced Metadata Extraction**: Extract client names, service categories, equipment types, and more
- **Vector-Based Search**: Find similar documents using OpenAI embeddings and ChromaDB
- **Comprehensive Filtering**: Search by client, RFP type, service category, equipment type
- **CLI Interface**: Easy-to-use command-line interface with rich output formatting
- **API-Ready Design**: Modular architecture ready for future web/chatbot integration

## Installation

1. Clone or download the project
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Quick Start

### 1. Index Your Documents

Index all RFP documents in a directory:
```bash
python main.py index --directory ./RFP_Documents
```

### 2. Search for Templates

Search for similar RFP templates:
```bash
python main.py search --query "electrical infrastructure distribution station"
```

Search with filters:
```bash
python main.py search --query "transformer maintenance" --client CESC_Kolkata --rfp-type Service_Agreement
```

### 3. Get Document Details

View detailed information about a specific document:
```bash
python main.py get <document_id> --show-content
```

### 4. Find Similar Documents

Find documents similar to a specific document:
```bash
python main.py similar <document_id> --limit 5
```

## CLI Commands

### Search Commands
- `search` - Search for similar RFP templates
- `similar` - Find documents similar to a specific document
- `recommend` - Get recommendations based on document characteristics

### Document Management
- `add` - Add a single document or batch process directory
- `index` - Index all documents in a directory
- `get` - Retrieve detailed information about a specific document

### System Commands
- `status` - Show system statistics and health
- `reset` - Reset the entire database (with confirmation)

## Search Options

The `search` command supports multiple filtering options:

```bash
python main.py search \
  --query "your search query" \
  --client CESC_Kolkata \
  --rfp-type EPC_Project \
  --service Electrical_Infrastructure \
  --equipment PTR \
  --limit 10 \
  --verbose \
  --output table
```

### Available Filters

- **--client**: Filter by client name (CESC_Kolkata, CPDL, MPSL, etc.)
- **--rfp-type**: Filter by RFP type (EPC_Project, Supply_Contract, Service_Agreement, etc.)
- **--service**: Filter by service category (Electrical_Infrastructure, Mechanical_Boiler, etc.)
- **--equipment**: Filter by equipment type (PTR, DTR, HT_LT_Cable, etc.)

### RFP Types

The system automatically categorizes documents into these RFP types:
- **EPC_Project**: Engineering, Procurement, Construction projects
- **Supply_Contract**: Equipment and material supply contracts
- **Service_Agreement**: Maintenance and service agreements
- **Safety_Specification**: Safety requirements and specifications
- **Maintenance_Contract**: Maintenance and overhaul contracts
- **Survey_Contract**: Survey and inspection contracts
- **Metering_Project**: Energy metering and billing projects
- **General_Terms**: General conditions and terms

## Metadata Schema

Each document is enriched with comprehensive metadata:

```json
{
  "document_id": "unique_identifier",
  "filename": "original_filename.docx",
  "document_type": "EPC|Supply|Service|Annexure",
  "client_name": "CESC_Kolkata|CPDL|MPSL|CESC_Rajasthan|CDPL",
  "service_category": "Electrical_Infrastructure|Mechanical_Boiler|Survey_Inspection|...",
  "specific_service": "detailed_service_description",
  "equipment_type": "PTR|DTR|HT_LT_Cable|Energy_Meters|GIS|Boiler|Tower",
  "rfp_type": "EPC_Project|Supply_Contract|Service_Agreement|Safety_Specification|...",
  "rfp_subtype": "AI-generated subtype based on content",
  "document_version": "v1.0|v1.1|v2.0",
  "content_summary": "AI-generated comprehensive summary",
  "key_terms": ["relevant", "keywords"],
  "document_purpose": "template|contract|specification|requirement",
  "complexity": "Simple|Medium|Complex|Very_Complex",
  "word_count": "integer",
  "confidence_score": "AI_confidence_in_metadata_extraction"
}
```

## Architecture

The system is built with a modular architecture:

```
rfp_rag_system/
├── main.py                 # CLI entry point
├── config/                 # Configuration and schemas
├── core/                   # Document processing and metadata extraction
├── rag_engine/             # Vector search and embeddings
├── cli/                    # Command-line interface
├── utils/                  # Utility functions
└── tests/                  # Testing framework
```

### Core Components

1. **DocumentProcessor**: Extract text from DOCX files
2. **MetadataExtractor**: Extract and classify metadata
3. **VersionManager**: Handle semantic versioning for duplicates
4. **DocumentSummarizer**: Generate AI-powered summaries
5. **EmbeddingEngine**: Create vector embeddings using OpenAI
6. **VectorStore**: ChromaDB operations for vector storage
7. **SearchEngine**: RAG search and retrieval logic

## API Integration

The system is designed for easy API integration. The core `RAGService` class can be used in web applications or chatbots:

```python
from rag_engine.search_engine import SearchEngine

# Initialize service
search_engine = SearchEngine()

# Search for templates
results = search_engine.search_templates(
    query="electrical infrastructure",
    filters={"client_name": "CESC_Kolkata"},
    limit=5
)

# Get recommendations
recommendations = search_engine.get_document_recommendations(
    document_id="doc_id_here",
    limit=3
)
```

## Performance Features

- **Batch Processing**: Efficient processing of multiple documents
- **Embedding Caching**: Cache embeddings to reduce API calls
- **Hybrid Search**: Combine semantic and keyword-based search
- **Similarity Thresholds**: Configurable minimum similarity scores
- **Optimized Vector Storage**: ChromaDB with HNSW indexing

## Error Handling

The system includes comprehensive error handling:
- Graceful fallbacks for AI service failures
- Retry logic for API calls
- Validation for document formats
- Detailed error messages and logging

## Future Enhancements

- Web interface for document management
- REST API for external integration
- Support for additional document formats (PDF, etc.)
- Advanced analytics and reporting
- Document comparison and diff features
- Multi-language support

## Requirements

- Python 3.8+
- OpenAI API key
- DOCX files for processing

## Dependencies

See `requirements.txt` for the complete list of dependencies including:
- OpenAI (embeddings and chat completions)
- ChromaDB (vector database)
- python-docx (document processing)
- Click (CLI interface)
- Rich (output formatting)

## License

This project is part of the RFP Generator POC system.