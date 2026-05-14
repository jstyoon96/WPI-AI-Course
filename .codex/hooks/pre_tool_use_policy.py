#!/usr/bin/env python3
"""PreToolUse command guardrails for the WPI AI Bootcamp course repo."""

from __future__ import annotations

import json
import re
import sys


DENY_PATTERNS = [
    (re.compile(r"\brm\s+-rf\s+/(?:\s|$)"), "Refusing destructive root deletion."),
    (re.compile(r"\bcat\s+~?/?.*\.ssh/id_[A-Za-z0-9_-]*", re.I), "Refusing to read SSH private keys."),
    (re.compile(r"(^|[;&|]\s*)(printenv|env)(\s|$)"), "Refusing to dump environment variables."),
    (re.compile(r"\bgit\s+push\s+--force\b"), "Refusing force push without explicit approval."),
    (re.compile(r"\bgit\s+add\b.*\binstructor/"), "Refusing to stage instructor-only materials."),
    (re.compile(r"\bgit\s+add\b.*\bdraft/"), "Refusing to stage draft source materials."),
    (re.compile(r"\bgit\s+add\b.*(?<!src/wpi_ai_bootcamp/)data/"), "Refusing to stage root data files."),
    (
        re.compile(r"\bWPI_week\d+/lab\d+/[^\s]*?(solution|answer|instructor|key|draft)[^\s]*", re.I),
        "Refusing public lab path that looks instructor-only.",
    ),
    (re.compile(r"\bMATLAB(?:\s+Online)?\b", re.I), "Refusing prohibited runtime wording for public Colab labs."),
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

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
