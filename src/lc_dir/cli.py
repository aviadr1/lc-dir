#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import shutil
import textwrap
from argparse import RawDescriptionHelpFormatter

REQUIRED_CMDS = ["lc-set-rule", "lc-sel-files", "lc-context"]
LLM_CONTEXT_URL = "https://github.com/cyberchitta/llm-context.py"

def ensure_llm_context_installed():
    """
    Verify that the llm-context CLI is available on PATH.
    """
    missing = [cmd for cmd in REQUIRED_CMDS if shutil.which(cmd) is None]
    if missing:
        # report each missing tool individually so tests can detect it
        for cmd in missing:
            print(f"Error: '{cmd}' not found")
        print("Please install llm-context CLI first:")
        print("  pipx install llm-context")
        print(f"See {LLM_CONTEXT_URL} for more.")
        sys.exit(1)

def find_git_root(path):
    orig = os.path.abspath(path)
    while True:
        if os.path.isfile(os.path.join(path, ".gitignore")):
            return os.path.abspath(path)
        parent = os.path.dirname(path)
        if parent == path:
            print("Error: Could not find .gitignore in any parent directory of", orig)
            sys.exit(1)
        path = parent

def find_folder(root, query):
    # If the query is an existing path, use it
    candidate = os.path.abspath(os.path.join(root, query))
    if os.path.isdir(candidate):
        return os.path.relpath(candidate, root)

    # Otherwise, search for a folder of that name anywhere under root
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
            print(f"{idx}: {match}")
        idx = input("Enter index of folder to use: ")
        try:
            return matches[int(idx)]
        except Exception:
            print("Invalid selection.")
            sys.exit(1)
    return matches[0]

def write_temp_rule(root, rel_folder, rule_name="temp-folder-rule"):
    rules_dir = os.path.join(root, ".llm-context", "rules")
    os.makedirs(rules_dir, exist_ok=True)
    rule_path = os.path.join(rules_dir, f"{rule_name}.md")
    rel = rel_folder.replace("\\", "/").strip("./")
    pattern = f'{rel}/**/*' if rel else '**/*'
    rule_content = f"""---
description: "Temp rule for {rel or '.'}"
only-include:
  full_files:
    - "{pattern}"
---
"""
    with open(rule_path, "w", encoding="utf-8") as f:
        f.write(rule_content)
    return rule_name

def run_llm_context_commands(root, rule_name):
    for cmd in [["lc-set-rule", rule_name], ["lc-sel-files"], ["lc-context"]]:
        print(">>", " ".join(cmd))
        subprocess.run(cmd, cwd=root, check=True)

def main():
    ensure_llm_context_installed()

    parser = argparse.ArgumentParser(
        description="Copy all non-git-ignored files from a directory (or named folder anywhere) into your llm-context buffer.",
        epilog=textwrap.dedent("""\
            Examples:
              # copy everything under the current folder:
              $ lc-dir

              # copy a specific subfolder:
              $ lc-dir path/to/service

              # search for a folder named "common" anywhere in your repo:
              $ lc-dir common

              # from deep inside a tree, copy "api" wherever it lives:
              $ cd src/app/modules/foo
              $ lc-dir api
        """),
        formatter_class=RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="(optional) folder to export context from, or name of a folder anywhere in the repo",
    )
    args = parser.parse_args()

    cwd = os.getcwd()
    root = find_git_root(cwd)

    if args.target is None:
        rel_folder = os.path.relpath(cwd, root)
        if rel_folder == ".":
            rel_folder = ""
    else:
        rel_folder = find_folder(root, args.target)

    rule_name = write_temp_rule(root, rel_folder)
    run_llm_context_commands(root, rule_name)

if __name__ == "__main__":
    main()
