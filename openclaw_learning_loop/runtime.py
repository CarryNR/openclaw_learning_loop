"""Runtime guidance assembly for new agent tasks."""

from __future__ import annotations

from dataclasses import dataclass

from .models import ExperienceKind
from .store import ExperienceStore, RetrievalMatch, RetrievalQuery


@dataclass(frozen=True)
class RuntimeGuidance:
    """Experience snippets to inject before an agent run."""

    task: str
    matches: tuple[RetrievalMatch, ...]

    def to_markdown(self) -> str:
        if not self.matches:
            return "No relevant OpenClaw experience found for this task."

        sections = [
            "# OpenClaw Retrieved Experience",
            "",
            f"Task: {self.task}",
            "",
        ]
        sections.extend(self._section("Use These Skills", _positive_kinds()))
        sections.extend(self._section("Watch For These Failure Modes", _risk_kinds()))
        return "\n".join(sections).rstrip() + "\n"

    def _section(self, title: str, kinds: set[ExperienceKind]) -> list[str]:
        selected = [match for match in self.matches if match.asset.kind in kinds]
        if not selected:
            return []

        lines = [f"## {title}", ""]
        for index, match in enumerate(selected, start=1):
            asset = match.asset
            lines.extend(
                [
                    f"{index}. {asset.title}",
                    f"   Kind: `{asset.kind.value}` | Score: `{match.score}`",
                    f"   Why retrieved: {', '.join(match.reasons) or 'confidence match'}",
                    "",
                    _indent(asset.body),
                    "",
                ]
            )
        return lines


def build_guidance(
    task: str,
    store: ExperienceStore,
    *,
    task_type: str | None = None,
    repo_signals: tuple[str, ...] = (),
    tools: tuple[str, ...] = (),
    tags: tuple[str, ...] = (),
    limit: int = 5,
    min_score: float = 2.0,
) -> RuntimeGuidance:
    query = RetrievalQuery(
        task=task,
        task_type=task_type,
        repo_signals=repo_signals,
        tools=tools,
        tags=tags,
    )
    return RuntimeGuidance(
        task=task,
        matches=tuple(store.query(query, limit=limit, min_score=min_score)),
    )


def _positive_kinds() -> set[ExperienceKind]:
    return {ExperienceKind.SKILL_DRAFT, ExperienceKind.CHECKLIST}


def _risk_kinds() -> set[ExperienceKind]:
    return {ExperienceKind.ANTI_PATTERN, ExperienceKind.WARNING_RULE}


def _indent(text: str) -> str:
    return "\n".join(f"   {line}" if line else "" for line in text.splitlines())
