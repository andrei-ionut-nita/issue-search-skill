#!/usr/bin/env python3
"""
Idempotently register issue-search hooks into ~/.claude/settings.json
Called by setup.sh during installation.

Usage:
  python3 register_hooks.py <settings_file_path> <skill_root_dir>
Example:
  python3 register_hooks.py ~/.claude/settings.json ~/.claude/skills/issue-search-skill
"""
import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 3:
        print("Usage: register_hooks.py <settings_path> <skill_root_dir>")
        sys.exit(1)

    settings_path = Path(sys.argv[1]).expanduser()
    skill_root = sys.argv[2]

    # Construct absolute paths to hook scripts
    bash_hook_cmd = f"python3 {skill_root}/scripts/hooks/on_bash_error.py"
    prompt_hook_cmd = f"python3 {skill_root}/scripts/hooks/on_prompt_error.py"

    # Marker to detect if hooks are already installed (idempotency check)
    BASH_MARKER = "on_bash_error"
    PROMPT_MARKER = "on_prompt_error"

    # Load or initialize settings
    if settings_path.exists():
        with open(settings_path, "r") as f:
            settings = json.load(f)
    else:
        settings = {}

    hooks = settings.setdefault("hooks", {})

    # ==========================================
    # Register PostToolUse hook (Bash errors)
    # ==========================================
    post_tool_use = hooks.setdefault("PostToolUse", [])

    # Check if hook is already registered (idempotent)
    already_registered = any(
        BASH_MARKER in json.dumps(h) for h in post_tool_use
    )

    if not already_registered:
        post_tool_use.append({
            "matcher": "Bash",
            "hooks": [
                {
                    "type": "command",
                    "command": bash_hook_cmd,
                    "timeout": 30
                }
            ]
        })
        print("[OK] Registered PostToolUse hook for Bash errors")
    else:
        print("[OK] PostToolUse hook already registered (idempotent)")

    # ==========================================
    # Register UserPromptSubmit hook
    # ==========================================
    user_prompt_submit = hooks.setdefault("UserPromptSubmit", [])

    # Check if hook is already registered (idempotent)
    already_registered = any(
        PROMPT_MARKER in json.dumps(h) for h in user_prompt_submit
    )

    if not already_registered:
        user_prompt_submit.append({
            "matcher": "",
            "hooks": [
                {
                    "type": "command",
                    "command": prompt_hook_cmd,
                    "timeout": 15
                }
            ]
        })
        print("[OK] Registered UserPromptSubmit hook for error detection")
    else:
        print("[OK] UserPromptSubmit hook already registered (idempotent)")

    # Write updated settings back to file
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)

    print(f"[OK] settings.json updated at {settings_path}")


if __name__ == "__main__":
    main()
