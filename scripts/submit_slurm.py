#!/usr/bin/env python3
"""Slurm submission placeholder."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a Slurm submission.")
    parser.add_argument("--config", required=True, help="Path to experiment config.")
    parser.add_argument("--stage", default="proxy", help="Experiment stage.")
    parser.add_argument("--approved", action="store_true", help="Only set after explicit human approval.")
    args = parser.parse_args()

    config = Path(args.config)
    if not config.exists():
        parser.error(f"config not found: {config}")

    if not args.approved:
        print("Slurm submission requires explicit human approval. No job was submitted.")
        return 2

    print("Slurm submission is not implemented in the skeleton. No job was submitted.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

