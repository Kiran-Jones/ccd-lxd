from enum import Enum
from pydantic import BaseModel, Field, model_validator


class ResponseOption(str, Enum):
    STRONGLY_DISAGREE = "strongly_disagree"
    DISAGREE = "disagree"
    AGREE = "agree"
    STRONGLY_AGREE = "strongly_agree"


class RecommendationRequest(BaseModel):
    responses: list[ResponseOption] = Field(..., min_length=18, max_length=18)


class QuestionItem(BaseModel):
    id: int
    statement: str


class QuestionsResponse(BaseModel):
    questions: list[QuestionItem]


class RecommendationItem(BaseModel):
    name: str
    description: str
    phase: str


class RecommendationResponse(BaseModel):
    recommendations: list[RecommendationItem]
    total_questions: int
    completion_percent: int
    scoring_note: str
    prerequisite_note: str | None = None

    @model_validator(mode="after")
    def validate_non_empty_recommendations(self) -> "RecommendationResponse":
        if not self.recommendations:
            raise ValueError("recommendations cannot be empty")
        return self
