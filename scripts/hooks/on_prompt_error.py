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


# Pattern to detect issues in user prompt
# Matches code errors (traceback, exceptions) and user-reported problems (broken, doesn't work, etc.)
# Negative lookahead (?!.*\bno\b) prevents false positives like "no issues with it"
ISSUE_PATTERNS = re.compile(
    r"(traceback|exception|error:|nameerror|typeerror|valueerror|"
    r"syntaxerror|importerror|filenotfounderror|exit code [1-9]|"
    r"failed|failing|crash|crashed|broken|doesn't work|doesn't|not working|"
    r"(?<!no\s)(?<!no\s)bug|(?<!no\s)problem|wrong|incorrect|undefined|can't|unable to|stopped|stopped working|"
    r"doesn't handle|not handling|not following|not respecting|inconsistent)",
    re.IGNORECASE
)


def map_symptom(text):
    """Map error text to a symptom category."""
    t = text.lower()

    if any(x in t for x in ["timeout", "timed out", "deadline exceeded", "hangs"]):
        return "timeout"
    if any(x in t for x in ["import", "no module", "modulenotfounderror", "dependency", "missing package"]):
        return "dependency_failure"
    if any(x in t for x in ["nameerror", "attributeerror", "nonetype", "undefined", "not defined"]):
        return "null_pointer"
    if any(x in t for x in ["auth", "permission", "unauthorized", "forbidden", "login"]):
        return "auth_failure"
    if any(x in t for x in ["connection", "refused", "network", "unreachable", "offline", "down"]):
        return "api_error"
    if any(x in t for x in ["memory", "out of", "leak", "heap"]):
        return "memory_leak"
    if any(x in t for x in ["race", "concurrent", "thread", "lock"]):
        return "race_condition"
    if any(x in t for x in ["corrupt", "loss", "truncated", "missing data"]):
        return "data_loss"

    return "config_error"


def main():
    try:
        data = json.load(sys.stdin)

        # Extract user's message
        prompt = data.get("prompt", "")
        if not prompt:
            sys.exit(0)

        # Check if prompt contains issue patterns
        if not ISSUE_PATTERNS.search(prompt):
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
