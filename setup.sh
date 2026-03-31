#!/bin/bash

# Issue Search Skill — Installation Script
# Sets up the knowledge management system and verifies installation

set -e

echo "=========================================="
echo "Issue Search Skill — Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version found"

# Check required Python version (3.8+)
required_version="3.8"
if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)" 2>/dev/null; then
    echo "✗ Python 3.8+ required, found $python_version"
    exit 1
fi

echo ""
echo "Creating ~/.knowledge_base/ directory..."
mkdir -p ~/.knowledge_base/{issues,postmortems,qa,symptom_index,meta}
echo "✓ Knowledge base directory created"

echo ""
echo "Running system tests..."
if python3 tests/test_system.py > /dev/null 2>&1; then
    echo "✓ All tests passed!"
else
    echo "✗ Tests failed. Check output above."
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ Installation complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Read:     docs/QUICKSTART.md"
echo "  2. Try:      python3 scripts/cli.py capture --help"
echo "  3. Capture:  python3 scripts/cli.py capture --description \"...\" --symptoms timeout"
echo "  4. Search:   python3 scripts/cli.py search --symptom timeout"
echo ""
echo "Knowledge base location: ~/.knowledge_base/"
echo ""
