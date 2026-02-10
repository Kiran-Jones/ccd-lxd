import json
import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .data_loader import load_activities, load_activity_descriptions, load_questions
from .models import QuestionItem, QuestionsResponse, RecommendationRequest, RecommendationResponse
from .scoring import build_recommendation_payload


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
def recommendations(payload: RecommendationRequest) -> RecommendationResponse:
    questions = load_questions()
    items, prerequisite_note = build_recommendation_payload(payload.responses)

    return RecommendationResponse(
        recommendations=items,
        total_questions=len(questions),
        completion_percent=100,
        scoring_note="Recommendations are calculated from your survey responses.",
        prerequisite_note=prerequisite_note,
    )
