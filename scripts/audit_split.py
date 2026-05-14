#!/usr/bin/env python3
"""Placeholder split audit entrypoint."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit train/validation/test splits.")
    parser.add_argument("--config", default="configs/base.yaml", help="Path to experiment config.")
    args = parser.parse_args()

    config = Path(args.config)
    if not config.exists():
        parser.error(f"config not found: {config}")

    print(f"Split audit placeholder passed for {config}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

