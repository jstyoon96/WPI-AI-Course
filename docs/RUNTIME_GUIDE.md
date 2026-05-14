# Runtime Guide

## Official Runtime For V1
Google Colab is the official student runtime for the first version of the
bootcamp labs.

## Colab Checklist
- Include a Colab badge or clear Colab instruction in each notebook.
- Keep setup cells self-contained.
- State when GPU runtime is required.
- Avoid local absolute paths.
- Keep datasets small or downloaded from stable public sources.

## Local Development
Local development is allowed for authors and reviewers. The repository's
lightweight checks can be run with:

```bash
python3 scripts/check_labs.py
pytest tests/unit tests/smoke
```

## Future Turing/HPC Support
If WPI Turing/HPC becomes an official runtime, add a dedicated section with
environment setup, job submission policy, storage paths, and expected resource
limits. Do not mix Turing-only instructions into student Colab notebooks unless
that lab explicitly targets Turing.
