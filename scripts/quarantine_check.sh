#!/usr/bin/env bash
# quarantine_check.sh — pre-publish gate for flipper-fleet-kit.
# Fails (exit 1) if the git-tracked tree contains anything that must not be
# published: fleet IPs/MACs, raw captures, or secret-shaped strings.
#
# Run before ANY public push. Clean exit = safe to share.
set -uo pipefail

cd "$(dirname "$0")/.." || exit 2
fail=0

say()  { printf '%s\n' "$*"; }
flag() { printf '  [BLOCK] %s\n' "$*"; fail=1; }

# Only inspect git-tracked files (so git-ignored local/ + captures/ are exempt).
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  mapfile -t FILES < <(git ls-files)
else
  # Not a git repo yet: inspect everything except ignored dirs.
  mapfile -t FILES < <(find . -type f \
    -not -path './.git/*' -not -path './local/*' -not -path './captures/*' \
    -not -name 'EXAMPLE.targets.json')
fi

say "quarantine_check: scanning ${#FILES[@]} tracked file(s)…"

# 1. Private LAN ranges (RFC1918) + tailscale CGNAT range (don't leak topology).
#    Tighten IP_RE to your own subnet in your private copy; EXAMPLE/scrubbed files
#    are allowed to contain placeholders, not real IPs. Patterns in a git-ignored
#    local/quarantine_patterns file (one extended regex per line) are also blocked.
IP_RE='(10\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})|(192\.168\.[0-9]{1,3}\.[0-9]{1,3})|(172\.(1[6-9]|2[0-9]|3[01])\.[0-9]{1,3}\.[0-9]{1,3})|(100\.(6[4-9]|[7-9][0-9]|1[01][0-9]|12[0-7])\.[0-9]{1,3}\.[0-9]{1,3})'
if [ -f local/quarantine_patterns ]; then
  while IFS= read -r extra; do
    [ -n "$extra" ] && IP_RE="$IP_RE|($extra)"
  done < local/quarantine_patterns
fi
MAC_RE='([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}'
SECRET_RE='(BEGIN [A-Z ]*PRIVATE KEY|api[_-]?key|password[[:space:]]*=|secret[[:space:]]*=|AKIA[0-9A-Z]{16})'

for f in "${FILES[@]}"; do
  [ -f "$f" ] || continue
  case "$f" in
    *EXAMPLE.targets.json) continue ;;   # the one allowed scrubbed sample
  esac
  if grep -IEnq "$IP_RE" "$f";     then flag "$f: contains a real fleet IP"; grep -IEn "$IP_RE" "$f" | sed 's/^/        /'; fi
  if grep -IEnq "$MAC_RE" "$f";    then flag "$f: contains a MAC address";    fi
  if grep -IEnq "$SECRET_RE" "$f"; then flag "$f: contains a secret-shaped string"; fi
done

# 2. Raw captures must never be tracked.
for f in "${FILES[@]}"; do
  case "$f" in
    *.sub|*.nfc|*.rfid|*.ir|*.pcap|*.pcapng) flag "$f: raw capture is tracked (must be git-ignored)";;
  esac
done

if [ "$fail" -ne 0 ]; then
  say ""
  say "QUARANTINE FAILED — do NOT publish. Move the flagged data into local/ or a"
  say "root-owned env file, then re-run. See catalog/QUARANTINE.md."
  exit 1
fi
say "quarantine_check: clean — safe to publish."
exit 0
