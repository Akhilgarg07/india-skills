"""Repo-level checks: every skill passes tools/check_skills.py, manifests are valid JSON."""

import importlib.util
import json

from conftest import REPO_ROOT

_spec = importlib.util.spec_from_file_location("check_skills", REPO_ROOT / "tools" / "check_skills.py")
check_skills = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check_skills)


def test_all_skills_pass_lint():
    errors = []
    for d in check_skills.skill_dirs():
        errors.extend(check_skills.check_skill(d))
    assert errors == []


def test_frontmatter_parser():
    fm, body = check_skills.parse_frontmatter(
        "---\nname: x\ndescription: d: with colon\nmetadata:\n  version: \"1\"\n---\nbody\n")
    assert fm == {"name": "x", "description": "d: with colon", "metadata": {"version": "1"}}
    assert body == "body\n"


def test_plugin_manifests():
    plugin = json.loads((REPO_ROOT / ".claude-plugin" / "plugin.json").read_text())
    market = json.loads((REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text())
    assert plugin["name"] == "india-skills"
    assert market["plugins"][0]["name"] == plugin["name"]
    assert market["plugins"][0]["source"] == "./"
    assert market["owner"]["name"]
