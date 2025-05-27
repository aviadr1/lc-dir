# tests/test_multi_targets.py

import sys
import shutil
import subprocess
import re
from pathlib import Path

import pytest

from lc_dir.cli import main, write_temp_rule

class DummyWhich:
    def __init__(self, avail):
        self.avail = set(avail)
    def __call__(self, cmd):
        return cmd if cmd in self.avail else None

def strip_ansi(s):
    return re.sub(r'\x1b\[[0-9;]*m', '', s)

def test_multiple_targets(tmp_path, monkeypatch, capsys):
    # fake repo
    root = tmp_path / "repo"
    root.mkdir()
    (root / ".gitignore").write_text("")

    # three folders
    (root / "common").mkdir()
    (root / "kafka").mkdir()
    (root / "models").mkdir()

    monkeypatch.chdir(root)
    monkeypatch.setattr(shutil, "which", DummyWhich(["lc-set-rule", "lc-sel-files", "lc-context"]))

    calls = []
    monkeypatch.setattr(subprocess, "run", lambda cmd, cwd, check: calls.append(cmd))

    monkeypatch.setattr(sys, "argv", ["lc-dir", "common", "kafka", "models"])
    main()

    out = strip_ansi(capsys.readouterr().out)
    assert "Found: 'common' → common" in out
    assert "Found: 'kafka' → kafka" in out
    assert "Found: 'models' → models" in out

    # rule file should contain all three patterns
    rule = root / ".llm-context" / "rules" / "temp-lc-dir-rule.md"
    txt = rule.read_text()
    assert '- "common/**/*"' in txt
    assert '- "kafka/**/*"' in txt
    assert '- "models/**/*"' in txt

    # single invocation of each llm-context command
    assert calls == [
        ["lc-set-rule", "temp-lc-dir-rule"],
        ["lc-sel-files"],
        ["lc-context"],
    ]
