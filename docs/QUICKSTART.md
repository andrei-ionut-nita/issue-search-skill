# Quick Start Guide

## Installation

No external dependencies required. Uses only Python standard library.

### For Claude Code Users

```bash
# Clone into your project
git clone https://github.com/andrei-ionut-nita/issue-search-skill.git .claude/skills/issue-search-skill
cd .claude/skills/issue-search-skill

# Run setup (registers hooks automatically)
./setup.sh
```

That's it! Hooks are now active. When you encounter errors, the system will automatically search your knowledge base for solutions.

### For Manual Installation

```bash
cd issue-search-skill
```

## Run Tests

Verify the system works correctly:

```bash
python3 tests/test_system.py
```

Also verify hook patterns:

```bash
python3 tests/test_hook_patterns.py
```

Expected output:
```
==================================================
Issue Search Skill - Test Suite
==================================================
Testing schema validation...
✓ Valid issue passes validation
✓ Invalid issue detected
✓ Valid postmortem passes validation
✓ Symptom validation works

Testing serialization...
✓ Issue serialization works
✓ Postmortem serialization works
✓ Q&A serialization works

Testing Q&A generation...
✓ Generated Q&A:
  Q: How do I debug timeout in Database connection timeout?
  A: Root cause: Connection pool exhausted | Resolution: Increased...

Testing indexing...
✓ Q&A entry added to index
✓ Q&A usage recorded
✓ Issue linked to symptom index

Testing retrieval...
✓ Found 1 result(s) for 'timeout'
✓ Found 2 result(s) for 'timeout, latency_high'

Testing complete workflow...
✓ Created issue 550e8400-e29b-41d4-a716-446655440000
✓ Created postmortem 550e8400-e29b-41d4-a716-446655440000
✓ Generated and indexed Q&A d41d8cd98f00b204-e9800998ecf8427e
✓ Linked issue to symptom index
✓ Retrieved Q&A by symptom 'api_error'

==================================================
✓ All tests passed!
==================================================
```

## Capture Your First Issue

An issue is a problem or error encountered in your system. Every issue should be captured with:
- A clear description
- Symptoms (from the controlled vocabulary)
- Environment details (optional but helpful)

```bash
python3 cli.py capture \
  --source user \
  --description "Database returns 503 Service Unavailable during deployment" \
  --symptoms api_error,timeout \
  --backend python \
  --infra kubernetes
```

Output:
```
✓ Captured issue 550e8400-e29b-41d4-a716-446655440000
  Description: Database returns 503 Service Unavailable during deployment
  Symptoms: api_error, timeout
```

Note the issue ID (the long UUID). You'll use it to create a postmortem.

## Generate a Postmortem

After investigating, you understand what happened. Convert that knowledge into a postmortem:

```bash
python3 cli.py postmortem \
  --issue-id 550e8400-e29b-41d4-a716-446655440000 \
  --summary "Database connection pool exhaustion during rolling deployment" \
  --symptoms api_error,timeout \
  --root-cause "Connection pool was drained by long-running queries during deployment. New queries had no available connections and timed out." \
  --resolution "Added connection timeout of 30 seconds to kill hanging queries immediately. Reduced deployment concurrency from 5 to 2 to lower peak connection demand." \
  --prevention "Set up dashboard alerts for connection pool > 80% utilization. Conduct load testing before deployments. Document deployment procedure." \
  --impact "15 minutes of 503 errors affecting 2000 users" \
  --tags "database,connection-pool,deployment"
```

Output:
```
✓ Generated postmortem 550e8400-e29b-41d4-a716-446655440000
✓ Generated Q&A entry d41d8cd98f00b204-e9800998ecf8427e
  Q: How do I debug api_error in Database connection pool exhaustion during rolling deployment?
```

The system automatically:
1. Stores the postmortem
2. Derives a realistic Q&A entry
3. Updates indices for fast retrieval

## List Recent Issues

See what issues have been captured:

```bash
python3 cli.py list --limit 5
```

Output:
```
1. [USER] 550e8400-e29b-41d4-a716-446655440000
   Database returns 503 Service Unavailable during deployment
   Symptoms: api_error, timeout
   2026-03-31 14:25:00 UTC

```

## Search for Solutions by Symptom

Now imagine a new issue arises with similar symptoms. Search the knowledge base:

```bash
python3 cli.py search --symptom timeout
```

Output:
```
Searching for solutions: timeout

Relevant past solutions (1 found):

1. Q: How do I debug api_error in Database connection pool exhaustion during rolling deployment?
   A: Root cause: Connection pool was drained... | Resolution: Added connection timeout... | Prevention: Set up dashboard alerts...
   Confidence: 80% | Used: 0 times | Score: 0.80

```

You've just found the prior solution! No investigation needed.

## Show Issue Details

Get full details of a specific issue:

```bash
python3 cli.py show-issue 550e8400-e29b-41d4-a716-446655440000
```

## Show Postmortem Details

Get the complete postmortem:

```bash
python3 cli.py show-postmortem 550e8400-e29b-41d4-a716-446655440000
```

## View Statistics

See the size of your knowledge base:

```bash
python3 cli.py stats
```

Output:
```
Knowledge Base Statistics
========================================
Issues captured: 5
Postmortems generated: 4
Q&A entries: 4
Date partitions: 2
```

## Valid Symptoms

Always use these controlled vocabulary terms:

| Symptom | Meaning |
|---------|---------|
| `timeout` | Operation exceeded time limit |
| `latency_high` | Response time unusually slow |
| `api_error` | HTTP error response (4xx, 5xx) |
| `schema_mismatch` | Data structure incompatibility |
| `null_pointer` | Null/undefined reference |
| `auth_failure` | Authentication/authorization failure |
| `rate_limit` | Exceeded rate limits |
| `dependency_failure` | External service unavailable |
| `config_error` | Misconfiguration |
| `race_condition` | Concurrent access issue |
| `memory_leak` | Unbounded memory growth |
| `crash` | Process termination |
| `data_loss` | Unintended data deletion |
| `corruption` | Data integrity violation |

## Knowledge Base Location

All data is stored at: `~/.knowledge_base/`

Directory structure:
```
~/.knowledge_base/
  issues/
    2026-03-31/
      issue_550e8400-e29b-41d4-a716-446655440000.jsonl
  postmortems/
    2026-03-31/
      postmortem_550e8400-e29b-41d4-a716-446655440000.json
  qa/
    qa_index.jsonl
  symptom_index/
    symptom_index.jsonl
  meta/
    global_index.jsonl
```

All files are human-readable. You can inspect them directly:

```bash
cat ~/.knowledge_base/issues/2026-03-31/issue_550e8400-e29b-41d4-a716-446655440000.jsonl
cat ~/.knowledge_base/postmortems/2026-03-31/postmortem_550e8400-e29b-41d4-a716-446655440000.json
```

## Workflow: Issue → Solution

1. **Capture issue** — you encounter a problem
   ```bash
   python3 cli.py capture --description "..." --symptoms "..."
   ```

2. **Investigate** — understand root cause and resolution

3. **Generate postmortem** — encode the knowledge
   ```bash
   python3 cli.py postmortem --issue-id <uuid> --root-cause "..." --resolution "..."
   ```

4. **Retrieve solutions** — when similar issues occur in future
   ```bash
   python3 cli.py search --symptom timeout
   ```

## Tips

- **Be specific in root causes** — avoid "bad configuration" or "network issue". Use "database connection pool size was 10, insufficient for peak traffic"
- **Make resolutions actionable** — "increased pool size from 10 to 50" is better than "fixed it"
- **Document prevention** — "set up monitoring alerts for pool > 80% utilization" prevents recurrence
- **Use multiple symptoms** — "timeout,latency_high" makes the issue easier to find
- **Add tags** — tags like "database", "performance", "deployment" help categorize
- **Search multiple symptoms** — `python3 cli.py search --symptom api_error,timeout` finds issues matching either

## Inspecting Raw Data

All data is JSON or JSONL. You can inspect it directly:

```bash
# View a single issue (JSONL format)
cat ~/.knowledge_base/issues/2026-03-31/issue_*.jsonl | python3 -m json.tool

# View all Q&A entries
cat ~/.knowledge_base/qa/qa_index.jsonl | python3 -m json.tool

# View symptom index
cat ~/.knowledge_base/symptom_index/symptom_index.jsonl | python3 -m json.tool
```

## Limitations & Design

- **Local-first only** — no network calls, no external APIs
- **No UI required** — CLI-based for simplicity
- **Append-only logs** — durability through immutability
- **Human-readable** — all files are JSON/JSONL
- **Zero dependencies** — uses Python standard library only
- **Deterministic retrieval** — same symptoms always rank the same way

---

## Next Steps

1. Run the test suite: `python3 test_system.py`
2. Capture an issue: `python3 cli.py capture --description "..." --symptoms "..."`
3. Generate a postmortem: `python3 cli.py postmortem --issue-id <uuid> --root-cause "..." --resolution "..."`
4. Search solutions: `python3 cli.py search --symptom timeout`

Your knowledge base grows with every postmortem. Over time, you build a searchable library of solutions.
