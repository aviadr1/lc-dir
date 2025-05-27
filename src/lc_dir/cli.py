#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import shutil

TOOL_URL = 'https://github.com/cyberchitta/llm-context.py'


def ensure_llm_context_installed():
    """
    Verify that the llm-context CLI is available on PATH.
    """
    cmds = ['lc-set-rule', 'lc-sel-files', 'lc-context']
    for cmd in cmds:
        if shutil.which(cmd) is None:
            print(f"Error: '{cmd}' not found. Make sure you have installed the llm-context CLI.")
            print(f"See {TOOL_URL} for installation instructions.")
            sys.exit(1)


def find_git_root(path):
    """
    Walk upwards from 'path' until a directory containing .gitignore is found.
    """
    orig = os.path.abspath(path)
    while True:
        if os.path.isfile(os.path.join(path, ".gitignore")):
            return os.path.abspath(path)
        parent = os.path.dirname(path)
        if parent == path:
            print(f"Error: Could not find .gitignore in any parent directory of {orig}")
            sys.exit(1)
        path = parent


def find_folder(root, query):
    """
    Locate a folder given by 'query' under 'root'.
    If 'query' is an existing path, returns its relative path.
    Otherwise, searches for directories matching the name (case-insensitive).
    """
    candidate = os.path.abspath(os.path.join(root, query))
    if os.path.isdir(candidate):
        return os.path.relpath(candidate, root)

    matches = []
    for dirpath, dirnames, _ in os.walk(root):
        for d in dirnames:
            if d.lower() == query.lower():
                matches.append(os.path.relpath(os.path.join(dirpath, d), root))
    if not matches:
        print(f"Error: Folder '{query}' not found in project.")
        sys.exit(1)
    if len(matches) > 1:
        print(f"Multiple matches found for '{query}':")
        for idx, match in enumerate(matches):
            print(f"  {idx}: {match}")
        try:
            idx = int(input("Enter index of folder to use: "))
            return matches[idx]
        except Exception:
            print("Invalid selection.")
            sys.exit(1)
    return matches[0]


def write_temp_rule(root, rel_folder, rule_name="temp-folder-rule"):
    """
    Create a temporary llm-context rule to include all files under rel_folder.
    """
    rules_dir = os.path.join(root, ".llm-context", "rules")
    os.makedirs(rules_dir, exist_ok=True)
    rule_path = os.path.join(rules_dir, f"{rule_name}.md")
    rel = rel_folder.replace("\\", "/").strip("./")
    pattern = f'{rel}/**/*' if rel else '**/*'
    rule_content = f"""
---
# Temporary rule to include all files under '{rel or '.'}'
only-include:
  full_files:
    - "{pattern}"
---
"""
    with open(rule_path, "w", encoding="utf-8") as f:
        f.write(rule_content)
    return rule_name


def run_llm_context_commands(root, rule_name):
    """
    Execute the llm-context commands to set the rule, select files, and copy to clipboard.
    """
    cmds = [
        ["lc-set-rule", rule_name],
        ["lc-sel-files"],
        ["lc-context"]
    ]
    for cmd in cmds:
        print(">>", " ".join(cmd))
        subprocess.run(cmd, cwd=root, check=True)


def main():
    ensure_llm_context_installed()

    parser = argparse.ArgumentParser(
        prog='lc-dir',
        description='Copy all non-git-ignored files under a directory to your clipboard via llm-context.',
        epilog=(
            'Examples:\n'
            '  lc-dir               # copy from current folder\n'
            '  lc-dir src/my_module # copy from specific folder'
        )
    )
    parser.add_argument(
        'target', nargs='?', default=None,
        help='Optional: folder name or path to include in context (searches case-insensitive).'
    )
    args = parser.parse_args()

    cwd = os.getcwd()
    root = find_git_root(cwd)

    if args.target is None:
        rel_folder = os.path.relpath(cwd, root)
        rel_folder = '' if rel_folder == '.' else rel_folder
    else:
        rel_folder = find_folder(root, args.target)

    rule = write_temp_rule(root, rel_folder)
    run_llm_context_commands(root, rule)


if __name__ == '__main__':
    main()
