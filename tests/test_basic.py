import os
import sys
import shutil
import pytest
from lc_dir.cli import find_git_root, find_folder, write_temp_rule
from lc_dir.cli import ensure_llm_context_installed, TOOL_URL

def test_find_git_root(tmp_path, monkeypatch):
    # create nested folder with a fake .gitignore at root
    root = tmp_path / "repo"
    root.mkdir()
    (root / ".gitignore").write_text("")
    sub = root / "sub" / "sub2"
    sub.mkdir(parents=True)
    # simulate running from nested directory by changing cwd after import
    monkeypatch.chdir(sub)
    assert find_git_root(str(sub)) == str(root)


def test_find_folder(tmp_path):
    root = tmp_path / "project"
    (root / "common").mkdir(parents=True)
    assert find_folder(str(root), "common") == "common"


def test_find_folder_existing_path(tmp_path):
    root = tmp_path / "project2"
    sub = root / "sub"
    sub.mkdir(parents=True)
    # provide existing absolute path
    existing = str(sub)
    rel = find_folder(str(root), existing)
    assert rel == os.path.relpath(existing, str(root))


def test_write_temp_rule(tmp_path):
    root = tmp_path / "proj"
    root.mkdir()
    # create .gitignore so write_temp_rule finds root
    (root / ".gitignore").write_text("")
    # test default (root)
    rule_name = write_temp_rule(str(root), "")
    rule_path = root / ".llm-context" / "rules" / f"{rule_name}.md"
    assert rule_path.exists()
    content = rule_path.read_text()
    assert 'only-include' in content
    # now includes all files, not just .py
    assert '"**/*"' in content

    # test with specific subfolder
    rel_folder = "src"
    rule_name2 = write_temp_rule(str(root), rel_folder)
    rule_path2 = root / ".llm-context" / "rules" / f"{rule_name2}.md"
    assert rule_path2.exists()
    content2 = rule_path2.read_text()
    assert f'"{rel_folder}/**/*"' in content2




class DummyWhich:
    def __init__(self, available):
        # available: set of command names that exist
        self.available = set(available)
    def __call__(self, cmd):
        return cmd if cmd in self.available else None


def test_ensure_llm_context_all_present(monkeypatch):
    # Simulate all commands present
    monkeypatch.setattr(shutil, 'which', DummyWhich(['lc-set-rule', 'lc-sel-files', 'lc-context']))
    # Should not raise or exit
    ensure_llm_context_installed()


def test_ensure_llm_context_missing_one(monkeypatch, capsys):
    # Simulate missing "lc-sel-files"
    monkeypatch.setattr(shutil, 'which', DummyWhich(['lc-set-rule', 'lc-context']))
    with pytest.raises(SystemExit) as exc:
        ensure_llm_context_installed()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    # Expect error mention of missing command and TOOL_URL
    assert "'lc-sel-files' not found" in captured.out
    assert TOOL_URL in captured.out


def test_ensure_llm_context_missing_all(monkeypatch, capsys):
    # Simulate none present
    monkeypatch.setattr(shutil, 'which', DummyWhich([]))
    with pytest.raises(SystemExit) as exc:
        ensure_llm_context_installed()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    # First missing command reported is lc-set-rule
    assert "'lc-set-rule' not found" in captured.out
    assert TOOL_URL in captured.out
