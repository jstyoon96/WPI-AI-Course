# EXPERIMENT_POLICY

## Allowed Without Approval
- small code refactors
- config schema changes
- unit tests
- dry runs
- fast-dev-runs
- small evaluation smoke tests
- report generation

## Forbidden Without Approval
- final test split changes
- primary metric definition changes
- label generation rule changes
- dataset filtering rule changes
- final report selection criteria changes
- printing, storing, or committing secrets

## Requires Approval
- full training
- Slurm submission
- multi-GPU job
- large hyperparameter sweep
- remote job submission
- external dependency additions
- model family replacement

## Promotion Rules
Use staged promotion:

1. static checks
2. dry run / fast-dev-run
3. tiny proxy experiment
4. medium proxy experiment
5. full training with human approval

## Reporting Requirements
Every task must report changed files, tests run, test results, risks, and recommended next step.

