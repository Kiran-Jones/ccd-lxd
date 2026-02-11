# Backend (FastAPI)

## Run

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Test

```bash
cd backend
pytest
```

## Deployment CORS

Set `CORS_ALLOW_ORIGINS` to your deployed frontend origin(s), comma-separated.

Example:

```bash
export CORS_ALLOW_ORIGINS="https://app.example.com,https://staging.example.com"
```

In hosting dashboards, store the raw value without surrounding quotes.

Optional preview-domain regex:

```bash
export CORS_ALLOW_ORIGIN_REGEX="^https://.*\\.vercel\\.app$"
```

## Data Files

Runtime data files are loaded from `backend/data/`:

- `backend/data/questions.json`
- `backend/data/order.csv`
- `backend/data/descriptions.txt`

## Google Sheets Submission Storage (MVP)

Survey submissions are appended to Google Sheets from `POST /api/v1/recommendations`.
This write path is non-blocking: if Sheets fails, the API still returns recommendations.

### 1) Google Cloud Setup

1. Create a Google Cloud project.
2. Enable **Google Sheets API**.
3. Create a service account and generate a JSON key.
4. Create a spreadsheet with a worksheet tab (for example `Submissions`).
5. Share the spreadsheet with the service account email as **Editor**.

### 2) Backend Environment Variables

Set these variables where the backend runs:

```bash
export GOOGLE_SHEETS_ENABLED=true
export GOOGLE_SHEETS_SPREADSHEET_ID="your-spreadsheet-id"
export GOOGLE_SHEETS_WORKSHEET_NAME="Submissions"

# Choose one credential source:
export GOOGLE_SERVICE_ACCOUNT_FILE="/absolute/path/to/service-account.json"
# or:
# export GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'

# Optional tuning:
export GOOGLE_SHEETS_REQUEST_TIMEOUT_SECONDS=5
export GOOGLE_SHEETS_MAX_RETRIES=2

# Optional anonymous visitor hash:
export ENABLE_VISITOR_HASH=false
# export VISITOR_HASH_SECRET="set-this-only-if-ENABLE_VISITOR_HASH=true"

# Optional schema tag:
export SUBMISSION_SCHEMA_VERSION="v1"
```

If `GOOGLE_SHEETS_ENABLED=true` but required values are missing, backend logs a warning and falls back to no-op storage.

### 3) Sheet Column Layout

Rows are appended in this order:

`submitted_at_utc`, `submission_id`, `q1` ... `q18`, `rec_1` ... `rec_5`, `visitor_hash`, `schema_version`

### 4) Local vs Deploy

- Local: easiest path is `GOOGLE_SERVICE_ACCOUNT_FILE=/path/to/key.json`.
- Deploy: prefer `GOOGLE_SERVICE_ACCOUNT_JSON` as a secret env var.
- In both cases, the same service account must have editor access to the target spreadsheet.
