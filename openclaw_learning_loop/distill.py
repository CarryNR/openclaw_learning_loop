"""Compile trajectories into reusable agent guidance."""

from __future__ import annotations

from .models import ExperienceAsset, ExperienceKind, Outcome, Trajectory


class ExperienceDistiller:
    """Deterministic MVP distiller for success and failure trajectories.

    The first release keeps distillation explainable: every generated asset
    points back to concrete trajectory fields instead of relying on opaque model
    output.
    """

    def distill(self, trajectory: Trajectory) -> list[ExperienceAsset]:
        if trajectory.outcome is Outcome.SUCCESS:
            return [
                self._skill_draft(trajectory),
                self._checklist(trajectory),
            ]
        return [
            self._anti_pattern(trajectory),
            self._warning_rule(trajectory),
        ]

    def _skill_draft(self, trajectory: Trajectory) -> ExperienceAsset:
        body = "\n".join(
            [
                f"Use this when: {trajectory.context_summary}",
                "",
                "Procedure:",
                *_numbered(step.summary for step in trajectory.steps),
                "",
                f"Expected result: {trajectory.result_summary}",
            ]
        )
        return self._asset(
            trajectory,
            ExperienceKind.SKILL_DRAFT,
            f"Skill draft: {trajectory.goal}",
            body,
            confidence=0.78,
        )

    def _checklist(self, trajectory: Trajectory) -> ExperienceAsset:
        items = [f"- {step.summary}" for step in trajectory.steps]
        if trajectory.result_summary:
            items.append(f"- Verify result: {trajectory.result_summary}")
        body = "\n".join(items)
        return self._asset(
            trajectory,
            ExperienceKind.CHECKLIST,
            f"Checklist: {trajectory.task_type}",
            body,
            confidence=0.82,
        )

    def _anti_pattern(self, trajectory: Trajectory) -> ExperienceAsset:
        evidence = [
            f"- {step.summary}" + (f" Evidence: {step.evidence}" if step.evidence else "")
            for step in trajectory.steps
        ]
        body = "\n".join(
            [
                f"Failure mode: {trajectory.failure_reason}",
                "",
                "Observed signals:",
                *evidence,
                "",
                f"Recovery: {trajectory.human_fix or 'Stop, narrow scope, and retry.'}",
            ]
        )
        return self._asset(
            trajectory,
            ExperienceKind.ANTI_PATTERN,
            f"Avoid: {trajectory.goal}",
            body,
            confidence=0.84,
        )

    def _warning_rule(self, trajectory: Trajectory) -> ExperienceAsset:
        body = "\n".join(
            [
                f"When working on `{trajectory.task_type}`, watch for this risk:",
                f"{trajectory.failure_reason}",
                "",
                f"If detected, do this first: {trajectory.human_fix or 'Ask for scope clarification.'}",
            ]
        )
        return self._asset(
            trajectory,
            ExperienceKind.WARNING_RULE,
            f"Warning rule: {trajectory.task_type}",
            body,
            confidence=0.8,
        )

    def _asset(
        self,
        trajectory: Trajectory,
        kind: ExperienceKind,
        title: str,
        body: str,
        confidence: float,
    ) -> ExperienceAsset:
        return ExperienceAsset(
            kind=kind,
            title=title,
            body=body,
            source_trajectory_id=trajectory.id,
            task_type=trajectory.task_type,
            tags=_unique((*trajectory.tags, trajectory.task_type, kind.value)),
            repo_signals=trajectory.repo_signals,
            tools=_unique(call.name for call in trajectory.tool_calls),
            confidence=confidence,
        )


def _numbered(items: list[str] | tuple[str, ...] | object) -> list[str]:
    return [f"{index}. {item}" for index, item in enumerate(items, start=1)]


def _unique(items: object) -> tuple[str, ...]:
    seen: set[str] = set()
    values: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            values.append(item)
    return tuple(values)
