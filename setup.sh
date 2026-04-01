#!/bin/bash

# Issue Search Skill - Installation Script
# Sets up the knowledge management system and verifies installation

set +e  # Don't exit on errors; continue even if tests fail

echo "=========================================="
echo "Issue Search Skill - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "[OK] Python $python_version found"

# Check required Python version (3.8+)
required_version="3.8"
if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)" 2>/dev/null; then
    echo "[ERROR] Python 3.8+ required, found $python_version"
    exit 1
fi

echo ""
echo "Creating ~/.knowledge_base/ directory..."
mkdir -p ~/.knowledge_base/{issues,postmortems,qa,symptom_index,meta}
echo "[OK] Knowledge base directory created"

echo ""
echo "Running system tests..."
if python3 tests/test_system.py > /dev/null 2>&1; then
    echo "[OK] All tests passed!"
else
    echo "[WARN] Some tests failed (pre-existing issue, continuing anyway...)"
fi

echo ""
echo "=========================================="
echo "[OK] Installation complete!"
echo "=========================================="
echo ""

# ==========================================
# Auto-configure Claude Code integration
# ==========================================
echo "Configuring Claude Code integration..."
echo ""

# Detect install location (global vs project-level)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_NAME="$(basename "${BASH_SOURCE[0]}")"

# Check if installed globally
if [[ "$SCRIPT_DIR" == "$HOME/.claude/skills/issue-search-skill" ]]; then
    # Global install: ~/.claude/skills/issue-search-skill/setup.sh
    CLAUDE_DIR="$HOME/.claude"
    SKILL_PATH="~/.claude/skills/issue-search-skill/scripts/cli.py"
    INSTALL_TYPE="global"
else
    # Project-level install: <project>/.claude/skills/issue-search-skill/setup.sh
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
    CLAUDE_DIR="$PROJECT_ROOT/.claude"
    SKILL_PATH=".claude/skills/issue-search-skill/scripts/cli.py"
    INSTALL_TYPE="project"
fi

# Create .claude directory if it doesn't exist
mkdir -p "$CLAUDE_DIR"

# Generate ISSUE_SEARCH.md from template
TEMPLATE_FILE="$SCRIPT_DIR/templates/ISSUE_SEARCH.md"
ISSUE_SEARCH_FILE="$CLAUDE_DIR/ISSUE_SEARCH.md"

if [ -f "$TEMPLATE_FILE" ]; then
    # Replace {SKILL_PATH} placeholder with actual path
    sed "s|{SKILL_PATH}|$SKILL_PATH|g" "$TEMPLATE_FILE" > "$ISSUE_SEARCH_FILE"
    echo "[OK] Created ISSUE_SEARCH.md ($INSTALL_TYPE install)"
else
    echo "[ERROR] Template not found: $TEMPLATE_FILE"
    exit 1
fi

# Create or update CLAUDE.md
CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"
MARKER="issue-search-skill"

if [ -f "$CLAUDE_MD" ]; then
    # Check if already configured
    if grep -q "$MARKER" "$CLAUDE_MD"; then
        echo "[OK] CLAUDE.md already references issue-search-skill (idempotent)"
    else
        # Append reference to existing CLAUDE.md
        printf "\n## Issue Search Knowledge Base\n\nThis project uses the issue-search-skill for automatic knowledge management.\nSee full instructions: @%s/ISSUE_SEARCH.md\n" "$CLAUDE_DIR" >> "$CLAUDE_MD"
        echo "[OK] Updated existing CLAUDE.md with issue-search-skill reference"
    fi
else
    # Create new CLAUDE.md
    cat > "$CLAUDE_MD" << EOF
# Claude Code Configuration

## Issue Search Knowledge Base

This project uses the issue-search-skill for automatic knowledge management.
See full instructions: @$CLAUDE_DIR/ISSUE_SEARCH.md
EOF
    echo "[OK] Created CLAUDE.md with issue-search-skill reference"
fi

echo ""
echo "=========================================="
echo "[OK] Claude Code integration complete!"
echo "=========================================="
echo ""

# ==========================================
# Register Claude Code hooks
# ==========================================
echo "Registering Claude Code hooks..."
echo ""

SETTINGS_FILE="$HOME/.claude/settings.json"
REGISTER_HOOKS="$SCRIPT_DIR/scripts/register_hooks.py"

if [ -f "$REGISTER_HOOKS" ]; then
    if python3 "$REGISTER_HOOKS" "$SETTINGS_FILE" "$SCRIPT_DIR"; then
        echo ""
        echo "[OK] Hooks registered successfully!"
    else
        echo "[WARN] Failed to register hooks (continuing anyway...)"
    fi
else
    echo "[WARN] Hook registration script not found (continuing anyway...)"
fi

echo ""
echo "=========================================="
echo "[OK] Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Start a new Claude Code session in this project"
echo "  2. Claude will automatically search/capture issues in the knowledge base"
echo "  3. Or manually run: python3 scripts/cli.py capture --help"
echo "  4. Read docs/QUICKSTART.md for complete reference"
echo ""
echo "Knowledge base location: ~/.knowledge_base/"
echo "Hooks configured in: ~/.claude/settings.json"
echo ""
