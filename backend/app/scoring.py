from __future__ import annotations

from dataclasses import dataclass

from .data_loader import (
    Activity,
    load_activities,
    load_activity_descriptions,
    load_questions,
)
from .models import ResponseOption

TOP_K = 5
MIN_SCORE_CLAMP = 0

RESPONSE_WEIGHTS = {
    ResponseOption.STRONGLY_DISAGREE: -2,
    ResponseOption.DISAGREE: -1,
    ResponseOption.AGREE: 1,
    ResponseOption.STRONGLY_AGREE: 2,
}


@dataclass(frozen=True)
class RankedActivity:
    code: str
    name: str
    phase: str
    score: int


def compute_ranked_activities(responses: list[ResponseOption]) -> list[RankedActivity]:
    questions = load_questions()
    activities = load_activities()

    if len(responses) != len(questions):
        raise ValueError(
            f"Expected {len(questions)} responses, received {len(responses)}"
        )

    score_map = {activity.code: 0 for activity in activities}

    for question, response in zip(questions, responses, strict=True):
        delta = RESPONSE_WEIGHTS[response]
        for tag in question.tags:
            score_map[tag] = score_map.get(tag, 0) + delta

    ranked = [
        RankedActivity(
            code=activity.code,
            name=activity.name,
            phase=activity.phase,
            score=max(MIN_SCORE_CLAMP, score_map.get(activity.code, 0)),
        )
        for activity in activities
    ]

    return sorted(ranked, key=lambda item: (-item.score, item.name))


def _find_highest_phase_a(ranked: list[RankedActivity]) -> RankedActivity | None:
    for activity in ranked:
        if activity.phase == "Phase A":
            return activity
    return None


def _find_energy_mapping(
    activities: tuple[Activity, ...], ranked_by_code: dict[str, RankedActivity]
) -> RankedActivity | None:
    energy = next(
        (activity for activity in activities if activity.name == "Energy Mapping"), None
    )
    if not energy:
        return None
    return ranked_by_code.get(energy.code)


def select_top_recommendations(
    ranked: list[RankedActivity],
) -> tuple[list[RankedActivity], str | None]:
    activities = load_activities()
    ranked_by_code = {item.code: item for item in ranked}

    has_phase_c_in_top_window = any(
        activity.phase == "Phase C" for activity in ranked[:TOP_K]
    )
    should_inject_prerequisites = has_phase_c_in_top_window

    selected: list[RankedActivity] = []
    seen_codes: set[str] = set()

    if should_inject_prerequisites:
        phase_a = _find_highest_phase_a(ranked)
        energy_mapping = _find_energy_mapping(activities, ranked_by_code)

        for required in (phase_a, energy_mapping):
            if required and required.code not in seen_codes:
                selected.append(required)
                seen_codes.add(required.code)

    for activity in ranked:
        if len(selected) >= TOP_K:
            break
        if activity.code in seen_codes:
            continue
        selected.append(activity)
        seen_codes.add(activity.code)

    prerequisite_note = None
    # if should_inject_prerequisites:
    #     prerequisite_note = (
    #         "Phase C activities are sequenced after one Phase A foundation activity and Energy Mapping."
    #     )

    return selected[:TOP_K], prerequisite_note


def build_recommendation_payload(
    responses: list[ResponseOption],
) -> tuple[list[dict[str, str]], str | None]:
    descriptions = load_activity_descriptions()
    ranked = compute_ranked_activities(responses)
    selected, prerequisite_note = select_top_recommendations(ranked)

    items = [
        {
            "name": item.name,
            "description": descriptions[item.code],
            "phase": item.phase,
        }
        for item in selected
    ]

    return items, prerequisite_note
