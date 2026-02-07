import difflib
import hashlib
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import re
import logging

logger = logging.getLogger(__name__)


class VersionManager:
    """Handles semantic versioning for duplicate document detection"""

    def __init__(self):
        self.document_versions = {}  # Track versions by base document
        self.similarity_thresholds = {
            "minor": 0.95,  # Minor changes (v1.0 -> v1.1)
            "major": 0.80,  # Major changes but same doc (v1.0 -> v2.0)
            "new": 0.80,  # New document despite similar name
        }

    def extract_base_name(self, filename: str) -> str:
        """Extract base name from filename for version comparison"""
        # Remove extension and version indicators
        base_name = os.path.splitext(filename)[0]

        # Remove common version patterns
        patterns_to_remove = [
            r"\s*\(\d+\)$",  # (2), (3) at end
            r"\s*\(Copy\).*$",  # (Copy), (Copy 2)
            r"\s*v\d+.*$",  # v1, v2.0, etc.
            r"\s*Version\s*\d+.*$",  # Version 1, Version 2
            r"\s*Rev\s*\d+.*$",  # Rev 1, Rev 2
        ]

        for pattern in patterns_to_remove:
            base_name = re.sub(pattern, "", base_name, flags=re.IGNORECASE)

        # Remove trailing spaces and normalize
        return base_name.strip().lower()

    def generate_content_hash(self, content: str) -> str:
        """Generate SHA-256 hash of content for versioning"""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def calculate_similarity(self, content1: str, content2: str) -> float:
        """Calculate text similarity ratio using difflib"""
        return difflib.SequenceMatcher(None, content1, content2).ratio()

    def get_next_minor_version(self, base_name: str) -> str:
        """Get next minor version (v1.0 -> v1.1)"""
        if base_name not in self.document_versions:
            return "v1.0"

        versions = self.document_versions[base_name]
        if not versions:
            return "v1.0"

        # Find highest major version
        major_versions = {}
        for version_info in versions.values():
            major = int(version_info.split(".")[0][1:])
            minor = int(version_info.split(".")[1])
            if major not in major_versions or minor > major_versions[major]:
                major_versions[major] = minor

        latest_major = max(major_versions.keys())
        latest_minor = major_versions[latest_major]

        return f"v{latest_major}.{latest_minor + 1}"

    def get_next_major_version(self, base_name: str) -> str:
        """Get next major version (v1.1 -> v2.0)"""
        if base_name not in self.document_versions:
            return "v1.0"

        versions = self.document_versions[base_name]
        if not versions:
            return "v1.0"

        # Find highest major version
        major_versions = set()
        for version_info in versions.values():
            major = int(version_info.split(".")[0][1:])
            major_versions.add(major)

        if not major_versions:
            return "v1.0"

        latest_major = max(major_versions)
        return f"v{latest_major + 1}.0"

    def determine_version(
        self, content: str, filename: str, existing_documents: Dict[str, Dict] = None
    ) -> Tuple[str, bool, Optional[str]]:
        """
        Determine document version based on content similarity

        Returns:
            (version, is_duplicate, parent_document_id)
        """
        if existing_documents is None:
            existing_documents = {}

        base_name = self.extract_base_name(filename)
        content_hash = self.generate_content_hash(content)

        # Check if exact content already exists
        for doc_id, doc_info in existing_documents.items():
            if doc_info.get("content_hash") == content_hash:
                return doc_info.get("document_version", "v1.0"), True, doc_id

        # Check for similar documents by base name
        similar_docs = []
        for doc_id, doc_info in existing_documents.items():
            existing_base = self.extract_base_name(doc_info.get("filename", ""))

            if base_name == existing_base:
                similarity = self.calculate_similarity(
                    content, doc_info.get("content", "")
                )
                if similarity > self.similarity_thresholds["new"]:
                    similar_docs.append((doc_id, similarity, doc_info))

        if not similar_docs:
            # No similar documents found - new document
            return "v1.0", False, None

        # Sort by similarity (highest first)
        similar_docs.sort(key=lambda x: x[1], reverse=True)
        best_match_id, best_similarity, best_match_info = similar_docs[0]

        if best_similarity >= self.similarity_thresholds["minor"]:
            # Minor change
            new_version = self.get_next_minor_version(base_name)
            return new_version, True, best_match_id

        elif best_similarity >= self.similarity_thresholds["major"]:
            # Major change but same document
            new_version = self.get_next_major_version(base_name)
            return new_version, True, best_match_id

        else:
            # Different document despite similar name
            return "v1.0", False, None

    def register_document(
        self, document_id: str, filename: str, content: str, version: str
    ):
        """Register a document in the version tracking system"""
        base_name = self.extract_base_name(filename)
        content_hash = self.generate_content_hash(content)

        if base_name not in self.document_versions:
            self.document_versions[base_name] = {}

        self.document_versions[base_name][content_hash] = version
        logger.info(
            f"Registered document {document_id} as {version} for base '{base_name}'"
        )

    def get_document_versions(self, base_name: str) -> List[str]:
        """Get all versions for a given base document"""
        if base_name not in self.document_versions:
            return []

        return list(set(self.document_versions[base_name].values()))

    def get_version_info(self) -> Dict:
        """Get version tracking statistics"""
        total_base_docs = len(self.document_versions)
        total_versions = sum(
            len(versions) for versions in self.document_versions.values()
        )

        return {
            "total_base_documents": total_base_docs,
            "total_versions": total_versions,
            "avg_versions_per_document": total_versions / max(total_base_docs, 1),
            "base_documents": list(self.document_versions.keys()),
        }
