import openai
import re
from typing import Dict, List, Optional
import logging
from config.settings import settings

logger = logging.getLogger(__name__)


class DocumentSummarizer:
    """Handles automatic document summarization using OpenAI"""

    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.max_tokens

    def generate_summary(self, content: str, metadata: Dict[str, any] = None) -> str:
        """Generate comprehensive summary of document content"""
        try:
            # Prepare context from metadata
            context = ""
            if metadata:
                context = f"""
                Document Type: {metadata.get("document_type", "Unknown")}
                Client: {metadata.get("client_name", "Unknown")}
                RFP Type: {metadata.get("rfp_type", "Unknown")}
                Service: {metadata.get("specific_service", "Unknown")}
                """

            # Truncate content if too long
            truncated_content = self._truncate_content(content)

            prompt = f"""
            You are an expert RFP (Request for Proposal) analyst. Please provide a comprehensive summary of the following RFP document.
            
            {context}
            
            Focus on:
            1. Main purpose and scope of the RFP
            2. Key requirements and specifications
            3. Technical details and equipment involved
            4. Timeline and deliverables (if mentioned)
            5. Special conditions or safety requirements
            6. Commercial terms (if mentioned)
            
            Document Content:
            {truncated_content}
            
            Please provide a structured summary in 3-4 paragraphs that would be useful for someone searching for similar RFP templates.
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert RFP analyst providing comprehensive document summaries.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
                temperature=0.3,
            )

            summary = response.choices[0].message.content.strip()
            logger.info(f"Generated summary of {len(summary)} characters")
            return summary

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return self._generate_fallback_summary(content, metadata)

    def generate_key_points(
        self, content: str, metadata: Dict[str, any] = None
    ) -> List[str]:
        """Extract key points from document"""
        try:
            truncated_content = self._truncate_content(content, max_length=2000)

            prompt = f"""
            Extract the 5-7 most important key points from this RFP document. Focus on critical requirements, 
            technical specifications, timeline, and special conditions.
            
            Document Content:
            {truncated_content}
            
            Return as a numbered list of key points.
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert RFP analyst extracting key points from documents.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=300,
                temperature=0.2,
            )

            key_points_text = response.choices[0].message.content.strip()

            # Parse numbered list
            key_points = []
            for line in key_points_text.split("\n"):
                line = line.strip()
                if line and (
                    line[0].isdigit() or line.startswith("-") or line.startswith("•")
                ):
                    # Remove numbering/bullets
                    clean_point = re.sub(r"^[\d\.\-\•]\s*", "", line)
                    key_points.append(clean_point.strip())

            return key_points[:7]  # Limit to 7 points

        except Exception as e:
            logger.error(f"Error extracting key points: {str(e)}")
            return self._generate_fallback_key_points(content, metadata)

    def classify_document_complexity(
        self, content: str, metadata: Dict[str, any] = None
    ) -> str:
        """Classify document complexity level"""
        try:
            truncated_content = self._truncate_content(content, max_length=1500)

            prompt = f"""
            Classify the complexity of this RFP document as one of: Simple, Medium, Complex, Very Complex.
            
            Consider factors like:
            - Technical complexity
            - Scope and scale
            - Number of requirements
            - Specialized equipment or services
            - Timeline and coordination complexity
            
            Document Content:
            {truncated_content}
            
            Respond with just the complexity level.
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert RFP analyst classifying document complexity.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=50,
                temperature=0.1,
            )

            complexity = response.choices[0].message.content.strip()

            # Validate response
            valid_levels = ["Simple", "Medium", "Complex", "Very Complex"]
            for level in valid_levels:
                if level.lower() in complexity.lower():
                    return level

            return "Medium"  # Default fallback

        except Exception as e:
            logger.error(f"Error classifying complexity: {str(e)}")
            return "Medium"

    def _truncate_content(self, content: str, max_length: int = 3000) -> str:
        """Truncate content to fit within token limits"""
        if len(content) <= max_length:
            return content

        # Try to truncate at sentence boundaries
        truncated = content[:max_length]
        last_sentence = truncated.rfind(".")

        if last_sentence > max_length * 0.8:  # If we have a good sentence ending
            return truncated[: last_sentence + 1]

        return truncated + "..."

    def _generate_fallback_summary(
        self, content: str, metadata: Dict[str, any] = None
    ) -> str:
        """Generate fallback summary when AI is unavailable"""
        word_count = len(content.split())

        summary_parts = []

        if metadata:
            if metadata.get("document_type"):
                summary_parts.append(
                    f"This is a {metadata.get('document_type')} document"
                )
            if metadata.get("client_name"):
                summary_parts.append(f"for {metadata.get('client_name')}")
            if metadata.get("specific_service"):
                summary_parts.append(f"related to {metadata.get('specific_service')}")

        summary_parts.append(f"containing approximately {word_count} words.")

        # Extract first few sentences as preview
        sentences = content.split(".")[:3]
        if sentences:
            preview = ". ".join(sentences).strip()
            summary_parts.append(f"Key topics include: {preview[:100]}...")

        return " ".join(summary_parts)

    def _generate_fallback_key_points(
        self, content: str, metadata: Dict[str, any] = None
    ) -> List[str]:
        """Generate fallback key points when AI is unavailable"""
        key_points = []

        if metadata:
            if metadata.get("document_type"):
                key_points.append(f"Document Type: {metadata.get('document_type')}")
            if metadata.get("client_name"):
                key_points.append(f"Client: {metadata.get('client_name')}")
            if metadata.get("rfp_type"):
                key_points.append(f"RFP Type: {metadata.get('rfp_type')}")
            if metadata.get("specific_service"):
                key_points.append(f"Service: {metadata.get('specific_service')}")

        # Add basic content analysis
        word_count = len(content.split())
        key_points.append(f"Document length: {word_count} words")

        # Look for common RFP sections
        content_lower = content.lower()
        if "scope" in content_lower:
            key_points.append("Contains scope of work")
        if "timeline" in content_lower or "schedule" in content_lower:
            key_points.append("Includes timeline/schedule")
        if "safety" in content_lower:
            key_points.append("Includes safety requirements")

        return key_points[:7]
