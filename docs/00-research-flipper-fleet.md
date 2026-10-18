# 00 — Flipper Zero → fleet integration research

_Research notes written for fARM.nET. Goal: use a Flipper Zero as a portable
diagnostic / telemetry probe for our own nodes and our own RF-linked IoT, and feed
what it collects into the fleet-core metrics catalog._

## 1. What the Flipper actually is (and isn't) for us

The Flipper Zero is a battery-powered multitool built on an STM32WB55 (dual-core
Cortex-M4 + M0 for the radio). For a homelab fleet it is useful as a **physical-layer
probe** — the one tool that reaches the sub-IP layers our existing host scripts can't:

- **Sub-GHz radio (CC1101, ~300–348 / 387–464 / 779–928 MHz).** Receive/transmit OOK
  & 2-FSK. This is where most cheap 433 MHz / 915 MHz home sensors live.
- **125 kHz RFID** (T5577/EM4100-class) and **13.56 MHz NFC** (ST25R3916).
- **Infrared** TX/RX with a learning receiver.
- **1-Wire / iButton.**
- **GPIO header** (18 pins): 3V3, 5V (when USB powered), GND, plus UART (TX pin 13 /
  RX pin 14), SPI, I²C, and ADC. **This is the most valuable pin for fleet work.**
- **USB-C** presenting a CDC ACM serial device (the Flipper **CLI**) and, with
  firmware, USB-HID (BadUSB — out of scope for this kit).

What it is **not**, for our purposes: a Wi-Fi radio. 802.11 capture needs the external
ESP32 "Wi-Fi Dev Board" running Marauder firmware; see §4 — we keep that optional and
read-only.

## 2. The three fleet use-cases we actually want

### A. Serial console rescue (GPIO/UART) — _highest value_
When a node wedges and SSH is dead, a laptop isn't always next to it. The Flipper's
`UART bridge` app turns the GPIO UART into a USB-serial adapter: wire pin 13 (TX) →
node RX, pin 14 (RX) → node TX, GND→GND, and you get a console at 115200 8N1 without
carrying a dedicated FTDI cable. `collectors/serial notes` live in
`collectors/README.md`. This is the classic "troubleshoot or interact with the fleet"
path from the request.

### B. Sub-GHz telemetry capture — _"collect signals/packets"_
Our 433/915 MHz sensors beacon periodically. Using **Read RAW** (or the decoded
**Read** for known protocols like Princeton, Nice FloR-S, etc. — for sensors we own)
the Flipper logs `.sub` files to `/ext/subghz`. The host then pulls them (see §3) and
we turn the decoded values into metrics rows in the fleet catalog. We capture **our
own** sensors only — the protocol/ID allow-list in `local/targets.json` enforces that.

### C. Access-tag inventory (NFC/RFID/iButton)
Read our own door fobs / 1-Wire keys to keep an inventory and to test the door node.
Store only a salted hash of each UID in the catalog, never the raw dump (raw dumps are
quarantined like secrets).

## 3. Host ↔ Flipper transport

The Flipper exposes a line-oriented CLI over USB CDC serial (typically
`/dev/ttyACM0` on Linux, 115200 baud). Useful commands:

```
storage list /ext/subghz      # enumerate captures
storage read  /ext/subghz/x.sub
storage stat  /ext/subghz/x.sub
device_info                   # firmware / hardware / name
```

`collectors/flipper_cli.py` wraps this with pyserial. `collectors/pull_captures.py`
walks a source dir on the Flipper, copies each file into the git-ignored `captures/`
tree, and writes a `provenance.json` line (source path, size, sha256, pulled-at,
flipper name) — mirroring fleet-core's `catalog/provenance.json` convention.

## 4. Optional: Wi-Fi Dev Board (ESP32 / Marauder) — read-only posture

If we attach the dev board, we use it **only** for passive sniffing / channel survey
of **our own** SSIDs to cross-check Omada's view — captures land as `.pcap` and are
quarantined. We do **not** ship or script deauth/beacon-spam/evil-portal flows; those
target other people's clients and have no place in a fleet-diagnostics kit.

## 5. Metrics shape (what feeds fleet-core)

Each pulled capture becomes one JSON row:

```json
{
  "ts": "2026-10-17T21:50:00Z",
  "probe": "flipper:<device-name>",
  "channel": "subghz-433.92",
  "source_node": "garage-sensor-01",
  "metric": "door_state",
  "value": "open",
  "raw_ref": "captures/subghz/2026-10-17/garage-....sub"
}
```

The `raw_ref` points into the git-ignored `captures/` tree, so metrics can be shared
while the raw RF never is.

## 6. Open items for the operator (only you can decide)

- **SD mount path** on your Flipper build (stock = `/ext`; some custom firmwares
  differ). Default assumed `/ext`.
- **Custom firmware?** Stock OFW vs. Unleashed/RogueMaster/Momentum changes which
  Sub-GHz regions/protocols are enabled. The loadout manifest flags firmware as a
  variable, it does not pick one for you.
- Which sensors/fobs are **yours** — populate `local/targets.json` from the example.
