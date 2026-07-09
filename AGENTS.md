# Agent Guidelines — TheUSDX / Acme Redactors

## After Every Change: Commit, Push, and Deploy

**This is required after any code change, no exceptions.**

```bash
git add <changed files>
git commit -m "..."
git push origin main
./deploy.sh
```

Do not stop after editing files locally. Always push to GitHub and run `./deploy.sh` to sync and restart the server at `root@143.110.131.237` (https://themithrilcompany.com). The service is `usdx.service` managed by systemd.

## Project Overview

Acme Redactors is a FOIA-compliant public records management platform demo. Core files:

- `api_server.py` — Flask server, `/get_data` and `/redact` endpoints
- `handlers.py` — LLM redaction logic (three tiers: `reduced`/`standard`/`aggressive`, selected via `privacy_level`)
- `index.html` — Single-page demo UI with Query Datasets and Paste & Redact tabs, plus a per-query privacy-level pricing selector
- `deploy.sh` — SSH deploy script (pulls latest main on server, restarts service)

## Privacy Tiers (Paid, Per Query)

`privacy_level` on `/get_data` and `/redact` selects the redaction tier (see `PRIVACY_TIERS`
in `api_server.py` for pricing, `_SYSTEM_BY_LEVEL`/`_RULES_BY_LEVEL` in `handlers.py` for
prompts):

- `reduced` — pays to *subtract* discretionary privacy: only mandatory Tier 1 statutory
  exemptions are withheld; personal identifiers are released in full. Statutory exemptions
  are never waivable, even at this tier.
- `standard` — free/included tier. Tier 1 + Tier 2 smart cloaking.
- `aggressive` — pays to *add* privacy: Tier 1 + Tier 2 + aggressive cloaking of indirect identifiers.

## Redaction Color Convention

- **Red** — FOIA blind redaction (`[b(Ex.N)]` markers, `.c-blind`)
- **Green** — Standard smart cloaking (names, DOB, address, phone, email, `.c-smart`)
- **Yellow** — Aggressive cloaking (`[~value~]` markers, locations/dates/employers/etc., `.c-aggr`)

## Demo Data Disclaimer

All demo datasets are AI-generated synthetic records — not real government data and not derived from any actual public records release. This must be clearly communicated in the UI.
