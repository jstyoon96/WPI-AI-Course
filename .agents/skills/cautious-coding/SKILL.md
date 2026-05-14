---
name: "cautious-coding"
description: "Use when writing, editing, debugging, refactoring, or reviewing code. Applies behavioral guardrails for explicit assumptions, simplicity, surgical changes, goal-driven verification, tests, and concise reporting."
---

# Cautious Coding

Use this skill for code work in any repository. Merge these guardrails with project-specific instructions, and let stricter project rules win.

## Before Coding

- State assumptions explicitly when they affect the implementation.
- If the request has multiple reasonable interpretations, name them and ask before editing unless one interpretation is clearly low risk.
- Surface tradeoffs when they matter, including when a simpler approach is enough.
- Stop and ask when uncertainty would make the change risky or hard to verify.

## Simplicity First

- Write the minimum code that solves the requested problem.
- Do not add speculative features, abstractions, configurability, or broad error handling.
- Prefer direct, local changes over new shared machinery for one-off needs.
- If the implementation grows large, look for a smaller design before continuing.

## Surgical Changes

- Touch only files needed for the request.
- Match existing style, naming, and patterns even when another style is personally preferable.
- Do not refactor adjacent code, reformat unrelated blocks, or remove pre-existing dead code unless asked.
- Remove only imports, variables, helpers, and tests made unused by your own change.
- Every changed line should trace back to the user request or the verification needed for it.

## Goal-Driven Execution

- Convert the task into verifiable success criteria before implementing.
- For bugs, prefer a failing test or small reproduction first, then make it pass.
- For validation changes, test invalid and valid inputs.
- For refactors, preserve behavior and run the relevant checks before and after when practical.
- Keep looping until the chosen verification passes or a concrete blocker is found.

## Reporting

- Summarize what changed, why, files changed, checks run, results, risks, and the next useful action.
- Report skipped checks and why they were skipped.
- Mention unrelated issues observed during the work, but do not fix them unless asked.
