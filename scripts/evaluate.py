#!/usr/bin/env python3
"""Evaluation entrypoint placeholder."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate a model with the research harness.")
    parser.add_argument("--config", default="configs/base.yaml", help="Path to experiment config.")
    parser.add_argument("--run-id", help="Experiment run identifier.")
    parser.add_argument("--small", action="store_true", help="Run a small evaluation smoke path.")
    args = parser.parse_args()

    config = Path(args.config)
    if not config.exists():
        parser.error(f"config not found: {config}")

    if args.small:
        target = f" for run {args.run_id}" if args.run_id else ""
        print(f"Small evaluation placeholder passed{target} with {config}.")
        return 0

    print("Full evaluation requires a real run artifact and is not implemented in the skeleton.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
