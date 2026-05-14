#!/usr/bin/env python3
"""Stop hook validation for final course-material task summaries."""

from __future__ import annotations

import json
import re
import sys


REQUIRED = [
    ("Summary", re.compile(r"\bsummary\b|요약", re.I)),
    ("Changed files", re.compile(r"\bchanged files?\b|\bfiles changed\b|변경\s*파일", re.I)),
    ("Tests run", re.compile(r"\btests? run\b|실행한\s*테스트|테스트\s*실행", re.I)),
    ("Test results", re.compile(r"\btest results?\b|테스트\s*결과", re.I)),
    ("Risks", re.compile(r"\brisks?\b|위험|리스크", re.I)),
    (
        "Next recommended step",
        re.compile(r"\bnext recommended step\b|\bnext action\b|권장\s*다음\s*단계|다음\s*(권장\s*)?(단계|작업)", re.I),
    ),
]


def _read_event() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"last_assistant_message": raw}


def _emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=True))


def main() -> int:
    event = _read_event()
    message = str(event.get("last_assistant_message") or "")
    if not message.strip():
        _emit({})
        return 0

    missing = [label for label, pattern in REQUIRED if not pattern.search(message)]
    if missing:
        _emit(
            {
                "decision": "block",
                "reason": "Final response is missing required course-material report fields: "
                + ", ".join(missing)
                + ". Continue and provide the required summary.",
            }
        )
        return 0

    _emit({})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
