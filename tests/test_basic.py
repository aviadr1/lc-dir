import os
from lc_dir.cli import find_git_root, find_folder, write_temp_rule


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
    assert '"**/*.py"' in content
    # test with specific subfolder
    rel_folder = "src"
    rule_name2 = write_temp_rule(str(root), rel_folder)
    rule_path2 = root / ".llm-context" / "rules" / f"{rule_name2}.md"
    assert rule_path2.exists()
    content2 = rule_path2.read_text()
    assert f'"{rel_folder}/**/*.py"' in content2
