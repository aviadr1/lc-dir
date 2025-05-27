import os
import pytest
from lc_dir.cli import ensure_temp_rule_in_gitignore, write_temp_rule


def test_ensure_temp_rule_in_gitignore_new_file(tmp_path):
    """Test adding temp-folder-rule.md to a new .gitignore file"""
    root = tmp_path / "repo"
    root.mkdir()
    (root / ".gitignore").write_text("")  # Create main gitignore

    # Call the function
    ensure_temp_rule_in_gitignore(str(root))

    # Check that .llm-context/.gitignore was created with the rule
    gitignore_path = root / ".llm-context" / ".gitignore"
    assert gitignore_path.exists()
    content = gitignore_path.read_text()
    assert "temp-folder-rule.md" in content


def test_ensure_temp_rule_in_gitignore_existing_file(tmp_path):
    """Test adding temp-folder-rule.md to existing .gitignore that doesn't have it"""
    root = tmp_path / "repo"
    root.mkdir()
    (root / ".gitignore").write_text("")  # Create main gitignore

    # Create existing .llm-context/.gitignore with other content
    llm_context_dir = root / ".llm-context"
    llm_context_dir.mkdir()
    gitignore_path = llm_context_dir / ".gitignore"
    gitignore_path.write_text("some-other-file.md\n")

    # Call the function
    ensure_temp_rule_in_gitignore(str(root))

    # Check that temp-folder-rule.md was added while preserving existing content
    content = gitignore_path.read_text()
    lines = content.strip().split('\n')
    assert "some-other-file.md" in lines
    assert "temp-folder-rule.md" in lines


def test_ensure_temp_rule_in_gitignore_already_exists(tmp_path):
    """Test that temp-folder-rule.md is not duplicated if already in .gitignore"""
    root = tmp_path / "repo"
    root.mkdir()
    (root / ".gitignore").write_text("")  # Create main gitignore

    # Create existing .llm-context/.gitignore with the rule already there
    llm_context_dir = root / ".llm-context"
    llm_context_dir.mkdir()
    gitignore_path = llm_context_dir / ".gitignore"
    original_content = "temp-folder-rule.md\nother-file.md\n"
    gitignore_path.write_text(original_content)

    # Call the function
    ensure_temp_rule_in_gitignore(str(root))

    # Check that content didn't change (no duplication)
    content = gitignore_path.read_text()
    assert content == original_content
    # Count occurrences to ensure no duplication
    assert content.count("temp-folder-rule.md") == 1


def test_write_temp_rule_calls_gitignore_function(tmp_path):
    """Test that write_temp_rule calls the gitignore function"""
    root = tmp_path / "proj"
    root.mkdir()
    (root / ".gitignore").write_text("")

    # Call write_temp_rule
    rule_name = write_temp_rule(str(root), "src")

    # Verify the rule file was created
    rule_path = root / ".llm-context" / "rules" / f"{rule_name}.md"
    assert rule_path.exists()

    # Verify the .gitignore was updated
    gitignore_path = root / ".llm-context" / ".gitignore"
    assert gitignore_path.exists()
    content = gitignore_path.read_text()
    assert "temp-folder-rule.md" in content


def test_custom_rule_name_in_gitignore(tmp_path):
    """Test that custom rule names are properly added to .gitignore"""
    root = tmp_path / "repo"
    root.mkdir()
    (root / ".gitignore").write_text("")

    custom_rule_name = "my-custom-rule"

    # Call with custom rule name
    ensure_temp_rule_in_gitignore(str(root), custom_rule_name)

    # Check that the custom rule name was added
    gitignore_path = root / ".llm-context" / ".gitignore"
    content = gitignore_path.read_text()
    assert f"{custom_rule_name}.md" in content
    assert "temp-folder-rule.md" not in content  # Should not have default name