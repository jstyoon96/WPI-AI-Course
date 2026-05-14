#!/usr/bin/env python3
"""Slurm monitoring placeholder."""

from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description="Monitor a Slurm job.")
    parser.add_argument("--job-id", required=True, help="Slurm job identifier.")
    args = parser.parse_args()

    print(f"Slurm monitor placeholder for job {args.job_id}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

