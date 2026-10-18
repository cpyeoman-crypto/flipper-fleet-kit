# Quarantine policy — flipper-fleet-kit

Same discipline as fleet-core's `catalog/QUARANTINE.md`: **secrets and raw captures
never enter version control.**

## What is quarantined (git-ignored, never committed)

| Class | Where it lives | Why |
| --- | --- | --- |
| Real node targets (IPs/MACs/fob UIDs) | `local/*` (except `EXAMPLE.targets.json`) | Fleet topology / access data |
| Raw RF/NFC/RFID/IR captures | `captures/*`, `*.sub` `*.nfc` `*.rfid` `*.ir` | May contain rolling codes, UIDs, payloads |
| Packet captures | `*.pcap` `*.pcapng` | Network contents |
| Env / keys | `*.env` `*.pem` `*.key` `*_secret*` | Credentials |

## The gate

Before **any** public push (GitHub, Reddit link, pastebin, screenshot of the tree),
run:

```bash
scripts/quarantine_check.sh
```

It fails (non-zero) if a tracked file looks like it contains a secret, a fleet IP/MAC,
or a raw capture. A clean exit is your green light. If it flags something, move the
secret into `local/` or `/etc/yourfleet/fleet.env` (root-owned) and re-run — mirroring the
fleet-core scrub-then-reimport workflow.

## Quarantined entries log

| Date | File | Why | Resolution |
| --- | --- | --- | --- |
| _(none yet)_ | | | |
