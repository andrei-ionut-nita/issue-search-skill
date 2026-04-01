#!/usr/bin/env python3
"""
PostToolUse hook: Fires after every Bash command.
If the command failed (exit code != 0), automatically searches the knowledge base
for similar issues and captures the error.
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


def map_symptom(text):
    """Map error output to a symptom category."""
    t = text.lower()

    if any(x in t for x in ["timeout", "timed out", "deadline exceeded"]):
        return "timeout"
    if any(x in t for x in ["import", "no module", "not found", "modulenotfounderror", "cannot find"]):
        return "dependency_failure"
    if any(x in t for x in ["nameerror", "undefined", "nonetype", "attributeerror", "referenceerror"]):
        return "null_pointer"
    if any(x in t for x in ["auth", "permission denied", "unauthorized", "forbidden", "unauthenticated"]):
        return "auth_failure"
    if any(x in t for x in ["connection", "refused", "network", "unreachable", "econnrefused", "offline"]):
        return "api_error"
    if any(x in t for x in ["out of memory", "memory", "oom", "heap"]):
        return "memory_leak"
    if any(x in t for x in ["deadlock", "race condition", "concurrent", "thread"]):
        return "race_condition"
    if any(x in t for x in ["corrupt", "data loss", "truncated", "incomplete"]):
        return "data_loss"

    return "config_error"


def main():
    try:
        data = json.load(sys.stdin)

        # Only process Bash tool results
        if data.get("tool_name") != "Bash":
            sys.exit(0)

        response = data.get("tool_response", {})

        # Extract exit code (may be in different keys depending on Claude Code version)
        exit_code = response.get("exit_code", response.get("returncode", 0))
        if not exit_code or exit_code == 0:
            sys.exit(0)

        # Build error context from stdout + stderr
        stdout = str(response.get("stdout", ""))
        stderr = str(response.get("stderr", ""))
        output = stdout + stderr

        symptom = map_symptom(output)
        cli_path = get_cli_path()

        # Search knowledge base
        search_result = subprocess.run(
            [sys.executable, cli_path, "search", "--symptom", symptom],
            capture_output=True,
            text=True,
            timeout=10
        )

        # Auto-capture the error
        cmd = data.get("tool_input", {}).get("command", "unknown command")
        subprocess.run(
            [sys.executable, cli_path, "capture",
             "--description", f"Bash failed (exit {exit_code}): {cmd[:120]}",
             "--symptoms", symptom],
            capture_output=True,
            timeout=10
        )

        # Return search results as system message so Claude sees them
        search_output = search_result.stdout.strip()
        if search_output:
            msg = f"[issue-search] Auto-searched for '{symptom}' errors.\n{search_output}"
            print(json.dumps({"systemMessage": msg}))

    except Exception:
        # Silently fail — don't let hook errors break the session
        pass
    finally:
        sys.exit(0)


if __name__ == "__main__":
    main()
