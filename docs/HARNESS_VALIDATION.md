# HARNESS_VALIDATION

## Purpose

This document records template-local Codex harness checks before deeper project
implementation. The goal is to verify that repository guidance, hooks, skills,
custom agents, and safe smoke commands work before changing split, metric, or
training behavior.

## Official OpenAI Docs Checks

- Hooks are enabled through `[features] codex_hooks = true` in
  `.codex/config.toml`.
- Project-local hooks live in `.codex/hooks.json`.
- Project `.codex/` layers load only when the project is trusted by Codex.
- Repo-local skills are read from `.agents/skills`.
- Repo-local custom agents are defined as `.codex/agents/*.toml`.
- `AGENTS.md` at the repository root is the project instruction source.

Sources:

- Hooks: https://developers.openai.com/codex/hooks
- Config basics: https://developers.openai.com/codex/config-basic
- Agent skills: https://developers.openai.com/codex/skills
- Subagents: https://developers.openai.com/codex/subagents
- AGENTS.md: https://developers.openai.com/codex/guides/agents-md

## Hook Expectations

- `UserPromptSubmit` blocks prompts that appear to include secrets or SSH
  private keys, and adds approval context for full training, Slurm, split, and
  metric-risk prompts.
- `PreToolUse` denies destructive root deletion, SSH private-key reads,
  environment dumps, force pushes, direct Slurm submission, and full training
  commands that do not use `--dry-run` or `--fast-dev-run`.
- `PostToolUse` interrupts when command output indicates tests failed, Python
  tracebacks occurred, CUDA OOM happened, NaN metrics/loss appeared, or
  protected policy files are implicated.
- `Stop` requires final harness summaries to include summary, changed files,
  tests run, test results, risks, and next recommended step.

Hook commands are anchored to the repository root with
`git rev-parse --show-toplevel` so they keep working when Codex is launched from
subdirectories.

## Safe Smoke Commands

These commands are allowed without human approval:

```bash
python3 scripts/train.py --config configs/base.yaml --dry-run
python3 scripts/train.py --config configs/base.yaml --fast-dev-run
python3 scripts/audit_data.py --config configs/base.yaml
python3 scripts/evaluate.py --config configs/base.yaml --run-id smoke_test --small
python3 scripts/generate_report.py --latest
```

Full training, Slurm submission, multi-GPU jobs, split finalization, metric
definition changes, and label/target generation changes require explicit human
approval.

## Validation Checklist

- Parse `.codex/hooks.json` as JSON.
- Parse `.codex/config.toml` and `.codex/agents/*.toml` as TOML.
- Compile hook and harness Python files or parse them with `ast`.
- Verify `PreToolUse` denies full training and allows dry-run commands.
- Verify `UserPromptSubmit` adds context for full-training prompts and blocks
  secret/private-key prompts.
- Verify `PostToolUse` blocks failing Python/test output.
- Verify `Stop` blocks final summaries missing required harness fields and
  accepts English or Korean report labels.
- Verify generic dry-run, smoke train, small evaluation, and report commands.

## Known Limitations

- Local skill discovery may require a Codex restart after editing
  `.agents/skills/*/SKILL.md`.
- Hooks are guardrails, not a complete enforcement boundary. The policy still
  depends on `AGENTS.md`, docs, and human approval for protected research
  actions.
