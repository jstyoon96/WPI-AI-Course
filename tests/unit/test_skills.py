import re
from pathlib import Path


SKILLS_DIR = Path(".agents/skills")


def test_skill_frontmatter_names_are_unique_and_described():
    skill_files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    names = []

    for path in skill_files:
        text = path.read_text(encoding="utf-8")
        match = re.match(
            r"---\n(?P<body>.*?)\n---",
            text,
            flags=re.DOTALL,
        )
        assert match, f"missing YAML frontmatter: {path}"
        body = match.group("body")
        name = _frontmatter_value(body, "name")
        description = _frontmatter_value(body, "description")
        assert name
        assert description
        names.append(name)

    assert len(names) == len(set(names))


def test_course_skills_cover_material_production_workflow():
    names = {
        _frontmatter_value(
            re.match(r"---\n(?P<body>.*?)\n---", path.read_text(encoding="utf-8"), flags=re.DOTALL).group("body"),
            "name",
        )
        for path in SKILLS_DIR.glob("*/SKILL.md")
    }

    required = {
        "course-material-authoring",
        "draft-to-lab-conversion",
        "colab-notebook-authoring",
        "data-source-review",
        "lab-release-review",
    }
    assert required.issubset(names)


def test_skills_do_not_use_old_research_harness_wording():
    text = "\n".join(path.read_text(encoding="utf-8") for path in SKILLS_DIR.glob("*/SKILL.md"))
    forbidden_phrase = "research " + "harness"
    assert forbidden_phrase not in text.lower()
    assert "ml-research" not in text.lower()


def _frontmatter_value(frontmatter: str, key: str) -> str:
    for line in frontmatter.splitlines():
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip().strip('"')
    return ""
