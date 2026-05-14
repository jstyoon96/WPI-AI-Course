from pathlib import Path


def test_base_config_exists():
    assert Path("configs/base.yaml").is_file()
    assert Path("configs/search_space.yaml").is_file()


def test_base_config_has_required_top_level_keys():
    text = Path("configs/base.yaml").read_text(encoding="utf-8")
    required_keys = ["run", "stage", "data", "model", "loss", "trainer", "eval", "logging"]

    for key in required_keys:
        assert f"{key}:\n" in text


def test_search_space_is_conservative_placeholder():
    text = Path("configs/search_space.yaml").read_text(encoding="utf-8")
    assert "learning_rate:" in text
    assert "max_epochs:" in text
    assert "full training" in text


def test_base_config_is_domain_neutral():
    text = Path("configs/base.yaml").read_text(encoding="utf-8")

    assert "generic_ml_harness" in text
    assert "node_120" not in text
    assert "/home/gyoon/datasets" not in text
