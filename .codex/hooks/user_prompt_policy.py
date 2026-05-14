#!/usr/bin/env python3
"""UserPromptSubmit guardrails for the ML research harness."""

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
    (re.compile(r"\b(full training|full train|run full|--full)\b", re.I), "Full training requires explicit approval and passing smoke checks first."),
    (re.compile(r"\b(sbatch|slurm|multi-gpu|multi gpu)\b", re.I), "Slurm, multi-GPU, or long-running jobs require explicit approval."),
    (re.compile(r"\b(test split|final split|dataset split)\b.*\b(change|modify|edit)\b", re.I), "Dataset split changes require explicit approval and a proposal."),
    (re.compile(r"\b(metric|evaluation code)\b.*\b(change|modify|edit)\b", re.I), "Metric and evaluation-code changes require explicit approval."),
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
