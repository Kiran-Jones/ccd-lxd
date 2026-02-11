from fastapi.testclient import TestClient

from app.main import app
from app.settings import Settings
from app.submission_store import SubmissionStoreError


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


def test_recommendations_appends_submission_row(monkeypatch) -> None:
    calls: list[dict[str, object]] = []

    class FakeStore:
        def append_submission(self, **kwargs: object) -> None:
            calls.append(kwargs)

    monkeypatch.setattr(client.app.state, "submission_store", FakeStore(), raising=False)
    monkeypatch.setattr(
        client.app.state,
        "settings",
        Settings(
            google_sheets_enabled=False,
            google_sheets_spreadsheet_id=None,
            google_sheets_worksheet_name="Submissions",
            google_service_account_json=None,
            google_service_account_file=None,
            google_sheets_request_timeout_seconds=5.0,
            google_sheets_max_retries=2,
            enable_visitor_hash=False,
            visitor_hash_secret=None,
            schema_version="v1",
        ),
        raising=False,
    )

    payload = {"responses": ["agree"] * 18}
    response = client.post("/api/v1/recommendations", json=payload)

    assert response.status_code == 200
    assert len(calls) == 1
    assert calls[0]["schema_version"] == "v1"
    assert len(calls[0]["responses"]) == 18


def test_recommendations_returns_success_when_submission_store_fails(monkeypatch) -> None:
    class FailingStore:
        def append_submission(self, **kwargs: object) -> None:
            raise SubmissionStoreError("boom")

    monkeypatch.setattr(client.app.state, "submission_store", FailingStore(), raising=False)
    monkeypatch.setattr(
        client.app.state,
        "settings",
        Settings(
            google_sheets_enabled=False,
            google_sheets_spreadsheet_id=None,
            google_sheets_worksheet_name="Submissions",
            google_service_account_json=None,
            google_service_account_file=None,
            google_sheets_request_timeout_seconds=5.0,
            google_sheets_max_retries=2,
            enable_visitor_hash=False,
            visitor_hash_secret=None,
            schema_version="v1",
        ),
        raising=False,
    )

    payload = {"responses": ["agree"] * 18}
    response = client.post("/api/v1/recommendations", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert len(data["recommendations"]) == 5
