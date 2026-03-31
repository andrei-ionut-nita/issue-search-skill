#!/bin/bash

# Issue Search Skill — Installation Verification Script
# Quick check that everything is installed and working correctly

echo "=========================================="
echo "Issue Search Skill — Verification"
echo "=========================================="
echo ""

# Check Python
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "✗ Python 3 not found"
    exit 1
fi
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version"

# Check knowledge base directory
echo ""
echo "Checking knowledge base directory..."
if [ -d "$HOME/.knowledge_base" ]; then
    echo "✓ ~/.knowledge_base exists"
else
    echo "✗ ~/.knowledge_base not found (run setup.sh first)"
    exit 1
fi

# Check core files
echo ""
echo "Checking core files..."
required_files=(
    "scripts/cli.py"
    "src/schema.py"
    "src/utils.py"
    "src/indexer.py"
    "src/retriever.py"
    "tests/test_system.py"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file not found"
        exit 1
    fi
done

# Run quick test
echo ""
echo "Running tests..."
if python3 tests/test_system.py > /dev/null 2>&1; then
    echo "✓ All tests passed"
else
    echo "✗ Tests failed"
    exit 1
fi

# Test CLI is callable
echo ""
echo "Testing CLI..."
if python3 scripts/cli.py --help > /dev/null 2>&1; then
    echo "✓ CLI is working"
else
    echo "✗ CLI failed"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ Installation verified!"
echo "=========================================="
echo ""
echo "You're ready to use the system:"
echo "  python3 scripts/cli.py capture --description \"...\" --symptoms timeout"
echo ""
