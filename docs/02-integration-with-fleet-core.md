# 02 — Integrating with a fleet repo

_This is the genericized public version of an internal integration doc. Adapt the
names/paths to your own fleet._

## Where this repo lives (and why NOT inside the synced fleet checkout)

If your fleet controller rsyncs a canonical repo to each client on a timer, anything
you create inside the client's synced checkout is **transient** — the next sync
clobbers it. So keep `flipper-fleet-kit` as a **standalone repo in your home dir**,
and attach it to the fleet repo **on the controller node** (the one that owns the
canonical copy), then let the sync propagate it:

```bash
# on your controller node:
cd /path/to/canonical/fleet-repo
git submodule add <remote-url-or-path> client-core/flipper-fleet-kit
git commit -m "Add flipper-fleet-kit as a fleet diagnostics probe"
```

If you have no live remote yet, seed a local bare mirror next to the canonical repo
and use that path as the submodule URL.

## Metrics handoff

`collectors/pull_captures.py` writes `captures/provenance.json` (one row per pulled
file: source path, size, sha256, pulled-at, probe name). A fleet-side import step can
read the **metrics rows** (not the raw captures) into your fleet catalog/index. Raw
`.sub` / `.nfc` files stay git-ignored and never leave the probe host.

## Governance / guardrails

- **No trust-anchor changes.** This kit touches no controller config, manifest, or SSH
  trust anchor. It is additive and isolated.
- **Quarantine discipline.** Secrets and raw captures are scrubbed/ignored, never
  committed — see `catalog/QUARANTINE.md`.
- **Human in the loop.** This is advisory/diagnostic tooling; a human on the
  controller decides what gets merged into the fleet repo.

## Node targets

`local/targets.json` (git-ignored) lists the sensors/fobs/nodes that are **yours** and
therefore in-scope for capture. Seed it from `local/EXAMPLE.targets.json`. Your fleet's
real node inventory (IPs/MACs) stays in your private fleet repo — this kit references
it, it does not copy it into git.
