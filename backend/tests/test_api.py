from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ready_endpoint_returns_ok() -> None:
    response = client.get("/api/v1/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_cors_allows_localhost_frontend_origin() -> None:
    response = client.options(
        "/api/v1/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


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
