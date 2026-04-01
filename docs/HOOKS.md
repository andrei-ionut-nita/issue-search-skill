# Issue Search Hooks — Automatic Error Detection

## Overview

The issue-search-skill uses Claude Code **hooks** to automatically detect and respond to errors, independent of Claude reading CLAUDE.md instructions. This makes the system more reliable.

## How It Works

Two hooks are registered in `~/.claude/settings.json` during installation:

### 1. PostToolUse Hook: `on_bash_error.py`

**Trigger:** After every Bash command executes

**Behavior:**
- If the command failed (exit code ≠ 0):
  - Maps error output to a symptom category (timeout, dependency_failure, null_pointer, etc.)
  - Searches the knowledge base for past solutions
  - Auto-captures the error for future reference
  - Outputs search results as a system message so Claude sees them

**Why this matters:** Even if Claude doesn't search proactively, the hook ensures past solutions surface automatically.

### 2. UserPromptSubmit Hook: `on_prompt_error.py`

**Trigger:** When the user sends a message

**Behavior:**
- Detects error patterns in the prompt text (Traceback, NameError, exit code, etc.)
- Maps to a symptom category
- Searches the knowledge base
- Outputs matching solutions as a system message

**Why this matters:** When users paste errors and ask for help, the hook finds relevant past solutions before Claude even responds.

## Symptom Mapping

Both hooks use the same symptom classifier:

| Pattern | Symptom |
|---------|---------|
| timeout, timed out | `timeout` |
| import, no module, ModuleNotFoundError | `dependency_failure` |
| NameError, undefined, NonType, AttributeError | `null_pointer` |
| auth, permission denied, unauthorized | `auth_failure` |
| connection, refused, network | `api_error` |
| config, missing, invalid | `config_error` (default) |

## Hook Lifecycle

```
Setup (setup.sh)
  ↓
register_hooks.py adds hook commands to ~/.claude/settings.json
  ↓
Claude Code harness reads settings.json at session start
  ↓
When Bash command fails or user sends error message:
  ↓
Hook script runs with JSON input (stdin) → JSON output (stdout)
  ↓
System message injected into Claude's context
```

## What Gets Stored

When a Bash hook fires:
1. **Auto-captures** the error via `cli.py capture`
2. **Searches** for past solutions via `cli.py search`
3. **Outputs** search results

When a prompt hook fires:
1. **Searches** for past solutions (no auto-capture — user decides if it's a new issue)

## Disabling Hooks

To disable hooks, remove them from `~/.claude/settings.json`:

```bash
# Edit settings.json and delete the PostToolUse and UserPromptSubmit entries under "hooks"
```

Or re-run setup.sh and manually remove the entries afterward (idempotent, won't re-add).

## Hook Configuration

Default timeouts:
- **PostToolUse (Bash):** 30 seconds
- **UserPromptSubmit (prompt):** 15 seconds

Both hooks fail silently — if a hook times out or crashes, it won't break your session.

## Testing Hooks

Manually test the hooks:

```bash
# Test Bash error hook
echo '{"tool_name":"Bash","tool_input":{"command":"fail"},"tool_response":{"exit_code":1,"stderr":"error"}}' \
  | python3 ~/.claude/skills/issue-search-skill/scripts/hooks/on_bash_error.py

# Test prompt error hook
echo '{"prompt":"I got a NameError"}' \
  | python3 ~/.claude/skills/issue-search-skill/scripts/hooks/on_prompt_error.py
```

## Answers to Common Questions

**Q: Do hooks run if CLAUDE.md isn't read?**  
A: Yes. Hooks are system-level — they execute regardless of Claude's awareness or CLAUDE.md. This is the entire point.

**Q: What if both hooks fire (Bash error + user pastes error)?**  
A: Both run independently. The prompt hook checks for errors in user text; the Bash hook monitors actual commands. They can trigger simultaneously.

**Q: Can I customize the symptom mapping?**  
A: Edit the `map_symptom()` function in either hook script and re-run setup.sh. Or file an issue with your suggested mappings.

**Q: Will hooks slow down my session?**  
A: No. Hooks run in parallel with Claude's response; they have strict timeouts (15–30s) and fail silently if they exceed them.

**Q: Where are hook inputs/outputs logged?**  
A: Nowhere by default. The hooks print JSON to stdout, which Claude Code captures as a system message. If you need debugging, modify the hook scripts to log to `/tmp/issue_search_hook.log`.

## Further Reading

- [ISSUE_SEARCH.md](../templates/ISSUE_SEARCH.md) — User-facing instructions Claude sees
- [QUICKSTART.md](QUICKSTART.md) — How to use the CLI manually
- [ARCHITECTURE.md](ARCHITECTURE.md) — System design details
