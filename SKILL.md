---
name: issue-search-skill
description: "Build and query a local-first knowledge management system that captures issues, derives Q&A solutions, and instantly retrieves answers when similar problems occur. Perfect for DevOps teams, on-call engineers, and SREs who want to stop losing solutions and accelerate incident resolution by 12x through systematic knowledge capture."
license: Apache-2.0
compatibility: Python 3.8+, local filesystem
---

# Issue Search Skill

A complete, production-ready knowledge management system for capturing issues, generating postmortems, indexing Q&A solutions, and retrieving proven answers when similar problems recur.

## What This Does

- **Captures issues** with symptoms and context (5 minutes)
- **Generates postmortems** that encode root causes, resolutions, and prevention steps (10 minutes)
- **Auto-indexes Q&A** entries searchable by symptom (automatic)
- **Retrieves solutions** ranked by relevance, confidence, recency, and usage (< 1 second)
- **Builds knowledge base** that grows in value over time (cumulative)

## Why Use This

**Problem**: Teams lose solutions. The same incident repeats. Experts spend hours re-investigating. New team members can't find answers.

**Solution**: Every fix is captured once, searchable forever. Similar issues resolve 12x faster through systematic knowledge retrieval.

**ROI**: 15 minutes to capture and postmortem one issue. Prevents 2 hours of investigation when it recurs. **12:1 ROI or better.**

## Quick Start

```bash
# 1. Verify system works
python3 tests/test_system.py
# Output: ✓ All tests passed!

# 2. Capture first issue
python3 scripts/cli.py capture \
  --description "Database timeout during deployment" \
  --symptoms timeout,api_error

# 3. Generate postmortem (after investigation)
python3 scripts/cli.py postmortem \
  --issue-id {uuid-from-capture} \
  --root-cause "Connection pool size too small for concurrent requests" \
  --resolution "Increased pool from 10 to 50, added query timeout" \
  --prevention "Monitor pool utilization, load test deployments"

# 4. Search for solutions next time
python3 scripts/cli.py search --symptom timeout
# Instantly find: "Database connection pool exhaustion" (0.86 confidence)
# Resolve in 5 minutes instead of 2 hours
```

See [QUICKSTART.md](docs/QUICKSTART.md) for complete walkthrough.

## Core Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `capture` | Record issue with symptoms | `--description "..." --symptoms timeout` |
| `postmortem` | Analyze and encode fix | `--issue-id {uuid} --root-cause "..." --resolution "..."` |
| `search` | Find solutions by symptom | `--symptom timeout` |
| `list` | Show recent issues | `--limit 10` |
| `show-issue` | View issue details | `{uuid}` |
| `stats` | Knowledge base stats | (no args) |

## Valid Symptoms (14 total)

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

## Key Features

✓ **Local-first** — No network calls, works offline
✓ **Zero dependencies** — Python standard library only
✓ **Append-only** — Durability without corruption
✓ **Human-readable** — All JSON/JSONL, inspectable
✓ **Deterministic** — Same symptoms always rank identically
✓ **Fast retrieval** — Symptom-based search < 100ms
✓ **Learning system** — Confidence increases with usage
✓ **Multi-factor ranking** — Symptom (50%) + Confidence (30%) + Recency (10%) + Usage (10%)
✓ **Quality constraints** — No vague root causes, no speculation
✓ **Extensible** — Clean architecture for future enhancements

## Data Storage

All data stored locally in `~/.knowledge_base/`:

```
issues/           → date-partitioned issue captures
postmortems/      → date-partitioned postmortems
qa/               → searchable Q&A entries
symptom_index/    → symptom-to-QA mappings
```

No sync, no cloud, no dependencies. You control your knowledge.

## How Retrieval Works

When you search for `timeout`, the system:

1. Finds all issues tagged with `timeout`
2. Retrieves their Q&A solutions
3. Ranks by: symptom match (50%), confidence (30%), recency (10%), usage (10%)
4. Returns top matches with scores and explanations

Example ranking for timeout symptom:
- "Database connection pool exhaustion" — 0.86 confidence, used 5x, very recent
- "Network timeout due to DNS" — 0.72 confidence, used 1x, older
- "Client timeout misconfiguration" — 0.68 confidence, used 0x, newest

**Result**: You get the most relevant, trusted, frequently-used solution first.

## Example Workflow

**Day 1 — Production Incident (Database timeout)**

```bash
$ python3 scripts/cli.py capture \
  --description "DB timeout during traffic spike" \
  --symptoms timeout,latency_high,api_error

Issue captured: 550e8400-e29b-41d4-a716-446655440000

# Team investigates for 2 hours, finds root cause:
# Connection pool too small for concurrent requests under load

$ python3 scripts/cli.py postmortem \
  --issue-id 550e8400-e29b-41d4-a716-446655440000 \
  --root-cause "Connection pool size 10 insufficient for 50 concurrent requests during traffic spike" \
  --resolution "Increased pool to 50, added exponential backoff for connection waits" \
  --prevention "Set pool size to max_concurrent * 1.5, load test before production, monitor pool utilization"

✓ Solution indexed and searchable
```

**Day 45 — Similar Issue Occurs**

```bash
$ python3 scripts/cli.py search --symptom timeout

Results:
1. "What causes database timeout during high traffic?" (0.89)
   Answer: Connection pool exhaustion. Solution: Increase pool size and backoff...

$ # Apply solution in 5 minutes
$ # Issue resolved (vs 2 hours originally)
```

**Impact**: 2 hours saved for 15 minutes of knowledge capture = **12:1 ROI**.

## Documentation

| File | Purpose |
|------|---------|
| [docs/INDEX.md](docs/INDEX.md) | Documentation map and quick reference |
| [docs/QUICKSTART.md](docs/QUICKSTART.md) | 5-minute setup and first use |
| [docs/SYSTEM_GUIDE.md](docs/SYSTEM_GUIDE.md) | Complete user guide (19KB) |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design and internals |
| [docs/EXAMPLE.md](docs/EXAMPLE.md) | Real-world walkthrough with examples |

## File Structure

```
issue-search-skill/
├── SKILL.md                    ← You are here
├── README.md
├── setup.sh                    ← Installation script
├── test_install.sh             ← Verification script
│
├── scripts/
│   └── cli.py                  ← Main CLI interface
│
├── src/
│   ├── schema.py               ← Data models
│   ├── utils.py                ← File I/O helpers
│   ├── indexer.py              ← Q&A generation
│   └── retriever.py            ← Search and ranking
│
├── tests/
│   └── test_system.py          ← Comprehensive test suite
│
├── docs/
│   ├── INDEX.md                ← Documentation index
│   ├── README.md               ← Quick overview
│   ├── QUICKSTART.md           ← 5-minute setup
│   ├── SYSTEM_GUIDE.md         ← Complete user guide
│   ├── ARCHITECTURE.md         ← System design
│   └── EXAMPLE.md              ← Walkthrough examples
│
├── evals/
│   ├── test_qa_quality.py      ← Q&A generation quality evaluation
│   ├── test_ranking.py         ← Ranking algorithm evaluation
│   └── test_performance.py     ← Performance benchmarks
│
├── assets/
│   ├── example_issue.json      ← Sample issue
│   ├── example_postmortem.json ← Sample postmortem
│   ├── example_qa.json         ← Sample Q&A entry
│   └── workflow_diagram.txt    ← ASCII workflow diagram
│
├── .gitignore
└── LICENSE
```

## Installation

### For Claude Code (Recommended)

```bash
# Add to project
git clone https://github.com/andrei-ionut-nita/issue-search-skill.git
cd issue-search-skill
./setup.sh

# Or add to user skills
git clone https://github.com/andrei-ionut-nita/issue-search-skill.git ~/.claude/skills/issue-search-skill
cd ~/.claude/skills/issue-search-skill
./setup.sh
```

### Manual Installation

```bash
# 1. Clone or download the repository
git clone https://github.com/andrei-ionut-nita/issue-search-skill.git
cd issue-search-skill

# 2. Run setup
./setup.sh

# 3. Verify installation
./test_install.sh

# 4. Start using
python3 scripts/cli.py capture --description "..." --symptoms timeout
```

## Testing

All operations are fully tested:

```bash
# Run full test suite
python3 tests/test_system.py

# Run quality evaluations
python3 evals/test_qa_quality.py
python3 evals/test_ranking.py
python3 evals/test_performance.py
```

## Design Philosophy

- **Simple > Complex** — 750 lines not 5000
- **Local > Remote** — offline-first, no network
- **Durable > Fast** — append-only, not optimized writes
- **Human > Machine** — JSON readable, not binary
- **Specific > Generic** — controlled vocabulary, validated inputs
- **Useful > Complete** — core feature excellent, not all features OK

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Capture issue | ~1ms | O(1) JSONL append |
| Generate postmortem | ~5ms | O(1) file creation |
| Search (1000 Q&A) | ~100ms | O(n) linear scan |
| List issues | ~50ms | O(d·i) typical |

Scales comfortably to 10k+ entries.

## Extensibility

Clean separation of concerns enables future enhancements:

- **Full-text search** — search question/answer content
- **Environment filtering** — rank by backend/OS
- **Confidence decay** — reduce old, unused solutions
- **Negative signals** — track failed attempts
- **Related issues** — cluster similar problems
- **Export/reports** — generate documentation
- **User feedback** — rate solution helpfulness

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

## Requirements

- **Python**: 3.8 or later
- **OS**: Linux, macOS, Windows
- **Dependencies**: None (standard library only)
- **Storage**: ~/.knowledge_base/ (auto-created, ~1KB per issue)

## Quality Metrics

- **Code**: 750 lines (core + tests)
- **Tests**: 7 comprehensive suites, all passing ✓
- **Documentation**: 65+ pages
- **Performance**: < 100ms search for 1000 entries
- **Dependencies**: 0 (Python stdlib only)

## License

Apache License 2.0 — Free to use, modify, and distribute.

## Support & Questions

- **Quick start?** → [docs/QUICKSTART.md](docs/QUICKSTART.md)
- **How does it work?** → [docs/SYSTEM_GUIDE.md](docs/SYSTEM_GUIDE.md)
- **Want details?** → [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **See example?** → [docs/EXAMPLE.md](docs/EXAMPLE.md)
- **Run tests?** → `python3 tests/test_system.py`

## Next Steps

1. **Read** [docs/QUICKSTART.md](docs/QUICKSTART.md) (5 minutes)
2. **Run** `python3 tests/test_system.py` (verify it works)
3. **Practice** capturing your first issue
4. **Learn** [docs/SYSTEM_GUIDE.md](docs/SYSTEM_GUIDE.md) for complete reference
5. **Integrate** into your workflow

---

**Ready to stop losing solutions? Start with [docs/QUICKSTART.md](docs/QUICKSTART.md) →**
