# Issue Search Skill

A local-first, offline-capable knowledge management system for capturing issues, generating postmortems, and retrieving proven solutions. **Zero dependencies, zero network calls, ready for production use.**

## ⚡ Quick Start

```bash
# 1. Setup (one time)
./setup.sh

# 2. Capture issue
python3 scripts/cli.py capture --description "DB timeout" --symptoms timeout

# 3. Generate postmortem (after investigation)
python3 scripts/cli.py postmortem --issue-id {uuid} --root-cause "..." --resolution "..." --prevention "..."

# 4. Next similar issue — search and resolve in seconds
python3 scripts/cli.py search --symptom timeout
```

## Purpose

**Problem**: Teams lose solutions. The same incident repeats. New team members can't find answers.

**Solution**: Every fix is captured once, searchable forever. Similar issues resolve 12x faster.

1. **Capture** every issue with symptoms and context
2. **Generate** structured postmortems encoding root causes and fixes
3. **Index** Q&A entries automatically by symptom
4. **Retrieve** proven solutions ranked by relevance and confidence
5. **Learn** as your knowledge base grows and solutions are reused

## Principles

- **Local-first** — no outbound connections, works completely offline
- **Append-only** — durable, crash-safe, prevents corruption
- **Deterministic** — same symptoms always rank identically
- **Zero dependencies** — Python standard library only
- **Minimal complexity** — 750 lines of code, highly focused
- **Human-readable** — all JSON/JSONL, fully inspectable

## Directory Structure

```
scripts/
  cli.py               # Main CLI interface

src/
  schema.py            # Data models and validation
  utils.py             # File I/O helpers
  indexer.py           # Q&A generation and indexing
  retriever.py         # Search and ranking

tests/
  test_system.py       # Comprehensive test suite

docs/
  QUICKSTART.md        # 5-minute setup guide
  SYSTEM_GUIDE.md      # Complete user manual
  ARCHITECTURE.md      # System design
  EXAMPLE.md           # Real-world walkthrough

evals/
  test_qa_quality.py   # Q&A quality tests
  test_ranking.py      # Ranking algorithm tests
  test_performance.py  # Performance benchmarks

assets/
  example_issue.json
  example_postmortem.json
  example_qa.json
  workflow_diagram.txt
```

## Installation

**Recommended:** Follow [docs/QUICKSTART.md](docs/QUICKSTART.md) for complete setup (5 minutes).

**Quick version:**
```bash
./setup.sh              # Creates ~/.knowledge_base/, runs tests
./test_install.sh       # Verify installation
```

## Usage

### Capture an Issue

```bash
python3 scripts/cli.py capture \
  --description "Database timeout during traffic spike" \
  --symptoms timeout,api_error,latency_high
```

### Generate Postmortem

```bash
python3 scripts/cli.py postmortem \
  --issue-id {uuid} \
  --root-cause "Connection pool exhausted" \
  --resolution "Increased pool size to 50" \
  --prevention "Monitor pool utilization, load test deployments"
```

### Search Solutions

```bash
python3 scripts/cli.py search --symptom timeout
```

### List Issues & Statistics

```bash
python3 scripts/cli.py list --limit 10
python3 scripts/cli.py stats
```

## How It Works

### Data Flow

```
Issue (capture)
    ↓
Postmortem (analyze)
    ↓
Q&A (auto-generate)
    ↓
Symptom Index (map)
    ↓
Retriever (search & rank)
    ↓
Instant Solution
```

### Retrieval Algorithm

Solutions ranked by multi-factor score:
- **Symptom match** (50%) — does it address your symptom?
- **Confidence** (30%) — how reliable is the solution?
- **Recency** (10%) — newer solutions preferred
- **Usage** (10%) — frequently-used solutions more trusted

Example: Search for `timeout` returns ranked results:
1. "Database connection pool exhaustion" — 0.89 confidence, used 5x
2. "Network timeout due to DNS" — 0.72 confidence, used 1x
3. "Client timeout misconfiguration" — 0.68 confidence, used 0x

## Key Features

✓ **Local-first** — No network calls, works offline
✓ **Zero dependencies** — Python standard library only
✓ **Append-only durability** — Safe from corruption
✓ **Human-readable** — All JSON/JSONL, inspectable
✓ **Deterministic ranking** — Same symptoms, same results
✓ **Fast search** — < 100ms for 1000+ entries
✓ **Learning system** — Confidence grows with usage
✓ **Quality constraints** — No vague answers, validated inputs
✓ **Extensible architecture** — Designed for future enhancements

## Valid Symptoms (14 total)

`timeout`, `latency_high`, `api_error`, `schema_mismatch`, `null_pointer`, `auth_failure`, `rate_limit`, `dependency_failure`, `config_error`, `race_condition`, `memory_leak`, `crash`, `data_loss`, `corruption`

## Storage

All data stored in `~/.knowledge_base/`:
- `issues/YYYY-MM-DD/` — Issue captures
- `postmortems/YYYY-MM-DD/` — Postmortems
- `qa/qa_index.jsonl` — Q&A entries
- `symptom_index/` — Symptom mappings

## Testing

```bash
# Run full test suite
python3 tests/test_system.py

# Run quality evaluations
python3 evals/test_qa_quality.py
python3 evals/test_ranking.py
python3 evals/test_performance.py
```

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Capture | ~1ms | O(1) |
| Postmortem | ~5ms | O(1) |
| Search (1000 Q&A) | ~100ms | O(n) |

Scales to 10k+ entries comfortably.

## Documentation

- **[docs/QUICKSTART.md](docs/QUICKSTART.md)** — 5-minute setup
- **[docs/SYSTEM_GUIDE.md](docs/SYSTEM_GUIDE.md)** — Complete guide
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — System design
- **[docs/EXAMPLE.md](docs/EXAMPLE.md)** — Walkthrough
- **[docs/INDEX.md](docs/INDEX.md)** — Documentation map

## Next Steps

1. **Read** [docs/QUICKSTART.md](docs/QUICKSTART.md)
2. **Run** `./setup.sh` (install & verify)
3. **Capture** your first issue
4. **Generate** a postmortem
5. **Search** to retrieve solutions
6. **Learn** [docs/SYSTEM_GUIDE.md](docs/SYSTEM_GUIDE.md) for complete reference

---

**Ready to build your knowledge base? Start with [docs/QUICKSTART.md](docs/QUICKSTART.md) →**
