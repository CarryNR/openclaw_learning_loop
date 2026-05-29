"""Core schemas for task trajectories and reusable experience assets."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


class Outcome(str, Enum):
    """Final task outcome."""

    SUCCESS = "success"
    FAILURE = "failure"


class ExperienceKind(str, Enum):
    """Kinds of intelligence assets produced by the learning loop."""

    SKILL_DRAFT = "skill_draft"
    CHECKLIST = "checklist"
    ANTI_PATTERN = "anti_pattern"
    WARNING_RULE = "warning_rule"


@dataclass(frozen=True)
class ToolCall:
    """A tool invocation that materially affected the task."""

    name: str
    purpose: str
    result: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ToolCall":
        return cls(
            name=_required_str(data, "name"),
            purpose=_required_str(data, "purpose"),
            result=_optional_str(data, "result"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {"name": self.name, "purpose": self.purpose, "result": self.result}


@dataclass(frozen=True)
class TrajectoryStep:
    """A decision or action in the task trace."""

    summary: str
    evidence: str | None = None
    tool: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrajectoryStep":
        return cls(
            summary=_required_str(data, "summary"),
            evidence=_optional_str(data, "evidence"),
            tool=_optional_str(data, "tool"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {"summary": self.summary, "evidence": self.evidence, "tool": self.tool}


@dataclass(frozen=True)
class Trajectory:
    """Minimal record of an agent task run.

    A trajectory should be small enough to review by humans, but structured
    enough to compile into reusable agent guidance.
    """

    goal: str
    outcome: Outcome
    context_summary: str
    task_type: str
    steps: tuple[TrajectoryStep, ...]
    repo_signals: tuple[str, ...] = ()
    tool_calls: tuple[ToolCall, ...] = ()
    result_summary: str | None = None
    failure_reason: str | None = None
    human_fix: str | None = None
    tags: tuple[str, ...] = ()
    id: str = field(default_factory=lambda: f"traj_{uuid4().hex[:12]}")
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        if not self.goal.strip():
            raise ValueError("trajectory goal is required")
        if not self.context_summary.strip():
            raise ValueError("trajectory context_summary is required")
        if not self.task_type.strip():
            raise ValueError("trajectory task_type is required")
        if not self.steps:
            raise ValueError("trajectory must include at least one step")
        if self.outcome is Outcome.SUCCESS and not self.result_summary:
            raise ValueError("successful trajectories require result_summary")
        if self.outcome is Outcome.FAILURE and not self.failure_reason:
            raise ValueError("failed trajectories require failure_reason")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Trajectory":
        return cls(
            id=_optional_str(data, "id") or f"traj_{uuid4().hex[:12]}",
            created_at=_optional_str(data, "created_at")
            or datetime.now(timezone.utc).isoformat(),
            goal=_required_str(data, "goal"),
            outcome=Outcome(_required_str(data, "outcome")),
            context_summary=_required_str(data, "context_summary"),
            task_type=_required_str(data, "task_type"),
            repo_signals=tuple(_str_list(data.get("repo_signals", []), "repo_signals")),
            steps=tuple(TrajectoryStep.from_dict(item) for item in data.get("steps", [])),
            tool_calls=tuple(
                ToolCall.from_dict(item) for item in data.get("tool_calls", [])
            ),
            result_summary=_optional_str(data, "result_summary"),
            failure_reason=_optional_str(data, "failure_reason"),
            human_fix=_optional_str(data, "human_fix"),
            tags=tuple(_str_list(data.get("tags", []), "tags")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "goal": self.goal,
            "outcome": self.outcome.value,
            "context_summary": self.context_summary,
            "task_type": self.task_type,
            "repo_signals": list(self.repo_signals),
            "steps": [step.to_dict() for step in self.steps],
            "tool_calls": [call.to_dict() for call in self.tool_calls],
            "result_summary": self.result_summary,
            "failure_reason": self.failure_reason,
            "human_fix": self.human_fix,
            "tags": list(self.tags),
        }


@dataclass(frozen=True)
class ExperienceAsset:
    """A human-reviewable, machine-retrievable piece of agent experience."""

    kind: ExperienceKind
    title: str
    body: str
    source_trajectory_id: str
    task_type: str
    tags: tuple[str, ...] = ()
    repo_signals: tuple[str, ...] = ()
    tools: tuple[str, ...] = ()
    confidence: float = 0.75
    id: str = field(default_factory=lambda: f"exp_{uuid4().hex[:12]}")
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def __post_init__(self) -> None:
        if not self.title.strip():
            raise ValueError("experience title is required")
        if not self.body.strip():
            raise ValueError("experience body is required")
        if not 0 <= self.confidence <= 1:
            raise ValueError("experience confidence must be between 0 and 1")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ExperienceAsset":
        return cls(
            id=_optional_str(data, "id") or f"exp_{uuid4().hex[:12]}",
            created_at=_optional_str(data, "created_at")
            or datetime.now(timezone.utc).isoformat(),
            kind=ExperienceKind(_required_str(data, "kind")),
            title=_required_str(data, "title"),
            body=_required_str(data, "body"),
            source_trajectory_id=_required_str(data, "source_trajectory_id"),
            task_type=_required_str(data, "task_type"),
            tags=tuple(_str_list(data.get("tags", []), "tags")),
            repo_signals=tuple(_str_list(data.get("repo_signals", []), "repo_signals")),
            tools=tuple(_str_list(data.get("tools", []), "tools")),
            confidence=float(data.get("confidence", 0.75)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "created_at": self.created_at,
            "kind": self.kind.value,
            "title": self.title,
            "body": self.body,
            "source_trajectory_id": self.source_trajectory_id,
            "task_type": self.task_type,
            "tags": list(self.tags),
            "repo_signals": list(self.repo_signals),
            "tools": list(self.tools),
            "confidence": self.confidence,
        }


def _required_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} is required")
    return value


def _optional_str(data: dict[str, Any], key: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{key} must be a string")
    return value


def _str_list(value: Any, key: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list of strings")
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{key} must be a list of non-empty strings")
    return value
