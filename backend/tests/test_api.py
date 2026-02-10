from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_questions_endpoint_returns_18_questions() -> None:
    response = client.get("/api/v1/questions")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["questions"]) == 18
    assert payload["questions"][0]["id"] == 1


def test_recommendations_endpoint_returns_top_five() -> None:
    payload = {"responses": ["agree"] * 18}

    response = client.post("/api/v1/recommendations", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert len(data["recommendations"]) == 5
    assert data["completion_percent"] == 100


def test_recommendations_endpoint_validates_response_length() -> None:
    payload = {"responses": ["agree"] * 17}

    response = client.post("/api/v1/recommendations", json=payload)

    assert response.status_code == 422
