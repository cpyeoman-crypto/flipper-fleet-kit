# 01 — Flipper loadout ("the zipper")

A **loadout** is the curated set of files we keep on the Flipper's SD card so it is
ready for fleet work the moment we pick it up. The declarative version lives in
`loadout/loadout.manifest.json`; this doc is the human read.

## Firmware (operator chooses — manifest leaves it variable)

| Option | Notes |
| --- | --- |
| Stock OFW | Safest, fewest Sub-GHz regions. Fine for UART + NFC + IR. |
| Unleashed / RogueMaster / Momentum | More Sub-GHz protocols/regions unlocked. Use only with region rules you're allowed to operate under. |

The kit does not flash firmware; it only records which one is loaded so captures are
interpreted correctly.

## SD-card tree we care about

```
/ext/
├── subghz/            # .sub captures (telemetry from our own sensors)
├── nfc/               # our own tag reads (raw = quarantined)
├── lfrfid/            # our own 125 kHz fobs
├── infrared/          # saved remotes for lab AV / power
├── ibutton/           # our own 1-Wire keys
└── apps/              # extra .fap apps
```

## Apps to keep loaded (all first-party / standard)

- **UART bridge** (built-in) — serial-console rescue. _Core of the loadout._
- **GPIO** / **USB-UART** — pin control + bridge.
- **Sub-GHz → Read / Read RAW** (built-in) — sensor telemetry capture.
- **NFC / RFID / iButton** (built-in) — access inventory.
- **Infrared** (built-in) — lab AV/power runbook steps.

## Physical kit (the "pro loadout" for carrying to a node)

- Flipper Zero + charged battery.
- Short DuPont jumper set (for GPIO UART: TX/RX/GND, plus optional 3V3).
- A labeled GND + TX + RX pigtail so console hookups are repeatable.
- USB-C cable (host pull + charging).
- _Optional:_ ESP32 Wi-Fi Dev Board (read-only survey only, see research §4).

## Pinout cheat-sheet (GPIO UART)

| Flipper pin | Signal | Wire to node |
| --- | --- | --- |
| 13 | USART TX | node RX |
| 14 | USART RX | node TX |
| 11 / 8 / 18 | GND | node GND |
| 9 | 3V3 (out) | only if powering a 3V3 adapter |

Default console: **115200 8N1**, no flow control.
