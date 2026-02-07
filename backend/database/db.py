"""
Database connection and initialization
SQLite database for RFP sessions and sections
"""

import aiosqlite
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Database file path
DB_PATH = Path(__file__).parent.parent / "rfp_generator.db"

# SQL schema
SCHEMA = """
-- RFP Sessions table
CREATE TABLE IF NOT EXISTS rfp_sessions (
    id TEXT PRIMARY KEY,
    title TEXT,
    rfp_type TEXT,
    context TEXT,  -- JSON stored as text
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Generated Sections table
CREATE TABLE IF NOT EXISTS sections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    name TEXT NOT NULL,
    source_type TEXT CHECK(source_type IN ('new', 'old', 'rules')),
    content TEXT,
    assumptions TEXT,  -- JSON stored as text
    ai_eval TEXT,  -- JSON stored as text
    is_approved BOOLEAN DEFAULT FALSE,
    regen_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES rfp_sessions(id)
);

-- Langfuse-ready traces table (for future observability)
CREATE TABLE IF NOT EXISTS generation_traces (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    section_name TEXT,
    action TEXT,  -- 'generate', 'regenerate'
    latency_ms INTEGER,
    token_count INTEGER,
    rag_sources TEXT,  -- JSON stored as text
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES rfp_sessions(id)
);

-- Index for faster queries
CREATE INDEX IF NOT EXISTS idx_sections_session ON sections(session_id);
CREATE INDEX IF NOT EXISTS idx_traces_session ON generation_traces(session_id);
"""


async def get_db():
    """Get database connection"""
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_database():
    """Initialize database with schema"""
    logger.info(f"Initializing database at {DB_PATH}")
    
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(SCHEMA)
        await db.commit()
    
    logger.info("Database initialized successfully")


async def close_database():
    """Close database connection"""
    # Connection is managed per-request, no global connection to close
    pass
