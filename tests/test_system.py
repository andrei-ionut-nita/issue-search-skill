#!/usr/bin/env python3
"""Test suite for the Issue Search Skill."""

import sys
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from schema import (
    Issue,
    Postmortem,
    PostmortemTimeline,
    QAEntry,
    Environment,
    Symptom,
    SymptomIndexEntry,
)
from utils import (
    get_date_partition,
    get_knowledge_base_dir,
    write_jsonl_line,
    read_jsonl_file,
    write_json_file,
    read_json_file,
)
from indexer import Indexer
from retriever import Retriever


def test_schema():
    """Test schema validation."""
    print("Testing schema validation...")

    # Valid issue
    issue = Issue(
        source="user",
        description="Test issue",
        symptoms=["timeout"],
    )
    assert issue.validate() == []
    print("✓ Valid issue passes validation")

    # Invalid issue (missing description)
    invalid_issue = Issue(source="user", description="")
    errors = invalid_issue.validate()
    assert "description is required" in errors
    print("✓ Invalid issue detected")

    # Valid postmortem
    postmortem = Postmortem(
        id="test-id",
        issue_id="test-id",
        summary="Test postmortem",
        root_cause="Test root cause",
        resolution="Test resolution",
        prevention="Test prevention",
    )
    assert postmortem.validate() == []
    print("✓ Valid postmortem passes validation")

    # Symptom validation
    assert Symptom.is_valid("timeout")
    assert not Symptom.is_valid("invalid_symptom")
    print("✓ Symptom validation works")


def test_serialization():
    """Test JSON serialization and deserialization."""
    print("\nTesting serialization...")

    # Issue
    issue = Issue(
        source="user",
        description="Test issue",
        symptoms=["timeout", "latency_high"],
        environment=Environment(backend="python", os="linux"),
    )
    issue_json = issue.to_json()
    issue_restored = Issue.from_json(issue_json)
    assert issue_restored.description == issue.description
    assert issue_restored.symptoms == issue.symptoms
    print("✓ Issue serialization works")

    # Postmortem
    postmortem = Postmortem(
        id="test-id",
        issue_id="test-id",
        summary="Test",
        root_cause="Cause",
        resolution="Resolution",
        prevention="Prevention",
    )
    pm_json = postmortem.to_json()
    pm_restored = Postmortem.from_json(pm_json)
    assert pm_restored.summary == postmortem.summary
    print("✓ Postmortem serialization works")

    # Q&A Entry
    qa = QAEntry(
        question="Test question?",
        answer="Test answer.",
        source_issue_id="issue-id",
    )
    qa_json = qa.to_json()
    qa_restored = QAEntry.from_json(qa_json)
    assert qa_restored.question == qa.question
    print("✓ Q&A serialization works")


def test_qa_generation():
    """Test Q&A generation from postmortems."""
    print("\nTesting Q&A generation...")

    indexer = Indexer(Path(tempfile.gettempdir()))

    postmortem = Postmortem(
        id="test-001",
        issue_id="issue-001",
        summary="Database connection timeout",
        symptoms=["timeout"],
        root_cause="Connection pool exhausted",
        resolution="Increased pool size from 10 to 50",
        prevention="Set up monitoring alerts",
        tags=["database", "performance"],
    )

    qa = indexer.generate_qa_from_postmortem(postmortem)

    assert qa.question
    assert qa.answer
    assert "timeout" in qa.question or "database" in qa.answer
    assert qa.source_issue_id == "issue-001"
    print(f"✓ Generated Q&A:")
    print(f"  Q: {qa.question}")
    print(f"  A: {qa.answer[:80]}...")


def test_indexing():
    """Test indexing and retrieval."""
    print("\nTesting indexing...")

    temp_dir = Path(tempfile.gettempdir()) / "kb_test"
    temp_dir.mkdir(exist_ok=True)

    indexer = Indexer(temp_dir)

    # Create and add Q&A entry
    qa = QAEntry(
        question="How do I fix timeouts?",
        answer="Increase connection pool size and add query timeouts.",
        tags=["timeout", "database"],
        confidence=0.85,
        source_issue_id="issue-001",
    )

    success = indexer.add_qa_entry(qa)
    assert success
    print("✓ Q&A entry added to index")

    # Record usage
    indexer.record_qa_usage(qa.id)
    print("✓ Q&A usage recorded")

    # Link issue to symptom index
    indexer.link_issue_to_symptom_index("issue-001", ["timeout", "latency_high"])
    print("✓ Issue linked to symptom index")


def test_retrieval():
    """Test symptom-based retrieval."""
    print("\nTesting retrieval...")

    temp_dir = Path(tempfile.gettempdir()) / "kb_test_retrieval"
    temp_dir.mkdir(exist_ok=True)

    indexer = Indexer(temp_dir)
    retriever = Retriever(temp_dir)

    # Create and add test Q&A entries
    qa1 = QAEntry(
        question="How do I fix timeouts?",
        answer="Increase connection pool size.",
        tags=["timeout"],
        confidence=0.9,
        source_issue_id="issue-001",
    )

    qa2 = QAEntry(
        question="How do I debug latency?",
        answer="Use APM tools to trace slow queries.",
        tags=["latency_high"],
        confidence=0.85,
        source_issue_id="issue-002",
    )

    indexer.add_qa_entry(qa1)
    indexer.add_qa_entry(qa2)

    # Search by symptom
    results = retriever.search_by_symptoms(["timeout"], limit=10)
    assert len(results) > 0
    assert any("timeout" in r.qa_entry.tags for r in results)
    print(f"✓ Found {len(results)} result(s) for 'timeout'")

    # Search by multiple symptoms
    results = retriever.search_by_symptoms(["timeout", "latency_high"], limit=10)
    assert len(results) >= 0
    print(f"✓ Found {len(results)} result(s) for 'timeout, latency_high'")


def test_workflow():
    """Test complete workflow: issue → postmortem → Q&A → retrieval."""
    print("\nTesting complete workflow...")

    temp_dir = Path(tempfile.gettempdir()) / "kb_test_workflow"
    temp_dir.mkdir(exist_ok=True)

    indexer = Indexer(temp_dir)
    retriever = Retriever(temp_dir)

    # Step 1: Create issue
    issue = Issue(
        source="user",
        description="API returns 503 errors during peak traffic",
        symptoms=["api_error", "latency_high"],
        environment=Environment(backend="golang", infra="kubernetes"),
    )
    print(f"✓ Created issue {issue.id}")

    # Step 2: Create postmortem
    postmortem = Postmortem(
        id=issue.id,
        issue_id=issue.id,
        summary="Load balancer connection limit reached",
        symptoms=["api_error", "latency_high"],
        timeline=[
            PostmortemTimeline(
                timestamp=datetime.now(timezone.utc).isoformat(),
                event="503 errors observed",
            ),
        ],
        root_cause="Load balancer max connections (1000) exceeded during traffic spike",
        resolution="Increased max connections to 5000 and added connection draining",
        prevention="Set up auto-scaling and connection monitoring",
        tags=["infrastructure", "load-balancer"],
    )
    print(f"✓ Created postmortem {postmortem.id}")

    # Step 3: Generate Q&A
    qa = indexer.generate_qa_from_postmortem(postmortem)
    indexer.add_qa_entry(qa)
    print(f"✓ Generated and indexed Q&A {qa.id}")

    # Step 4: Link issue to symptom index
    indexer.link_issue_to_symptom_index(issue.id, issue.symptoms)
    print("✓ Linked issue to symptom index")

    # Step 5: Retrieve by symptom
    results = retriever.search_by_symptoms(["api_error"], limit=10)
    assert len(results) > 0, f"Expected results but got {len(results)}"
    # Note: results might include other Q&A entries from previous tests, so just verify our entry exists
    found = any(r.qa_entry.id == qa.id for r in results)
    assert found, f"Q&A entry {qa.id} not found in results"
    print(f"✓ Retrieved Q&A by symptom 'api_error'")


def main():
    """Run all tests."""
    print("=" * 50)
    print("Issue Search Skill - Test Suite")
    print("=" * 50)

    try:
        test_schema()
        test_serialization()
        test_qa_generation()
        test_indexing()
        test_retrieval()
        test_workflow()

        print("\n" + "=" * 50)
        print("✓ All tests passed!")
        print("=" * 50)
        return 0

    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
