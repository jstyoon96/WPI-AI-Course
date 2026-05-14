"""Slurm guard skeleton."""

from __future__ import annotations


def require_approval(approved: bool) -> None:
    if not approved:
        raise PermissionError("Slurm submission requires explicit human approval.")


def build_submit_message(config_path: str, stage: str, approved: bool = False) -> str:
    require_approval(approved)
    return f"Slurm submission placeholder for config={config_path} stage={stage}"

