# Example: Using the Issue Search Skill

## Workflow: From Issue to Searchable Solution

### Step 1: Capture an Issue

A developer encounters a timeout error in production.

```bash
python3 cli.py capture \
  --source user \
  --description "Database connection timeout during high-traffic periods" \
  --symptoms timeout,latency_high \
  --backend python \
  --infra kubernetes \
  --os linux
```

Output:
```
✓ Captured issue 550e8400-e29b-41d4-a716-446655440000
  Description: Database connection timeout during high-traffic periods
  Symptoms: timeout, latency_high
```

### Step 2: Investigate and Generate Postmortem

After investigation, the team identifies the root cause: the connection pool was too small.

```bash
python3 cli.py postmortem \
  --issue-id 550e8400-e29b-41d4-a716-446655440000 \
  --summary "Database connection pool exhaustion under load" \
  --symptoms timeout,latency_high \
  --root-cause "Connection pool size of 10 was insufficient for peak traffic. Under load, all connections were consumed by slow queries, causing new requests to timeout waiting for a connection." \
  --resolution "Increased connection pool size from 10 to 50. Added query timeout of 30 seconds to cancel hanging queries immediately." \
  --prevention "Set up CloudWatch alarms for connection pool utilization > 80%. Added connection pool metrics to dashboards. Conduct load testing before deployments." \
  --tags "database,connection-pool,performance" \
  --impact "Production downtime for 15 minutes affecting 2000 users"
```

Output:
```
✓ Generated postmortem 550e8400-e29b-41d4-a716-446655440000
✓ Generated Q&A entry d41d8cd98f00b204-e9800998ecf8427e
  Q: How do I debug timeout in Database connection pool exhaustion under load?
```

### Step 3: Retrieve Solution When Similar Issue Arises

Weeks later, another team member encounters a timeout error:

```bash
python3 cli.py search --symptom timeout
```

Output:
```
Searching for solutions: timeout

Relevant past solutions (1 found):

1. Q: How do I debug timeout in Database connection pool exhaustion under load?
   A: Root cause: Connection pool size of 10 was insufficient for peak traffic... | Resolution: Increased connection pool size from 10 to 50... | Prevention: Set up CloudWatch alarms...
   Confidence: 82% | Used: 2 times | Score: 0.82

```

The developer immediately finds the prior solution, avoiding the investigation time.

---

## Data Model: Before and After

### Before: Raw Issue (JSONL)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-03-31T14:25:00Z",
  "source": "user",
  "description": "Database connection timeout during high-traffic periods",
  "symptoms": ["timeout", "latency_high"],
  "environment": {
    "backend": "python",
    "infra": "kubernetes",
    "os": "linux"
  },
  "raw_context": {}
}
```

**File**: `~/.knowledge_base/issues/2026-03-31/issue_550e8400-e29b-41d4-a716-446655440000.jsonl`

### After: Structured Postmortem (JSON)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "issue_id": "550e8400-e29b-41d4-a716-446655440000",
  "summary": "Database connection pool exhaustion under load",
  "symptoms": ["timeout", "latency_high"],
  "timeline": [],
  "root_cause": "Connection pool size of 10 was insufficient for peak traffic...",
  "resolution": "Increased connection pool size from 10 to 50...",
  "prevention": "Set up CloudWatch alarms for connection pool utilization...",
  "impact": "Production downtime for 15 minutes affecting 2000 users",
  "tags": ["database", "connection-pool", "performance"],
  "created_at": "2026-03-31T14:26:00Z"
}
```

**File**: `~/.knowledge_base/postmortems/2026-03-31/postmortem_550e8400-e29b-41d4-a716-446655440000.json`

### Derived Q&A Entry (JSONL)

```json
{
  "id": "d41d8cd98f00b204-e9800998ecf8427e",
  "question": "How do I debug timeout in Database connection pool exhaustion under load?",
  "answer": "Root cause: Connection pool size of 10 was insufficient... | Resolution: Increased connection pool size from 10 to 50... | Prevention: Set up CloudWatch alarms...",
  "tags": ["database", "connection-pool", "performance"],
  "confidence": 0.8,
  "source_issue_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-03-31T14:26:00Z",
  "usage_count": 2,
  "last_used": "2026-04-05T10:15:00Z"
}
```

**File**: `~/.knowledge_base/qa/qa_index.jsonl`

### Symptom Index Entry (JSONL)

```json
{
  "symptom": "timeout",
  "issue_ids": ["550e8400-e29b-41d4-a716-446655440000"],
  "qa_ids": ["d41d8cd98f00b204-e9800998ecf8427e"],
  "tags": []
}
```

**File**: `~/.knowledge_base/symptom_index/symptom_index.jsonl`

---

## Commands Reference

### Capture an Issue

```bash
python3 cli.py capture \
  --source user \
  --description "..." \
  --symptoms timeout,api_error \
  --backend python \
  --frontend react \
  --infra kubernetes \
  --language python \
  --os linux
```

### Generate Postmortem

```bash
python3 cli.py postmortem \
  --issue-id <uuid> \
  --summary "..." \
  --symptoms timeout,latency_high \
  --root-cause "..." \
  --resolution "..." \
  --prevention "..." \
  --impact "..." \
  --tags "tag1,tag2"
```

### Search by Symptom

```bash
python3 cli.py search --symptom timeout
python3 cli.py search --symptom timeout,latency_high --limit 10
```

### List Recent Issues

```bash
python3 cli.py list --limit 20
```

### Show Issue Details

```bash
python3 cli.py show-issue <issue-id>
```

### Show Postmortem Details

```bash
python3 cli.py show-postmortem <issue-id>
```

### Show Statistics

```bash
python3 cli.py stats
```

---

## Valid Symptoms

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
