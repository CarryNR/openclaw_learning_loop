# OpenClaw Learning Loop

OpenClaw Learning Loop is a lightweight experience compiler for agent systems.
It turns real task trajectories into reusable skills, checklists, anti-patterns,
and warning rules, then retrieves the most relevant experience before the next
agent run.

The goal is to help OpenClaw become smarter over time without starting from a
large training system or platform UI.

## MVP Shape

The first release is intentionally small:

- `spec/` defines the trajectory and experience JSON schemas.
- `openclaw_learning_loop/models.py` provides typed Python dataclasses.
- `openclaw_learning_loop/distill.py` compiles successful and failed runs into
  reusable experience assets.
- `openclaw_learning_loop/store.py` stores assets in JSONL and retrieves them
  with structured relevance scoring.
- `openclaw_learning_loop/runtime.py` renders retrieved assets as agent-ready
  Markdown guidance.
- `openclaw_learning_loop/cli.py` exposes the loop as a command line tool.

## Quick Start

Validate a trajectory:

```bash
python -m openclaw_learning_loop.cli validate-trajectory examples/success_task.json
```

Distill a trajectory into experience assets:

```bash
python -m openclaw_learning_loop.cli distill examples/success_task.json --json
```

Append assets to a local store:

```bash
python -m openclaw_learning_loop.cli distill examples/success_task.json --store .openclaw/experiences.jsonl
python -m openclaw_learning_loop.cli distill examples/failure_task.json --store .openclaw/experiences.jsonl
```

Retrieve guidance for a new task:

```bash
python -m openclaw_learning_loop.cli retrieve \
  --task "Bootstrap a Python CLI MVP without losing scope" \
  --task-type project_bootstrap \
  --repo-signal python \
  --repo-signal cli \
  --tag mvp
```

## Trajectory Outcomes

Successful trajectories produce:

- `skill_draft`: a reusable procedure extracted from the task.
- `checklist`: a compact verification list for similar future work.

Failed trajectories produce:

- `anti_pattern`: a documented failure mode with observed signals.
- `warning_rule`: a short runtime warning and recovery instruction.

## Why This Is Not Another Agent Wrapper

The package does not decide how an agent should think in general. Instead, it
captures what worked or failed in specific tasks and turns that history into
reviewable, retrievable assets. That keeps the intelligence layer inspectable
and makes it possible for an open-source community to contribute experience
without contributing opaque model weights.

## Run Tests

The test suite uses only the Python standard library plus `pytest` if available:

```bash
python -m pytest
```

If `pytest` is not installed, the package modules can still be exercised through
the CLI examples above.
