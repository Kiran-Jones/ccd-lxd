from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BACKEND_DIR / "data"
LEGACY_ROOT_DIR = Path(__file__).resolve().parents[2]


def resolve_data_path(filename: str) -> Path:
    candidates = (
        DATA_DIR / filename,
        LEGACY_ROOT_DIR / filename,
    )

    for path in candidates:
        if path.exists():
            return path

    searched_paths = ", ".join(str(path) for path in candidates)
    raise FileNotFoundError(f"Missing required data file '{filename}'. Checked: {searched_paths}")


QUESTIONS_PATH = resolve_data_path("questions.json")
ORDER_PATH = resolve_data_path("order.csv")
DESCRIPTIONS_PATH = resolve_data_path("descriptions.txt")


@dataclass(frozen=True)
class Question:
    statement: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class Activity:
    code: str
    name: str
    phase: str
    prerequisite: str


_CODE_PATTERN = re.compile(r"\(([A-Z]+)\)")


def _split_activity_name(raw_name: str) -> tuple[str, str]:
    code_match = _CODE_PATTERN.search(raw_name)
    if not code_match:
        raise ValueError(f"Could not extract activity code from: {raw_name}")

    code = code_match.group(1)
    name = raw_name[: code_match.start()].strip()
    return name, code


@lru_cache(maxsize=1)
def load_questions() -> tuple[Question, ...]:
    raw = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))
    return tuple(Question(statement=item["statement"], tags=tuple(item["tags"])) for item in raw)


@lru_cache(maxsize=1)
def load_activities() -> tuple[Activity, ...]:
    activities: list[Activity] = []
    with ORDER_PATH.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file, skipinitialspace=True)
        for row in reader:
            normalized_row = {key.strip(): (value or "").strip() for key, value in row.items()}
            raw_name = normalized_row["Activity"]
            name, code = _split_activity_name(raw_name)
            activities.append(
                Activity(
                    code=code,
                    name=name,
                    phase=normalized_row["Phase"],
                    prerequisite=normalized_row["Prerequisite"].strip("`"),
                )
            )
    return tuple(activities)


@lru_cache(maxsize=1)
def load_activity_descriptions() -> dict[str, str]:
    text = DESCRIPTIONS_PATH.read_text(encoding="utf-8")

    descriptions = {
        "VAL": "Clarifies your core career values so decisions align with what matters most.",
        "STR": "Identifies natural strengths you can build into confident career direction.",
        "SKL": "Helps you name transferable skills and gaps from your experiences.",
        "NRG": "Tracks what energizes or drains you to ground decisions in daily reality.",
        "AI": "Uses guided reflection to generate career pathways from your self-knowledge.",
        "MM": "Expands possibilities through structured, creative exploration of pathways.",
        "DM": "Compares options across practical factors to support clear decisions.",
    }

    # Keep a light dependency on source content so failures are obvious if the file goes missing.
    if "The Activity Library" not in text:
        raise ValueError("descriptions.txt format looks unexpected")

    return descriptions
