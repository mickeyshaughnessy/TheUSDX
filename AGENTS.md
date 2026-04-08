# Agent Guidelines — TheUSDX / Poseidon

## After Every Change: Commit, Push, and Deploy

**This is required after any code change, no exceptions.**

```bash
git add <changed files>
git commit -m "..."
git push origin main
./deploy.sh
```

Do not stop after editing files locally. Always push to GitHub and run `./deploy.sh` to sync and restart the server at `root@143.110.131.237`. The service is `usdx.service` managed by systemd.

## Project Overview

Poseidon is a FOIA-compliant federal data exchange demo. Core files:

- `api_server.py` — Flask server, `/get_data` and `/redact` endpoints
- `handlers.py` — LLM redaction logic (two-tier: blind `[b(Ex.N)]` + smart cloaking)
- `index.html` — Single-page demo UI with Query Datasets and Paste & Redact tabs
- `deploy.sh` — SSH deploy script (pulls latest main on server, restarts service)

## Redaction Color Convention

- **Red** — FOIA blind redaction (`[b(Ex.N)]` markers, `.c-blind`)
- **Green** — Standard smart cloaking (names, DOB, address, phone, email, `.c-smart`)
- **Yellow** — Aggressive cloaking (`[~value~]` markers, locations/dates/employers/etc., `.c-aggr`)

## Demo Data Disclaimer

All demo datasets are AI-generated synthetic records — not real government data and not derived from any actual public records release. This must be clearly communicated in the UI.
