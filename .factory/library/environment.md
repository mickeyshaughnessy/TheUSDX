# Environment

Environment variables, external dependencies, and setup notes.

**What belongs here:** Required env vars, external API keys/services, dependency quirks, platform-specific notes.
**What does NOT belong here:** Service ports/commands (use `.factory/services.yaml`).

---

## External Dependencies

- **OpenRouter API** — LLM provider for dataset matching and redaction. Key in config.py.
- **Digital Ocean Spaces** — S3-compatible object storage. Credentials in config.py. Bucket: mithril-media, region: sfo3, prefix: usdx/
- **Production Server** — 143.110.131.237, SSH via ~/.ssh/id_ed25519, systemd service "usdx"

## Config File

config.py is gitignored. Contains:
- OPENROUTER_API_KEY, OPENROUTER_MODEL, OPENROUTER_FALLBACK_MODEL
- DO_SPACES_KEY, DO_SPACES_SECRET, DO_SPACES_REGION, DO_SPACES_BUCKET, DO_SPACES_PREFIX
- SECRET_KEY (JWT), HOST, PORT, DEBUG
- SSL_CERT_PATH, SSL_KEY_PATH (both None)

## Python Dependencies

Flask, flask-cors, gunicorn, boto3, bcrypt, PyJWT, requests (see requirements.txt)

## Operational Notes

- `deploy.sh` uses a remote `git stash` / `git stash pop` around `git pull`. If the server has local uncommitted edits, deploys can fail with conflicts and require manual cleanup.
- Production SSH to `143.110.131.237` may intermittently reset during rapid repeated attempts. Add a short delay before retrying deployment verification steps.
