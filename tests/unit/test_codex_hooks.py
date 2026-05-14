import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
HOOKS_JSON = ROOT / ".codex" / "hooks.json"
PRE_TOOL_HOOK = ROOT / ".codex" / "hooks" / "pre_tool_use_policy.py"
STOP_HOOK = ROOT / ".codex" / "hooks" / "stop_validation.py"


def test_tool_hook_matchers_cover_shell_and_file_edits():
    config = json.loads(HOOKS_JSON.read_text(encoding="utf-8"))

    pre_matcher = config["hooks"]["PreToolUse"][0]["matcher"]
    post_matcher = config["hooks"]["PostToolUse"][0]["matcher"]

    for tool_name in ("Bash", "apply_patch", "Edit", "Write"):
        assert tool_name in pre_matcher
        assert tool_name in post_matcher


def test_pre_tool_hook_denies_private_or_public_answer_paths():
    private_stage = _run_hook(
        PRE_TOOL_HOOK,
        {
            "tool_name": "Bash",
            "tool_input": {"command": "git add instructor/slides/week1.pptx"},
        },
    )
    public_answer = _run_hook(
        PRE_TOOL_HOOK,
        {
            "tool_name": "Bash",
            "tool_input": {
                "command": "git add "
                + "WPI_week"
                + "1"
                + "/lab"
                + "1/WPI_week1_"
                + "lab"
                + "1_answer.ipynb"
            },
        },
    )
    draft_stage = _run_hook(
        PRE_TOOL_HOOK,
        {
            "tool_name": "Bash",
            "tool_input": {"command": "git add draft/Week 1_final_v1/Lab.ipynb"},
        },
    )
    root_data_stage = _run_hook(
        PRE_TOOL_HOOK,
        {
            "tool_name": "Bash",
            "tool_input": {"command": "git add data/example.csv"},
        },
    )
    package_data_stage = _run_hook(
        PRE_TOOL_HOOK,
        {
            "tool_name": "Bash",
            "tool_input": {"command": "git add src/wpi_ai_bootcamp/data/signals.py"},
        },
    )
    safe_check = _run_hook(
        PRE_TOOL_HOOK,
        {
            "tool_name": "Bash",
            "tool_input": {"command": "python3 scripts/check_labs.py"},
        },
    )

    assert private_stage["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert public_answer["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert draft_stage["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert root_data_stage["hookSpecificOutput"]["permissionDecision"] == "deny"
    assert package_data_stage == {}
    assert safe_check == {}


def test_stop_hook_accepts_english_and_korean_final_reports():
    english = "\n".join(
        [
            "Summary",
            "Changed files",
            "Tests run",
            "Test results",
            "Risks",
            "Next recommended step",
        ]
    )
    korean = "\n".join(
        [
            "요약",
            "변경 파일",
            "실행한 테스트",
            "테스트 결과",
            "위험",
            "권장 다음 단계",
        ]
    )

    assert _run_hook(STOP_HOOK, {"last_assistant_message": english}) == {}
    assert _run_hook(STOP_HOOK, {"last_assistant_message": korean}) == {}


def test_stop_hook_blocks_incomplete_final_report():
    result = _run_hook(STOP_HOOK, {"last_assistant_message": "Summary only"})

    assert result["decision"] == "block"
    assert "Changed files" in result["reason"]


def _run_hook(path: Path, event: dict) -> dict:
    result = subprocess.run(
        [sys.executable, str(path)],
        input=json.dumps(event),
        capture_output=True,
        check=True,
        text=True,
    )
    return json.loads(result.stdout or "{}")
