from pathlib import Path

from sml.config import load_config


def test_config_loads() -> None:
    cfg = load_config()
    assert cfg.max_items_per_feed > 0


def test_project_has_readme() -> None:
    assert Path("README.md").exists()
