#!/usr/bin/env bash
set -euo pipefail

# release.sh — bump, tag, push, publish with Poetry

# 1) Determine bump type (patch|minor|major), default to patch
BUMP_TYPE=${1:-patch}

# 2) Bump version in pyproject.toml via Poetry and capture the new version
#    Poetry will update the file for us
NEW_VERSION=$(poetry version "$BUMP_TYPE" | awk '{print $NF}')
echo "Bumped to version $NEW_VERSION"

# 3) Commit the change and tag
git add pyproject.toml
git commit -m "Bump version to v$NEW_VERSION"
git tag "v$NEW_VERSION"

# 4) Push commits & tags
git push origin HEAD
git push origin "v$NEW_VERSION"

# 5) Publish to PyPI
poetry publish --build --no-interaction

echo "Released v$NEW_VERSION 🎉"
