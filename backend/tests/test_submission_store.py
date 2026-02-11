from app.submission_store import GoogleSheetsSubmissionStore, build_submission_row, build_visitor_hash


def test_build_submission_row_uses_fixed_columns() -> None:
    row = build_submission_row(
        submitted_at_utc="2026-02-11T00:00:00Z",
        submission_id="test-submission",
        responses=["agree"] * 18,
        recommendations=["Alpha", "Bravo"],
        visitor_hash=None,
        schema_version="v1",
    )

    assert len(row) == 27
    assert row[0] == "2026-02-11T00:00:00Z"
    assert row[1] == "test-submission"
    assert row[2] == "agree"
    assert row[20] == "Alpha"
    assert row[21] == "Bravo"
    assert row[23] == ""
    assert row[24] == ""
    assert row[25] == ""
    assert row[26] == "v1"


def test_build_visitor_hash_is_deterministic() -> None:
    first = build_visitor_hash(
        ip_address="203.0.113.50",
        user_agent="Mozilla/5.0",
        secret="secret",
    )
    second = build_visitor_hash(
        ip_address="203.0.113.50",
        user_agent="Mozilla/5.0",
        secret="secret",
    )

    assert first == second
    assert len(first) == 24


def test_google_store_retries_then_succeeds(monkeypatch) -> None:
    store = GoogleSheetsSubmissionStore(
        spreadsheet_id="spreadsheet-id",
        worksheet_name="Submissions",
        service_account_json='{"type":"service_account"}',
        service_account_file=None,
        request_timeout_seconds=5.0,
        max_retries=2,
    )
    attempts = {"count": 0}

    def fail_then_succeed(row: list[str]) -> None:
        attempts["count"] += 1
        if attempts["count"] < 2:
            raise RuntimeError("temporary error")

    monkeypatch.setattr(store, "_append_row", fail_then_succeed)
    monkeypatch.setattr("app.submission_store.time.sleep", lambda _: None)

    store.append_submission(
        submitted_at_utc="2026-02-11T00:00:00Z",
        submission_id="abc",
        responses=["agree"] * 18,
        recommendations=["A", "B", "C", "D", "E"],
        visitor_hash=None,
        schema_version="v1",
    )

    assert attempts["count"] == 2
