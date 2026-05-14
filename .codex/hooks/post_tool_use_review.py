#!/usr/bin/env python3
"""PostToolUse review guardrails for course-material commands."""

from __future__ import annotations

import json
import re
import sys


SIGNALS = [
    (re.compile(r"(FAILED|ERROR).*(pytest|tests?)|assertionerror|traceback", re.I | re.S), "A test or Python command appears to have failed."),
    (re.compile(r"invalid notebook JSON|missing Colab|missing TODO", re.I), "A lab material validation check appears to have failed."),
    (re.compile(r"\binstructor/|\b(answer key|completed notebook)\b", re.I), "Output mentions instructor-only material; verify it is not public or staged."),
    (re.compile(r"secret-like|private key|api[_-]?key|token|password", re.I), "Output mentions possible secret material."),
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


def main() -> int:
    event = _read_event()
    text = "\n".join(_walk_strings(event))
    notes = [message for pattern, message in SIGNALS if pattern.search(text)]
    if notes:
        sys.stdout.write(
            json.dumps(
                {
                    "decision": "block",
                    "reason": "Command result needs review before continuing.",
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": " ".join(notes),
                    },
                    "continue": False,
                },
                ensure_ascii=True,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
