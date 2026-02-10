from app.models import ResponseOption
from app.scoring import compute_ranked_activities, select_top_recommendations


def test_all_strongly_disagree_clamps_scores_to_zero() -> None:
    responses = [ResponseOption.STRONGLY_DISAGREE] * 18

    ranked = compute_ranked_activities(responses)

    assert all(item.score == 0 for item in ranked)


def test_prerequisites_are_prepended_when_phase_c_is_high() -> None:
    responses = [ResponseOption.STRONGLY_AGREE] * 18

    ranked = compute_ranked_activities(responses)
    selected, note = select_top_recommendations(ranked)

    assert [item.name for item in selected[:2]] == [
        "Knowdell Values",
        "Energy Mapping",
    ]
    assert note is not None
