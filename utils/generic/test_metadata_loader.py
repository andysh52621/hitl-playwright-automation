# utils/test_metadata_loader.py
import logging
import os
from pathlib import Path

import allure
import yaml

hitlLogger = logging.getLogger("HitlLogger")


def load_test_meta(test_user, test_file_path: str) -> dict:
    # 🔧 Use absolute path from project root
    test_file_path = os.path.abspath(test_file_path)
    meta_path = Path(test_file_path).with_suffix(".yaml")
    if not meta_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {meta_path}")
    with open(meta_path) as f:
        # hitlLogger.info(f"Metadata file was found: {meta_path}")
        full_meta = yaml.safe_load(f)

    # Extract and clean meta structure
    meta = {k: v for k, v in full_meta.items() if k != "test_data"}
    meta["name"] = meta.get("name", Path(test_file_path).stem)
    meta["test_env"] = test_user.test_env

    # Inject test_data separately if present
    if "test_data" in full_meta:
        meta["test_data"] = full_meta["test_data"]

    return meta


def apply_allure_labels(meta: dict):
    """
    Applies Allure metadata from the loaded YAML.
    """
    allure_meta = meta.get("allure", {})
    if "feature" in allure_meta:
        allure.feature(allure_meta["feature"])
    if "story" in allure_meta:
        allure.story(allure_meta["story"])
    if "title" in allure_meta:
        allure.title(allure_meta["title"])
    if "description" in allure_meta:
        allure.description(allure_meta["description"])
    if "severity" in allure_meta:
        severity = allure_meta["severity"].lower()
        severity_level = getattr(allure.severity_level, severity, allure.severity_level.NORMAL)
        allure.severity(severity_level)
    if "tags" in allure_meta:
        for tag in allure_meta["tags"]:
            allure.label("tag", tag)
    if "owner" in allure_meta:
        allure.label("owner", allure_meta["owner"])


def get_meta_path_from_test_file(filename: str) -> str:
    """
    Resolves the full absolute path to a .yaml metadata file
    based on a given Python test file name.

    Args:
        filename (str): e.g., "test_create_domain_entity.py"

    Returns:
        str: Absolute path to corresponding .yaml file
    """
    project_root = Path(__file__).resolve().parent.parent.parent  # utils/
    tests_dir = project_root / "tests" / "ui_test_suite"
    meta_path = tests_dir / filename.replace(".py", ".yaml")
    if not meta_path.exists():
        raise FileNotFoundError(f"Metadata file not found: {meta_path}")
    return str(meta_path)
