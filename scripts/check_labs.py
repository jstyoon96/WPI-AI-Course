#!/usr/bin/env python3
"""Validate the WPI AI Bootcamp lab repository structure."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from wpi_ai_bootcamp import check_repository  # noqa: E402


def main() -> int:
    errors = check_repository(ROOT)
    if errors:
        for error in errors:
            print(f"{error.path}: {error.message}")
        return 1

    print("Lab repository checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
