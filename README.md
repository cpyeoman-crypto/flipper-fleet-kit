# flipper-fleet-kit

A Flipper Zero ("the zipper") loadout and host-side toolkit for **testing, metrics,
and troubleshooting your own lab fleet** — reading your own Sub-GHz sensors, driving
serial consoles on your own nodes over GPIO/UART, and pulling capture files off the
Flipper into a tidy, provenance-tracked archive.

> **Scope / authorized use.** Everything here is for devices and radio links **you
> own or are explicitly authorized to test**. Sub-GHz capture, RFID/NFC reads, and
> packet capture are legal to do on your own equipment and your own network; doing
> them against other people's devices or networks is not. This kit deliberately ships
> **no** attack tooling (no deauth, no replay-against-third-parties, no credential
> capture) — it is a diagnostics and telemetry kit.

## Why this exists

The fleet already has host-side network tooling (Omada scripts, `wifi_analyzer.py`,
`network_auditor.py`). Those see the *IP* layer. The Flipper sees the layer *below*
that the fleet is otherwise blind to:

| Flipper capability | Fleet use |
| --- | --- |
| Sub-GHz (300–928 MHz) | Log your own 433/915 MHz IoT sensors (temp, door, leak, PIR) as metrics |
| GPIO / UART bridge | USB-serial console into a wedged node or switch when SSH is down |
| Infrared | Power-cycle / drive lab displays & AV during runbooks |
| 125 kHz RFID / 13.56 MHz NFC | Inventory your own access fobs/tags; door-node testing |
| iButton | Read your own 1-Wire keys |
| USB (CDC serial) | Host pulls captures & telemetry off the Flipper CLI |

## Layout

```
flipper-fleet-kit/
├── README.md                 # this file (public-safe)
├── LICENSE                   # MIT
├── PUBLIC_RELEASE.md         # how to publish to GitHub/Reddit safely
├── .gitignore                # keeps captures + real node data OUT of git
├── docs/
│   ├── 00-research-flipper-fleet.md   # capability research + design
│   ├── 01-loadout.md                  # what to put on the SD card
│   └── 02-integration-with-fleet-core.md
├── loadout/
│   └── loadout.manifest.json          # declarative SD-card loadout
├── collectors/               # host-side Python (talks to Flipper over USB serial)
│   ├── flipper_cli.py        # thin Flipper CLI client (pyserial)
│   ├── pull_captures.py      # pull .sub/.nfc/.rfid off the Flipper -> captures/
│   └── README.md
├── catalog/
│   └── QUARANTINE.md         # same secret-scrubbing discipline as fleet-core
├── scripts/
│   ├── quarantine_check.sh   # pre-publish gate: fails if secrets/captures leak
│   └── export-public.sh      # produce a sanitized tree for public sharing
├── local/                    # GIT-IGNORED: your real node targets live here
│   └── EXAMPLE.targets.json  # the one committed, scrubbed example
└── captures/                 # GIT-IGNORED: raw captures never enter git
```

## Quick start

```bash
# 1. list files on the Flipper (connect it over USB first)
python3 collectors/flipper_cli.py --list /ext/subghz

# 2. pull captures into the quarantined captures/ dir with provenance
python3 collectors/pull_captures.py --src /ext/subghz --kind subghz

# 3. before you ever share this repo publicly, run the gate:
scripts/quarantine_check.sh
```

## Quarantine

This repo is built **public-first**: real IPs, MACs, fob IDs, and raw captures never
enter version control. They live in `local/` and `captures/`, both git-ignored. The
`scripts/quarantine_check.sh` gate greps the tracked tree for secret-shaped strings
and refuses to pass if any slipped in — run it before any public push. See
`catalog/QUARANTINE.md`.
