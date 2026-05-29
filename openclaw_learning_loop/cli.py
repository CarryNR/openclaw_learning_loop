"""Command line interface for OpenClaw Learning Loop."""

from __future__ import annotations

import argparse
import sys

from .distill import ExperienceDistiller
from .io import dump_json, load_trajectory
from .runtime import build_guidance
from .store import ExperienceStore


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.handler(args)
    except Exception as error:  # pragma: no cover - argparse path
        print(f"error: {error}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="openclaw-loop",
        description="Compile OpenClaw task trajectories into reusable guidance.",
    )
    subcommands = parser.add_subparsers(required=True)

    validate = subcommands.add_parser(
        "validate-trajectory", help="Validate and normalize a trajectory JSON file."
    )
    validate.add_argument("trajectory")
    validate.set_defaults(handler=_validate_trajectory)

    distill = subcommands.add_parser(
        "distill", help="Distill a trajectory into experience assets."
    )
    distill.add_argument("trajectory")
    distill.add_argument(
        "--store",
        default=None,
        help="Optional JSONL path to append generated assets.",
    )
    distill.add_argument(
        "--json",
        action="store_true",
        help="Print assets as JSON instead of a compact summary.",
    )
    distill.set_defaults(handler=_distill)

    retrieve = subcommands.add_parser(
        "retrieve", help="Retrieve guidance for a new task from an experience store."
    )
    retrieve.add_argument("--task", required=True)
    retrieve.add_argument("--store", default=".openclaw/experiences.jsonl")
    retrieve.add_argument("--task-type", default=None)
    retrieve.add_argument("--repo-signal", action="append", default=[])
    retrieve.add_argument("--tool", action="append", default=[])
    retrieve.add_argument("--tag", action="append", default=[])
    retrieve.add_argument("--limit", type=int, default=5)
    retrieve.add_argument("--min-score", type=float, default=2.0)
    retrieve.set_defaults(handler=_retrieve)

    return parser


def _validate_trajectory(args: argparse.Namespace) -> int:
    trajectory = load_trajectory(args.trajectory)
    print(dump_json(trajectory.to_dict()))
    return 0


def _distill(args: argparse.Namespace) -> int:
    trajectory = load_trajectory(args.trajectory)
    assets = ExperienceDistiller().distill(trajectory)

    if args.store:
        ExperienceStore(args.store).add_many(assets)

    if args.json:
        print(dump_json({"assets": [asset.to_dict() for asset in assets]}))
        return 0

    for asset in assets:
        print(f"{asset.kind.value}: {asset.title}")
    return 0


def _retrieve(args: argparse.Namespace) -> int:
    guidance = build_guidance(
        args.task,
        ExperienceStore(args.store),
        task_type=args.task_type,
        repo_signals=tuple(args.repo_signal),
        tools=tuple(args.tool),
        tags=tuple(args.tag),
        limit=args.limit,
        min_score=args.min_score,
    )
    print(guidance.to_markdown())
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
