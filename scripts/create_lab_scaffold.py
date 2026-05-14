#!/usr/bin/env python3
"""Create WPI AI Bootcamp week/lab scaffolds from templates."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LAB_TEMPLATE_DIR = ROOT / "templates" / "lab"
WEEK_TEMPLATE_DIR = ROOT / "templates" / "week"
DEFAULT_TITLES = {
    (1, 1): "Biomedical Imaging",
    (1, 2): "Biomedical Signals",
}


def week_dir_name(week: int) -> str:
    return f"WPI_week{week}"


def lab_dir_name(lab: int) -> str:
    return f"lab{lab}"


def notebook_name(week: int, lab: int) -> str:
    return f"WPI_week{week}_lab{lab}.ipynb"


def default_title(week: int, lab: int) -> str:
    return DEFAULT_TITLES.get((week, lab), f"Topic Placeholder")


def _render(template: str, values: dict[str, str]) -> str:
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace("{{" + key + "}}", value)
    return rendered


def _write_rendered(template_path: Path, output_path: Path, values: dict[str, str], overwrite: bool) -> Path | None:
    if output_path.exists() and not overwrite:
        return None
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        _render(template_path.read_text(encoding="utf-8"), values),
        encoding="utf-8",
    )
    return output_path


def create_week(week: int, overwrite: bool = False) -> list[Path]:
    week_dir = ROOT / week_dir_name(week)
    values = {
        "WEEK_NUMBER": str(week),
        "WEEK_TITLE": f"WPI Week {week}",
        "LAB1_TITLE": default_title(week, 1),
        "LAB2_TITLE": default_title(week, 2),
    }
    written = _write_rendered(WEEK_TEMPLATE_DIR / "README.md", week_dir / "README.md", values, overwrite)
    return [written] if written else []


def create_lab(week: int, lab: int, title: str | None = None, overwrite: bool = False) -> list[Path]:
    if week < 1 or lab < 1:
        raise ValueError("week and lab must be positive integers")

    week_dir = ROOT / week_dir_name(week)
    lab_dir = week_dir / lab_dir_name(lab)
    nb_name = notebook_name(week, lab)
    values = {
        "LAB_DIR": f"{week_dir.name}/{lab_dir.name}",
        "LAB_TITLE": title or default_title(week, lab),
        "NOTEBOOK_NAME": nb_name,
        "NOTEBOOK_STEM": Path(nb_name).stem,
    }

    outputs = [
        (LAB_TEMPLATE_DIR / "README.md", lab_dir / "README.md"),
        (LAB_TEMPLATE_DIR / "notebook.ipynb", lab_dir / nb_name),
        (LAB_TEMPLATE_DIR / "img_README.md", lab_dir / "img" / "README.md"),
    ]

    written: list[Path] = []
    written.extend(create_week(week, overwrite=overwrite))
    for template_path, output_path in outputs:
        result = _write_rendered(template_path, output_path, values, overwrite)
        if result:
            written.append(result)
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description="Create WPI week/lab scaffolds.")
    parser.add_argument("--week", type=int, help="Week number.")
    parser.add_argument("--lab", type=int, help="Lab number within the week.")
    parser.add_argument("--title", help="Student-facing lab title.")
    parser.add_argument("--all", action="store_true", help="Create Week 1-4, Lab 1-2 scaffolds.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing scaffold files.")
    args = parser.parse_args()

    if args.all:
        targets = [(week, lab, default_title(week, lab)) for week in range(1, 5) for lab in range(1, 3)]
    else:
        if args.week is None or args.lab is None:
            parser.error("provide --week and --lab, or use --all")
        targets = [(args.week, args.lab, args.title or default_title(args.week, args.lab))]

    for week, lab, title in targets:
        written = create_lab(week, lab, title=title, overwrite=args.overwrite)
        status = "updated" if written else "already exists"
        print(f"{week_dir_name(week)}/{lab_dir_name(lab)}: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
