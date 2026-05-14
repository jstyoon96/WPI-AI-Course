"""Static checks for the WPI AI Bootcamp course repository."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


WEEKS = tuple(f"WPI_week{week}" for week in range(1, 5))
LABS = ("lab1", "lab2")
PRIVATE_NAME_RE = re.compile(r"(solution|answer|instructor|key|draft)", re.IGNORECASE)
SECRET_RE = re.compile(
    r"(-----BEGIN [A-Z ]*PRIVATE KEY-----|\bsk-[A-Za-z0-9_-]{20,}\b|"
    r"\b(api[_-]?key|token|password|secret)\s*[:=]\s*\S+)",
    re.IGNORECASE,
)
LOCAL_PATH_RE = re.compile(r"(/home/|/Users/|C:\\\\Users\\\\)")
PROHIBITED_RUNTIME_RE = re.compile(r"\bMATLAB(?:\s+Online)?\b", re.IGNORECASE)
WPI_STYLE_RE = re.compile(r"(apply_wpi_plot_style|wpi_ai_bootcamp\.style|WPI_COLORS)")
ASSESSMENT_RE = re.compile(r"(100 pts|100 points)")
WORD_RESPONSE_RE = re.compile(r"(Word response|responses_LastName_FirstName\.docx)")


@dataclass(frozen=True)
class LabCheckError:
    """A validation issue found in the course repository."""

    path: str
    message: str


def expected_notebook_name(week_name: str, lab_name: str) -> str:
    """Return the required notebook filename for a week/lab directory."""

    return f"{week_name}_{lab_name}.ipynb"


def _read_notebook(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid notebook JSON: {exc}") from exc


def _cell_text(notebook: dict) -> str:
    parts: list[str] = []
    for cell in notebook.get("cells", []):
        source = cell.get("source", [])
        if isinstance(source, list):
            parts.extend(str(item) for item in source)
        else:
            parts.append(str(source))
    return "".join(parts)


def _has_colab_guidance(text: str) -> bool:
    lowered = text.lower()
    return "colab.research.google.com" in lowered or "google colab" in lowered


def _notebook_output_count(notebook: dict) -> int:
    count = 0
    for cell in notebook.get("cells", []):
        outputs = cell.get("outputs", [])
        if isinstance(outputs, list):
            count += len(outputs)
    return count


def _check_text(path: Path, text: str) -> list[LabCheckError]:
    errors: list[LabCheckError] = []
    if SECRET_RE.search(text):
        errors.append(LabCheckError(str(path), "contains secret-like text"))
    if LOCAL_PATH_RE.search(text):
        errors.append(LabCheckError(str(path), "contains local absolute path"))
    if PROHIBITED_RUNTIME_RE.search(text):
        errors.append(LabCheckError(str(path), "contains prohibited runtime wording"))
    return errors


def _check_lab(root: Path, week_name: str, lab_name: str) -> list[LabCheckError]:
    errors: list[LabCheckError] = []
    lab_dir = root / week_name / lab_name
    readme = lab_dir / "README.md"
    img_readme = lab_dir / "img" / "README.md"
    expected_notebook = lab_dir / expected_notebook_name(week_name, lab_name)

    if not lab_dir.is_dir():
        return [LabCheckError(str(lab_dir), "lab directory is missing")]

    for required in (readme, img_readme):
        if not required.is_file():
            errors.append(LabCheckError(str(required), "required lab file is missing"))
        else:
            errors.extend(_check_text(required, required.read_text(encoding="utf-8")))

    if not expected_notebook.is_file():
        errors.append(LabCheckError(str(expected_notebook), "matching lab notebook is missing"))

    notebooks = sorted(lab_dir.glob("*.ipynb"))
    for notebook in [path for path in notebooks if path != expected_notebook]:
        errors.append(LabCheckError(str(notebook), "unexpected public notebook filename"))

    for public_file in lab_dir.rglob("*"):
        if public_file.is_file() and PRIVATE_NAME_RE.search(public_file.name):
            errors.append(
                LabCheckError(
                    str(public_file),
                    "public lab folder contains private or instructor-only filename",
                )
            )

    if expected_notebook.is_file():
        try:
            notebook = _read_notebook(expected_notebook)
        except ValueError as exc:
            errors.append(LabCheckError(str(expected_notebook), str(exc)))
        else:
            text = _cell_text(notebook)
            if not _has_colab_guidance(text):
                errors.append(LabCheckError(str(expected_notebook), "missing Colab guidance"))
            if "TODO" not in text:
                errors.append(LabCheckError(str(expected_notebook), "missing TODO marker"))
            if not WPI_STYLE_RE.search(text):
                errors.append(LabCheckError(str(expected_notebook), "missing WPI visual style setup"))
            if not ASSESSMENT_RE.search(text):
                errors.append(LabCheckError(str(expected_notebook), "missing 100-point assessment total"))
            if not WORD_RESPONSE_RE.search(text):
                errors.append(LabCheckError(str(expected_notebook), "missing Word response instructions"))
            errors.extend(_check_text(expected_notebook, text))
            if _notebook_output_count(notebook) > 5:
                errors.append(LabCheckError(str(expected_notebook), "contains too many outputs"))

    return errors


def _check_week(root: Path, week_name: str) -> list[LabCheckError]:
    errors: list[LabCheckError] = []
    week_dir = root / week_name
    readme = week_dir / "README.md"

    if not week_dir.is_dir():
        return [LabCheckError(str(week_dir), "week directory is missing")]

    if not readme.is_file():
        errors.append(LabCheckError(str(readme), "week README is missing"))
    else:
        errors.extend(_check_text(readme, readme.read_text(encoding="utf-8")))

    for lab_name in LABS:
        errors.extend(_check_lab(root, week_name, lab_name))
    return errors


def _check_gitignore(root: Path) -> list[LabCheckError]:
    gitignore = root / ".gitignore"
    if not gitignore.is_file():
        return [LabCheckError(".gitignore", "missing .gitignore")]

    text = gitignore.read_text(encoding="utf-8")
    errors: list[LabCheckError] = []
    for pattern in ("instructor/", "draft/", "data/"):
        if pattern not in text:
            errors.append(LabCheckError(".gitignore", f"{pattern} is not ignored"))
    return errors


def check_repository(root: Path | str = ".") -> list[LabCheckError]:
    """Return validation errors for the course repository."""

    root_path = Path(root)
    errors: list[LabCheckError] = []

    for week_name in WEEKS:
        errors.extend(_check_week(root_path, week_name))

    errors.extend(_check_gitignore(root_path))
    return errors
