"""Retriever: symptom-based search and ranking of Q&A entries."""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple
from schema import QAEntry, SymptomIndexEntry, SearchResult, Symptom
from utils import (
    get_knowledge_base_dir,
    read_jsonl_file,
    read_json_file,
    get_qa_file_path,
    get_symptom_index_file_path,
    format_iso_datetime,
    truncate_text,
)


class Retriever:
    """Search and rank Q&A entries by symptom."""

    def __init__(self, kb_dir: Path = None):
        self.kb_dir = kb_dir or get_knowledge_base_dir()

    def search_by_symptoms(self, symptoms: List[str], limit: int = 5) -> List[SearchResult]:
        """
        Search Q&A entries by symptoms.

        Returns top-ranked matches based on:
        1. Exact symptom match
        2. Confidence score
        3. Recency
        4. Usage frequency

        Args:
            symptoms: List of symptom names to search for
            limit: Maximum number of results to return

        Returns:
            List of SearchResult objects, ranked by relevance
        """
        # Normalize and validate symptoms
        normalized_symptoms = [s.lower().strip() for s in symptoms]
        invalid = [s for s in normalized_symptoms if not Symptom.is_valid(s)]
        if invalid:
            print(f"Warning: invalid symptoms ignored: {', '.join(invalid)}")
            normalized_symptoms = [s for s in normalized_symptoms if Symptom.is_valid(s)]

        if not normalized_symptoms:
            return []

        # Load symptom index and QA entries
        symptom_index = self._load_symptom_index()
        qa_entries = self._load_qa_entries()

        if not qa_entries:
            return []

        # Find all relevant QA IDs
        relevant_qa_ids: Dict[str, Tuple[int, float, str]] = {}  # qa_id -> (match_count, confidence, reason)

        for symptom in normalized_symptoms:
            if symptom in symptom_index:
                entry = symptom_index[symptom]
                for qa_id in entry.qa_ids:
                    if qa_id not in relevant_qa_ids:
                        relevant_qa_ids[qa_id] = (0, 0.0, "")

                    # Update match count and record reason
                    match_count, _, _ = relevant_qa_ids[qa_id]
                    relevant_qa_ids[qa_id] = (match_count + 1, qa_entries[qa_id].confidence, f"matches symptom: {symptom}")

        if not relevant_qa_ids:
            return []

        # Rank by match count, confidence, recency, and usage
        results: List[Tuple[SearchResult, float]] = []

        for qa_id, (match_count, confidence, reason) in relevant_qa_ids.items():
            qa = qa_entries[qa_id]

            # Calculate match score
            # Higher match count is better
            match_score_factor = min(match_count / len(normalized_symptoms), 1.0)

            # Recency boost (newer is better)
            try:
                created = datetime.fromisoformat(qa.created_at.replace("Z", "+00:00"))
                now = datetime.utcnow().replace(tzinfo=created.tzinfo)
                days_old = (now - created).days
                recency_factor = 1.0 / (1.0 + days_old / 30.0)  # Decay over 30 days
            except Exception:
                recency_factor = 0.5

            # Usage boost (frequently used solutions are more trusted)
            usage_factor = min(qa.usage_count / 10.0, 1.0)  # Cap at 10 uses

            # Combined score
            final_score = (
                match_score_factor * 0.5 +
                confidence * 0.3 +
                recency_factor * 0.1 +
                usage_factor * 0.1
            )

            results.append((
                SearchResult(
                    qa_entry=qa,
                    match_type="exact" if match_count == len(normalized_symptoms) else "related",
                    match_score=final_score,
                    reason=reason
                ),
                final_score
            ))

        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)

        # Return top N results
        return [r[0] for r in results[:limit]]

    def _load_symptom_index(self) -> Dict[str, SymptomIndexEntry]:
        """Load symptom index from file."""
        symptom_index: Dict[str, SymptomIndexEntry] = {}
        qa_file = get_symptom_index_file_path(self.kb_dir)
        lines = read_jsonl_file(qa_file)

        for line in lines:
            try:
                entry = SymptomIndexEntry.from_json(line)
                symptom_index[entry.symptom] = entry
            except Exception as e:
                print(f"Warning: failed to parse symptom index entry: {e}")

        return symptom_index

    def _load_qa_entries(self) -> Dict[str, QAEntry]:
        """Load all QA entries from file."""
        qa_entries: Dict[str, QAEntry] = {}
        qa_file = get_qa_file_path(self.kb_dir)
        lines = read_jsonl_file(qa_file)

        for line in lines:
            try:
                entry = QAEntry.from_json(line)
                qa_entries[entry.id] = entry
            except Exception as e:
                print(f"Warning: failed to parse QA entry: {e}")

        return qa_entries

    def print_results(self, results: List[SearchResult]) -> None:
        """Pretty-print search results."""
        if not results:
            print("No matching solutions found.")
            return

        print(f"\nRelevant past solutions ({len(results)} found):\n")

        for i, result in enumerate(results, 1):
            qa = result.qa_entry
            print(f"{i}. Q: {qa.question}")
            print(f"   A: {truncate_text(qa.answer, 150)}")
            print(f"   Confidence: {qa.confidence:.1%} | Used: {qa.usage_count} times | Score: {result.match_score:.2f}")
            if qa.tags:
                print(f"   Tags: {', '.join(qa.tags)}")
            print()


def main():
    """CLI for retriever."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 retriever.py <symptom1> [symptom2] ...")
        print(f"\nValid symptoms: {', '.join(Symptom.all_symptoms())}")
        return

    symptoms = sys.argv[1:]
    retriever = Retriever()
    results = retriever.search_by_symptoms(symptoms, limit=10)
    retriever.print_results(results)


if __name__ == "__main__":
    main()
