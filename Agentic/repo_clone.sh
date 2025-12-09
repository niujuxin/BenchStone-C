#!/usr/bin/env bash

set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 github-user/repo-name [destination]" >&2
  exit 1
fi

if ! command -v git >/dev/null 2>&1; then
  echo "Error: git is not installed or not in PATH." >&2
  exit 1
fi

repo="$1"
dest="${2:-${repo##*/}}"

if [[ "$repo" != */* ]]; then
  echo "Error: repository must be in the form user/repo." >&2
  exit 1
fi

if [[ -e "$dest" ]]; then
  echo "Error: destination path '$dest' already exists. Aborting to avoid overwriting." >&2
  exit 1
fi

tmpdir="$(mktemp -d)"
cleanup() {
  rm -rf "$tmpdir"
}
trap cleanup EXIT

git_url="https://github.com/${repo}.git"

echo "Cloning $git_url ..."
git clone --depth=1 "$git_url" "$tmpdir/repo" >/dev/null

rm -rf "$tmpdir/repo/.git"

mkdir -p "$dest"
cp -a "$tmpdir/repo/." "$dest/"

echo "Repository contents copied to '$dest' without .git history."