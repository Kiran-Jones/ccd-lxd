import hashlib
import hmac
import json
import logging
import time
from dataclasses import dataclass
from typing import Protocol

from .settings import Settings


logger = logging.getLogger(__name__)

GOOGLE_SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SUBMISSION_COLUMNS = (
    ["submitted_at_utc", "submission_id"]
    + [f"q{index}" for index in range(1, 19)]
    + [f"rec_{index}" for index in range(1, 6)]
    + ["visitor_hash", "schema_version"]
)


class SubmissionStoreError(RuntimeError):
    pass


class SubmissionStore(Protocol):
    def append_submission(
        self,
        *,
        submitted_at_utc: str,
        submission_id: str,
        responses: list[str],
        recommendations: list[str],
        visitor_hash: str | None,
        schema_version: str,
    ) -> None: ...


class NoopSubmissionStore:
    def append_submission(
        self,
        *,
        submitted_at_utc: str,
        submission_id: str,
        responses: list[str],
        recommendations: list[str],
        visitor_hash: str | None,
        schema_version: str,
    ) -> None:
        return


@dataclass
class GoogleSheetsSubmissionStore:
    spreadsheet_id: str
    worksheet_name: str
    service_account_json: str | None
    service_account_file: str | None
    request_timeout_seconds: float
    max_retries: int
    _service: object | None = None

    def append_submission(
        self,
        *,
        submitted_at_utc: str,
        submission_id: str,
        responses: list[str],
        recommendations: list[str],
        visitor_hash: str | None,
        schema_version: str,
    ) -> None:
        row = build_submission_row(
            submitted_at_utc=submitted_at_utc,
            submission_id=submission_id,
            responses=responses,
            recommendations=recommendations,
            visitor_hash=visitor_hash,
            schema_version=schema_version,
        )

        for attempt in range(self.max_retries + 1):
            try:
                self._append_row(row)
                return
            except Exception as exc:  # pragma: no cover - broad catch required for API client failures.
                is_last_attempt = attempt >= self.max_retries
                if is_last_attempt:
                    raise SubmissionStoreError("Failed to append submission to Google Sheets.") from exc
                time.sleep(0.2 * (2**attempt))

    def _append_row(self, row: list[str]) -> None:
        service = self._get_service()
        body = {"values": [row]}
        range_name = f"{self.worksheet_name}!A:Z"

        service.spreadsheets().values().append(
            spreadsheetId=self.spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body,
        ).execute()

    def _get_service(self) -> object:
        if self._service is not None:
            return self._service

        try:
            import google_auth_httplib2
            import httplib2
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise SubmissionStoreError(
                "Google Sheets dependencies are not installed. Install backend requirements."
            ) from exc

        credentials = _build_service_account_credentials(
            service_account_json=self.service_account_json,
            service_account_file=self.service_account_file,
            service_account_module=service_account,
        )

        authorized_http = google_auth_httplib2.AuthorizedHttp(
            credentials,
            http=httplib2.Http(timeout=self.request_timeout_seconds),
        )
        self._service = build("sheets", "v4", http=authorized_http, cache_discovery=False)
        return self._service


def _build_service_account_credentials(
    *,
    service_account_json: str | None,
    service_account_file: str | None,
    service_account_module: object,
) -> object:
    credentials_cls = service_account_module.Credentials

    if service_account_json:
        try:
            info = json.loads(service_account_json)
        except json.JSONDecodeError as exc:
            raise SubmissionStoreError("GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON.") from exc
        return credentials_cls.from_service_account_info(info, scopes=GOOGLE_SHEETS_SCOPES)

    if service_account_file:
        return credentials_cls.from_service_account_file(service_account_file, scopes=GOOGLE_SHEETS_SCOPES)

    raise SubmissionStoreError("Missing Google service account credentials.")


def build_submission_row(
    *,
    submitted_at_utc: str,
    submission_id: str,
    responses: list[str],
    recommendations: list[str],
    visitor_hash: str | None,
    schema_version: str,
) -> list[str]:
    response_columns = [str(response) for response in responses]
    recommendation_columns = [str(recommendation) for recommendation in recommendations[:5]]
    while len(recommendation_columns) < 5:
        recommendation_columns.append("")

    return [
        submitted_at_utc,
        submission_id,
        *response_columns,
        *recommendation_columns,
        visitor_hash or "",
        schema_version,
    ]


def build_visitor_hash(*, ip_address: str, user_agent: str | None, secret: str) -> str:
    message = f"{ip_address}|{user_agent or ''}"
    digest = hmac.new(secret.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()
    return digest[:24]


def create_submission_store(settings: Settings) -> SubmissionStore:
    if not settings.google_sheets_enabled:
        logger.info("Google Sheets submission storage is disabled.")
        return NoopSubmissionStore()

    if not settings.google_sheets_spreadsheet_id:
        logger.warning("GOOGLE_SHEETS_ENABLED is true, but GOOGLE_SHEETS_SPREADSHEET_ID is missing.")
        return NoopSubmissionStore()

    if not settings.google_service_account_json and not settings.google_service_account_file:
        logger.warning(
            "GOOGLE_SHEETS_ENABLED is true, but no service account credentials were provided "
            "(GOOGLE_SERVICE_ACCOUNT_JSON or GOOGLE_SERVICE_ACCOUNT_FILE)."
        )
        return NoopSubmissionStore()

    return GoogleSheetsSubmissionStore(
        spreadsheet_id=settings.google_sheets_spreadsheet_id,
        worksheet_name=settings.google_sheets_worksheet_name,
        service_account_json=settings.google_service_account_json,
        service_account_file=settings.google_service_account_file,
        request_timeout_seconds=settings.google_sheets_request_timeout_seconds,
        max_retries=settings.google_sheets_max_retries,
    )
