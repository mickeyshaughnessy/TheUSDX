# User Testing

## Validation Surface

### Web UI (agent-browser)
- URL: http://143.110.131.237:6732/
- Auth: signup/login with email+password, JWT stored in localStorage
- Key interactions: demo buttons, query submission, result display

### API (curl)
- Base URL: http://143.110.131.237:6732
- Auth: POST /signup or /login → get JWT token → use in Authorization: Bearer header
- Key endpoints: /ping, /get_data (POST with {"description": "..."})

## Validation Concurrency

### curl surface
- Max concurrent: 5 (curl is lightweight, ~10MB per process)
- No special setup needed

### agent-browser surface
- Max concurrent: 3 (16GB machine with ~6GB used at baseline; each browser instance ~800MB; 3 * 800MB = 2.4GB within 70% of ~10GB headroom)
- Requires production server to be deployed and running
- Auth state: each validator should create its own test account

## Testing Notes

- The API uses in-memory caching (1hr TTL for LLM results). Repeat queries will return cached results.
- LLM-dependent assertions (query matching) may vary slightly between runs. Accept reasonable matches.
- Production server runs gunicorn with 4 workers, so concurrent requests are handled.
- First-time `agent-browser` use may require running `agent-browser install` to provision Chromium.
- For result metadata checks in browser flows, a short fallback delay plus DOM evaluation is more reliable than strict text-only waits during transient rendering.

## Flow Validator Guidance: curl

- Use production base URL: `http://143.110.131.237:6732`.
- Create a unique account per flow (`validator+<group>-<timestamp>@example.com`) to avoid auth-state collisions.
- Keep all generated artifacts inside assigned evidence directory only.
- For cache assertions, use a query string unique to your group so another validator cannot pre-warm cache.
- Treat fallback sample records (`FED-001`/`FED-002`) as immediate failure for dataset assertions.
- Do not modify application code, server state, or deployment; validation is read/test only.

## Flow Validator Guidance: agent-browser

- Use a dedicated browser session and dedicated test account for your assigned flow.
- Stay on `http://143.110.131.237:6732/` unless an assertion explicitly requires an API endpoint check.
- Capture screenshots for page-load, demo button visibility, pre-fill behavior, and result rendering steps.
- Validate console for uncaught errors during page load and form interactions.
- Do not alter data outside normal user actions (signup/login/query submit).
