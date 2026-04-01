# Issue Search Skill — Documentation Index

This directory contains a complete, offline-capable knowledge management system for capturing issues, analyzing root causes, and retrieving proven solutions.

## Getting Started (Start Here)

1. **[QUICKSTART.md](QUICKSTART.md)** — 5-minute setup and first use
   - Install & verify
   - Run tests
   - Capture first issue
   - Generate postmortem
   - Search solutions

2. **[SYSTEM_GUIDE.md](SYSTEM_GUIDE.md)** — Complete user guide
   - Why use this system
   - Core concepts
   - Command reference
   - Quality guidelines
   - Common questions

## For Developers

3. **[HOOKS.md](HOOKS.md)** — Automatic error detection via system-level hooks (NEW)
   - How hooks work (PostToolUse, UserPromptSubmit)
   - Symptom mapping
   - Hook lifecycle
   - Configuration and testing
   - Disabling hooks if needed

4. **[ARCHITECTURE.md](ARCHITECTURE.md)** — System design & internals
   - Module overview (schema, utils, indexer, retriever, cli)
   - Data models and validation
   - Storage strategy (JSONL, JSON, date partitioning)
   - Retrieval algorithm (ranking, scoring)
   - Performance characteristics
   - Future extensions

5. **[README.md](README.md)** — High-level overview
   - Purpose and principles
   - Directory structure
   - Data model
   - Symptom taxonomy
   - Retrieval behavior
   - Quality constraints

## Examples & Learning

6. **[EXAMPLE.md](EXAMPLE.md)** — Walkthrough with real examples
   - Capturing an issue
   - Investigating and generating postmortem
   - Retrieving solution
   - Complete data model examples
   - Command reference with examples

## Code Files

### Core Modules

- **schema.py** — Data models and validation
  - `Issue` — raw issue capture
  - `Postmortem` — structured analysis
  - `QAEntry` — derived Q&A
  - `SymptomIndexEntry` — index mapping
  - `Symptom` — controlled vocabulary (enum)

- **utils.py** — File operations and I/O
  - Directory management
  - File path helpers
  - JSONL append operations
  - File reading
  - Formatting utilities

- **indexer.py** — Q&A generation and indexing
  - `Indexer` class
  - `generate_qa_from_postmortem()` — derive Q&A from postmortem
  - `add_qa_entry()` — persist and index Q&A
  - `record_qa_usage()` — track usage and confidence
  - `link_issue_to_symptom_index()` — create mappings

- **retriever.py** — Symptom-based search and ranking
  - `Retriever` class
  - `search_by_symptoms()` — find relevant Q&A entries
  - Multi-factor ranking algorithm
  - Result formatting

- **cli.py** — Command-line interface
  - `capture` — record issue
  - `postmortem` — generate analysis
  - `search` — find solutions
  - `list` — show issues
  - `show-issue`, `show-postmortem` — details
  - `stats` — knowledge base size

### Testing

- **test_system.py** — Comprehensive test suite
  - Schema validation
  - Serialization round-trips
  - Q&A generation
  - Indexing
  - Retrieval and ranking
  - End-to-end workflow

## File Organization

```
skill_maker/
├── INDEX.md                 ← You are here
├── README.md                ← Quick overview
├── QUICKSTART.md            ← 5-minute setup
├── SYSTEM_GUIDE.md          ← Complete user guide
├── ARCHITECTURE.md          ← System design
├── EXAMPLE.md               ← Walkthrough examples
│
├── schema.py                ← Data models
├── utils.py                 ← File I/O helpers
├── indexer.py               ← Q&A generation
├── retriever.py             ← Search and ranking
├── cli.py                   ← Command-line interface
├── test_system.py           ← Test suite
│
└── .gitignore
```

## Quick Reference

### Common Commands

```bash
# Capture an issue
python3 cli.py capture --description "..." --symptoms timeout

# Generate postmortem
python3 cli.py postmortem --issue-id {uuid} --root-cause "..." --resolution "..." --prevention "..."

# Search solutions
python3 cli.py search --symptom timeout

# List recent issues
python3 cli.py list --limit 10

# Show issue details
python3 cli.py show-issue {uuid}

# View statistics
python3 cli.py stats
```

### Valid Symptoms

- `timeout` — operation exceeded time limit
- `latency_high` — response time unusually slow
- `api_error` — HTTP error response
- `schema_mismatch` — data structure incompatibility
- `null_pointer` — null/undefined reference
- `auth_failure` — authentication/authorization failure
- `rate_limit` — exceeded rate limits
- `dependency_failure` — external service unavailable
- `config_error` — misconfiguration
- `race_condition` — concurrent access issue
- `memory_leak` — unbounded memory growth
- `crash` — process termination
- `data_loss` — unintended data deletion
- `corruption` — data integrity violation

## Knowledge Base Location

All data: `~/.knowledge_base/`

```
issues/           → date-partitioned issue captures
postmortems/      → date-partitioned postmortems
qa/               → searchable Q&A entries
symptom_index/    → symptom-to-QA mappings
meta/             → metadata (future use)
```

## Design Philosophy

- **Local-first**: No network, no external APIs
- **Append-only**: Durability through immutability
- **Human-readable**: All JSON/JSONL, inspectable
- **Zero dependencies**: Python standard library only
- **Offline-capable**: Complete functionality without connectivity

## Workflow Overview

```
CAPTURE ISSUE → INVESTIGATE → GENERATE POSTMORTEM → INDEX Q&A → RETRIEVE SOLUTION
   (Day 1)      (Team work)        (Knowledge)    (Searchable)    (Next occurrence)
   5 minutes    N hours         10 minutes         Automatic       < 1 minute
```

## ROI Example

- **Cost**: 15 minutes to capture and postmortem one issue
- **Value**: Prevent 2 hours of investigation when it recurs
- **ROI**: 12:1 or better
- **Scaling**: Grows more valuable as knowledge base grows

## Next Steps

1. **Read**: Start with [QUICKSTART.md](QUICKSTART.md)
2. **Run**: `python3 test_system.py`
3. **Practice**: Capture your first issue
4. **Learn**: Refer to [SYSTEM_GUIDE.md](SYSTEM_GUIDE.md) for details
5. **Dive deep**: See [ARCHITECTURE.md](ARCHITECTURE.md) for internals

## Key Files to Read

| File | Purpose | Time |
|------|---------|------|
| QUICKSTART.md | Get started quickly | 5 min |
| HOOKS.md | Understand automatic error detection | 5 min |
| SYSTEM_GUIDE.md | Understand the system | 20 min |
| ARCHITECTURE.md | Learn how it works | 30 min |
| EXAMPLE.md | See real examples | 10 min |
| test_system.py | Verify system works | 2 min |

## Key Code to Review

| File | Purpose |
|------|---------|
| schema.py | Data models (60 lines) |
| utils.py | File I/O (90 lines) |
| indexer.py | Q&A generation (150 lines) |
| retriever.py | Search and ranking (100 lines) |
| cli.py | CLI interface (320 lines) |

**Total**: ~750 lines of code (excluding tests and docs)

## Extensibility

The system is designed to be extended. Potential future enhancements:

- **Negative signal tracking** — record failed attempts
- **Confidence decay** — reduce old, unused solutions
- **Symptom relationships** — learn which symptoms co-occur
- **Full-text search** — search question/answer content
- **Environment filtering** — refine by backend/OS/infra
- **User feedback** — rate solution helpfulness
- **Related issues** — cluster similar problems
- **Export/reports** — generate documentation

See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

## Support

- **How do I use this?** → [QUICKSTART.md](QUICKSTART.md)
- **I have a question** → [SYSTEM_GUIDE.md](SYSTEM_GUIDE.md) (Common Questions section)
- **I want to understand the design** → [ARCHITECTURE.md](ARCHITECTURE.md)
- **I want to see an example** → [EXAMPLE.md](EXAMPLE.md)
- **I want to run the tests** → `python3 test_system.py`
- **I want to modify the code** → [ARCHITECTURE.md](ARCHITECTURE.md) (Code reference)

## License

This system is free to use, modify, and distribute.

---

**Start with [QUICKSTART.md](QUICKSTART.md) →**
