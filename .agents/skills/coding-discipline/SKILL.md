---
name: "coding-discipline"
description: "Use when writing, refactoring, debugging, or reviewing code in this repository, including CLI scripts, tests, hooks, adapters, registries, runners, and report helpers."
---

# Coding Discipline

Use this skill whenever the task changes code or tests. Pair it with
`ml-research-harness` when the change also touches research policy, experiment
workflow, metrics, data, training, evaluation, Slurm, or reports.

## Core Rule
Make the smallest correct change that can be explained, reviewed, and checked.

## Ground Before Coding
- Read the relevant files before editing.
- Identify the current local pattern and follow it.
- State important assumptions when the code or request leaves a real ambiguity.
- Prefer existing helpers and interfaces over inventing a new abstraction.

## Simplicity First
- Start with the direct implementation that solves the stated problem.
- Add abstractions only when they remove real duplication or clarify a stable interface.
- Avoid speculative generality, broad rewrites, and unrelated cleanup.
- Keep placeholder code honest: mark it as placeholder and do not claim real behavior.

## Surgical Changes
- Modify only files needed for the task.
- Preserve user edits and unrelated work.
- Keep public interfaces stable unless the task requires changing them.
- Do not silently change dataset splits, metric definitions, label rules, or final evaluation behavior.

## Goal-Driven Execution
- Define what success means before coding.
- Choose the cheapest checks that prove the change works.
- Prefer fast feedback: syntax checks, import checks, unit tests, smoke commands.
- Do not run full training, Slurm jobs, multi-GPU jobs, or large sweeps without explicit approval.

## Validation Loop
- After editing, run focused checks when available.
- If a check fails, report the exact failure and likely cause.
- If a tool is missing, say so instead of pretending the check passed.
- Remove generated caches or temporary files unless they are intended artifacts.

## Failure Honesty
- Never hide failing tests, NaN losses, OOMs, skipped checks, or unimplemented paths.
- Do not claim scientific improvement without metrics from the defined evaluation protocol.
- Do not claim production readiness for skeleton, placeholder, or smoke-only code.

## Final Report
For code changes, summarize:

- what changed
- files changed
- checks run
- check results
- remaining risks
- next recommended step

