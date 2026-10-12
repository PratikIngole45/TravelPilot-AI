from typing import List, Set
from app.schemas.retrieval import SourceCitation


class CitationValidator:
    """
    Validates that cited sources in LLM outputs exist in retrieved documents or tool results.
    Prevents hallucinated references.
    """

    @staticmethod
    def validate_citations(
        claimed_source_ids: List[str],
        valid_source_ids: Set[str]
    ) -> List[str]:
        """
        Returns only the source IDs that are confirmed present in valid_source_ids.
        """
        return [sid for sid in claimed_source_ids if sid in valid_source_ids]

    @staticmethod
    def filter_citations(
        citations: List[SourceCitation],
        valid_source_ids: Set[str]
    ) -> List[SourceCitation]:
        """
        Filters list of SourceCitation objects against allowlist of retrieved source IDs.
        """
        return [c for c in citations if c.source_id in valid_source_ids]
