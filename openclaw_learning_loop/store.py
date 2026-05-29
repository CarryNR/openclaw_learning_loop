"""File-backed experience storage and retrieval."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .models import ExperienceAsset


@dataclass(frozen=True)
class RetrievalQuery:
    """Signals available before a new agent run starts."""

    task: str
    task_type: str | None = None
    repo_signals: tuple[str, ...] = ()
    tools: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class RetrievalMatch:
    asset: ExperienceAsset
    score: float
    reasons: tuple[str, ...]


class ExperienceStore:
    """Append-friendly JSONL store for MVP deployments."""

    def __init__(self, path: str | Path = ".openclaw/experiences.jsonl") -> None:
        self.path = Path(path)

    def add(self, asset: ExperienceAsset) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asset.to_dict(), ensure_ascii=False, sort_keys=True))
            handle.write("\n")

    def add_many(self, assets: list[ExperienceAsset]) -> None:
        for asset in assets:
            self.add(asset)

    def all(self) -> list[ExperienceAsset]:
        if not self.path.exists():
            return []

        assets: list[ExperienceAsset] = []
        with self.path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    assets.append(ExperienceAsset.from_dict(json.loads(line)))
                except (json.JSONDecodeError, ValueError) as error:
                    raise ValueError(
                        f"Invalid experience record at {self.path}:{line_number}: {error}"
                    ) from error
        return assets

    def query(
        self,
        query: RetrievalQuery,
        *,
        limit: int = 5,
        min_score: float = 2.0,
    ) -> list[RetrievalMatch]:
        matches = [
            match
            for asset in self.all()
            if (match := score_asset(asset, query)).score >= min_score
        ]
        matches.sort(key=lambda item: item.score, reverse=True)
        return matches[:limit]


def score_asset(asset: ExperienceAsset, query: RetrievalQuery) -> RetrievalMatch:
    score = 0.0
    reasons: list[str] = []
    query_terms = _terms(query.task)

    if query.task_type and query.task_type == asset.task_type:
        score += 3.0
        reasons.append(f"same task_type `{query.task_type}`")

    repo_overlap = set(query.repo_signals) & set(asset.repo_signals)
    if repo_overlap:
        score += 1.5 * len(repo_overlap)
        reasons.append("repo signals: " + ", ".join(sorted(repo_overlap)))

    tool_overlap = set(query.tools) & set(asset.tools)
    if tool_overlap:
        score += 1.0 * len(tool_overlap)
        reasons.append("tools: " + ", ".join(sorted(tool_overlap)))

    tag_overlap = set(query.tags) & set(asset.tags)
    if tag_overlap:
        score += 1.25 * len(tag_overlap)
        reasons.append("tags: " + ", ".join(sorted(tag_overlap)))

    text_terms = _terms(" ".join([asset.title, asset.body, " ".join(asset.tags)]))
    term_overlap = query_terms & text_terms
    if term_overlap:
        capped = min(len(term_overlap), 4)
        score += 0.5 * capped
        reasons.append("text overlap: " + ", ".join(sorted(term_overlap)[:4]))

    score *= asset.confidence
    return RetrievalMatch(asset=asset, score=round(score, 3), reasons=tuple(reasons))


def _terms(text: str) -> set[str]:
    normalized = "".join(
        character.lower() if character.isalnum() else " " for character in text
    )
    return {term for term in normalized.split() if len(term) >= 3}
