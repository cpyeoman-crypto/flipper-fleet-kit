# collectors/

Host-side tools that talk to the Flipper over USB serial. **Authorized use only:**
your own Flipper, your own devices and radio links.

## Requirements
```bash
# Debian/Ubuntu/Pop!_OS block system-wide pip (PEP 668) — use the kit's venv:
python3 -m venv .venv            # from the repo root, once
.venv/bin/pip install pyserial
.venv/bin/python collectors/flipper_cli.py --info
```
Add yourself to the `dialout` group (or use sudo) so you can open `/dev/ttyACM0`:
```bash
sudo usermod -aG dialout "$USER"   # log out/in afterwards
```

## flipper_cli.py
Thin CLI client. The Flipper presents a serial console on `/dev/ttyACM0` @ 115200.
```bash
python3 flipper_cli.py --info
python3 flipper_cli.py --list /ext/subghz
python3 flipper_cli.py --read /ext/subghz/foo.sub
```

## pull_captures.py
Pulls a directory of captures into the git-ignored `captures/` tree and records a
provenance row per file (same shape as fleet-core's `catalog/provenance.json`).
```bash
python3 pull_captures.py --src /ext/subghz --kind subghz
python3 pull_captures.py --src /ext/nfc    --kind nfc --dry-run
```

## Serial-console rescue (no script needed)

When a node's SSH is down, use the Flipper as a USB-serial adapter instead of carrying
an FTDI cable:

1. On the Flipper: **GPIO → USB-UART Bridge**, set baud 115200.
2. Wire: Flipper **pin 13 (TX) → node RX**, **pin 14 (RX) → node TX**, **GND → GND**.
3. On the host: `screen /dev/ttyACM0 115200`  (or `minicom -D /dev/ttyACM0 -b 115200`).

This is the "troubleshoot / interact with the fleet" path — a console into a wedged
node when the network layer is gone.
