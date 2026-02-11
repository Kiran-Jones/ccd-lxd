import os
from dataclasses import dataclass


DEFAULT_WORKSHEET_NAME = "Submissions"
DEFAULT_REQUEST_TIMEOUT_SECONDS = 5.0
DEFAULT_MAX_RETRIES = 2
DEFAULT_SCHEMA_VERSION = "v1"


def _parse_bool(raw_value: str | None, *, default: bool = False) -> bool:
    if raw_value is None:
        return default

    normalized = raw_value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    return default


def _parse_float(raw_value: str | None, *, default: float) -> float:
    if raw_value is None or raw_value.strip() == "":
        return default
    try:
        parsed = float(raw_value)
    except ValueError:
        return default
    return parsed if parsed > 0 else default


def _parse_int(raw_value: str | None, *, default: int) -> int:
    if raw_value is None or raw_value.strip() == "":
        return default
    try:
        parsed = int(raw_value)
    except ValueError:
        return default
    return parsed if parsed >= 0 else default


@dataclass(frozen=True)
class Settings:
    google_sheets_enabled: bool
    google_sheets_spreadsheet_id: str | None
    google_sheets_worksheet_name: str
    google_service_account_json: str | None
    google_service_account_file: str | None
    google_sheets_request_timeout_seconds: float
    google_sheets_max_retries: int
    enable_visitor_hash: bool
    visitor_hash_secret: str | None
    schema_version: str


def load_settings_from_env() -> Settings:
    worksheet_name = (os.getenv("GOOGLE_SHEETS_WORKSHEET_NAME") or "").strip() or DEFAULT_WORKSHEET_NAME

    spreadsheet_id = (os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID") or "").strip() or None
    service_account_json = (os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON") or "").strip() or None
    service_account_file = (os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE") or "").strip() or None
    visitor_hash_secret = (os.getenv("VISITOR_HASH_SECRET") or "").strip() or None
    schema_version = (os.getenv("SUBMISSION_SCHEMA_VERSION") or "").strip() or DEFAULT_SCHEMA_VERSION

    return Settings(
        google_sheets_enabled=_parse_bool(os.getenv("GOOGLE_SHEETS_ENABLED"), default=False),
        google_sheets_spreadsheet_id=spreadsheet_id,
        google_sheets_worksheet_name=worksheet_name,
        google_service_account_json=service_account_json,
        google_service_account_file=service_account_file,
        google_sheets_request_timeout_seconds=_parse_float(
            os.getenv("GOOGLE_SHEETS_REQUEST_TIMEOUT_SECONDS"),
            default=DEFAULT_REQUEST_TIMEOUT_SECONDS,
        ),
        google_sheets_max_retries=_parse_int(
            os.getenv("GOOGLE_SHEETS_MAX_RETRIES"),
            default=DEFAULT_MAX_RETRIES,
        ),
        enable_visitor_hash=_parse_bool(os.getenv("ENABLE_VISITOR_HASH"), default=False),
        visitor_hash_secret=visitor_hash_secret,
        schema_version=schema_version,
    )
