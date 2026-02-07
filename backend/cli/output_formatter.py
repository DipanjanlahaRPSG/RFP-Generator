from typing import Dict, List, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint
import json


class OutputFormatter:
    """Formats RAG search results for CLI output"""

    def __init__(self):
        self.console = Console()

    def format_search_results(
        self, results: List[Dict[str, Any]], verbose: bool = False
    ) -> None:
        """Format and display search results"""

        if not results:
            self.console.print("[yellow]No results found.[/yellow]")
            return

        # Create results table
        table = Table(title="RFP Template Search Results")
        table.add_column("Rank", style="cyan", width=6)
        table.add_column("Similarity", style="green", width=12)
        table.add_column("Document ID", style="white", width=25)
        table.add_column("Client", style="blue", width=15)
        table.add_column("RFP Type", style="magenta", width=15)
        table.add_column("Service", style="yellow", width=20)

        if verbose:
            table.add_column("Summary", style="dim", width=40)

        for i, result in enumerate(results, 1):
            metadata = result.get("metadata", {})
            similarity = result.get("similarity_score", 0)

            row_data = [
                str(i),
                f"{similarity:.3f}",
                result.get("document_id", "N/A")[:22] + "..."
                if len(result.get("document_id", "")) > 22
                else result.get("document_id", "N/A"),
                metadata.get("client_name", "Unknown")[:12] + "..."
                if len(metadata.get("client_name", "")) > 12
                else metadata.get("client_name", "Unknown"),
                metadata.get("rfp_type", "Unknown")[:12] + "..."
                if len(metadata.get("rfp_type", "")) > 12
                else metadata.get("rfp_type", "Unknown"),
                metadata.get("specific_service", "Unknown")[:17] + "..."
                if len(metadata.get("specific_service", "")) > 17
                else metadata.get("specific_service", "Unknown"),
            ]

            if verbose:
                summary = metadata.get("content_summary", "No summary available")
                row_data.append(summary[:37] + "..." if len(summary) > 37 else summary)

            table.add_row(*row_data)

        self.console.print(table)

        # Show result count
        self.console.print(f"\n[green]Found {len(results)} results[/green]")

    def format_document_details(
        self, document: Dict[str, Any], show_content: bool = False
    ) -> None:
        """Display detailed document information"""

        metadata = document.get("metadata", {})

        # Create document details panel
        details_text = f"""
[bold cyan]Document ID:[/bold cyan] {document.get("document_id", "N/A")}
[bold cyan]Filename:[/bold cyan] {metadata.get("filename", "N/A")}
[bold cyan]Client:[/bold cyan] {metadata.get("client_name", "Unknown")}
[bold cyan]RFP Type:[/bold cyan] {metadata.get("rfp_type", "Unknown")}
[bold cyan]Document Type:[/bold cyan] {metadata.get("document_type", "Unknown")}
[bold cyan]Service Category:[/bold cyan] {metadata.get("service_category", "Unknown")}
[bold cyan]Specific Service:[/bold cyan] {metadata.get("specific_service", "Unknown")}
[bold cyan]Equipment Type:[/bold cyan] {metadata.get("equipment_type", "Unknown")}
[bold cyan]Version:[/bold cyan] {metadata.get("document_version", "v1.0")}
[bold cyan]Word Count:[/bold cyan] {metadata.get("word_count", "N/A")}
[bold cyan]Confidence:[/bold cyan] {metadata.get("overall_confidence", 0):.2f}
        """

        # Add summary if available
        if metadata.get("content_summary"):
            details_text += f"\n[bold cyan]Summary:[/bold cyan] {metadata.get('content_summary', '')[:200]}..."

        # Add key terms if available
        if metadata.get("key_terms"):
            terms = ", ".join(metadata["key_terms"][:10])
            details_text += f"\n[bold cyan]Key Terms:[/bold cyan] {terms}"

        panel = Panel(
            details_text.strip(), title="Document Details", border_style="blue"
        )

        self.console.print(panel)

        # Show content if requested
        if show_content and document.get("content"):
            content_panel = Panel(
                document["content"][:1000] + "..."
                if len(document["content"]) > 1000
                else document["content"],
                title="Document Content (Preview)",
                border_style="green",
            )
            self.console.print(content_panel)

    def format_system_status(self, status: Dict[str, Any]) -> None:
        """Display system status and statistics"""

        # Create status table
        table = Table(title="System Status")
        table.add_column("Component", style="cyan", width=20)
        table.add_column("Status", style="green", width=15)
        table.add_column("Details", style="white", width=40)

        # Vector store status
        vector_stats = status.get("vector_store", {})
        table.add_row(
            "Vector Store",
            "Active" if vector_stats.get("document_count", 0) > 0 else "Empty",
            f"{vector_stats.get('document_count', 0)} documents in {vector_stats.get('collection_name', 'Unknown')}",
        )

        # Embedding status
        embedding_stats = status.get("embeddings", {})
        table.add_row(
            "Embedding Engine",
            "Ready",
            f"Model: {embedding_stats.get('model', 'Unknown')}, Cache: {embedding_stats.get('cache_size', 0)} items",
        )

        # RAG Engine status
        table.add_row(
            "RAG Engine",
            "Ready",
            f"Similarity threshold: {status.get('similarity_threshold', 0.7)}",
        )

        self.console.print(table)

        # Show version info if available
        if status.get("version_info"):
            version_info = status["version_info"]
            version_panel = Panel(
                f"Base Documents: {version_info.get('total_base_documents', 0)}\n"
                f"Total Versions: {version_info.get('total_versions', 0)}\n"
                f"Avg Versions/Doc: {version_info.get('avg_versions_per_document', 0):.2f}",
                title="Version Management",
                border_style="magenta",
            )
            self.console.print(version_panel)

    def format_error(self, error_message: str) -> None:
        """Display error message"""
        error_panel = Panel(
            f"[red]{error_message}[/red]", title="Error", border_style="red"
        )
        self.console.print(error_panel)

    def format_success(self, message: str) -> None:
        """Display success message"""
        success_panel = Panel(
            f"[green]{message}[/green]", title="Success", border_style="green"
        )
        self.console.print(success_panel)

    def format_recommendations(self, recommendations: List[Dict[str, Any]]) -> None:
        """Display document recommendations"""

        if not recommendations:
            self.console.print("[yellow]No recommendations available.[/yellow]")
            return

        # Create recommendations table
        table = Table(title="Recommended Documents")
        table.add_column("Rank", style="cyan", width=6)
        table.add_column("Document ID", style="white", width=25)
        table.add_column("Client", style="blue", width=15)
        table.add_column("RFP Type", style="magenta", width=15)
        table.add_column("Reason", style="yellow", width=25)

        for i, rec in enumerate(recommendations, 1):
            metadata = rec.get("metadata", {})

            # Determine recommendation reason
            reason = "Similar characteristics"
            if rec.get("search_type") == "metadata_only":
                reason = "Metadata match"
            elif rec.get("search_type") == "hybrid":
                reason = "Combined similarity"

            table.add_row(
                str(i),
                rec.get("document_id", "N/A")[:22] + "..."
                if len(rec.get("document_id", "")) > 22
                else rec.get("document_id", "N/A"),
                metadata.get("client_name", "Unknown")[:12] + "..."
                if len(metadata.get("client_name", "")) > 12
                else metadata.get("client_name", "Unknown"),
                metadata.get("rfp_type", "Unknown")[:12] + "..."
                if len(metadata.get("rfp_type", "")) > 12
                else metadata.get("rfp_type", "Unknown"),
                reason,
            )

        self.console.print(table)

    def format_json_output(self, data: Any, indent: int = 2) -> str:
        """Format data as JSON string"""
        return json.dumps(data, indent=indent, ensure_ascii=False)

    def format_progress_bar(
        self, current: int, total: int, description: str = "Processing"
    ) -> None:
        """Display progress bar (simple text version)"""
        percentage = (current / total) * 100 if total > 0 else 0
        bar_length = 40
        filled_length = int(bar_length * current // total) if total > 0 else 0
        bar = "█" * filled_length + "-" * (bar_length - filled_length)

        self.console.print(
            f"[cyan]{description}:[/cyan] |{bar}| {current}/{total} ({percentage:.1f}%)"
        )
