#!/usr/bin/env python3
"""
RFP Document RAG System - Main Entry Point

A CLI tool for searching and retrieving RFP document templates using
Retrieval-Augmented Generation with comprehensive metadata.

Usage:
    python main.py search --query "electrical infrastructure" --client CESC_Kolkata
    python main.py index --directory ./documents
    python main.py status
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from cli.commands import cli

if __name__ == "__main__":
    cli()
