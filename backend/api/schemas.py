"""
Pydantic models for API request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# Request/Response Models

class AnalyzeRequest(BaseModel):
    """Request to analyze initial RFP prompt"""
    prompt: str = Field(..., description="User's initial RFP request")


class AnalyzeResponse(BaseModel):
    """Response from analyze endpoint"""
    rfp_type: str
    entities: Dict[str, Any]
    questions: List[str]
    session_id: str


class QuestionRequest(BaseModel):
    """Request for next question"""
    session_id: str
    context: Dict[str, Any]
    answers: List[str]


class QuestionResponse(BaseModel):
    """Response with next question"""
    next_question: Optional[str]
    is_complete: bool


class GenerateRequest(BaseModel):
    """Request to generate all sections"""
    session_id: str
    context: Dict[str, Any]


class RAGSource(BaseModel):
    """RAG source document"""
    doc_name: str = Field(..., alias="docName")
    section: str
    similarity: float


class AIEvalScores(BaseModel):
    """AI evaluation scores"""
    coherence: float
    rag_confidence: float = Field(..., alias="ragConfidence")
    format_compliance: float = Field(..., alias="formatCompliance")
    sources: Optional[List[RAGSource]] = None
    latency_ms: Optional[int] = Field(None, alias="latencyMs")
    token_count: Optional[int] = Field(None, alias="tokenCount")

    class Config:
        populate_by_name = True


class Section(BaseModel):
    """RFP Section"""
    name: str
    content: str
    assumptions: Optional[List[str]] = None
    ai_eval: Optional[AIEvalScores] = Field(None, alias="aiEval")

    class Config:
        populate_by_name = True


class RFPSections(BaseModel):
    """All RFP sections"""
    new: List[Section]
    old: List[Section]
    rules: List[Section]


class GenerateResponse(BaseModel):
    """Response from generate endpoint"""
    session_id: str
    sections: RFPSections


class RegenerateRequest(BaseModel):
    """Request to regenerate a section"""
    session_id: str
    section_name: str
    context: Dict[str, Any]
    iteration: int
    additional_context: Optional[str] = None


class RegenerateResponse(BaseModel):
    """Response from regenerate endpoint"""
    section: Section


class ExportRequest(BaseModel):
    """Request to export RFP"""
    session_id: str


# RAG Context Discovery
class DiscoverContextRequest(BaseModel):
    session_id: str
    context: Dict[str, Any]


class DiscoverContextResponse(BaseModel):
    session_id: str
    relevant_rfps: List[Dict[str, Any]]
    extracted_insights: Dict[str, Any]
    search_query: str
    total_found: int
