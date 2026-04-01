#!/usr/bin/env python3
"""
UserPromptSubmit hook: Fires when the user sends a message.
Detects error patterns (tracebacks, exceptions, error codes) in the prompt.
If detected, automatically searches the knowledge base for similar issues.
Does NOT auto-capture — leaves that decision to Claude.
"""
import json
import subprocess
import sys
import os
import re


def get_cli_path():
    """Resolve the CLI path relative to this script's location."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # scripts/hooks/ -> scripts/ -> . (root)
    skill_root = os.path.dirname(os.path.dirname(script_dir))
    return os.path.join(skill_root, "scripts", "cli.py")


# Pattern to detect error mentions in user prompt
ERROR_PATTERNS = re.compile(
    r"(traceback|exception|error:|nameerror|typeerror|valueerror|"
    r"syntaxerror|importerror|filenotfounderror|exit code [1-9]|"
    r"failed|crashed|broken|not working|undefined)",
    re.IGNORECASE
)


def map_symptom(text):
    """Map error text to a symptom category."""
    t = text.lower()

    if any(x in t for x in ["timeout", "timed out"]):
        return "timeout"
    if any(x in t for x in ["import", "no module", "modulenotfounderror"]):
        return "dependency_failure"
    if any(x in t for x in ["nameerror", "attributeerror", "nonetype"]):
        return "null_pointer"
    if any(x in t for x in ["auth", "permission denied", "unauthorized"]):
        return "auth_failure"
    if any(x in t for x in ["connection", "refused", "network"]):
        return "api_error"

    return "config_error"


def main():
    try:
        data = json.load(sys.stdin)

        # Extract user's message
        prompt = data.get("prompt", "")
        if not prompt:
            sys.exit(0)

        # Check if prompt contains error patterns
        if not ERROR_PATTERNS.search(prompt):
            sys.exit(0)

        # Map to symptom and search knowledge base
        symptom = map_symptom(prompt)
        cli_path = get_cli_path()

        search_result = subprocess.run(
            [sys.executable, cli_path, "search", "--symptom", symptom],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Only output if we found matching solutions
        search_output = search_result.stdout.strip()
        if search_output and "No matching" not in search_output:
            msg = f"[issue-search] Found past solutions for '{symptom}':\n{search_output}"
            print(json.dumps({"systemMessage": msg}))

    except Exception:
        # Silently fail — don't let hook errors break the session
        pass
    finally:
        sys.exit(0)


if __name__ == "__main__":
    main()
