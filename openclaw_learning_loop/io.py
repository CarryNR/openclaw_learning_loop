"""JSON loading helpers for the learning loop."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import ExperienceAsset, Trajectory


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def load_trajectory(path: str | Path) -> Trajectory:
    return Trajectory.from_dict(load_json(path))


def load_experience(path: str | Path) -> ExperienceAsset:
    return ExperienceAsset.from_dict(load_json(path))


def dump_json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
