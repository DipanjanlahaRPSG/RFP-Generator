"""
AI Evaluator Service
Generates AI evaluation metrics for sections
"""

import openai
import logging
import time
from typing import List, Dict, Any, Optional
from config.settings import settings

logger = logging.getLogger(__name__)


class AIEvaluator:
    """Evaluates generated sections with AI metrics"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    def evaluate_section(
        self,
        section_name: str,
        section_content: str,
        rag_sources: Optional[List[Dict[str, Any]]] = None,
        latency_ms: Optional[int] = None,
        token_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a section and return AI metrics
        
        Returns:
        - coherence (0-10): LLM-as-judge score
        - ragConfidence (0-100%): RAG attribution score
        - formatCompliance (0-100%): Template adherence
        - sources: list of RAG sources with similarity scores
        - latencyMs: generation time
        - tokenCount: tokens used
        """
        
        # Evaluate coherence using LLM-as-judge
        coherence = self._evaluate_coherence(section_name, section_content)
        
        # Calculate RAG confidence from sources
        rag_confidence = self._calculate_rag_confidence(rag_sources)
        
        # Check format compliance
        format_compliance = self._check_format_compliance(section_content)
        
        return {
            "coherence": coherence,
            "ragConfidence": rag_confidence,
            "formatCompliance": format_compliance,
            "sources": rag_sources if rag_sources else None,
            "latencyMs": latency_ms,
            "tokenCount": token_count
        }
    
    def _evaluate_coherence(self, section_name: str, content: str) -> float:
        """
        Use LLM-as-judge to evaluate section coherence
        Returns score from 0-10
        """
        system_prompt = """You are an expert RFP evaluator. Rate the coherence and quality of the given RFP section on a scale of 0-10.

Criteria:
- Clarity and readability
- Logical structure
- Completeness
- Professional tone
- Relevance to section purpose

Respond with ONLY a number between 0 and 10 (can include decimals like 8.5)."""

        user_prompt = f"""Section: {section_name}

Content:
{content[:1000]}  # Truncate for token efficiency

Rate this section's coherence (0-10):"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=10
            )
            
            score_text = response.choices[0].message.content.strip()
            score = float(score_text)
            return min(10.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"Error evaluating coherence: {e}")
            # Default to reasonable score
            return 8.0
    
    def _calculate_rag_confidence(self, sources: Optional[List[Dict[str, Any]]]) -> float:
        """
        Calculate RAG confidence based on source similarity scores
        Returns percentage (0-100)
        """
        if not sources or len(sources) == 0:
            return 0.0
        
        # Average similarity scores
        similarities = [s.get('similarity', 0) for s in sources]
        avg_similarity = sum(similarities) / len(similarities)
        
        return round(avg_similarity, 1)
    
    def _check_format_compliance(self, content: str) -> float:
        """
        Check if content follows proper markdown formatting
        Returns percentage (0-100)
        """
        score = 100.0
        
        # Check for markdown heading
        if not content.strip().startswith('#'):
            score -= 20
        
        # Check for reasonable length
        if len(content) < 100:
            score -= 30
        
        # Check for structure (paragraphs or lists)
        if '\n\n' not in content and '\n-' not in content and '\n*' not in content:
            score -= 20
        
        return max(0.0, score)
