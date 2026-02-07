import click
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.document_processor import DocumentProcessor
from core.metadata_extractor import MetadataExtractor
from core.version_manager import VersionManager
from core.summarizer import DocumentSummarizer
from rag_engine.embedding_engine import EmbeddingEngine
from rag_engine.vector_store import VectorStore
from rag_engine.search_engine import SearchEngine
from cli.output_formatter import OutputFormatter
from config.settings import settings

# Global components
formatter = OutputFormatter()


@click.group()
@click.option("--debug", is_flag=True, help="Enable debug logging")
def cli(debug):
    """RFP Document RAG System - Search and retrieve RFP templates"""
    if debug:
        import logging

        logging.basicConfig(level=logging.DEBUG)


@cli.command()
@click.option("--query", "-q", required=True, help="Search query for similar templates")
@click.option("--client", "-c", help="Filter by client name")
@click.option("--rfp-type", "-t", help="Filter by RFP type")
@click.option("--service", "-s", help="Filter by service category")
@click.option("--equipment", "-e", help="Filter by equipment type")
@click.option("--limit", "-l", default=5, help="Number of results to return")
@click.option("--verbose", "-v", is_flag=True, help="Detailed output")
@click.option(
    "--output",
    "-o",
    type=click.Choice(["table", "json"]),
    default="table",
    help="Output format",
)
@click.option("--debug", is_flag=True, help="Enable debug logging")
def search(query, client, rfp_type, service, equipment, limit, verbose, output, debug):
    """Search for similar RFP templates"""
    try:
        # Enable debug logging if requested
        if debug:
            import logging

            logging.basicConfig(level=logging.DEBUG)

        # Initialize search engine
        search_engine = SearchEngine()

        # Prepare filters
        filters = {}
        if client:
            filters["client_name"] = client
        if rfp_type:
            filters["rfp_type"] = rfp_type
        if service:
            filters["service_category"] = service
        if equipment:
            filters["equipment_type"] = equipment

        # Perform search
        results = search_engine.search_templates(
            query=query, filters=filters, limit=limit
        )

        # Format output
        if output == "json":
            json_output = formatter.format_json_output(results)
            click.echo(json_output)
        else:
            formatter.format_search_results(results, verbose)

    except Exception as e:
        formatter.format_error(f"Search failed: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument("document_path", type=click.Path(exists=True))
@click.option("--batch", is_flag=True, help="Process all documents in directory")
def add(document_path, batch):
    """Add a document to the RAG system"""
    try:
        # Initialize components
        processor = DocumentProcessor()
        metadata_extractor = MetadataExtractor()
        version_manager = VersionManager()
        summarizer = DocumentSummarizer()
        embedding_engine = EmbeddingEngine()
        vector_store = VectorStore()

        if batch:
            # Process all documents in directory
            directory = Path(document_path)
            docx_files = list(directory.glob("*.docx"))

            formatter.format_progress_bar(0, len(docx_files), "Processing documents")

            for i, file_path in enumerate(docx_files):
                _process_single_document(
                    str(file_path),
                    processor,
                    metadata_extractor,
                    version_manager,
                    summarizer,
                    embedding_engine,
                    vector_store,
                )
                formatter.format_progress_bar(
                    i + 1, len(docx_files), "Processing documents"
                )

            formatter.format_success(f"Added {len(docx_files)} documents to the system")
        else:
            # Process single document
            result = _process_single_document(
                document_path,
                processor,
                metadata_extractor,
                version_manager,
                summarizer,
                embedding_engine,
                vector_store,
            )

            formatter.format_success(f"Added document: {result['document_id']}")

    except Exception as e:
        formatter.format_error(f"Failed to add document: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument("document_id")
@click.option("--show-content", is_flag=True, help="Display document content")
def get(document_id, show_content):
    """Retrieve a specific document by ID"""
    try:
        vector_store = VectorStore()
        document = vector_store.get_document_by_id(document_id)

        if document:
            formatter.format_document_details(document, show_content)
        else:
            formatter.format_error(f"Document {document_id} not found")

    except Exception as e:
        formatter.format_error(f"Failed to retrieve document: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument("document_id")
@click.option("--limit", "-l", default=5, help="Number of similar documents")
def similar(document_id, limit):
    """Find documents similar to a specific document"""
    try:
        search_engine = SearchEngine()
        results = search_engine.find_similar_documents(document_id, limit)

        if results:
            formatter.format_search_results(results, verbose=False)
        else:
            formatter.format_error(f"No similar documents found for {document_id}")

    except Exception as e:
        formatter.format_error(f"Failed to find similar documents: {str(e)}")
        sys.exit(1)


@cli.command()
@click.argument("document_id")
@click.option("--limit", "-l", default=3, help="Number of recommendations")
def recommend(document_id, limit):
    """Get document recommendations based on characteristics"""
    try:
        search_engine = SearchEngine()
        recommendations = search_engine.get_document_recommendations(document_id, limit)

        formatter.format_recommendations(recommendations)

    except Exception as e:
        formatter.format_error(f"Failed to get recommendations: {str(e)}")
        sys.exit(1)


@cli.command()
def status():
    """Show system status and statistics"""
    try:
        search_engine = SearchEngine()
        stats = search_engine.get_search_statistics()

        # Get version manager info
        version_manager = VersionManager()
        version_info = version_manager.get_version_info()
        stats["version_info"] = version_info

        formatter.format_system_status(stats)

    except Exception as e:
        formatter.format_error(f"Failed to get system status: {str(e)}")
        sys.exit(1)


@cli.command()
@click.confirmation_option(prompt="Are you sure you want to reset the entire database?")
def reset():
    """Reset the entire document database"""
    try:
        vector_store = VectorStore()
        success = vector_store.reset_collection()

        if success:
            formatter.format_success("Database reset successfully")
        else:
            formatter.format_error("Failed to reset database")

    except Exception as e:
        formatter.format_error(f"Failed to reset database: {str(e)}")
        sys.exit(1)


@cli.command()
@click.option("--directory", "-d", default=".", help="Directory to scan for documents")
def index(directory):
    """Index all RFP documents in a directory"""
    try:
        # Initialize all components
        processor = DocumentProcessor()
        metadata_extractor = MetadataExtractor()
        version_manager = VersionManager()
        summarizer = DocumentSummarizer()
        embedding_engine = EmbeddingEngine()
        vector_store = VectorStore()

        # Find all DOCX files
        directory_path = Path(directory)
        docx_files = list(directory_path.rglob("*.docx"))

        if not docx_files:
            formatter.format_error(f"No DOCX files found in {directory}")
            return

        # Get existing documents to avoid duplicates
        existing_docs = {}
        try:
            all_doc_ids = vector_store.list_all_documents()
            for doc_id in all_doc_ids:
                doc_info = vector_store.get_document_by_id(doc_id)
                if doc_info:
                    existing_docs[doc_id] = doc_info
        except:
            existing_docs = {}

        formatter.format_progress_bar(0, len(docx_files), "Indexing documents")

        processed_count = 0
        for i, file_path in enumerate(docx_files):
            try:
                # Check if already indexed
                filename = file_path.name
                already_indexed = any(
                    doc.get("metadata", {}).get("filename") == filename
                    for doc in existing_docs.values()
                )

                if not already_indexed:
                    result = _process_single_document(
                        str(file_path),
                        processor,
                        metadata_extractor,
                        version_manager,
                        summarizer,
                        embedding_engine,
                        vector_store,
                        existing_docs,
                    )
                    processed_count += 1

            except Exception as e:
                formatter.format_error(f"Failed to process {file_path.name}: {str(e)}")

            formatter.format_progress_bar(i + 1, len(docx_files), "Indexing documents")

        formatter.format_success(
            f"Indexed {processed_count} new documents from {directory}"
        )

    except Exception as e:
        formatter.format_error(f"Indexing failed: {str(e)}")
        sys.exit(1)


def _process_single_document(
    file_path,
    processor,
    metadata_extractor,
    version_manager,
    summarizer,
    embedding_engine,
    vector_store,
    existing_docs=None,
):
    """Process a single document through the complete pipeline"""

    # 1. Extract text and basic metadata
    doc_data = processor.process_document(file_path)
    content = doc_data["content"]
    filename_metadata = doc_data["filename_metadata"]

    # 2. Extract enhanced metadata
    enhanced_metadata = metadata_extractor.extract_comprehensive_metadata(
        content, file_path, filename_metadata
    )

    # 3. Determine version
    if existing_docs is None:
        existing_docs = {}

    version, is_duplicate, parent_id = version_manager.determine_version(
        content, file_path, existing_docs
    )

    # 4. Generate summary
    summary = summarizer.generate_summary(content, enhanced_metadata)

    # 5. Extract key points
    key_points = summarizer.generate_key_points(content, enhanced_metadata)

    # 6. Classify complexity
    complexity = summarizer.classify_document_complexity(content, enhanced_metadata)

    # 7. Generate document ID
    import uuid

    document_id = str(uuid.uuid4())

    # 8. Prepare final metadata (convert lists to strings for ChromaDB compatibility)
    final_metadata = {
        **enhanced_metadata,
        "content_summary": summary,
        "key_points": ", ".join(key_points)
        if isinstance(key_points, list)
        else key_points,
        "complexity": complexity,
        "document_version": version,
        "is_duplicate": is_duplicate,
        "parent_document_id": parent_id,
        "word_count": doc_data["stats"]["word_count"],
        "file_path": file_path,
        "processing_date": doc_data["processing_timestamp"],
    }

    # Convert any list values in enhanced_metadata to strings
    for key, value in final_metadata.items():
        if isinstance(value, list):
            final_metadata[key] = ", ".join(str(v) for v in value)

    # 9. Generate embedding
    embedding = embedding_engine.generate_document_embedding(content, final_metadata)

    # 10. Add to vector store
    vector_store.add_document(document_id, content, embedding, final_metadata)

    # 11. Register in version manager
    version_manager.register_document(document_id, file_path, content, version)

    return {
        "document_id": document_id,
        "version": version,
        "is_duplicate": is_duplicate,
    }


if __name__ == "__main__":
    cli()
