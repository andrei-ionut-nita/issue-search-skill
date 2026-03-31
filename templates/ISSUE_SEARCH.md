# Issue Search — Active Knowledge Management

## MANDATORY BEHAVIOR

You MUST follow these rules in every session without being asked:

### On Every Error, Bug, or Issue

When you encounter or are asked to debug an error, bug, or unexpected behavior:

1. **Search first** — before investigating, run:
   ```bash
   python3 {SKILL_PATH} search --symptom <closest_symptom>
   ```
   Valid symptoms: `timeout`, `latency_high`, `api_error`, `schema_mismatch`, `null_pointer`, `auth_failure`, `rate_limit`, `dependency_failure`, `config_error`, `race_condition`, `memory_leak`, `crash`, `data_loss`, `corruption`

2. **Show results** — if past solutions exist, present them to the user before investigating further

3. **Capture the issue** — after identifying the problem, capture it:
   ```bash
   python3 {SKILL_PATH} capture \
     --description "<brief description>" \
     --symptoms <comma_separated_symptoms>
   ```
   Note the UUID returned; you'll use it in the next step.

4. **After resolution** — once the issue is resolved, document it:
   ```bash
   python3 {SKILL_PATH} postmortem \
     --issue-id <uuid-from-capture> \
     --root-cause "<what caused it>" \
     --resolution "<what fixed it>" \
     --prevention "<how to prevent recurrence>"
   ```

## How It Works

- **Search**: Queries the knowledge base for past solutions matching the symptom
- **Capture**: Records a new issue with symptoms and context
- **Postmortem**: Analyzes the fix and stores it for future retrieval
- **Q&A**: Automatically generated from postmortems, ranked by confidence and usage

Over time, your team resolves issues **12x faster** through systematic knowledge retrieval.

## Manual Commands (User Can Run Directly)

```bash
# Search for solutions
python3 {SKILL_PATH} search --symptom timeout

# Capture a new issue
python3 {SKILL_PATH} capture --description "Database timeout" --symptoms timeout,latency_high

# Create postmortem after solving
python3 {SKILL_PATH} postmortem \
  --issue-id <uuid> \
  --root-cause "Connection pool exhausted" \
  --resolution "Increased pool to 50" \
  --prevention "Monitor pool utilization"

# List recent issues
python3 {SKILL_PATH} list

# Get statistics
python3 {SKILL_PATH} stats

# Get help
python3 {SKILL_PATH} --help
```

## Data Location

All knowledge is stored in `~/.knowledge_base/`:
- `issues/` — Issue captures (date-partitioned)
- `postmortems/` — Postmortem analyses
- `qa/` — Searchable Q&A entries
- `symptom_index/` — Symptom-to-solution mappings

## Key Features

✓ **Local-first** — No network calls, works completely offline  
✓ **Zero dependencies** — Uses only Python standard library  
✓ **Durable** — Append-only storage, crash-safe  
✓ **Automatic indexing** — Solutions ranked by relevance and confidence  
✓ **Team learning** — Shared knowledge base across all sessions  

---

**Every issue captured = faster resolution next time. Start documenting today.**
