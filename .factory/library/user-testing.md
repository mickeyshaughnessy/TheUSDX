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
