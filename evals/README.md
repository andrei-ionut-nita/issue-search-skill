# Evaluation Tests (Optional)

This directory is for quality evaluation tests that are not required for the core functionality.

The main test suite (`../tests/test_system.py`) contains comprehensive tests for all core functionality and is what matters for production use.

Optional evaluation tests can be added here to verify:
- Q&A generation quality
- Ranking algorithm behavior
- Performance characteristics
- Edge cases and stress tests

The core skill works perfectly without these optional evaluations. They're provided as optional validation tools for developers who want to extend or modify the system.
