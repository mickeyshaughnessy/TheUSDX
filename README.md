# Acme Redactors

A public records management platform for accessing US government records, with AI-powered differential privacy and automatic redaction of sensitive personal information. Privacy is configurable per query — pay to add extra cloaking, or pay to reduce redaction for verified access to identified records.

**Live at: https://themithrilcompany.com**

## Overview

Acme Redactors lets users request public records using natural language descriptions. AI-powered handlers collect relevant data from Digital Ocean Spaces and automatically apply differential privacy techniques and redact sensitive PII (names, locations, faces, etc.) before returning the data. Every query includes standard FOIA-compliant redaction at no charge; two paid tiers let requesters move the privacy dial in either direction on a per-query basis. See [Pricing](#pricing--privacy-per-query) below.

## Features

- **AI-Powered Data Collection**: Natural language queries to find relevant public records datasets
- **Automatic Privacy Protection**: Differential privacy and PII redaction via the Acme Redactors cloaking device
- **Privacy, Priced Per Query**: Pay to add or subtract redaction on any individual query
- **Secure Authentication**: JWT-based authentication with user data in cloud storage
- **Cloud Infrastructure**: Digital Ocean VM + Spaces for all storage (no local database)
- **HTTPS/HTTP Support**: Runs on port 6732 with SSL support
- **Modern API**: RESTful endpoints with comprehensive documentation
- **Git-Based Deployment**: Simple commit-push-pull-restart workflow

## Architecture

- **Storage**: Everything in Digital Ocean Spaces (users, data, metadata)
- **Authentication**: JWT tokens, user records stored as JSON in Spaces
- **AI Processing**: OpenRouter API (free tier available)
- **Deployment**: Git-based workflow with systemd service

## Quick Start (Local Development)

### Prerequisites

- Python 3.8+
- Digital Ocean account with Spaces configured
- OpenRouter API key (free tier: https://openrouter.ai)

### Local Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd TheUSDX
```

2. Install dependencies:
```bash
pip3 install -r requirements.txt
```

3. Configure application:
```bash
cp config.py.example config.py
# Edit config.py and add your credentials:
# - OPENROUTER_API_KEY
# - DO_SPACES_KEY, DO_SPACES_SECRET, DO_SPACES_BUCKET
# - SECRET_KEY (generate with: python3 -c "import secrets; print(secrets.token_hex(32))")
nano config.py
```

4. Run the server:
```bash
python3 api_server.py
```

The server will start on `http://localhost:6732`

**IMPORTANT:** Never commit `config.py` to git! It's in `.gitignore`.

## API Endpoints

### Authentication

- **POST /signup**: Create new user account (stored in DO Spaces)
- **POST /login**: Authenticate and receive JWT token

### Core Endpoints

- **GET /ping**: Health check (no auth required)
- **POST /get_data**: Request public records with privacy protection (optional auth); accepts `privacy_level`
- **POST /redact**: Redact a pasted record (JSON or text) at a chosen privacy tier

### Web Interface

- **GET /**: Landing page with project info
- **GET /api_docs.html**: Complete API documentation with interactive testing

See the full API documentation at https://themithrilcompany.com/api_docs.html (production) or `http://localhost:6732/api_docs.html` when running locally.

## Usage Example

```bash
# Signup
curl -X POST http://localhost:6732/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123!"}'

# Login
curl -X POST http://localhost:6732/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123!"}'

# Get data (use token from login response). privacy_level is optional:
# "reduced" | "standard" (default) | "aggressive" — see Pricing below.
curl -X POST http://localhost:6732/get_data \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"description": "Population data for Colorado from 2020-2023", "privacy_level": "standard"}'
```

## Testing

### Local Testing

Run the integration test suite:

```bash
# Make sure the server is running first (in another terminal)
python3 test_api.py
```

### Browser Testing

Open `http://localhost:6732/api_docs.html` and use the interactive test runner.

## Privacy & Redaction

All data returned through `/get_data` and `/redact` is automatically processed by the Acme
Redactors cloaking device:

- **Names**: Replaced with realistic alternatives ("Marcus Thompson" → "Robert Johnson")
- **Addresses**: Substituted with different but plausible addresses
- **SSN / credentials**: Masked with `[b(Ex.N)]` blind-redaction markers
- **Phone, email, DOB**: Replaced with realistic equivalents

### Pricing — Privacy, Per Query

Standard redaction (above) is included with every query. Two paid add-ons move the privacy
dial per query via the `privacy_level` request field. Statutory exemptions (SSNs,
classification markings, biometric identifiers) are withheld at every tier — they are never
for sale.

| `privacy_level` | Effect | Add-on price |
|---|---|---|
| `reduced` | Subtracts privacy — only statutory exemptions withheld; personal identifiers released in full | +$4.00 |
| `standard` (default) | Statutory exemptions + smart cloaking of personal privacy fields | Included |
| `aggressive` | Adds privacy — extends cloaking to indirect identifiers (locations, dates, employers, relationships) | +$1.50 |

Base query price is $0.25. This is a demonstration pricing model returned in the API
response (`pricing` field) — no payment is actually collected.

## Production Deployment

See **[PLAYBOOK.md](PLAYBOOK.md)** for complete deployment guide.

### Quick Deployment Overview

1. **Setup DO Spaces** - Create bucket, get API keys
2. **Setup VM** - Ubuntu droplet, install Python & git
3. **Clone repo** - `git clone` on VM
4. **Configure** - Create `config.py` locally, SCP to VM (**never commit config.py!**)
5. **Install deps** - `pip3 install -r requirements.txt`
6. **Setup service** - systemd service for auto-restart
7. **Deploy changes** - Commit → Push → SSH → Pull → Restart

### Deployment Workflow

```bash
# Local: Make changes and commit
git add .
git commit -m "Update feature"
git push

# Deploy to VM
./deploy.sh
```

The deploy script SSHes to `root@143.110.131.237` (themithrilcompany.com), pulls latest main, and restarts `usdx.service`.

### Digital Ocean Spaces Structure

```
usdx-data/
├── users/              # User accounts (JSON files)
│   ├── user@example.com.json
│   └── ...
├── metadata/           # Dataset metadata
│   ├── census-2023.json
│   └── ...
└── data/              # Actual datasets
    ├── census-2023.json
    └── ...
```

## Project Structure

```
TheUSDX/
├── api_server.py         # Flask application with JWT auth
├── handlers.py           # AI data collectors and redactors
├── config.py             # Configuration (gitignored - create from example)
├── config.py.example     # Configuration template
├── index.html            # Landing page
├── api_docs.html         # API documentation (Borland theme)
├── test_api.py           # Integration tests
├── requirements.txt      # Python dependencies
├── README.md             # This file
├── PLAYBOOK.md           # Deployment playbook
└── .gitignore            # Git ignore (includes config.py)
```

## Contact

**Project Lead**: Mickey Shaughnessy  
**X**: https://x.com/MichaelSha10041  

**Organization**: The Mithril Company (Colorado LLC)

## License

Copyright © 2026 The Mithril Company. All rights reserved.
