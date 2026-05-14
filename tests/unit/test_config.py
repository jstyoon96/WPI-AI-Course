import json
import re
from pathlib import Path

from wpi_ai_bootcamp import check_repository
from wpi_ai_bootcamp.checks import LABS, WEEKS, expected_notebook_name


def test_public_course_structure_exists():
    assert len(WEEKS) == 4
    assert len(LABS) == 2
    for week in WEEKS:
        assert Path(week).is_dir()
        assert Path(week, "README.md").is_file()
        for lab in LABS:
            assert Path(week, lab).is_dir()
            assert Path(week, lab, "README.md").is_file()
            assert Path(week, lab, expected_notebook_name(week, lab)).is_file()
            assert Path(week, lab, "img", "README.md").is_file()


def test_notebooks_parse_as_json():
    for week in WEEKS:
        for lab in LABS:
            notebook = Path(week, lab, expected_notebook_name(week, lab))
            data = json.loads(notebook.read_text(encoding="utf-8"))
            assert data["nbformat"] >= 4
            assert data["cells"]


def test_private_source_and_root_data_folders_are_ignored():
    text = Path(".gitignore").read_text(encoding="utf-8")
    assert "instructor/" in text
    assert "draft/" in text
    assert "data/" in text


def test_course_checks_pass():
    assert check_repository(".") == []


def test_public_docs_do_not_point_to_legacy_root_lab_paths():
    public_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [
            Path("README.md"),
            Path("docs/COURSE_STRUCTURE.md"),
            Path("docs/LAB_AUTHORING_GUIDE.md"),
            Path("docs/LAB_PRODUCTION_WORKFLOW.md"),
        ]
    )
    assert not re.search(r"WPI_week[0-9]+_lab[0-9]+/", public_text)


def test_data_loader_package_exists():
    assert Path("src/wpi_ai_bootcamp/data/__init__.py").is_file()
    assert Path("src/wpi_ai_bootcamp/data/sources.py").is_file()
    assert Path("src/wpi_ai_bootcamp/data/imaging.py").is_file()
    assert Path("src/wpi_ai_bootcamp/data/signals.py").is_file()


def test_style_package_exists():
    assert Path("src/wpi_ai_bootcamp/style/__init__.py").is_file()
    assert Path("src/wpi_ai_bootcamp/style/colors.py").is_file()
    assert Path("src/wpi_ai_bootcamp/style/plots.py").is_file()
    assert Path("docs/VISUAL_STYLE_GUIDE.md").is_file()


def test_notebooks_include_wpi_visual_style_setup():
    for week in WEEKS:
        for lab in LABS:
            notebook = Path(week, lab, expected_notebook_name(week, lab))
            text = notebook.read_text(encoding="utf-8")
            assert "apply_wpi_plot_style" in text
            assert "WPI_COLORS" in text


def test_notebooks_include_100_point_assessment_and_word_response_instructions():
    for week in WEEKS:
        for lab in LABS:
            notebook = Path(week, lab, expected_notebook_name(week, lab))
            text = notebook.read_text(encoding="utf-8")
            assert "100 pts" in text
            assert "60 pts" in text
            assert "40 pts" in text
            assert "responses_LastName_FirstName.docx" in text
