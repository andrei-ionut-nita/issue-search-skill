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


# Base pattern: detect issue-related keywords in user prompt
# Covers code errors (traceback, exceptions) and user-reported problems (broken, doesn't work, etc.)
ISSUE_PATTERNS = re.compile(
    r"(traceback|exception|error:|nameerror|typeerror|valueerror|"
    r"syntaxerror|importerror|filenotfounderror|exit code [1-9]|"
    r"failed|failing|crash|crashed|broken|doesn't work|doesn't|not working|"
    r"(?<!no\s)(?<!no\s)bug|(?<!no\s)problem|wrong|incorrect|undefined|can't|unable to|stopped|stopped working|"
    r"doesn't handle|not handling|not following|not respecting|inconsistent)",
    re.IGNORECASE
)

# False positive filters: legitimate, non-issue uses of issue keywords
# These patterns indicate the keyword is NOT describing a real problem
FALSE_POSITIVE_PATTERNS = [
    r"can't\s+wait",  # excited anticipation
    r"unable\s+to\s+contain",  # emotional expression
    r"broken\s+(?:down|out)",  # explanation/analysis or distribution
    r"break(?:ing)?\s+down",  # explanation/analysis (verb form)
    r"stopped\s+(?:raining|snowing|hailing)",  # weather
    r"for\s+maintenance",  # intentional downtime
    r"by\s+design",  # intentional behavior
    r"on\s+purpose",  # intentional action
    r"intentional",  # explicitly intentional
    r"is\s+expected",  # acknowledged as expected behavior
]


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


def should_match_prompt(prompt):
    """Determine if prompt describes a real issue or a false positive.

    Returns True if:
    - Prompt contains issue keywords AND
    - Doesn't match false positive patterns
    """
    # Must match base pattern
    if not ISSUE_PATTERNS.search(prompt):
        return False

    # Check for false positive indicators
    for fp_pattern in FALSE_POSITIVE_PATTERNS:
        if re.search(fp_pattern, prompt, re.IGNORECASE):
            return False

    return True


def main():
    try:
        data = json.load(sys.stdin)

        # Extract user's message
        prompt = data.get("prompt", "")
        if not prompt:
            sys.exit(0)

        # Check if prompt describes a real issue (not a false positive)
        if not should_match_prompt(prompt):
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
