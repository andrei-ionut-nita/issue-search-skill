"""Indexer: Q&A generation and index maintenance."""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict
from schema import (
    Issue,
    Postmortem,
    QAEntry,
    SymptomIndexEntry,
    Symptom,
)
from utils import (
    get_knowledge_base_dir,
    get_postmortem_file_path,
    get_qa_file_path,
    get_symptom_index_file_path,
    write_jsonl_line,
    read_jsonl_file,
)


class Indexer:
    """Generate Q&A entries from postmortems and maintain indices."""

    def __init__(self, kb_dir: Path = None):
        self.kb_dir = kb_dir or get_knowledge_base_dir()

    def generate_qa_from_postmortem(self, postmortem: Postmortem) -> QAEntry:
        """
        Derive a Q&A entry from a postmortem.

        Quality constraints:
        - Question must be a realistic developer question
        - Answer must be concise, actionable, derived strictly from postmortem
        - No generic phrasing
        - No speculation beyond the postmortem

        Args:
            postmortem: Postmortem object

        Returns:
            QAEntry derived from postmortem
        """
        # Derive question from symptoms + summary
        question = self._generate_question(postmortem)

        # Derive answer from resolution + prevention
        answer = self._generate_answer(postmortem)

        # Create Q&A entry
        # Tags should include symptoms for indexing
        qa_tags = list(set(postmortem.symptoms + postmortem.tags))
        qa_entry = QAEntry(
            question=question,
            answer=answer,
            tags=qa_tags,
            confidence=0.8,  # Start with baseline confidence
            source_issue_id=postmortem.issue_id,
            created_at=postmortem.created_at,
        )

        return qa_entry

    def _generate_question(self, postmortem: Postmortem) -> str:
        """Generate realistic developer question from postmortem."""
        # Question format: "How do I [resolve symptom]?" or "What causes [symptom]?"

        if not postmortem.symptoms:
            # Fall back to summary if no symptoms
            return f"How do I resolve: {postmortem.summary}?"

        symptom = postmortem.symptoms[0]
        symptom_friendly = symptom.replace("_", " ")

        if postmortem.symptoms[0] in ["api_error", "timeout", "latency_high"]:
            return f"How do I debug {symptom_friendly} in {postmortem.summary}?"
        elif postmortem.symptoms[0] in ["config_error"]:
            return f"Why does {postmortem.summary} result in {symptom_friendly}?"
        else:
            return f"How do I resolve {symptom_friendly} when {postmortem.summary}?"

    def _generate_answer(self, postmortem: Postmortem) -> str:
        """Generate actionable answer from postmortem."""
        # Answer includes: root cause + resolution + prevention

        parts = []

        if postmortem.root_cause:
            parts.append(f"Root cause: {postmortem.root_cause}")

        if postmortem.resolution:
            parts.append(f"Resolution: {postmortem.resolution}")

        if postmortem.prevention:
            parts.append(f"Prevention: {postmortem.prevention}")

        return " | ".join(parts)

    def add_qa_entry(self, qa_entry: QAEntry) -> bool:
        """
        Persist Q&A entry and update indices.

        Args:
            qa_entry: QAEntry to persist

        Returns:
            True if successful, False otherwise
        """
        # Validate
        errors = qa_entry.validate()
        if errors:
            print(f"Invalid Q&A entry: {', '.join(errors)}")
            return False

        # Write to QA index
        qa_file = get_qa_file_path(self.kb_dir)
        try:
            write_jsonl_line(qa_file, qa_entry.to_json())
        except Exception as e:
            print(f"Failed to write QA entry: {e}")
            return False

        # Update symptom index
        for symptom in qa_entry.tags:
            if Symptom.is_valid(symptom):
                self._add_qa_to_symptom_index(symptom, qa_entry.id)

        return True

    def _add_qa_to_symptom_index(self, symptom: str, qa_id: str) -> None:
        """Add QA entry to symptom index."""
        symptom_file = get_symptom_index_file_path(self.kb_dir)

        # Load existing index
        symptom_entries: Dict[str, SymptomIndexEntry] = {}
        lines = read_jsonl_file(symptom_file)
        for line in lines:
            try:
                entry = SymptomIndexEntry.from_json(line)
                symptom_entries[entry.symptom] = entry
            except Exception:
                pass

        # Update or create entry
        if symptom not in symptom_entries:
            symptom_entries[symptom] = SymptomIndexEntry(symptom=symptom)

        entry = symptom_entries[symptom]
        if qa_id not in entry.qa_ids:
            entry.qa_ids.append(qa_id)

        # Rewrite entire file
        symptom_file.parent.mkdir(parents=True, exist_ok=True)
        with open(symptom_file, "w") as f:
            for entry in symptom_entries.values():
                f.write(entry.to_json() + "\n")

    def link_issue_to_symptom_index(self, issue_id: str, symptoms: List[str]) -> None:
        """Link issue to symptom index for fast retrieval."""
        symptom_file = get_symptom_index_file_path(self.kb_dir)

        # Load existing index
        symptom_entries: Dict[str, SymptomIndexEntry] = {}
        lines = read_jsonl_file(symptom_file)
        for line in lines:
            try:
                entry = SymptomIndexEntry.from_json(line)
                symptom_entries[entry.symptom] = entry
            except Exception:
                pass

        # Update entries
        for symptom in symptoms:
            if not Symptom.is_valid(symptom):
                continue

            if symptom not in symptom_entries:
                symptom_entries[symptom] = SymptomIndexEntry(symptom=symptom)

            entry = symptom_entries[symptom]
            if issue_id not in entry.issue_ids:
                entry.issue_ids.append(issue_id)

        # Rewrite entire file
        symptom_file.parent.mkdir(parents=True, exist_ok=True)
        with open(symptom_file, "w") as f:
            for entry in symptom_entries.values():
                f.write(entry.to_json() + "\n")

    def record_qa_usage(self, qa_id: str) -> None:
        """
        Increment usage count and update last_used timestamp for a Q&A entry.

        This increases confidence in frequently-used solutions.
        """
        qa_file = get_qa_file_path(self.kb_dir)

        # Load all entries
        entries: Dict[str, QAEntry] = {}
        lines = read_jsonl_file(qa_file)
        for line in lines:
            try:
                entry = QAEntry.from_json(line)
                entries[entry.id] = entry
            except Exception:
                pass

        # Update target entry
        if qa_id not in entries:
            return

        entry = entries[qa_id]
        entry.usage_count += 1
        entry.last_used = datetime.utcnow().isoformat() + "Z"

        # Increase confidence gradually (cap at 0.95)
        entry.confidence = min(entry.confidence + 0.02, 0.95)

        # Rewrite entire file
        qa_file.parent.mkdir(parents=True, exist_ok=True)
        with open(qa_file, "w") as f:
            for e in entries.values():
                f.write(e.to_json() + "\n")


def main():
    """CLI for testing indexer."""
    from schema import Postmortem, PostmortemTimeline

    indexer = Indexer()

    # Test postmortem
    postmortem = Postmortem(
        id="test-001",
        issue_id="issue-001",
        summary="Database connection timeout under load",
        symptoms=["timeout", "latency_high"],
        timeline=[
            PostmortemTimeline(
                timestamp=datetime.utcnow().isoformat() + "Z",
                event="Received timeout error in production"
            ),
        ],
        root_cause="Connection pool was exhausted due to long-running queries not being cancelled",
        resolution="Added query timeout of 30s and implemented connection pool draining",
        prevention="Monitor connection pool utilization and set up alerts for > 80% usage",
        tags=["database", "connection", "performance"],
    )

    # Generate Q&A
    qa_entry = indexer.generate_qa_from_postmortem(postmortem)
    print("Generated Q&A:")
    print(f"Q: {qa_entry.question}")
    print(f"A: {qa_entry.answer}")
    print()

    # Add to index
    success = indexer.add_qa_entry(qa_entry)
    print(f"Added to index: {success}")


if __name__ == "__main__":
    main()
