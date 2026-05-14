#!/usr/bin/env python3
"""PreToolUse command guardrails for the ML research harness."""

from __future__ import annotations

import json
import re
import sys


DENY_PATTERNS = [
    (re.compile(r"\brm\s+-rf\s+/(?:\s|$)"), "Refusing destructive root deletion."),
    (re.compile(r"\bcat\s+~?/?.*\.ssh/id_[A-Za-z0-9_-]*", re.I), "Refusing to read SSH private keys."),
    (re.compile(r"(^|[;&|]\s*)(printenv|env)(\s|$)"), "Refusing to dump environment variables."),
    (re.compile(r"\bgit\s+push\s+--force\b"), "Refusing force push without explicit approval."),
    (re.compile(r"(^|[;&|]\s*)sbatch(\s|$)"), "Refusing direct sbatch submission without approved runner policy."),
]


def _read_event() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"raw": raw}


def _walk_strings(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        strings: list[str] = []
        for item in value.values():
            strings.extend(_walk_strings(item))
        return strings
    if isinstance(value, list):
        strings: list[str] = []
        for item in value:
            strings.extend(_walk_strings(item))
        return strings
    return []


def _command_text(event: dict) -> str:
    candidates = []
    for key in ("command", "cmd", "raw"):
        if key in event:
            candidates.append(str(event[key]))
    candidates.extend(_walk_strings(event.get("tool_input", {})))
    candidates.extend(_walk_strings(event.get("arguments", {})))
    candidates.extend(_walk_strings(event.get("toolCall", {})))
    return "\n".join(candidates)


def _is_full_training_command(command: str) -> bool:
    if not re.search(r"\bscripts/train\.py\b", command):
        return False
    safe_flags = ("--dry-run", "--fast-dev-run")
    if any(flag in command for flag in safe_flags):
        return False
    return True


def _deny(reason: str) -> None:
    sys.stdout.write(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                }
            },
            ensure_ascii=True,
        )
    )


def main() -> int:
    event = _read_event()
    command = _command_text(event)

    for pattern, reason in DENY_PATTERNS:
        if pattern.search(command):
            _deny(reason)
            return 0

    if _is_full_training_command(command) or re.search(r"\b(--full|stage\s*[:=]\s*full)\b", command, re.I):
        _deny("Full training requires explicit human approval and smoke checks first.")
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
