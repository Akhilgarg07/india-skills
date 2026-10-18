"""The _template example script must stay runnable (contributors copy it)."""

import importlib.util
import subprocess
import sys

from conftest import REPO_ROOT

PATH = REPO_ROOT / "_template" / "scripts" / "example_tool.py"
_spec = importlib.util.spec_from_file_location("template_example_tool", PATH)
tool = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tool)


def test_template_validate():
    assert tool.validate(" abc123 ")["valid"]
    assert not tool.validate("ab12")["valid"]


def test_template_cli_exit_codes():
    run = lambda *a: subprocess.run([sys.executable, str(PATH), *a], capture_output=True, text=True)
    assert run("ABC123").returncode == 0
    assert run("nope").returncode == 1
    assert run().returncode == 2


def test_template_has_required_files():
    for rel in ("SKILL.md", "references/sources.md", "references/details.md", "EVALS.md"):
        assert (REPO_ROOT / "_template" / rel).exists(), rel
