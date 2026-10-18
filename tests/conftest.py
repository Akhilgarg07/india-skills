"""Shared helpers for loading skill scripts by path.

Skill scripts are not a package, and some skills carry a copy of another skill's
script, so tests load each file under a unique module name instead of relying on
sys.path order.
"""

import importlib.util
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"


def load_script(skill: str, script: str):
    """Import skills/<skill>/scripts/<script>.py and return the module."""
    path = SKILLS_DIR / skill / "scripts" / f"{script}.py"
    name = f"{skill.replace('-', '_')}__{script}"
    if name in sys.modules:
        return sys.modules[name]
    scripts_dir = str(path.parent)
    # Scripts import siblings (e.g. aadhaar_validate -> verhoeff) via their own directory.
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def script_path(skill: str, script: str) -> pathlib.Path:
    return SKILLS_DIR / skill / "scripts" / f"{script}.py"
