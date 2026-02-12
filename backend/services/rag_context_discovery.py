"""
RAG Context Discovery Service
Searches historical RFPs to find relevant context before generation
"""

import logging
from typing import Dict, Any, List
from openai import OpenAI
import os
from config.settings import settings

logger = logging.getLogger(__name__)


class RAGContextDiscovery:
    """
    Service to discover relevant historical RFP context using RAG
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    async def discover_context(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search RAG system for relevant historical RFPs and extract context
        
        Args:
            user_context: Context from user's answers (rfp_type, service, duration, etc.)
            
        Returns:
            Dictionary with discovered context including:
            - relevant_rfps: List of similar RFPs found
            - extracted_insights: Key insights from historical RFPs
            - recommended_sections: Sections that worked well historically
        """
        logger.info(f"Discovering RAG context for: {user_context.get('rfp_type', 'unknown')}")
        
        try:
            # Build search query from user context
            search_query = self._build_search_query(user_context)
            
            # Search for relevant historical RFPs
            relevant_rfps = await self._search_historical_rfps(search_query, user_context)
            
            # Extract insights from found RFPs
            insights = await self._extract_insights(relevant_rfps, user_context)
            
            return {
                "relevant_rfps": relevant_rfps,
                "extracted_insights": insights,
                "search_query": search_query,
                "total_found": len(relevant_rfps)
            }
            
        except Exception as e:
            logger.error(f"Error discovering context: {e}")
            # Return empty context on error
            return {
                "relevant_rfps": [],
                "extracted_insights": {},
                "search_query": "",
                "total_found": 0
            }
    
    def _build_search_query(self, context: Dict[str, Any]) -> str:
        """Build semantic search query from user context"""
        parts = []
        
        if context.get("rfp_type"):
            parts.append(context["rfp_type"].replace("_", " "))
        
        if context.get("service"):
            parts.append(context["service"])
        
        if context.get("originalRequest"):
            # Extract key terms from original request
            parts.append(context["originalRequest"])
        
        query = " ".join(parts)
        logger.info(f"Built search query: {query[:100]}...")
        return query
    
    async def _search_historical_rfps(
        self, 
        query: str, 
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Search historical RFPs using RAG system
        """
        try:
            from rag_engine.search_engine import SearchEngine
            search_engine = SearchEngine()
            
            # Prepare filters based on context
            filters = {}
            if context.get("rfp_type"):
                filters["rfp_type"] = context.get("rfp_type")
                
            results = search_engine.search_templates(
                query=query,
                filters=filters,
                limit=5
            )
            
            logger.info(f"Found {len(results)} relevant historical RFPs")
            
            # Process results to match expected format
            formatted_results = []
            for r in results:
                formatted_results.append({
                    "doc_name": r.get('metadata', {}).get('filename', 'Unknown'),
                    "similarity": round((1 - r.get('distance', 0)) * 100, 1),
                    "rfp_type": r.get('metadata', {}).get('rfp_type', 'Unknown'),
                    "sections_found": [], # TODO: Extract sections from metadata if available
                    "summary": r.get('metadata', {}).get('content_summary', '')
                })
                
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching historical RFPs: {e}")
            return []
    
    async def _extract_insights(
        self, 
        rfps: List[Dict[str, Any]], 
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Use LLM to extract key insights from historical RFPs
        """
        if not rfps:
            return {}
        
        # Build prompt for insight extraction
        rfp_summaries = "\n".join([
            f"- {rfp['doc_name']} ({rfp['similarity']}% match): {rfp['summary']}"
            for rfp in rfps
        ])
        
        prompt = f"""Based on these historical RFPs similar to the current request:

{rfp_summaries}

Current RFP Context:
- Type: {user_context.get('rfp_type', 'Unknown')}
- Service: {user_context.get('service', 'Unknown')}
- Duration: {user_context.get('duration', 'Unknown')}

Extract key insights that should inform the new RFP generation:
1. Common requirements or patterns
2. Typical evaluation criteria
3. Standard deliverables
4. Important considerations

Provide a concise summary in JSON format with keys: common_requirements, evaluation_patterns, standard_deliverables, considerations"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert RFP analyst. Extract actionable insights from historical RFPs."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            import json
            insights_text = response.choices[0].message.content
            
            # Try to parse as JSON, fallback to text
            try:
                insights = json.loads(insights_text)
            except:
                insights = {"summary": insights_text}
            
            logger.info(f"Extracted insights: {list(insights.keys())}")
            return insights
            
        except Exception as e:
            logger.error(f"Error extracting insights: {e}")
            return {}
