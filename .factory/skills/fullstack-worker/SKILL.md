---
name: fullstack-worker
description: Handles Python backend, HTML frontend, seed data, config, and deployment tasks for the USDX Flask app.
---

# Fullstack Worker

NOTE: Startup and cleanup are handled by `worker-base`. This skill defines the WORK PROCEDURE.

## When to Use This Skill

Any feature involving changes to the USDX codebase: Python backend (api_server.py, handlers.py, config.py, seed_data.py), HTML frontend (index.html), configuration, seed data creation, or deployment operations.

## Required Skills

None

## Work Procedure

1. **Read the feature description carefully.** Understand preconditions, expected behavior, and verification steps. Read AGENTS.md for boundaries and conventions.

2. **Investigate affected files.** Read the files you'll modify and any related files to understand current patterns. Key files:
   - `config.py` — credentials and settings (module-level variables)
   - `seed_data.py` — dataset definitions and S3 upload logic
   - `handlers.py` — data collection and LLM-based redaction
   - `index.html` — single-file frontend with inline CSS/JS
   - `deploy.sh` — production deployment script
   - `api_server.py` — Flask routes and auth

3. **Write tests first (when applicable).** For data structure changes, add assertions in test files that validate the new structure. For config changes, verify the key works. Not all features need new tests (e.g., pure deployment steps).

4. **Implement the changes.** Follow existing patterns exactly:
   - Seed data: dict with id, category, title, description, keywords, data fields. The `data` field contains the actual records.
   - Frontend: inline CSS/JS in index.html, no external dependencies
   - Config: module-level Python variables, matching existing naming conventions

5. **Run verification commands.** At minimum:
   - `python3 -m unittest test_redactor` (unit tests must pass)
   - For seed data: verify the Python module loads without errors (`python3 -c "import seed_data; print(len(seed_data.DATASETS))"`)
   - For frontend: verify HTML is well-formed
   - For deployment: run deploy.sh and verify with curl

6. **For deployment features:** Follow this exact sequence:
   - Commit all code changes to git first
   - Run `python3 seed_data.py` to upload datasets to DO Spaces
   - Run `bash deploy.sh` to deploy to production
   - Verify with `curl http://143.110.131.237:6732/ping`
   - Verify data with `curl -X POST http://143.110.131.237:6732/get_data` (after auth)

7. **Commit your changes** with a clear commit message describing what was done.

## Example Handoff

```json
{
  "salientSummary": "Replaced 12 aggregate datasets in seed_data.py with 2 individual-record datasets (CIA contractors: 8 records with names/clearances/locations, Lakewood animal control: 10 records with resident names/addresses/pet info). Ran `python3 -m unittest test_redactor` (12 passing). Verified seed_data.py loads: `python3 -c \"import seed_data\"` succeeds.",
  "whatWasImplemented": "Created CIA human contractors employment dataset with 8 individual records containing realistic names, TS/SCI clearance levels, facility locations, contract dates, and GS pay grades. Created Lakewood CO animal control dataset with 10 service records containing resident names, Lakewood addresses (real ZIP codes 80226-80232), pet species/breeds, violation types, and case numbers. Removed all 12 previous aggregate datasets.",
  "whatWasLeftUndone": "",
  "verification": {
    "commandsRun": [
      {"command": "python3 -m unittest test_redactor", "exitCode": 0, "observation": "12 tests passed"},
      {"command": "python3 -c \"import seed_data; print(len(seed_data.DATASETS))\"", "exitCode": 0, "observation": "Prints 2"}
    ],
    "interactiveChecks": []
  },
  "tests": {
    "added": []
  },
  "discoveredIssues": []
}
```

## When to Return to Orchestrator

- SSH key not found or deploy.sh fails to connect to production server
- DO Spaces credentials are invalid (seed_data.py upload fails with auth errors)
- OpenRouter API key from Agreed/config.py also returns 401
- Feature depends on changes not yet made in another feature
- Requirements are ambiguous about what data fields to include in seed datasets
