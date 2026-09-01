#!/usr/bin/env bash
# Build, publish to PyPI, and tag a release branch.
#
# Usage: scripts/publish.sh "short commit summary"
#   e.g. scripts/publish.sh "server and router"

set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

SUMMARY="${1:-}"
if [ -z "$SUMMARY" ]; then
  read -r -p "Commit summary (e.g. 'server and router'): " SUMMARY
fi
if [ -z "$SUMMARY" ]; then
  echo "A commit summary is required." >&2
  exit 1
fi

VERSION="$(python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")"
BRANCH="v${VERSION}"
CURRENT_BRANCH="$(git branch --show-current)"

echo "==> Cleaning dist/"
rm -rf dist

echo "==> Building package"
python3 -m build

echo
read -r -p "Publish version ${VERSION} to PyPI? [y/N] " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 1
fi

echo "==> Uploading to PyPI"
python3 -m twine upload dist/*

echo "==> Committing"
git add -A
git commit -m "release(v${VERSION}): ${SUMMARY}"

echo "==> Pushing ${CURRENT_BRANCH}"
git push

if [ "$CURRENT_BRANCH" = "$BRANCH" ]; then
  echo "==> Already on ${BRANCH}, skipping branch creation"
else
  echo "==> Creating and publishing branch ${BRANCH}"
  git checkout -b "$BRANCH"
  git push -u origin "$BRANCH"
fi

echo "==> Done: v${VERSION} published"
