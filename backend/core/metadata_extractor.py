import re
from typing import Dict, Any, List, Tuple
from config.metadata_schema import (
    RFP_TYPE_PATTERNS,
    DOCUMENT_TYPE_PATTERNS,
    SERVICE_CATEGORY_PATTERNS,
    EQUIPMENT_TYPE_PATTERNS,
    add_custom_rfp_type,
)
import logging

logger = logging.getLogger(__name__)


class MetadataExtractor:
    """Enhanced metadata extraction from document content and filenames"""

    def __init__(self):
        self.confidence_threshold = 0.6

    def classify_rfp_type(self, content: str, filename: str) -> Tuple[str, float]:
        """Classify RFP type with confidence score"""
        content_lower = content.lower()
        filename_lower = filename.lower()

        scores = {}

        for rfp_type, config in RFP_TYPE_PATTERNS.items():
            score = 0
            keyword_matches = 0

            for keyword in config["keywords"]:
                # Higher weight for filename matches
                if keyword in filename_lower:
                    score += 3
                    keyword_matches += 1
                # Content matches
                if keyword in content_lower:
                    score += 1
                    keyword_matches += 1

            # Apply weight and normalize
            if keyword_matches > 0:
                scores[rfp_type] = (score / keyword_matches) * config["weight"]

        if not scores:
            return "Unknown", 0.0

        best_type = max(scores, key=scores.get)
        confidence = min(scores[best_type] / 10, 1.0)  # Normalize to 0-1

        return best_type, confidence

    def extract_client_name(self, content: str, filename: str) -> Tuple[str, float]:
        """Extract client name with confidence"""
        content_lower = content.lower()
        filename_lower = filename.lower()

        # Common client patterns
        client_patterns = {
            "CESC_Kolkata": ["cesc kolkata", "cesc"],
            "CPDL": ["cpdl"],
            "CESC_Rajasthan": ["cesc rajasthan"],
            "MPSL": ["mpsl"],
            "CDPL": ["cdpl"],
            "General": ["general", "common"],
        }

        scores = {}

        for client, patterns in client_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in filename_lower:
                    score += 3
                if pattern in content_lower:
                    score += 1

            if score > 0:
                scores[client] = score

        if not scores:
            return "Unknown", 0.0

        best_client = max(scores, key=scores.get)
        confidence = min(scores[best_client] / 5, 1.0)

        return best_client, confidence

    def classify_service_category(
        self, content: str, filename: str
    ) -> Tuple[str, float]:
        """Classify service category with confidence"""
        content_lower = content.lower()
        filename_lower = filename.lower()

        scores = {}

        for category, keywords in SERVICE_CATEGORY_PATTERNS.items():
            score = 0
            matches = 0

            for keyword in keywords:
                if keyword in filename_lower:
                    score += 2
                    matches += 1
                if keyword in content_lower:
                    score += 1
                    matches += 1

            if matches > 0:
                scores[category] = score / matches

        if not scores:
            return "Unknown", 0.0

        best_category = max(scores, key=scores.get)
        confidence = min(scores[best_category] / 3, 1.0)

        return best_category, confidence

    def extract_equipment_type(self, content: str, filename: str) -> Tuple[str, float]:
        """Extract equipment type with confidence"""
        content_lower = content.lower()
        filename_lower = filename.lower()

        scores = {}

        for equipment, keywords in EQUIPMENT_TYPE_PATTERNS.items():
            score = 0
            for keyword in keywords:
                if keyword in filename_lower:
                    score += 2
                if keyword in content_lower:
                    score += 1

            if score > 0:
                scores[equipment] = score

        if not scores:
            return "Unknown", 0.0

        best_equipment = max(scores, key=scores.get)
        confidence = min(scores[best_equipment] / 4, 1.0)

        return best_equipment, confidence

    def extract_key_terms(self, content: str, max_terms: int = 20) -> List[str]:
        """Extract key terms from document content"""
        # Simple keyword extraction based on frequency and importance
        content_lower = content.lower()

        # Common technical terms in RFP documents
        technical_terms = [
            "transformer",
            "substation",
            "distribution",
            "transmission",
            "cable",
            "installation",
            "commissioning",
            "testing",
            "maintenance",
            "inspection",
            "safety",
            "quality",
            "specification",
            "requirement",
            "technical",
            "commercial",
            "financial",
            "timeline",
            "delivery",
            "warranty",
            "gpr",
            "survey",
            "metering",
            "billing",
            "infrastructure",
            "equipment",
        ]

        found_terms = []
        for term in technical_terms:
            if term in content_lower:
                found_terms.append(term)

        # Also extract capitalized terms (might be specific equipment/brands)
        capitalized = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", content)
        unique_capitalized = list(set(capitalized))[:10]  # Limit to prevent noise

        key_terms = found_terms + unique_capitalized
        return key_terms[:max_terms]

    def detect_document_purpose(self, content: str, filename: str) -> str:
        """Detect the purpose of the document"""
        content_lower = content.lower()
        filename_lower = filename.lower()

        if any(
            word in filename_lower
            for word in ["annexure", "attachment", "supplementary"]
        ):
            return "supplement"
        elif any(
            word in content_lower for word in ["template", "format", "boilerplate"]
        ):
            return "template"
        elif any(word in content_lower for word in ["contract", "agreement", "terms"]):
            return "contract"
        elif any(
            word in content_lower for word in ["specification", "requirements", "scope"]
        ):
            return "specification"
        elif any(word in content_lower for word in ["tender", "bid", "proposal"]):
            return "requirement"
        else:
            return "document"

    def extract_comprehensive_metadata(
        self, content: str, filename: str, filename_metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Extract all metadata with confidence scores"""

        # Classify various aspects
        rfp_type, rfp_confidence = self.classify_rfp_type(content, filename)
        client_name, client_confidence = self.extract_client_name(content, filename)
        service_category, service_confidence = self.classify_service_category(
            content, filename
        )
        equipment_type, equipment_confidence = self.extract_equipment_type(
            content, filename
        )

        # Extract additional metadata
        key_terms = self.extract_key_terms(content)
        document_purpose = self.detect_document_purpose(content, filename)

        # Calculate overall confidence
        all_confidences = [
            rfp_confidence,
            client_confidence,
            service_confidence,
            equipment_confidence,
        ]
        overall_confidence = sum(all_confidences) / len(all_confidences)

        # Merge with filename metadata
        metadata = {
            **filename_metadata,
            "rfp_type": rfp_type,
            "rfp_type_confidence": rfp_confidence,
            "client_name": client_name,
            "client_confidence": client_confidence,
            "service_category": service_category,
            "service_confidence": service_confidence,
            "equipment_type": equipment_type,
            "equipment_confidence": equipment_confidence,
            "key_terms": key_terms,
            "document_purpose": document_purpose,
            "overall_confidence": overall_confidence,
        }

        return metadata
