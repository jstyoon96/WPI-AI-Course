#!/usr/bin/env python3
"""Training entrypoint placeholder."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Train a model with the research harness.")
    parser.add_argument("--config", default="configs/base.yaml", help="Path to experiment config.")
    parser.add_argument("--dry-run", action="store_true", help="Validate config without training.")
    parser.add_argument("--fast-dev-run", action="store_true", help="Run a tiny smoke training path.")
    args = parser.parse_args()

    config = Path(args.config)
    if not config.exists():
        parser.error(f"config not found: {config}")

    if args.dry_run:
        print(f"Dry run placeholder passed for {config}.")
        return 0

    if args.fast_dev_run:
        print(f"Fast-dev-run placeholder passed for {config}.")
        return 0

    print("Full training requires explicit human approval and is not implemented in the skeleton.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

