# US Federal Data Exchange (USDX)

A secure, privacy-first platform for accessing US federal data with AI-powered differential privacy and automatic redaction of sensitive personal information.

## Overview

The USDX platform allows users to request federal data using natural language descriptions. AI-powered handlers collect relevant data from Digital Ocean Spaces and automatically apply differential privacy techniques and redact sensitive PII (names, locations, faces, etc.) before returning the data.

## Features

- **AI-Powered Data Collection**: Natural language queries to find relevant federal datasets
- **Automatic Privacy Protection**: Differential privacy and PII redaction
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
- **POST /get_data**: Request federal data with privacy protection (auth required)

### Web Interface

- **GET /**: Landing page with project info
- **GET /api_docs.html**: Complete API documentation with interactive testing

See the full API documentation at `http://localhost:6732/api_docs.html` when running.

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

# Get data (use token from login response)
curl -X POST http://localhost:6732/get_data \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"description": "Population data for Colorado from 2020-2023"}'
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

All data returned through `/get_data` is automatically processed:

- **Proper Names**: Replaced with alternatives ("Mickey" → "Jamison")
- **Locations**: Generalized ("123 Main St, Denver" → "Colorado")
- **PII**: Removed or redacted (SSN, phone, email → "***")
- **Faces**: Marked in metadata ("[FACE_REDACTED]")

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
ssh YOUR_VM "cd ~/TheUSDX && git pull && sudo systemctl restart usdx"
```

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
**Email**: mickeyshaughnessy@gmail.com  
**Organization**: The Mithril Company (Colorado LLC)

## License

Copyright © 2026 The Mithril Company. All rights reserved.
