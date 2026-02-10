from pathlib import Path

from app import data_loader


def test_questions_path_prefers_backend_data_directory() -> None:
    expected_path = (Path(__file__).resolve().parents[1] / "data" / "questions.json").resolve()

    assert data_loader.QUESTIONS_PATH.resolve() == expected_path
    assert data_loader.QUESTIONS_PATH.exists()


def test_required_data_files_exist() -> None:
    assert data_loader.ORDER_PATH.exists()
    assert data_loader.DESCRIPTIONS_PATH.exists()
