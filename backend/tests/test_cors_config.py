from app.main import parse_cors_origins


def test_parse_cors_origins_defaults_to_localhost() -> None:
    assert parse_cors_origins(None) == ["http://localhost:3000"]


def test_parse_cors_origins_supports_comma_separated_values() -> None:
    origins = parse_cors_origins("https://ccd-lxd.vercel.app/, https://staging.example.com")

    assert origins == ["https://ccd-lxd.vercel.app", "https://staging.example.com"]


def test_parse_cors_origins_strips_quotes_from_values() -> None:
    origins = parse_cors_origins("\"https://ccd-lxd.vercel.app\"")

    assert origins == ["https://ccd-lxd.vercel.app"]


def test_parse_cors_origins_supports_json_array_format() -> None:
    origins = parse_cors_origins("[\"https://ccd-lxd.vercel.app\", \"https://preview.example.com\"]")

    assert origins == ["https://ccd-lxd.vercel.app", "https://preview.example.com"]
