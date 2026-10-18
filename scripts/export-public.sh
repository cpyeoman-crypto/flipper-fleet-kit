#!/usr/bin/env bash
# export-public.sh — produce a sanitized, shareable copy of the kit.
# Runs the quarantine gate first; refuses to export if it fails.
# Output: ../flipper-fleet-kit-public/ (a clean tree you can push to a public
# remote or zip for a Reddit post).
set -euo pipefail

cd "$(dirname "$0")/.." || exit 2
SRC="$(pwd)"
DEST="${1:-../flipper-fleet-kit-public}"

echo "== running quarantine gate =="
scripts/quarantine_check.sh

echo "== exporting public tree to ${DEST} =="
rm -rf "$DEST"
mkdir -p "$DEST"

# Copy only git-tracked files (so local/ + captures/ are excluded by construction),
# falling back to an explicit excludelist if not a git repo yet.
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  git ls-files -z | while IFS= read -r -d '' f; do
    mkdir -p "$DEST/$(dirname "$f")"
    cp "$f" "$DEST/$f"
  done
else
  rsync -a --exclude '.git' --exclude 'local' --exclude 'captures' \
        --exclude '*.sub' --exclude '*.nfc' --exclude '*.rfid' \
        --exclude '*.pcap' --exclude '*.pcapng' "$SRC/" "$DEST/"
fi

echo "== done =="
echo "Sanitized tree at: $DEST"
echo "Review it once more, then publish. See PUBLIC_RELEASE.md."
