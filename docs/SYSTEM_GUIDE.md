# Issue Search Skill — Complete System Guide

## What is This?

A **local-first, offline-capable knowledge management system** for capturing software issues, analyzing root causes, and retrieving proven solutions when similar problems recur.

Think of it as a **personal Stack Overflow** for your team's recurring problems—automatically indexed, ranked by relevance, and 100% under your control.

## Why Use It?

### Problem
- Same bugs recur across the team
- Investigation time is wasted re-solving known problems
- Tribal knowledge exists only in Slack/emails/memories
- No systematic way to learn from incidents

### Solution
1. **Capture** every issue (including non-critical ones)
2. **Convert** into structured postmortem
3. **Derive** searchable Q&A entry
4. **Retrieve** when similar issue arises (in seconds)
5. **Learn** from patterns in your knowledge base

### Example Timeline

```
Day 1 (Incident)
├─ 14:00 - "Database timeout in production"
├─ 14:15 - Root cause: connection pool exhausted
├─ 14:30 - Fix applied: increased pool size
└─ 14:45 - Postmortem written, solution indexed

Day 45 (Another timeout)
├─ 14:00 - New developer encounters similar timeout
└─ 14:02 - Finds prior solution in knowledge base
   (45 days of investigation time saved)
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│              Your Knowledge Base                        │
│          (~/.knowledge_base/ on your machine)           │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Issues          Postmortems     Q&A Index     Symptom │
│  (raw data)      (analyzed)      (searchable) (indexed) │
│                                                         │
│  issue_001       postmortem_001  qa_index      timeout  │
│  issue_002       postmortem_002              latency    │
│  ...             ...             ...           ...      │
│                                                         │
└─────────────────────────────────────────────────────────┘
         ↑             ↑              ↑            ↑
         │             │              │            │
    ┌────┴─────────────┴──────────────┴────────────┴─┐
    │                  CLI Tool                      │
    │  (python3 cli.py capture/postmortem/search)   │
    └──────────────────────────────────────────────┘
```

## Getting Started (5-Minute Setup)

### 1. Verify Python 3 is installed
```bash
python3 --version
```

### 2. Run tests to verify system works
```bash
cd skill_maker
python3 test_system.py
```

Expected output: `✓ All tests passed!`

### 3. Capture your first issue
```bash
python3 cli.py capture \
  --description "API timeout during peak traffic" \
  --symptoms timeout,latency_high \
  --backend python
```

### 4. Generate a postmortem
Replace `{issue_id}` with the ID from step 3:
```bash
python3 cli.py postmortem \
  --issue-id {issue_id} \
  --summary "Connection pool exhaustion" \
  --root-cause "Pool size insufficient for peak load" \
  --resolution "Increased pool from 10 to 50" \
  --prevention "Monitor pool utilization, load test before deploy"
```

### 5. Search for solutions
```bash
python3 cli.py search --symptom timeout
```

**Congratulations!** You now have a working knowledge base.

## Core Concepts

### 1. **Issue** — Raw Problem Report
What: A problem that occurred
When: Timestamp
Where: Environment (backend, OS, infra)
How: Symptoms (controlled vocabulary)

Example:
```
Description: "Database returns 503 Service Unavailable during deployment"
Symptoms: ["api_error", "timeout"]
Backend: "python"
```

### 2. **Postmortem** — Analysis & Solution
What happened: Summary + timeline
Why: Root cause (specific and technical)
How we fixed it: Resolution (actionable steps)
How to prevent: Prevention (monitoring, testing, changes)

Example:
```
Root cause: "Connection pool size of 10 was insufficient. 
             During deployment with 5 concurrent instances, 
             all 10 connections were consumed by 30-second queries."

Resolution: "Increased connection pool size from 10 to 50.
             Added query timeout of 30 seconds to cancel hanging queries."

Prevention: "Set up CloudWatch alerts for connection pool > 80%.
             Added connection metrics to dashboards.
             Conduct load testing before deployments."
```

### 3. **Q&A Entry** — Searchable Knowledge
Derived from postmortem, formatted as developer question + answer

Example:
```
Q: "How do I debug timeout in Database connection pool exhaustion?"
A: "Root cause: Pool size 10 insufficient... | 
    Resolution: Increased pool to 50, added 30s timeout... | 
    Prevention: Monitor pool utilization..."

Tags: ["database", "connection", "timeout"]
Confidence: 80%
Usage count: 3 times
```

### 4. **Symptom Index** — Fast Retrieval
Maps symptoms to Q&A entries
```
timeout → [qa_001, qa_003, qa_005, ...]
latency_high → [qa_002, qa_003, qa_007, ...]
api_error → [qa_001, qa_004, ...]
```

## Complete Command Reference

### Capture Issue
```bash
python3 cli.py capture \
  --source user \                          # or 'system'
  --description "..." \                     # REQUIRED
  --symptoms timeout,api_error \            # optional, comma-separated
  --backend python \                        # optional: python, go, nodejs, etc.
  --frontend react \                        # optional
  --infra kubernetes \                      # optional
  --language python \                       # optional
  --os linux \                              # optional
  --raw-context '{"stack_trace": "..."}' # optional JSON
```

### Generate Postmortem
```bash
python3 cli.py postmortem \
  --issue-id {uuid} \                       # REQUIRED, from capture output
  --summary "..." \                         # REQUIRED, one-line summary
  --symptoms timeout,latency_high \         # optional
  --timeline '[{"timestamp":"...", "event":"..."}]' \  # optional JSON
  --root-cause "..." \                      # REQUIRED, specific and technical
  --resolution "..." \                      # REQUIRED, actionable steps
  --prevention "..." \                      # REQUIRED, how to avoid recurrence
  --impact "..." \                          # optional: business impact
  --tags database,performance \             # optional, comma-separated
```

### Search Solutions
```bash
python3 cli.py search \
  --symptom timeout \                       # REQUIRED, comma-separated
  --limit 10                                # optional, default 5
```

### List Issues
```bash
python3 cli.py list --limit 20             # optional, default 10
```

### Show Issue Details
```bash
python3 cli.py show-issue {uuid}
```

### Show Postmortem Details
```bash
python3 cli.py show-postmortem {uuid}
```

### View Statistics
```bash
python3 cli.py stats
```

## Valid Symptoms (Controlled Vocabulary)

Always use these exact terms when capturing issues:

| Symptom | Meaning |
|---------|---------|
| `timeout` | Operation exceeded time limit |
| `latency_high` | Response time unusually slow |
| `api_error` | HTTP error response (4xx, 5xx) |
| `schema_mismatch` | Data structure incompatibility |
| `null_pointer` | Null/undefined reference error |
| `auth_failure` | Authentication/authorization failure |
| `rate_limit` | Exceeded rate limits |
| `dependency_failure` | External service unavailable |
| `config_error` | Misconfiguration |
| `race_condition` | Concurrent access issue |
| `memory_leak` | Unbounded memory growth |
| `crash` | Process termination |
| `data_loss` | Unintended data deletion |
| `corruption` | Data integrity violation |

## Quality Guidelines

### Writing Good Root Causes

❌ **Bad** (vague, non-specific)
```
"Bad configuration"
"Network issue"
"Unknown error"
"Bug in the system"
```

✓ **Good** (specific, technical, reproducible)
```
"Connection pool size of 10 was insufficient. During peak traffic, 
all connections consumed by 30-second queries, causing new requests 
to timeout waiting for available connection."

"Message queue had no dead-letter handling. Failed messages were silently 
dropped, causing data loss. Worked fine under normal load but failed 
under traffic spike when error rate increased 10x."

"Hash map iteration order undefined in Go. Concurrent reads/writes 
created race condition under load. Fixed with sync.Mutex."
```

### Writing Good Resolutions

❌ **Bad** (vague, non-actionable)
```
"Fixed it"
"Optimized performance"
"Updated configuration"
```

✓ **Good** (specific steps taken)
```
"Increased connection pool size from 10 to 50 in database.yml.
Added connection timeout of 30 seconds to cancel hanging queries.
Deployed with zero-downtime migration."

"Added Dead Letter Queue (DLQ) for failed messages.
Implemented retry logic with exponential backoff.
Set up alerting for DLQ depth > 100.
Deployed configuration change without downtime."

"Added sync.Mutex to protect shared state.
Reviewed all shared memory access patterns.
Added race detector to CI/CD pipeline."
```

### Writing Good Prevention

❌ **Bad** (vague, non-actionable)
```
"Be more careful"
"Don't make this mistake again"
"Test more thoroughly"
```

✓ **Good** (specific, measurable, implementable)
```
"Set up CloudWatch alarm: connection pool utilization > 80%.
Add connection metrics to Grafana dashboard.
Conduct load testing before every major deployment.
Document expected connection count in runbook."

"Monitor DLQ depth every minute. Alert if > 100 messages.
Add integration test for failed message handling.
Document DLQ procedures in incident response guide."

"Enable Go's race detector in all tests. Build fails if race detected.
Code review checklist includes 'Shared state protected?'
Add memory profiling to performance tests."
```

## Retrieval & Ranking Algorithm

When you search, the system ranks solutions based on:

1. **Symptom match** (50%) — does the solution address your symptom?
2. **Confidence** (30%) — how reliable is the solution?
3. **Recency** (10%) — newer solutions preferred (decay over 30 days)
4. **Usage** (10%) — frequently-used solutions ranked higher

Example scoring:
```
Solution 1: timeout + latency_high (your search)
  - Match: 100% (both symptoms match)
  - Confidence: 90% (5 successful uses)
  - Recency: 0.95 (1 week old)
  - Usage: 0.5 (used 5 times, capped at 10)
  - Final score: (1.0 * 0.5) + (0.9 * 0.3) + (0.95 * 0.1) + (0.5 * 0.1) = 0.86

Solution 2: timeout only
  - Match: 50% (1 of 2 symptoms match)
  - Confidence: 80% (unused, baseline)
  - Recency: 0.5 (30 days old)
  - Usage: 0.0 (never used)
  - Final score: (0.5 * 0.5) + (0.8 * 0.3) + (0.5 * 0.1) + (0.0 * 0.1) = 0.49
```

Result: Solution 1 ranked higher (0.86 vs 0.49)

## Knowledge Base Location & Structure

All data lives in: **`~/.knowledge_base/`**

```
~/.knowledge_base/
├── issues/                    # Raw issue captures
│   ├── 2026-03-31/            # Date-partitioned
│   │   ├── issue_550e8400....jsonl
│   │   └── issue_550e8400....jsonl
│   └── 2026-04-01/
│       └── issue_550e8400....jsonl
│
├── postmortems/               # Structured postmortems
│   ├── 2026-03-31/            # Same date partition as issues
│   │   ├── postmortem_550e8400....json
│   │   └── postmortem_550e8400....json
│   └── 2026-04-01/
│       └── postmortem_550e8400....json
│
├── qa/
│   └── qa_index.jsonl         # All Q&A entries (append-only)
│
├── symptom_index/
│   └── symptom_index.jsonl    # Symptom → QA/Issue mappings
│
└── meta/
    └── global_index.jsonl     # Metadata (future use)
```

**Important**: All files are human-readable JSON/JSONL. You can inspect them directly:

```bash
# View all issues from today
cat ~/.knowledge_base/issues/$(date +%Y-%m-%d)/*.jsonl | python3 -m json.tool

# View all Q&A entries
cat ~/.knowledge_base/qa/qa_index.jsonl | python3 -m json.tool

# Find issues matching a keyword
grep -r "database" ~/.knowledge_base/issues/
```

## Workflow Examples

### Example 1: Capturing a Production Bug

```bash
# 1. Incident occurs
# "Database connection timeout, API returns 503 errors"

# 2. Capture immediately
python3 cli.py capture \
  --source system \
  --description "Database connection timeout under peak traffic" \
  --symptoms timeout,api_error \
  --backend python \
  --infra kubernetes

# Output: Issue 550e8400-e29b-41d4-a716-446655440000

# 3. Team investigates (meanwhile, capture other related issues/errors)

# 4. Root cause found: connection pool too small
# 5. Fix: increase pool size + add query timeout

# 6. Generate postmortem
python3 cli.py postmortem \
  --issue-id 550e8400-e29b-41d4-a716-446655440000 \
  --summary "Connection pool exhaustion under peak load" \
  --root-cause "Pool size 10 insufficient; peak traffic uses all connections" \
  --resolution "Increased pool to 50, added 30s query timeout" \
  --prevention "Monitor pool utilization, load test before deploy" \
  --impact "15 mins downtime, 2000 users affected"

# 7. Solution is now indexed and searchable
```

### Example 2: Reusing Prior Solution

```bash
# 1. New timeout error reported
"API returning 503 errors, similar to incident from 45 days ago"

# 2. Search knowledge base
python3 cli.py search --symptom timeout

# 3. Immediately find relevant postmortem:
# "Connection pool exhaustion under peak load"
# "Resolution: Increased pool from 10 to 50, added 30s query timeout"
# "Confidence: 90% | Used: 5 times"

# 4. Apply same fix → problem resolved in 5 minutes
# (vs 2 hours of investigation if discovering for first time)

# 5. Solution usage count increases (5 → 6), confidence increases (90% → 92%)
```

### Example 3: Building Knowledge Over Time

```
Month 1: Capture 5 issues, generate 3 postmortems
  - Knowledge base: 3 searchable solutions

Month 2: Encounter 2 issues matching existing solutions
  - Time saved: 4 hours of investigation
  - Solution confidence increases

Month 3: New team members join
  - Hit 5 existing issues
  - Resolve in 30 minutes total (vs 20+ hours originally)
  - Team learns "this is how we handle X"

Month 6: New type of issue (hasn't occurred before)
  - Capture, investigate, postmortem, index
  - Next similar occurrence: instant resolution

Year 1: 40 issues captured, 25 postmortems, 60% of new issues resolve
        in < 30 minutes by referencing prior solutions
```

## Common Questions

### Q: Should I capture every issue?
**A:** Yes. Even small issues are worth capturing:
- Common misconfigurations
- Transient network errors
- Library version mismatches
- Deployment gotchas

The more data you have, the better your retrieval.

### Q: What if root cause is still unknown?
**A:** Don't force it. Document what you know:
```
Root cause: "Connection pool exhausted (verified by logs). 
            Why pool was exhausted unknown. Possibly slow queries or 
            unusual traffic pattern."

Resolution: "Increased pool size from 10 to 50. Issue resolved."

Prevention: "Add monitoring for pool utilization and query execution time
            to identify root cause if it recurs."
```

This is still valuable—the next occurrence, you'll look for slow queries.

### Q: How often should I search?
**A:** Every time you encounter an error or unusual behavior:
- API error? → `python3 cli.py search --symptom api_error`
- Timeout? → `python3 cli.py search --symptom timeout`
- Crash? → `python3 cli.py search --symptom crash`

Takes 5 seconds. Often saves hours.

### Q: Can I edit or delete entries?
**A:** Not directly (append-only design). If you need to:
1. **Correct an error**: Create new postmortem with same issue_id (overwrites in display)
2. **Delete stale data**: Manually edit `~/.knowledge_base/` files (carefully)
3. **Reset completely**: `rm -rf ~/.knowledge_base/` (starts fresh)

### Q: Can multiple users share the knowledge base?
**A:** Not currently. The system is single-user (filesystem-based). 
Options if you need sharing:
- Git repo with `~/.knowledge_base/` (conflicts possible)
- Periodic backup/merge (manual)
- Export to team wiki (future enhancement)

### Q: What if I have 10,000 Q&A entries?
**A:** Current design handles it, but:
- Search becomes linear O(n) = ~100ms
- Index file grows to ~50MB (acceptable)
- If performance degrades, consider: hash-based partitioning, SQLite, or dedicated vector DB

For now: simple and fast. Add complexity only if needed.

## Tips & Tricks

### Batch capturing related issues
```bash
# Capture multiple issues from same incident
for i in {1..3}; do
  python3 cli.py capture \
    --description "Issue $i: ..." \
    --symptoms timeout,api_error
done
```

### View knowledge base stats
```bash
python3 cli.py stats
cat ~/.knowledge_base/qa/qa_index.jsonl | wc -l    # Total Q&A entries
cat ~/.knowledge_base/qa/qa_index.jsonl | python3 -c "import sys, json; es=[json.loads(l) for l in sys.stdin]; print(f'Total uses: {sum(e[\"usage_count\"] for e in es)}'); print(f'Avg confidence: {sum(e[\"confidence\"] for e in es)/len(es):.1%}')"
```

### Search by multiple symptoms
```bash
python3 cli.py search --symptom timeout,latency_high
```

### Export knowledge base
```bash
# Backup
cp -r ~/.knowledge_base ~/.knowledge_base.backup

# Export as markdown (future enhancement)
# python3 cli.py export --format markdown > knowledge_base.md
```

### Find issues from a specific date
```bash
ls ~/.knowledge_base/issues/2026-03-31/
```

## Troubleshooting

### Issue not found after capture
```
If uuid from capture doesn't exist in search:
1. Check date partition matches
2. Verify command ran without error
3. Check ~/.knowledge_base/issues/ exists
```

### Search returns no results
```
1. Verify symptom is in controlled vocabulary
2. Try different symptoms (api_error vs timeout)
3. Check knowledge base isn't empty: python3 cli.py stats
4. Explicitly: cat ~/.knowledge_base/qa/qa_index.jsonl
```

### Python not found
```
Use: python3 (not python)
Check: python3 --version
```

## Next Steps

1. **Run tests**: `python3 test_system.py`
2. **Capture first issue**: `python3 cli.py capture --description "..." --symptoms "..."`
3. **Generate postmortem**: `python3 cli.py postmortem --issue-id {...} --root-cause "..." --resolution "..." --prevention "..."`
4. **Search solutions**: `python3 cli.py search --symptom timeout`
5. **Iterate** — grow your knowledge base over time

## Philosophy

> "Every issue is a lesson. Every lesson is a solution. Every solution prevents future wasted time."

This system embodies that philosophy: **Capture once, retrieve forever.**

The cost of capturing a postmortem: 10 minutes.
The value: prevent 2+ hours of investigation when it recurs.
ROI: 12:1 or better.

Start small. Grow your knowledge base. Save your team's time.

---

**Questions?** See README.md, QUICKSTART.md, ARCHITECTURE.md, or EXAMPLE.md for more details.
