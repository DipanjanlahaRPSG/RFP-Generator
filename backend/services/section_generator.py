"""
Section Generator Service
Generates RFP sections using three-source architecture: NEW, OLD, RULES
"""

import openai
import logging
import time
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from services.ai_evaluator import AIEvaluator

logger = logging.getLogger(__name__)


class SectionGenerator:
    """Generates RFP sections using NEW/OLD/RULES architecture"""
    
    # Section definitions
    NEW_SECTIONS = [
        "Scope of Work",
        "Deliverables",
        "Technical Requirements",
        "Evaluation Criteria",
        "Timeline & Milestones",
        "Budget & Payment Terms",
    ]
    
    OLD_SECTIONS = [
        "Background & Context",
        "Vendor Qualifications",
        "Proposal Format",
        "Submission Instructions",
        "Contract Terms",
        "Insurance Requirements",
        "Warranty & Support",
        "References Required",
    ]
    
    RULES_SECTIONS = [
        "General Terms & Conditions",
        "Safety & Compliance",
        "Intellectual Property",
        "Confidentiality",
        "Termination Clause",
        "Dispute Resolution",
        "Force Majeure",
        "Indemnification",
        "Liability Limitations",
        "Governing Law",
        "Amendment Procedures",
    ]
    
    def __init__(self, search_engine=None):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.search_engine = search_engine
        self.evaluator = AIEvaluator()
        self.templates_dir = Path(__file__).parent.parent / "templates"
    
    def generate_all_sections(self, context: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate all 25 RFP sections
        Returns: { "new": [...], "old": [...], "rules": [...] }
        """
        logger.info("Generating all RFP sections")
        
        new_sections = []
        old_sections = []
        rules_sections = []
        
        # Generate NEW sections (LLM-based)
        for section_name in self.NEW_SECTIONS:
            section = self.generate_new_section(section_name, context)
            new_sections.append(section)
        
        # Generate OLD sections (RAG-based)
        for section_name in self.OLD_SECTIONS:
            section = self.generate_old_section(section_name, context)
            old_sections.append(section)
        
        # Get RULES sections (templates)
        for section_name in self.RULES_SECTIONS:
            section = self.get_rules_section(section_name)
            rules_sections.append(section)
        
        return {
            "new": new_sections,
            "old": old_sections,
            "rules": rules_sections
        }
    
    def generate_new_section(
        self,
        section_name: str,
        context: Dict[str, Any],
        iteration: int = 1,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a NEW section using LLM with user context
        """
        logger.info(f"Generating NEW section: {section_name} (iteration {iteration})")
        
        start_time = time.time()
        
        # Build prompt
        system_prompt = self._get_new_section_system_prompt(section_name)
        user_prompt = self._build_new_section_prompt(section_name, context, additional_context)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            token_count = response.usage.total_tokens
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Extract assumptions
            assumptions = self._extract_assumptions(content, context)
            
            # Evaluate section
            ai_eval = self.evaluator.evaluate_section(
                section_name=section_name,
                section_content=content,
                rag_sources=None,  # NEW sections don't use RAG
                latency_ms=latency_ms,
                token_count=token_count
            )
            
            return {
                "name": section_name,
                "content": content,
                "assumptions": assumptions,
                "aiEval": ai_eval
            }
            
        except Exception as e:
            logger.error(f"Error generating NEW section {section_name}: {e}")
            return self._get_fallback_section(section_name, "new")
    
    def generate_old_section(
        self,
        section_name: str,
        context: Dict[str, Any],
        iteration: int = 1
    ) -> Dict[str, Any]:
        """
        Generate an OLD section using RAG retrieval
        """
        logger.info(f"Generating OLD section: {section_name}")
        
        start_time = time.time()
        
        # For now, generate with LLM (RAG integration comes next)
        # In production, this would use SearchEngine to find similar sections
        
        system_prompt = f"""You are an expert RFP writer. Generate the "{section_name}" section for an RFP.

This section should be based on standard industry practices and typical RFP requirements.
Use professional, formal language appropriate for procurement documents."""

        user_prompt = f"""Generate the "{section_name}" section for this RFP:

Context: {context}

Create a comprehensive, professional section in markdown format."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            token_count = response.usage.total_tokens
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Mock RAG sources (in production, these come from SearchEngine)
            rag_sources = [
                {"docName": "RFP_Services_2024.docx", "section": section_name, "similarity": 85.0},
                {"docName": "RFP_Consulting_2023.docx", "section": section_name, "similarity": 78.0}
            ]
            
            ai_eval = self.evaluator.evaluate_section(
                section_name=section_name,
                section_content=content,
                rag_sources=rag_sources,
                latency_ms=latency_ms,
                token_count=token_count
            )
            
            return {
                "name": section_name,
                "content": content,
                "aiEval": ai_eval
            }
            
        except Exception as e:
            logger.error(f"Error generating OLD section {section_name}: {e}")
            return self._get_fallback_section(section_name, "old")
    
    def get_rules_section(self, section_name: str) -> Dict[str, Any]:
        """
        Get a RULES section from fixed templates
        """
        logger.info(f"Loading RULES section: {section_name}")
        
        # Map section name to template file
        template_file = self._get_template_filename(section_name)
        template_path = self.templates_dir / template_file
        
        try:
            if template_path.exists():
                content = template_path.read_text(encoding='utf-8')
            else:
                # Fallback content
                content = self._get_fallback_rules_content(section_name)
            
            # RULES sections don't need evaluation (they're fixed)
            ai_eval = {
                "coherence": 10.0,
                "ragConfidence": 100.0,
                "formatCompliance": 100.0,
                "sources": None,
                "latencyMs": 0,
                "tokenCount": 0
            }
            
            return {
                "name": section_name,
                "content": content,
                "aiEval": ai_eval
            }
            
        except Exception as e:
            logger.error(f"Error loading RULES section {section_name}: {e}")
            return self._get_fallback_section(section_name, "rules")
    
    def _get_new_section_system_prompt(self, section_name: str) -> str:
        """Get system prompt for NEW section generation"""
        return f"""You are an expert RFP consultant specializing in creating comprehensive, professional RFP documents.

Your task is to generate the "{section_name}" section based on the user's requirements.

Guidelines:
- Use clear, professional language
- Format in markdown with proper headings
- Be specific and actionable
- Include relevant details from the context
- Flag any assumptions you make
- Follow standard RFP best practices"""
    
    def _build_new_section_prompt(
        self,
        section_name: str,
        context: Dict[str, Any],
        additional_context: Optional[str] = None
    ) -> str:
        """Build user prompt for NEW section"""
        prompt = f"""Generate the "{section_name}" section for an RFP with the following context:

{self._format_context(context)}"""
        
        if additional_context:
            prompt += f"\n\nAdditional requirements:\n{additional_context}"
        
        prompt += f"\n\nCreate a comprehensive, professional section in markdown format."
        
        return prompt
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context dictionary for prompt"""
        lines = []
        for key, value in context.items():
            lines.append(f"- {key}: {value}")
        return "\n".join(lines)
    
    def _extract_assumptions(self, content: str, context: Dict[str, Any]) -> List[str]:
        """Extract assumptions made during generation"""
        # Simple heuristic: look for common assumption indicators
        assumptions = []
        
        if "assumed" in content.lower():
            assumptions.append("Contains explicit assumptions in content")
        
        # Check for missing context
        if "budget" not in context and "budget" in content.lower():
            assumptions.append("Budget range estimated based on similar RFPs")
        
        if "duration" not in context and ("month" in content.lower() or "week" in content.lower()):
            assumptions.append("Timeline estimated based on typical project duration")
        
        return assumptions
    
    def _get_template_filename(self, section_name: str) -> str:
        """Map section name to template filename"""
        mapping = {
            "General Terms & Conditions": "general_terms.md",
            "Safety & Compliance": "safety_compliance.md",
            "Intellectual Property": "intellectual_property.md",
            "Confidentiality": "confidentiality.md",
            "Termination Clause": "termination.md",
            "Dispute Resolution": "dispute_resolution.md",
            "Force Majeure": "force_majeure.md",
            "Indemnification": "indemnification.md",
            "Liability Limitations": "liability.md",
            "Governing Law": "governing_law.md",
            "Amendment Procedures": "amendments.md",
        }
        return mapping.get(section_name, "default.md")
    
    def _get_fallback_rules_content(self, section_name: str) -> str:
        """Fallback content for RULES sections"""
        return f"""## {section_name}

Standard {section_name.lower()} clause as per company policy.

This section contains fixed legal and compliance terms."""
    
    def _get_fallback_section(self, section_name: str, source_type: str) -> Dict[str, Any]:
        """Fallback section if generation fails"""
        return {
            "name": section_name,
            "content": f"## {section_name}\n\nContent generation in progress...",
            "assumptions": [],
            "aiEval": {
                "coherence": 5.0,
                "ragConfidence": 0.0,
                "formatCompliance": 50.0,
                "sources": None,
                "latencyMs": 0,
                "tokenCount": 0
            }
        }
