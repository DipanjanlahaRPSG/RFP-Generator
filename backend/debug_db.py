import sys
from pathlib import Path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from rag_engine.vector_store import VectorStore
import logging

logging.basicConfig(level=logging.DEBUG)

def inspect_db():
    vs = VectorStore()
    print(f"Collection count: {vs.collection.count()}")
    
    # Peek at first item
    print("\n--- PEEK ---")
    peek = vs.collection.peek(limit=1)
    print(peek)
    
    # List all IDs
    print("\n--- IDs ---")
    ids = vs.list_all_documents()
    print(f"Total IDs: {len(ids)}")
    print(ids[:5])

if __name__ == "__main__":
    inspect_db()
