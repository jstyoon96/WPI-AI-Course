import importlib


def test_course_package_imports():
    module = importlib.import_module("wpi_ai_bootcamp")
    assert hasattr(module, "check_repository")


def test_data_loader_package_imports():
    module = importlib.import_module("wpi_ai_bootcamp.data")
    assert hasattr(module, "load_ecg_signal")
    assert hasattr(module, "load_imaging_sample")


def test_style_package_imports():
    module = importlib.import_module("wpi_ai_bootcamp.style")
    assert module.WPI_COLORS["crimson"] == "#AC2B37"
    assert hasattr(module, "apply_wpi_plot_style")
