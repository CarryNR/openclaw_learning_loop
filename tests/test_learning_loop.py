from pathlib import Path

from openclaw_learning_loop.cli import main
from openclaw_learning_loop.distill import ExperienceDistiller
from openclaw_learning_loop.io import load_trajectory
from openclaw_learning_loop.models import ExperienceKind
from openclaw_learning_loop.runtime import build_guidance
from openclaw_learning_loop.store import ExperienceStore


ROOT = Path(__file__).resolve().parents[1]


def test_success_trajectory_distills_to_skill_and_checklist() -> None:
    trajectory = load_trajectory(ROOT / "examples" / "success_task.json")

    assets = ExperienceDistiller().distill(trajectory)

    assert [asset.kind for asset in assets] == [
        ExperienceKind.SKILL_DRAFT,
        ExperienceKind.CHECKLIST,
    ]
    assert all(asset.source_trajectory_id == trajectory.id for asset in assets)


def test_failure_trajectory_distills_to_anti_pattern_and_warning() -> None:
    trajectory = load_trajectory(ROOT / "examples" / "failure_task.json")

    assets = ExperienceDistiller().distill(trajectory)

    assert [asset.kind for asset in assets] == [
        ExperienceKind.ANTI_PATTERN,
        ExperienceKind.WARNING_RULE,
    ]
    assert "scope" in assets[0].body.lower()


def test_store_retrieves_relevant_experience(tmp_path: Path) -> None:
    store = ExperienceStore(tmp_path / "experiences.jsonl")
    success = load_trajectory(ROOT / "examples" / "success_task.json")
    failure = load_trajectory(ROOT / "examples" / "failure_task.json")
    store.add_many(ExperienceDistiller().distill(success))
    store.add_many(ExperienceDistiller().distill(failure))

    guidance = build_guidance(
        "Bootstrap a Python CLI MVP without losing scope",
        store,
        task_type="project_bootstrap",
        repo_signals=("python", "cli"),
        tags=("mvp", "scope"),
    )

    rendered = guidance.to_markdown()
    assert "Use These Skills" in rendered
    assert "Watch For These Failure Modes" in rendered
    assert "scope" in rendered.lower()


def test_cli_distill_and_retrieve_roundtrip(tmp_path: Path, capsys) -> None:
    store_path = tmp_path / "experiences.jsonl"

    distill_code = main(
        [
            "distill",
            str(ROOT / "examples" / "success_task.json"),
            "--store",
            str(store_path),
        ]
    )
    assert distill_code == 0

    retrieve_code = main(
        [
            "retrieve",
            "--task",
            "Create the first schema for a Python CLI project",
            "--task-type",
            "project_bootstrap",
            "--repo-signal",
            "python",
            "--store",
            str(store_path),
        ]
    )

    assert retrieve_code == 0
    output = capsys.readouterr().out
    assert "OpenClaw Retrieved Experience" in output
