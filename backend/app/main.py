from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .data_loader import load_questions
from .models import QuestionItem, QuestionsResponse, RecommendationRequest, RecommendationResponse
from .scoring import build_recommendation_payload


app = FastAPI(title="DCCD Career Diagnostic API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
@app.get("/api/v1/health")
def health() -> dict[str, str]:
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
