"""Utility functions for file and directory operations."""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


def get_knowledge_base_dir() -> Path:
    """Get or create the knowledge base directory."""
    kb_dir = Path.home() / ".knowledge_base"
    subdirs = ["issues", "postmortems", "qa", "symptom_index", "meta"]
    for subdir in subdirs:
        (kb_dir / subdir).mkdir(parents=True, exist_ok=True)
    return kb_dir


def get_date_partition() -> str:
    """Get current date in YYYY-MM-DD format for partitioning."""
    return datetime.utcnow().strftime("%Y-%m-%d")


def ensure_dir(path: Path) -> Path:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_jsonl_line(file_path: Path, line: str) -> None:
    """Append a line to JSONL file (append-only)."""
    ensure_dir(file_path.parent)
    with open(file_path, "a") as f:
        f.write(line + "\n")


def read_jsonl_file(file_path: Path) -> List[str]:
    """Read JSONL file, return list of JSON lines."""
    if not file_path.exists():
        return []
    with open(file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def write_json_file(file_path: Path, data: Dict[str, Any]) -> None:
    """Write JSON file."""
    ensure_dir(file_path.parent)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def read_json_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """Read JSON file."""
    if not file_path.exists():
        return None
    with open(file_path, "r") as f:
        return json.load(f)


def get_issue_file_path(kb_dir: Path, issue_id: str, partition: str) -> Path:
    """Get file path for issue storage."""
    return kb_dir / "issues" / partition / f"issue_{issue_id}.jsonl"


def get_postmortem_file_path(kb_dir: Path, issue_id: str, partition: str) -> Path:
    """Get file path for postmortem storage."""
    return kb_dir / "postmortems" / partition / f"postmortem_{issue_id}.json"


def get_qa_file_path(kb_dir: Path) -> Path:
    """Get file path for QA index."""
    return kb_dir / "qa" / "qa_index.jsonl"


def get_symptom_index_file_path(kb_dir: Path) -> Path:
    """Get file path for symptom index."""
    return kb_dir / "symptom_index" / "symptom_index.jsonl"


def get_global_index_file_path(kb_dir: Path) -> Path:
    """Get file path for global index."""
    return kb_dir / "meta" / "global_index.jsonl"


def list_issues_by_date(kb_dir: Path, partition: str) -> List[str]:
    """List all issue files for a given date partition."""
    partition_dir = kb_dir / "issues" / partition
    if not partition_dir.exists():
        return []
    return sorted([f.name for f in partition_dir.glob("issue_*.jsonl")])


def list_postmortems_by_date(kb_dir: Path, partition: str) -> List[str]:
    """List all postmortem files for a given date partition."""
    partition_dir = kb_dir / "postmortems" / partition
    if not partition_dir.exists():
        return []
    return sorted([f.name for f in partition_dir.glob("postmortem_*.json")])


def list_all_dates(kb_dir: Path) -> List[str]:
    """List all date partitions that have issues."""
    issues_dir = kb_dir / "issues"
    if not issues_dir.exists():
        return []
    return sorted([d.name for d in issues_dir.iterdir() if d.is_dir()])


def format_iso_datetime(iso_str: str) -> str:
    """Format ISO datetime for display."""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except Exception:
        return iso_str


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length, add ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
