# Architecture: Issue Search Skill

## Overview

The Issue Search Skill is a local-first, filesystem-based system for capturing issues, generating postmortems, deriving Q&A entries, and enabling symptom-based retrieval of solutions.

**Core principle**: Issues → Postmortems → Q&A → Searchable Knowledge Base

## System Design

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI (cli.py)                             │
│  capture issue → postmortem → search → list → show → stats  │
└──────────────┬──────────────────────────────────────────────┘
               │
       ┌───────┴───────┐
       ↓               ↓
  ┌──────────┐    ┌──────────┐
  │ Indexer  │    │ Retriever│
  └────┬─────┘    └──────┬───┘
       │                 │
       └────────┬────────┘
                ↓
        ┌─────────────────┐
        │  Knowledge Base │
        │  (~/.kb/)       │
        ├─────────────────┤
        │ issues/         │
        │ postmortems/    │
        │ qa/             │
        │ symptom_index/  │
        │ meta/           │
        └─────────────────┘
```

## Modules

### 1. **schema.py** — Data Models & Validation

Defines the core entities with validation:

- **Issue** — Raw issue capture
  - `id`, `timestamp`, `source` (user|system)
  - `description`, `symptoms`, `environment`
  - `raw_context` (arbitrary data)

- **Postmortem** — Structured problem analysis
  - Same `id` as issue (immutable link)
  - `summary`, `root_cause`, `resolution`, `prevention`
  - `symptoms`, `timeline`, `impact`, `tags`
  - Validation: all required fields must be non-empty and specific

- **QAEntry** — Derived Q&A from postmortem
  - `question`, `answer` (derived from postmortem)
  - `tags` (symptoms + postmortem tags)
  - `confidence` (0.0-1.0, increases with usage)
  - `usage_count`, `last_used` (for ranking)

- **SymptomIndexEntry** — Index for fast retrieval
  - Maps `symptom` → `[issue_ids]`, `[qa_ids]`

- **Symptom** enum — Controlled vocabulary (14 values)
  - `timeout`, `latency_high`, `api_error`, etc.

### 2. **utils.py** — File Operations & I/O

Abstracts all filesystem interactions:

- **Directory management**: `get_knowledge_base_dir()`, `ensure_dir()`
- **File paths**: `get_issue_file_path()`, `get_postmortem_file_path()`, etc.
- **JSONL append**: `write_jsonl_line()` — append-only durability
- **File reading**: `read_jsonl_file()`, `read_json_file()`
- **Listing**: `list_issues_by_date()`, `list_all_dates()`
- **Formatting**: `format_iso_datetime()`, `truncate_text()`

**Design**: Centralized I/O layer enables consistent error handling and makes the knowledge base relocatable.

### 3. **indexer.py** — Q&A Generation & Index Maintenance

Transforms postmortems into searchable Q&A entries:

#### Key methods:

- **`generate_qa_from_postmortem(postmortem)`**
  - Derives realistic developer question
  - Generates actionable answer from root_cause + resolution + prevention
  - Validation: no generic phrasing, no speculation
  - Example:
    ```
    Q: How do I debug timeout in Database connection pool exhaustion?
    A: Root cause: ... | Resolution: ... | Prevention: ...
    ```

- **`add_qa_entry(qa_entry)`**
  - Validates Q&A entry
  - Persists to `qa/qa_index.jsonl` (append-only)
  - Updates symptom index

- **`record_qa_usage(qa_id)`**
  - Increments `usage_count`
  - Updates `last_used` timestamp
  - Increases `confidence` (0.02 per use, capped at 0.95)
  - Justification: frequently-used solutions are more trustworthy

- **`link_issue_to_symptom_index(issue_id, symptoms)`**
  - Maps issue → symptoms for quick discovery

#### Symptom Index Structure:

```jsonl
{"symptom": "timeout", "issue_ids": [...], "qa_ids": [...], "tags": [...]}
{"symptom": "latency_high", "issue_ids": [...], "qa_ids": [...], "tags": [...]}
...
```

### 4. **retriever.py** — Symptom-Based Search & Ranking

Finds relevant Q&A entries given symptoms:

#### Algorithm:

```
1. Normalize symptoms (validate against controlled vocabulary)
2. Load symptom index + all QA entries
3. For each input symptom:
   - Find all QA entries linked to that symptom
   - Track match count per QA entry
4. Rank by combined score:
   - Match count (50%): higher match = more relevant
   - Confidence (30%): higher confidence = more trusted
   - Recency (10%): newer solutions preferred (decay over 30 days)
   - Usage (10%): frequently-used solutions ranked higher
5. Return top N results
```

#### Ranking Formula:

```
final_score = (match_ratio * 0.5) + (confidence * 0.3) + (recency_factor * 0.1) + (usage_factor * 0.1)

recency_factor = 1.0 / (1.0 + days_old / 30.0)
usage_factor = min(usage_count / 10.0, 1.0)
```

**Design rationale**: 
- Symptom match is primary (50%) — must be relevant to the search
- Confidence is secondary (30%) — tested solutions are more valuable
- Recency prevents stale solutions from dominating
- Usage feedback improves ranking over time

#### Output Format:

```
Relevant past solutions (N found):

1. Q: How do I debug timeout in Database connection pool exhaustion?
   A: Root cause: ... | Resolution: ... | Prevention: ...
   Confidence: 80% | Used: 2 times | Score: 0.82
```

### 5. **cli.py** — Command-Line Interface

Orchestrates all operations:

#### Commands:

- **`capture`** — Record a new issue
  - Validates symptoms (must be in controlled vocabulary)
  - Calls indexer to link to symptom index
  
- **`postmortem`** — Generate postmortem from issue
  - Validates all required fields (root_cause, resolution, prevention must be specific)
  - Calls indexer to generate Q&A
  - Persists postmortem + Q&A
  
- **`search`** — Find solutions by symptom
  - Calls retriever
  - Pretty-prints results with confidence scores
  
- **`list`** — Show recent issues
- **`show-issue`** — Details of a specific issue
- **`show-postmortem`** — Details of a specific postmortem
- **`stats`** — Knowledge base size

## Data Storage

### Directory Structure

```
~/.knowledge_base/
  issues/
    2026-03-31/
      issue_550e8400-e29b-41d4-a716-446655440000.jsonl
      issue_550e8400-e29b-41d4-a716-446655440001.jsonl
    2026-04-01/
      issue_550e8400-e29b-41d4-a716-446655440002.jsonl
  
  postmortems/
    2026-03-31/
      postmortem_550e8400-e29b-41d4-a716-446655440000.json
      postmortem_550e8400-e29b-41d4-a716-446655440001.json
    2026-04-01/
      postmortem_550e8400-e29b-41d4-a716-446655440002.json
  
  qa/
    qa_index.jsonl        (all Q&A entries, append-only)
  
  symptom_index/
    symptom_index.jsonl   (symptom → QA/issue mappings)
  
  meta/
    global_index.jsonl    (metadata, future use)
```

### Partitioning Strategy

- **Issues & postmortems**: Date-based (`YYYY-MM-DD`)
  - Enables fast pruning of old data
  - Natural timeline for debugging
  - Files grow daily, manageable size

- **Q&A & symptoms**: Single append-only files
  - Small enough to fit in memory
  - No partitioning needed (linear scan acceptable)
  - If > 100k entries, could implement hash-based partitioning

### File Formats

- **JSONL** (JSON Lines) for append-only logs
  - Issues, Q&A entries, symptom index
  - One JSON object per line
  - Durability without locking (append is atomic)
  - Faster than SQLite for this use case

- **JSON** for structured postmortems
  - Pretty-printed for human readability
  - Entire postmortem in one file (enables transactionality)

### Durability Guarantees

- **Append-only**: once written, data is immutable
- **No locks**: filesystem handles concurrent reads
- **Atomic writes**: each line/file is atomic
- **Human-readable**: no binary encoding, survives tool failures
- **No external dependencies**: survives library/API changes

## Quality Constraints

The system enforces these constraints:

1. **No generic answers** — validation rejects vague root causes
   - ✗ "Bad configuration"
   - ✓ "Database pool size 10 insufficient for peak traffic"

2. **No hallucinated root causes** — postmortem must be derived from investigation
   - Answer is constructed from: root_cause + resolution + prevention
   - No speculation beyond what's provided

3. **No missing fields** — all required fields validated before persistence
   - Issue: id, timestamp, source, description
   - Postmortem: id, issue_id, summary, root_cause, resolution, prevention
   - QA: id, question, answer, confidence, source_issue_id

4. **No duplicate IDs** — UUIDs ensure uniqueness (collision probability negligible)

5. **No network calls** — entire system runs offline

6. **No external APIs** — uses only Python standard library

## Workflow: Issue to Solution

### Example: Database Timeout

```
1. CAPTURE (user reports issue)
   $ python3 cli.py capture \
     --description "Database returns 503 during deployment" \
     --symptoms api_error,timeout \
     --backend python
   
   → Issue {id} created
   → Linked to symptom_index["api_error"] and symptom_index["timeout"]

2. INVESTIGATE (team debug, find root cause)
   - Connection pool exhausted due to slow queries
   - Deployment reduced available connections

3. POSTMORTEM (encode solution into knowledge base)
   $ python3 cli.py postmortem \
     --issue-id {id} \
     --summary "Connection pool exhaustion during deployment" \
     --root-cause "Pool size 10 insufficient; queries not timing out" \
     --resolution "Increased pool to 50, added 30s query timeout" \
     --prevention "Monitor pool utilization, load test before deploy"
   
   → Postmortem {id} created
   → Q&A entry auto-generated:
     Q: "How do I debug api_error in Connection pool exhaustion...?"
     A: "Root cause: Pool size 10... | Resolution: Increased to 50... | Prevention: Monitor..."
   → Q&A entry indexed under symptom "api_error", "timeout"
   → Confidence set to 0.8 (baseline)

4. RETRIEVE (next developer encounters timeout)
   $ python3 cli.py search --symptom timeout
   
   → Retriever finds Q&A entries tagged "timeout"
   → Ranks by: match_count (1.0, exact), confidence (0.8), recency, usage
   → Returns: "How do I debug api_error in Connection pool exhaustion...?"
   → Developer gets solution in seconds
   → Confidence increases to 0.82 (first reuse)
   → Confidence increases to 0.84 (second reuse)
   → Over time, becomes trusted solution (confidence → 0.95)
```

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Capture issue | O(1) | Single JSONL append |
| Generate postmortem | O(1) | Create file + update symptom index |
| Search (1000 Q&A) | O(n) | Linear scan, < 100ms |
| List recent | O(d·i) | d dates, i issues/date. Typically < 50ms |
| Index update | O(m) | m = number of symptoms. Typical: O(14) |

For datasets up to 10k issues / 10k Q&A entries, this approach is fast and simple.

**If scaling beyond 100k entries**: consider hash-based partitioning or lightweight indexing (e.g., SQLite).

## Future Extensions

### Possible enhancements (not in MVP):

1. **Negative signal tracking** — record failed attempts
   - Store: `{attempt: "...", result: "failed"}`
   - Use: avoid repeating ineffective solutions
   - Requires: separate failed_attempts.jsonl

2. **Confidence decay** — reduce confidence if unused for 90 days
   - Formula: `new_confidence = old_confidence * (1 - days_unused / 180)`
   - Periodically recalculate (weekly job)

3. **Symptom relationships** — learn which symptoms co-occur
   - When searching "timeout", also suggest "latency_high"
   - Requires: symptom correlation matrix

4. **Full-text search** — search question/answer text
   - Index: question + answer content
   - Would require: inverted index (more complex)

5. **Environment filtering** — refine search by backend/os/infra
   - Rank higher: issues matching your environment
   - Would require: environment-based sub-indexing

6. **Feedback loop** — user rates solution helpfulness
   - Store: `qa_entry.ratings = [{"helpful": true, "date": "..."}]`
   - Adjust confidence based on feedback

7. **Related issues** — cluster similar issues
   - Use: description similarity + symptom overlap
   - Display: "5 similar issues"

8. **Export** — generate reports
   - Format: PDF, markdown, JSON
   - Content: timeline of issues, prevention measures, trends

## Testing

- **schema.py**: Validation tests for each entity
- **serialization**: JSON round-trip tests
- **qa_generation**: Question + answer derivation
- **indexing**: Symptom index creation and updates
- **retrieval**: Search ranking and scoring
- **workflow**: End-to-end issue → solution

Run: `python3 test_system.py`

## Constraints & Tradeoffs

### What we optimize for:
- **Fast retrieval** of prior solutions (primary goal)
- **Data durability** (append-only, no corruption)
- **Human readability** (all text/JSON, no binary)
- **Zero dependencies** (Python stdlib only)
- **Offline capability** (no network required)

### What we don't optimize for:
- **Storage efficiency** (JSON is verbose, but storage is cheap)
- **Complex queries** (no SQL; just symptom-based)
- **Concurrency** (filesystem handles it, but no transactions)
- **Authorization** (local user filesystem; no multi-user support)

### Design decisions:

| Decision | Why |
|----------|-----|
| Append-only JSONL | Durability without locking, fast writes |
| Date partitioning | Natural timeline, enables old-data pruning |
| Controlled vocabulary | Prevents symptom sprawl, enables reliable indexing |
| Local filesystem | Zero dependencies, offline-capable |
| No UI | Minimal complexity; CLI sufficient |
| Flat symptom index | Fast linear scan for small datasets |

## Summary

The Issue Search Skill is a minimal, durable, offline-first system for converting issue experiences into searchable solutions. It trades sophisticated querying for simplicity, durability, and human readability.

Core idea: **Capture once, retrieve forever**. Every issue becomes a postmortem. Every postmortem becomes Q&A. Every Q&A is indexed by symptom and ranked by evidence (confidence, recency, usage).
