import json
import logging
import os
from datetime import datetime, timezone
from typing import cast
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from .data_loader import load_activities, load_activity_descriptions, load_questions
from .models import QuestionItem, QuestionsResponse, RecommendationRequest, RecommendationResponse
from .settings import Settings, load_settings_from_env
from .scoring import build_recommendation_payload
from .submission_store import SubmissionStoreError, build_visitor_hash, create_submission_store


DEFAULT_CORS_ORIGINS = ("http://localhost:3000",)


def normalize_origin(origin: str) -> str:
    return origin.strip().strip("\"'").rstrip("/")


def parse_cors_origins(raw_value: str | None) -> list[str]:
    if raw_value is None or raw_value.strip() == "":
        return list(DEFAULT_CORS_ORIGINS)

    value = raw_value.strip()

    origins_raw: list[str]
    if value.startswith("["):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                origins_raw = [str(item) for item in parsed]
            else:
                origins_raw = value.split(",")
        except json.JSONDecodeError:
            origins_raw = value.split(",")
    else:
        origins_raw = value.split(",")

    origins = [normalize_origin(origin) for origin in origins_raw]
    filtered_origins = [origin for origin in origins if origin]

    return filtered_origins or list(DEFAULT_CORS_ORIGINS)


CORS_ALLOW_ORIGINS = parse_cors_origins(os.getenv("CORS_ALLOW_ORIGINS"))
CORS_ALLOW_ORIGIN_REGEX = normalize_origin(os.getenv("CORS_ALLOW_ORIGIN_REGEX") or "") or None

logger = logging.getLogger(__name__)

app = FastAPI(title="DCCD Career Diagnostic API", version="0.1.0")
app.state.settings = load_settings_from_env()
app.state.submission_store = create_submission_store(app.state.settings)
if app.state.settings.enable_visitor_hash and not app.state.settings.visitor_hash_secret:
    logger.warning("ENABLE_VISITOR_HASH is true, but VISITOR_HASH_SECRET is missing. visitor_hash will be omitted.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_origin_regex=CORS_ALLOW_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
@app.get("/api/v1/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/ready")
def ready() -> dict[str, str]:
    try:
        load_questions()
        load_activities()
        load_activity_descriptions()
    except Exception:
        logger.exception("Readiness check failed while loading backend data")
        raise HTTPException(status_code=503, detail="Backend data dependencies are unavailable.")

    return {"status": "ok"}


@app.get("/api/v1/questions", response_model=QuestionsResponse)
def questions() -> QuestionsResponse:
    loaded_questions = load_questions()
    return QuestionsResponse(
        questions=[
            QuestionItem(id=index + 1, statement=question.statement)
            for index, question in enumerate(loaded_questions)
        ]
    )


@app.post("/api/v1/recommendations", response_model=RecommendationResponse)
def recommendations(payload: RecommendationRequest, request: Request) -> RecommendationResponse:
    questions = load_questions()
    items, prerequisite_note = build_recommendation_payload(payload.responses)
    settings = cast(Settings, request.app.state.settings)

    submission_id = str(uuid4())
    submitted_at_utc = datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    response_values = [str(response) for response in payload.responses]
    recommendation_values = [item.get("name", "") for item in items]
    visitor_hash = _extract_visitor_hash(request=request, settings=settings)

    try:
        request.app.state.submission_store.append_submission(
            submitted_at_utc=submitted_at_utc,
            submission_id=submission_id,
            responses=response_values,
            recommendations=recommendation_values,
            visitor_hash=visitor_hash,
            schema_version=settings.schema_version,
        )
    except SubmissionStoreError:
        logger.exception("Failed to store survey submission (submission_id=%s)", submission_id)

    return RecommendationResponse(
        recommendations=items,
        total_questions=len(questions),
        completion_percent=100,
        scoring_note="Recommendations are calculated from your survey responses.",
        prerequisite_note=prerequisite_note,
    )


def _extract_visitor_hash(*, request: Request, settings: Settings) -> str | None:
    if not settings.enable_visitor_hash or not settings.visitor_hash_secret:
        return None

    ip_address = _extract_client_ip(request)
    if not ip_address:
        return None

    return build_visitor_hash(
        ip_address=ip_address,
        user_agent=request.headers.get("user-agent"),
        secret=settings.visitor_hash_secret,
    )


def _extract_client_ip(request: Request) -> str | None:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        first_ip = forwarded_for.split(",")[0].strip()
        if first_ip:
            return first_ip

    if request.client:
        return request.client.host

    return None
