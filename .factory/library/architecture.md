# Architecture

## System Overview

Flask API server + single-page HTML frontend for demonstrating privacy-preserving PII redaction on public records data. Uses LLM (via OpenRouter) for both dataset matching and redaction.

## Components

- **api_server.py** — Flask app with JWT auth, routes: /ping, /signup, /login, /get_data, /. User records in DO Spaces.
- **handlers.py** — Business logic: collect_data() matches queries to datasets via LLM, redact_data() sends data to LLM for PII redaction. Chunks large datasets for token limits.
- **config.py** — Module-level Python variables for credentials (OpenRouter, DO Spaces, JWT secret).
- **seed_data.py** — Dataset definitions + upload script. Splits each dataset into metadata (for matching) and data (for retrieval) in DO Spaces.
- **index.html** — Single-file frontend with inline CSS/JS. Auth form, query form, result display.
- **redactor.py** — Standalone configurable redactor module (NOT wired into the server; dead code from server perspective).

## Data Flow

1. User submits query via index.html
2. Frontend POSTs to /get_data with JWT auth
3. handlers.collect_data(): lists metadata from S3, asks LLM to match query to dataset IDs, fetches matched data
4. handlers.redact_data(): chunks data, sends to LLM for PII redaction
5. Response returned with redacted data, record count, processing time, privacy flag

## LLM Integration

- Provider: OpenRouter (https://openrouter.ai/api/v1/chat/completions)
- Primary: meta-llama/llama-3.2-3b-instruct:free
- Fallback: anthropic/claude-3.5-haiku (on 429 or error)
- Two call sites: dataset matching + redaction (both in handlers.py via call_openrouter())

## Storage

- DO Spaces (S3-compatible): mithril-media bucket, sfo3 region, usdx/ prefix
- Metadata: usdx/metadata/{id}.json (id, category, title, description, keywords)
- Data: usdx/data/{id}.json (id, category, data)
