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

Optional preview-domain regex:

```bash
export CORS_ALLOW_ORIGIN_REGEX="^https://.*\\.vercel\\.app$"
```
