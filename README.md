# DCCD Career Diagnostic MVP

MVP application for the Dartmouth Center for Career Design with:
- `frontend/`: Next.js + TypeScript UI (3 screens: welcome, survey, results)
- `backend/`: FastAPI recommendation API (scoring + prerequisite gating)

## Run Backend

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000
```

## Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:3000` and calls backend at `http://localhost:8000`.

## Deployment Config (CORS + API Base URL)

Set these environment variables in deployment:

- Backend:
  - `CORS_ALLOW_ORIGINS=https://your-frontend-domain.com` (comma-separated for multiple origins)
  - Optional: `CORS_ALLOW_ORIGIN_REGEX=^https://.*\\.vercel\\.app$` (for preview domains)
- Frontend:
  - `NEXT_PUBLIC_API_BASE_URL=https://your-backend-domain.com`

When entering values in Render/Vercel dashboards, do not include surrounding quotes in the stored value.

Without these, deployed requests can fail due to browser CORS restrictions or incorrect localhost API targets.

## Test

```bash
source .venv/bin/activate
cd backend
pytest tests
```

## Algorithm Rules Implemented

- 18 required questions.
- Response weights: `strongly_disagree=-2`, `disagree=-1`, `agree=+1`, `strongly_agree=+2`.
- Multi-tag questions add their score to each tagged activity.
- Scores are clamped at `MIN_SCORE_CLAMP=0`.
- Top results use `TOP_K=5`.
- Ties are sorted alphabetically by activity name.
- If any Phase C activity appears in the top-K window, recommendations are prepended with:
  - highest-ranked Phase A activity, and
  - Energy Mapping (Phase B)
  before filling remaining slots by rank.
