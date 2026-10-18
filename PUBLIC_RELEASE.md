# Publishing this kit (GitHub / Reddit) — quarantine in effect

This repo is built to be shareable, but **nothing leaves until the quarantine gate
passes.** Follow this every time.

## 1. Run the gate
```bash
scripts/quarantine_check.sh      # must exit clean (0)
```
It blocks on real fleet IPs (your LAN subnet), tailscale IPs, MACs, raw captures, and
secret-shaped strings. If it flags anything, move that data into `local/` (git-ignored)
and re-run.

## 2. Produce a sanitized tree
```bash
scripts/export-public.sh         # -> ../flipper-fleet-kit-public/
```
This copies only git-tracked files, so `local/` and `captures/` can't ride along.

## 3. Publish

**GitHub (public repo):**
```bash
cd ../flipper-fleet-kit-public
git init && git add -A && git commit -m "flipper-fleet-kit: public release"
# create an EMPTY public repo on GitHub first, then:
git remote add origin git@github.com:<you>/flipper-fleet-kit.git
git push -u origin main
```

**Reddit:** link the GitHub repo (e.g. r/flipperzero, r/homelab, r/selfhosted). Do
**not** paste `local/targets.json`, captures, or screenshots that show your LAN /
tailscale IPs / MACs. Good subs to consider: r/flipperzero (loadout + collectors),
r/homelab or r/selfhosted (fleet-integration angle).

## Pre-publish checklist
- [ ] `quarantine_check.sh` exits clean
- [ ] `local/` contains only `EXAMPLE.targets.json` in git
- [ ] `captures/` is empty in git (only `.gitkeep`)
- [ ] README's "authorized use" scope note is intact
- [ ] No node hostnames beyond the generic examples in docs

## What stays private forever
`local/targets.json`, everything under `captures/`, the real `config/nodes.json` from
fleet-core, and anything in `catalog/QUARANTINE.md`'s quarantine log.
