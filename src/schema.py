"""Data models and validation for the Issue Search Skill."""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid


class IssueSource(Enum):
    """Source of issue reporting."""
    USER = "user"
    SYSTEM = "system"


class Symptom(Enum):
    """Controlled vocabulary of symptoms."""
    TIMEOUT = "timeout"
    LATENCY_HIGH = "latency_high"
    API_ERROR = "api_error"
    SCHEMA_MISMATCH = "schema_mismatch"
    NULL_POINTER = "null_pointer"
    AUTH_FAILURE = "auth_failure"
    RATE_LIMIT = "rate_limit"
    DEPENDENCY_FAILURE = "dependency_failure"
    CONFIG_ERROR = "config_error"
    RACE_CONDITION = "race_condition"
    MEMORY_LEAK = "memory_leak"
    CRASH = "crash"
    DATA_LOSS = "data_loss"
    CORRUPTION = "corruption"

    @classmethod
    def is_valid(cls, symptom: str) -> bool:
        """Check if symptom is in controlled vocabulary."""
        return symptom in [s.value for s in cls]

    @classmethod
    def all_symptoms(cls) -> List[str]:
        """Return all valid symptoms."""
        return [s.value for s in cls]


@dataclass
class Environment:
    """Environment context for an issue."""
    backend: Optional[str] = None
    frontend: Optional[str] = None
    infra: Optional[str] = None
    language: Optional[str] = None
    os: Optional[str] = None

    def to_dict(self) -> Dict[str, Optional[str]]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class Issue:
    """Raw issue capture."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source: str = IssueSource.USER.value
    description: str = ""
    symptoms: List[str] = field(default_factory=list)
    environment: Environment = field(default_factory=Environment)
    raw_context: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False

    def validate(self) -> List[str]:
        """Validate issue. Return list of errors."""
        errors = []
        if not self.description or len(self.description.strip()) == 0:
            errors.append("description is required")
        if not self.source in [IssueSource.USER.value, IssueSource.SYSTEM.value]:
            errors.append(f"source must be 'user' or 'system', got '{self.source}'")
        for symptom in self.symptoms:
            if not Symptom.is_valid(symptom):
                errors.append(f"invalid symptom: '{symptom}'. valid symptoms: {', '.join(Symptom.all_symptoms())}")
        return errors

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(asdict(self), default=str)

    @classmethod
    def from_json(cls, json_str: str) -> "Issue":
        """Deserialize from JSON."""
        data = json.loads(json_str)
        data['environment'] = Environment(**data.get('environment', {}))
        return cls(**data)


@dataclass
class PostmortemTimeline:
    """Timeline entry in postmortem."""
    timestamp: str
    event: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Postmortem:
    """Structured postmortem derived from issue."""
    id: str  # same as issue id
    issue_id: str
    summary: str
    symptoms: List[str] = field(default_factory=list)
    timeline: List[PostmortemTimeline] = field(default_factory=list)
    root_cause: str = ""
    resolution: str = ""
    prevention: str = ""
    impact: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def validate(self) -> List[str]:
        """Validate postmortem. Return list of errors."""
        errors = []
        if not self.id or len(self.id.strip()) == 0:
            errors.append("id is required")
        if not self.issue_id or len(self.issue_id.strip()) == 0:
            errors.append("issue_id is required")
        if not self.summary or len(self.summary.strip()) == 0:
            errors.append("summary is required")
        if not self.root_cause or len(self.root_cause.strip()) == 0:
            errors.append("root_cause is required and must be specific and technical")
        if not self.resolution or len(self.resolution.strip()) == 0:
            errors.append("resolution is required and must describe what actually fixed the issue")
        if not self.prevention or len(self.prevention.strip()) == 0:
            errors.append("prevention is required and must describe how to avoid recurrence")
        for symptom in self.symptoms:
            if not Symptom.is_valid(symptom):
                errors.append(f"invalid symptom: '{symptom}'")
        return errors

    def to_json(self) -> str:
        """Serialize to JSON."""
        data = asdict(self)
        data['timeline'] = [t.to_dict() if isinstance(t, PostmortemTimeline) else t for t in data['timeline']]
        return json.dumps(data, default=str, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "Postmortem":
        """Deserialize from JSON."""
        data = json.loads(json_str)
        data['timeline'] = [PostmortemTimeline(**t) if isinstance(t, dict) else t for t in data.get('timeline', [])]
        return cls(**data)


@dataclass
class QAEntry:
    """Derived Q&A entry from postmortem."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    question: str = ""
    answer: str = ""
    tags: List[str] = field(default_factory=list)
    confidence: float = 0.8  # 0.0 to 1.0
    source_issue_id: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    usage_count: int = 0
    last_used: Optional[str] = None

    def validate(self) -> List[str]:
        """Validate Q&A entry. Return list of errors."""
        errors = []
        if not self.question or len(self.question.strip()) == 0:
            errors.append("question is required")
        if not self.answer or len(self.answer.strip()) == 0:
            errors.append("answer is required and must be concise and actionable")
        if not 0.0 <= self.confidence <= 1.0:
            errors.append(f"confidence must be between 0.0 and 1.0, got {self.confidence}")
        if not self.source_issue_id:
            errors.append("source_issue_id is required for traceability")
        return errors

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(asdict(self), default=str)

    @classmethod
    def from_json(cls, json_str: str) -> "QAEntry":
        """Deserialize from JSON."""
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class SymptomIndexEntry:
    """Symptom index entry for fast retrieval."""
    symptom: str
    issue_ids: List[str] = field(default_factory=list)
    qa_ids: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    def to_json(self) -> str:
        """Serialize to JSON."""
        return json.dumps(asdict(self), default=str)

    @classmethod
    def from_json(cls, json_str: str) -> "SymptomIndexEntry":
        """Deserialize from JSON."""
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class SearchResult:
    """Result from symptom-based search."""
    qa_entry: QAEntry
    match_type: str  # "exact" | "related"
    match_score: float  # 0.0 to 1.0
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "qa_entry": json.loads(self.qa_entry.to_json()),
            "match_type": self.match_type,
            "match_score": self.match_score,
            "reason": self.reason
        }
