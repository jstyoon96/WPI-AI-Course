from pathlib import Path


def test_bspm_candidate_config_uses_pca_qr_method_name():
    text = Path("examples/bspm/configs/bspm_baseline.yaml").read_text(encoding="utf-8")

    assert "pca_qr" in text
    assert "pca_svd" not in text
    assert "examples/bspm/experiments/candidate_selection_v1" in text
