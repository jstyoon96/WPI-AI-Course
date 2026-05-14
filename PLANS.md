# PLANS.md

This file records implementation plans for the WPI AI Bootcamp lab materials.

## Production System
- Use `WPI_week{n}/lab{m}` as the public lab folder convention.
- Keep Week 1-4, Lab 1-2 scaffolds available by default.
- Generate lab folders from `templates/lab/` with `scripts/create_lab_scaffold.py`.
- Keep reusable data loading code in `src/wpi_ai_bootcamp/data/`.
- Keep raw weekly drafts in gitignored `draft/`.
- Keep slides, completed answers, and review notes in gitignored `instructor/`.
- Validate public labs with `python3 scripts/check_labs.py`.

## Near-Term TODOs
- Replace Week 2-4 placeholder topics with instructor drafts.
- Convert Week 1 imaging and signals drafts into Colab notebook content.
- Review data choices before adding any public sample data.
- Add release review notes after the first complete lab conversion.
