#!/usr/bin/env python3
"""Pull capture files off the Flipper into the quarantined captures/ tree.

Walks a source directory on the Flipper (e.g. /ext/subghz), reads each file via
the CLI, and writes it under captures/<kind>/<date>/ with a provenance row — the
same shape fleet-core uses in catalog/provenance.json.

captures/ is git-ignored: raw RF/NFC/RFID data never enters version control.
Authorized use only: your own Flipper, your own devices/links.

Usage:
    python3 pull_captures.py --src /ext/subghz --kind subghz
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys

from flipper_cli import FlipperCLI, DEFAULT_PORT

KIT_ROOT = pathlib.Path(__file__).resolve().parent.parent
CAPTURES = KIT_ROOT / "captures"
PROVENANCE = CAPTURES / "provenance.json"

# `storage list` prints lines like: "[F] name 1234b" for files, "[D] name" for dirs.
_FILE_RE = re.compile(r"^\[F\]\s+(.+?)(?:\s+(\d+)b)?$")


def _now() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append_provenance(row: dict) -> None:
    rows = []
    if PROVENANCE.exists():
        try:
            rows = json.loads(PROVENANCE.read_text())
        except json.JSONDecodeError:
            rows = []
    rows.append(row)
    PROVENANCE.write_text(json.dumps(rows, indent=2) + "\n")


def parse_file_list(listing: str) -> list[tuple[str, int | None]]:
    out = []
    for line in listing.splitlines():
        m = _FILE_RE.match(line.strip())
        if m:
            out.append((m.group(1), int(m.group(2)) if m.group(2) else None))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Pull Flipper captures into captures/")
    ap.add_argument("--port", default=DEFAULT_PORT)
    ap.add_argument("--src", required=True, help="source dir on the Flipper, e.g. /ext/subghz")
    ap.add_argument("--kind", required=True, help="capture kind: subghz|nfc|lfrfid|ir|ibutton")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    date = dt.date.today().isoformat()
    dest_dir = CAPTURES / args.kind / date
    f = FlipperCLI(args.port)
    pulled = 0
    try:
        name = f.device_info().splitlines()
        probe = next((l.split(":", 1)[1].strip() for l in name if "name" in l.lower()), "flipper")
        listing = f.storage_list(args.src)
        files = parse_file_list(listing)
        if not files:
            print(f"No files found under {args.src}")
            return 0
        if not args.dry_run:
            dest_dir.mkdir(parents=True, exist_ok=True)
        for fname, size in files:
            src_path = f"{args.src}/{fname}"
            print(f"  pull {src_path}  ({size if size is not None else '?'}b)")
            if args.dry_run:
                continue
            data = f.storage_read(src_path)
            dest = dest_dir / fname
            dest.write_text(data)
            sha = hashlib.sha256(data.encode(errors="replace")).hexdigest()
            _append_provenance({
                "pulled_at": _now(),
                "probe": f"flipper:{probe}",
                "kind": args.kind,
                "source": src_path,
                "dest": str(dest.relative_to(KIT_ROOT)),
                "bytes": len(data),
                "sha256": sha,
            })
            pulled += 1
    finally:
        f.close()
    print(f"Done. Pulled {pulled} file(s) into {dest_dir if not args.dry_run else '(dry-run)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
