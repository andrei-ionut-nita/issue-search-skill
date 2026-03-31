# Contributing to Issue Search Skill

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the Issue Search Skill project.

## Code of Conduct

This project is committed to providing a welcoming and inclusive environment. Please be respectful and constructive in all interactions.

## Ways to Contribute

### 1. Report Bugs

If you find a bug, please open an issue with:

- **Title**: Brief description of the bug
- **Description**: What happened, what you expected, steps to reproduce
- **Environment**: Python version, OS, how you installed the skill
- **Example**: Paste the error message or unexpected behavior

### 2. Suggest Features

Feature suggestions are welcome! Open an issue with:

- **Title**: Brief feature description
- **Motivation**: Why this feature would be useful
- **Proposed solution**: How you'd like it to work
- **Alternatives**: Other approaches you considered

### 3. Improve Documentation

Documentation improvements are always appreciated:

- Fix typos or clarify confusing sections
- Add examples or use cases
- Improve explanations of how the system works
- Create tutorials or guides

### 4. Contribute Code

Want to write code? Great! Here's how:

#### Before You Start

1. **Check existing issues** — Make sure your idea isn't already being worked on
2. **Start a discussion** — For significant changes, open an issue first
3. **Review the architecture** — Read `docs/ARCHITECTURE.md` to understand the design

#### Development Setup

```bash
# Clone the repository
git clone https://github.com/andrei-ionut-nita/issue-search-skill.git
cd issue-search-skill

# Verify installation
./setup.sh
python3 tests/test_system.py

# You're ready to develop!
```

#### Code Style Guidelines

- **Python 3.8+ compatibility** — No newer syntax
- **No external dependencies** — Use only Python standard library
- **Type hints** — Add type hints to function signatures
- **Docstrings** — Add docstrings to classes and public functions
- **Tests** — Write tests for new functionality
- **Comments** — Comment complex logic, not obvious code

**Example:**

```python
def calculate_score(
    symptom_match: float,
    confidence: float,
    recency: float,
    usage: float,
) -> float:
    """Calculate multi-factor relevance score.
    
    Args:
        symptom_match: Ratio of matching symptoms (0.0-1.0)
        confidence: Solution confidence/reliability (0.0-1.0)
        recency: Recency factor, decays over time (0.0-1.0)
        usage: Usage frequency factor (0.0-1.0)
    
    Returns:
        Combined relevance score (0.0-1.0)
    """
    return (
        (symptom_match * 0.5) +
        (confidence * 0.3) +
        (recency * 0.1) +
        (usage * 0.1)
    )
```

#### Project Structure

```
src/
  schema.py        ← Data models and validation
  utils.py         ← File I/O helpers
  indexer.py       ← Q&A generation and indexing
  retriever.py     ← Search and ranking
scripts/
  cli.py           ← Command-line interface
tests/
  test_system.py   ← Comprehensive test suite
docs/
  *.md             ← User documentation
evals/
  test_*.py        ← Quality and performance evaluations
```

#### Making Changes

1. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes** with clear, focused commits:
   ```bash
   git add <files>
   git commit -m "Brief description of change"
   ```

3. **Add tests** for new functionality:
   ```bash
   # Add tests to tests/test_system.py
   python3 tests/test_system.py
   ```

4. **Run the full test suite** to ensure nothing breaks:
   ```bash
   python3 tests/test_system.py
   python3 evals/test_qa_quality.py
   python3 evals/test_ranking.py
   python3 evals/test_performance.py
   ```

5. **Update documentation** if you add/change features:
   - Update relevant `.md` files in `docs/`
   - Update `SKILL.md` if changing user-facing features
   - Update `CHANGELOG.md` with your changes

#### Pull Request Guidelines

1. **Title**: Brief, descriptive title (e.g., "Add confidence decay for unused solutions")
2. **Description**: 
   - What does this PR do?
   - Why is it needed?
   - How does it work?
   - Any breaking changes?
3. **Testing**: Explain how you tested this change
4. **Documentation**: Link to or note documentation updates

**Example PR Description:**

```
## Summary

Adds confidence decay for Q&A entries that haven't been used in 90 days.

## Why

Old, unused solutions accumulate and can appear in search results even when no 
longer relevant. This feature reduces their confidence score over time, pushing 
fresher solutions up in rankings.

## How

- New method: `Indexer.decay_unused_confidence(days_threshold=90)`
- Runs on `search` command (checks all Q&A entries)
- Formula: `new_confidence = old * (1 - days_unused / 180)`
- Performance: O(n) but cached, runs ~50ms for 1000 entries

## Testing

- Added `test_confidence_decay()` to test_system.py
- Verified formula correctness with edge cases
- Confirmed performance < 100ms for 1000 entries
- Tested with evals/test_ranking.py

## Breaking Changes

None. This is additive functionality with backward-compatible defaults.
```

### 5. Improve Tests and Evaluations

Help us ensure quality:

- Add test cases for edge cases
- Improve test coverage
- Add performance benchmarks
- Create evaluation suites for new features

## Development Tips

### Running Tests

```bash
# Full test suite
python3 tests/test_system.py

# Specific test (add to test_system.py)
python3 -m pytest tests/test_system.py::test_name -v

# With verbose output
python3 tests/test_system.py -v
```

### Debugging

```bash
# Run with Python debugger
python3 -m pdb scripts/cli.py capture --description "test" --symptoms timeout

# Add print statements for quick debugging
print(f"DEBUG: {variable_name}")

# Check knowledge base state
ls -la ~/.knowledge_base/
cat ~/.knowledge_base/qa/qa_index.jsonl
```

### Local Installation for Testing

```bash
# Install from your local branch
git clone <your-fork> /tmp/test-skill
cd /tmp/test-skill
./setup.sh
python3 tests/test_system.py
```

## Design Principles

Keep these in mind when contributing:

1. **Simple > Complex** — Prefer straightforward solutions
2. **Local > Remote** — Offline-first, no network dependency
3. **Durable > Fast** — Data integrity over performance micro-optimizations
4. **Human > Machine** — Readable formats (JSON), no binary encoding
5. **Specific > Generic** — Controlled vocabulary prevents sprawl
6. **Useful > Complete** — Core features excellent, not all features OK
7. **Zero Dependencies** — Use only Python standard library

## Questions?

- Check `docs/ARCHITECTURE.md` for system design
- Review `tests/test_system.py` for usage examples
- Open an issue with your question

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0, the same license as this project.

---

Thank you for helping make Issue Search Skill better! 🙏
