#!/usr/bin/env python3
"""Thin Flipper Zero CLI client over USB CDC serial.

The Flipper exposes a line-oriented CLI on a USB CDC ACM port (typically
/dev/ttyACM0 on Linux, 115200 baud). This wraps the handful of commands we need
for fleet diagnostics: device_info, storage list/stat/read.

Authorized use only: for a Flipper you own, talking to devices/links you own.

Usage:
    python3 flipper_cli.py --info
    python3 flipper_cli.py --list /ext/subghz
    python3 flipper_cli.py --read /ext/subghz/foo.sub
"""
from __future__ import annotations

import argparse
import sys
import time

DEFAULT_PORT = "/dev/ttyACM0"
BAUD = 115200
PROMPT = b">: "


def _require_serial():
    try:
        import serial  # type: ignore
    except ImportError:
        sys.exit(
            "pyserial is required: pip install pyserial\n"
            "(or: python3 -m pip install --user pyserial)"
        )
    return serial


class FlipperCLI:
    def __init__(self, port: str = DEFAULT_PORT, baud: int = BAUD, timeout: float = 2.0):
        serial = _require_serial()
        self.ser = serial.Serial(port, baud, timeout=timeout)
        self.port = port
        # Drain the banner the Flipper prints on connect.
        time.sleep(0.2)
        self.ser.reset_input_buffer()

    def command(self, cmd: str) -> str:
        """Send one CLI command, return everything up to the next prompt."""
        self.ser.write((cmd + "\r\n").encode())
        self.ser.flush()
        out = bytearray()
        deadline = time.time() + 5.0
        while time.time() < deadline:
            chunk = self.ser.read(256)
            if chunk:
                out += chunk
                if out.rstrip().endswith(PROMPT.strip()):
                    break
            else:
                if out:
                    break
        text = out.decode(errors="replace")
        # Strip the echoed command line and the trailing prompt.
        lines = [ln for ln in text.splitlines() if ln.strip() not in (cmd, ">:")]
        return "\n".join(lines).strip()

    def device_info(self) -> str:
        return self.command("device_info")

    def storage_list(self, path: str) -> str:
        return self.command(f"storage list {path}")

    def storage_stat(self, path: str) -> str:
        return self.command(f"storage stat {path}")

    def storage_read(self, path: str) -> str:
        return self.command(f"storage read {path}")

    def close(self) -> None:
        self.ser.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="Flipper Zero CLI client")
    ap.add_argument("--port", default=DEFAULT_PORT, help=f"serial port (default {DEFAULT_PORT})")
    ap.add_argument("--info", action="store_true", help="print device_info")
    ap.add_argument("--list", metavar="PATH", help="storage list PATH")
    ap.add_argument("--stat", metavar="PATH", help="storage stat PATH")
    ap.add_argument("--read", metavar="PATH", help="storage read PATH")
    args = ap.parse_args()

    if not any([args.info, args.list, args.stat, args.read]):
        ap.print_help()
        return 2

    f = FlipperCLI(args.port)
    try:
        if args.info:
            print(f.device_info())
        if args.list:
            print(f.storage_list(args.list))
        if args.stat:
            print(f.storage_stat(args.stat))
        if args.read:
            print(f.storage_read(args.read))
    finally:
        f.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
