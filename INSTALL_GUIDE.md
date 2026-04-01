# Installation Guide — Issue Search Skill

Complete installation instructions for users installing from SkillsMP or GitHub.

## System Requirements

- **Python**: 3.8 or later
- **OS**: Linux, macOS, or Windows
- **Storage**: ~1 KB per issue (minimal, grows slowly)
- **Dependencies**: None (Python standard library only)

## Quick Install (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/andrei-ionut-nita/issue-search-skill.git
cd issue-search-skill

# 2. Run setup (installs and verifies)
./setup.sh

# 3. Verify installation
./test_install.sh

# 4. Try it out
python3 scripts/cli.py --help
```

Expected output from setup:
```
==========================================
Issue Search Skill — Setup
==========================================

Checking Python version...
✓ Python 3.9.0 found

Creating ~/.knowledge_base/ directory...
✓ Knowledge base directory created

Running system tests...
✓ All tests passed!

==========================================
✓ Installation complete!
==========================================

Next steps:
  1. Read:     docs/QUICKSTART.md
  2. Try:      python3 scripts/cli.py capture --help
  3. Capture:  python3 scripts/cli.py capture --description "..." --symptoms timeout
  4. Search:   python3 scripts/cli.py search --symptom timeout

Knowledge base location: ~/.knowledge_base/
```

## Manual Installation

If `./setup.sh` doesn't work on your system:

```bash
# 1. Create knowledge base directory
mkdir -p ~/.knowledge_base/{issues,postmortems,qa,symptom_index,meta}

# 2. Run tests to verify
python3 tests/test_system.py

# Expected output:
# ==================================================
# ✓ All tests passed!
# ==================================================

# 3. Start using
python3 scripts/cli.py capture --description "Test issue" --symptoms timeout
```

## Installation for Claude Code

### Option A: Project-Level (Recommended)

```bash
# Place in your Claude Code project
git clone https://github.com/andrei-ionut-nita/issue-search-skill.git .claude/skills/issue-search-skill
cd .claude/skills/issue-search-skill
./setup.sh

# setup.sh will:
# 1. Create ~/.knowledge_base/ directory
# 2. Register hooks to ~/.claude/settings.json (automatic)
# 3. Run tests to verify installation
```

### Option B: User-Level

```bash
# Install to your user skills directory
git clone https://github.com/andrei-ionut-nita/issue-search-skill.git ~/.claude/skills/issue-search-skill
cd ~/.claude/skills/issue-search-skill
./setup.sh

# setup.sh will:
# 1. Create ~/.knowledge_base/ directory
# 2. Register hooks to ~/.claude/settings.json (automatic)
# 3. Run tests to verify installation
```

### After Installation

The hooks are now active in `~/.claude/settings.json`. When you start a Claude Code session:

- **PostToolUse hook** monitors Bash commands — auto-searches KB when a command fails
- **UserPromptSubmit hook** monitors your messages — auto-searches KB when you describe an error

You don't need to do anything; they activate automatically.

## Verification

### Quick Check

```bash
# Verify Python version
python3 --version
# Should output: Python 3.8.0 or later

# Verify installation
./test_install.sh
# Should output:
# ==========================================
# ✓ Installation verified!
# ==========================================
```

### Run Tests

```bash
# Run full test suite
python3 tests/test_system.py

# Run quality evaluations
python3 evals/test_qa_quality.py
python3 evals/test_ranking.py
python3 evals/test_performance.py
```

## Knowledge Base Location

All data is stored in `~/.knowledge_base/`:

```
~/.knowledge_base/
├── issues/              # Date-partitioned issue captures (YYYY-MM-DD/)
├── postmortems/         # Date-partitioned postmortems (YYYY-MM-DD/)
├── qa/                  # All Q&A entries (qa_index.jsonl)
├── symptom_index/       # Symptom-to-QA mappings (symptom_index.jsonl)
└── meta/                # Metadata (future use)
```

This directory:
- Is created automatically by setup.sh
- Grows slowly (~1 KB per issue)
- Is managed automatically by the system
- Can be backed up to version control if desired
- Is never synced or uploaded remotely

## First Steps

### 1. Read the Quick Start

```bash
cat docs/QUICKSTART.md
# Or open in editor
```

### 2. Capture Your First Issue

```bash
python3 scripts/cli.py capture \
  --description "Example issue" \
  --symptoms timeout
```

### 3. Generate a Postmortem

```bash
# Use the issue ID from the previous command
python3 scripts/cli.py postmortem \
  --issue-id {uuid-from-above} \
  --root-cause "Example root cause" \
  --resolution "Example fix" \
  --prevention "Example prevention"
```

### 4. Search Your Knowledge Base

```bash
python3 scripts/cli.py search --symptom timeout
```

## Troubleshooting

### Python Not Found

```bash
# Error: command not found: python3
# Solution: Install Python 3.8 or later
# macOS: brew install python3
# Ubuntu: sudo apt install python3
# Windows: Download from python.org
```

### Setup Script Fails

```bash
# Run manually instead:
mkdir -p ~/.knowledge_base/{issues,postmortems,qa,symptom_index,meta}
python3 tests/test_system.py
```

### Permission Denied on setup.sh

```bash
# Make script executable
chmod +x setup.sh
./setup.sh
```

### Tests Fail

```bash
# Check Python version (need 3.8+)
python3 --version

# Check if src files exist
ls -la src/

# Run with verbose output
python3 tests/test_system.py -v
```

### Knowledge Base Path Issues

```bash
# Verify directory exists and is writable
ls -la ~/.knowledge_base/

# If missing, create manually:
mkdir -p ~/.knowledge_base/{issues,postmortems,qa,symptom_index,meta}
```

## Uninstallation

To remove the skill:

```bash
# Remove the installation directory
rm -rf issue-search-skill

# Remove knowledge base (optional)
rm -rf ~/.knowledge_base
```

## Getting Help

- **Quick start?** → `cat docs/QUICKSTART.md`
- **Commands?** → `python3 scripts/cli.py --help`
- **Complete guide?** → `cat docs/SYSTEM_GUIDE.md`
- **How it works?** → `cat docs/ARCHITECTURE.md`
- **See example?** → `cat docs/EXAMPLE.md`

## Next Steps

1. **Read**: [docs/QUICKSTART.md](docs/QUICKSTART.md) (5 minutes)
2. **Try**: Capture your first issue
3. **Learn**: [docs/SYSTEM_GUIDE.md](docs/SYSTEM_GUIDE.md) for complete reference
4. **Integrate**: Add to your workflow

---

**Installation successful? Head to [docs/QUICKSTART.md](docs/QUICKSTART.md) →**
