from typing import Dict, Any, List
from datetime import datetime

# Comprehensive metadata schema for RFP documents
METADATA_SCHEMA = {
    "document_id": "str",
    "filename": "str",
    "file_path": "str",
    "document_type": "str",  # EPC, Supply, Service, Annexure
    "client_name": "str",  # CESC_Kolkata, CPDL, MPSL, etc.
    "service_category": "str",  # Electrical_Infrastructure, Mechanical_Boiler, etc.
    "specific_service": "str",
    "equipment_type": "str",  # PTR, DTR, HT_LT_Cable, etc.
    "rfp_type": "str",  # EPC_Project, Supply_Contract, etc.
    "rfp_subtype": "str",
    "document_version": "str",  # v1.0, v1.1, v2.0
    "content_summary": "str",
    "key_terms": "list[str]",
    "document_purpose": "str",
    "content_hash": "str",
    "similarity_score": "float",
    "word_count": "int",
    "processing_date": "datetime",
    "confidence_score": "float",
    "is_duplicate": "bool",
    "parent_document_id": "str",
}

# RFP Type classification patterns
RFP_TYPE_PATTERNS = {
    "EPC_Project": {
        "keywords": [
            "epc",
            "engineering",
            "construction",
            "distribution station",
            "streetlight",
            "enhancement",
        ],
        "weight": 2.0,
    },
    "Supply_Contract": {
        "keywords": [
            "supply",
            "procurement",
            "equipment",
            "meter",
            "cable",
            "ptr",
            "dtr",
            "transformer",
        ],
        "weight": 2.0,
    },
    "Service_Agreement": {
        "keywords": [
            "service",
            "maintenance",
            "annual overhauling",
            "repair",
            "o&m",
            "operations",
        ],
        "weight": 2.0,
    },
    "Safety_Specification": {
        "keywords": [
            "safety",
            "gate pass",
            "safety terms",
            "requirements",
            "safety requirements",
        ],
        "weight": 2.0,
    },
    "Maintenance_Contract": {
        "keywords": ["maintenance", "overhauling", "repair", "refurbishment", "annual"],
        "weight": 1.5,
    },
    "Survey_Contract": {
        "keywords": ["survey", "gpr", "inspection", "ground penetrating"],
        "weight": 2.0,
    },
    "Metering_Project": {
        "keywords": ["metering", "energy meters", "meter reading", "billing"],
        "weight": 2.0,
    },
    "General_Terms": {
        "keywords": [
            "general conditions",
            "contract",
            "terms",
            "conditions of contract",
        ],
        "weight": 2.0,
    },
}

# Document type patterns
DOCUMENT_TYPE_PATTERNS = {
    "EPC": ["epc", "engineering", "construction"],
    "Supply": ["supply", "procurement"],
    "Service": ["service", "maintenance", "operations"],
    "Annexure": ["annexure", "attachment", "additional"],
}

# Service category patterns
SERVICE_CATEGORY_PATTERNS = {
    "Electrical_Infrastructure": [
        "distribution",
        "transformer",
        "ptr",
        "dtr",
        "cable",
        "metering",
        "gis",
    ],
    "Mechanical_Boiler": ["boiler", "overhauling", "mechanical"],
    "Survey_Inspection": ["survey", "gpr", "inspection"],
    "Operations_Maintenance": ["o&m", "operations", "maintenance", "billing"],
    "Civil_Works": ["civil", "repair", "construction"],
    "Safety_Contract": ["safety", "gate pass", "requirements"],
}

# Equipment type patterns
EQUIPMENT_TYPE_PATTERNS = {
    "PTR": ["ptr", "power transformer"],
    "DTR": ["dtr", "distribution transformer"],
    "HT_LT_Cable": ["ht cable", "lt cable", "cable"],
    "Energy_Meters": ["energy meters", "meter"],
    "GIS": ["gis", "gas insulated"],
    "Boiler": ["boiler"],
    "Tower": ["tower", "enhancement"],
}


def validate_metadata(metadata: Dict[str, Any]) -> bool:
    """Validate metadata against schema requirements"""
    required_fields = [
        "document_id",
        "filename",
        "document_type",
        "client_name",
        "rfp_type",
    ]

    for field in required_fields:
        if field not in metadata or not metadata[field]:
            return False

    return True


def get_dynamic_rfp_types() -> List[str]:
    """Get list of available RFP types, including dynamic ones"""
    return list(RFP_TYPE_PATTERNS.keys()) + ["Unknown", "Custom"]


def add_custom_rfp_type(rfp_type: str, keywords: List[str], weight: float = 1.0):
    """Add a new custom RFP type for dynamic categorization"""
    RFP_TYPE_PATTERNS[rfp_type] = {"keywords": keywords, "weight": weight}
