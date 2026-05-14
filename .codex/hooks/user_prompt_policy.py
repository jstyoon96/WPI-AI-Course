#!/usr/bin/env python3
"""UserPromptSubmit guardrails for the WPI AI Bootcamp course repo."""

from __future__ import annotations

import json
import re
import sys


SECRET_PATTERNS = [
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.I),
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\b(api[_-]?key|token|password|secret)\s*[:=]\s*\S+", re.I),
    re.compile(r"\bcat\s+~?/?.*\.ssh/id_[A-Za-z0-9_-]*", re.I),
]

RISK_CONTEXT = [
    (
        re.compile(r"\b(solution|answer key|completed notebook)\b", re.I),
        "Keep completed answers in gitignored instructor folders unless the user explicitly asks for a public release artifact.",
    ),
    (
        re.compile(r"\b(slide|ppt|pptx|deck)\b", re.I),
        "Slides are instructor-only by default and should stay under gitignored instructor folders.",
    ),
    (
        re.compile(r"\b(MITDeepLearning|introtodeeplearning|MIT 6\.S191)\b", re.I),
        "MIT material is a structural reference; copying content requires attribution and license review.",
    ),
    (
        re.compile(r"\bMATLAB(?:\s+Online)?\b", re.I),
        "Public student labs should be converted to Python/Colab notebook instructions.",
    ),
    (
        re.compile(r"\b(Turing|HPC|Slurm|sbatch)\b", re.I),
        "Turing/HPC support is future runtime work; keep Colab as the v1 student default unless told otherwise.",
    ),
]


def _read_event() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"prompt": raw}


def _emit(payload: dict) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=True))


def main() -> int:
    event = _read_event()
    prompt = str(event.get("prompt", ""))

    for pattern in SECRET_PATTERNS:
        if pattern.search(prompt):
            _emit(
                {
                    "decision": "block",
                    "reason": "Prompt appears to include or request secrets/SSH private keys. Redact secrets and ask for a safe diagnostic instead.",
                }
            )
            return 0

    notes = [message for pattern, message in RISK_CONTEXT if pattern.search(prompt)]
    if notes:
        _emit(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": " ".join(notes),
                }
            }
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
