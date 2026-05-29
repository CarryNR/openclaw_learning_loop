# OpenClaw Learning Loop

## 中文说明

OpenClaw Learning Loop 是一个面向 agent 系统的轻量级“经验编译器”。它会把真实任务执行轨迹转化为可复用的 `skill`、`checklist`、`anti-pattern` 和 `warning rule`，并在后续相似任务开始前召回最相关的经验，帮助 OpenClaw 越用越聪明。

这个项目的重点不是再做一个 agent 聊天壳子，而是把成功经验和失败教训沉淀成可审查、可分享、可机器读取的智能资产。第一版刻意保持简单，只验证“轨迹输入 -> 经验蒸馏 -> 存储 -> 运行时召回”的闭环。

### MVP 结构

- `spec/`：定义任务轨迹和经验资产的 JSON schema。
- `openclaw_learning_loop/models.py`：提供核心 Python 数据模型。
- `openclaw_learning_loop/distill.py`：把成功/失败轨迹蒸馏成经验资产。
- `openclaw_learning_loop/store.py`：用 JSONL 存储经验，并基于任务类型、标签、工具和文本重叠做召回。
- `openclaw_learning_loop/runtime.py`：把召回结果渲染成可注入 agent 的 Markdown guidance。
- `openclaw_learning_loop/cli.py`：提供命令行入口，方便本地验证闭环。

### 快速开始

校验一条任务轨迹：

```bash
python -m openclaw_learning_loop.cli validate-trajectory examples/success_task.json
```

把轨迹蒸馏成经验资产：

```bash
python -m openclaw_learning_loop.cli distill examples/success_task.json --json
```

把成功和失败样例写入本地经验库：

```bash
python -m openclaw_learning_loop.cli distill examples/success_task.json --store .openclaw/experiences.jsonl
python -m openclaw_learning_loop.cli distill examples/failure_task.json --store .openclaw/experiences.jsonl
```

为一个新任务召回经验：

```bash
python -m openclaw_learning_loop.cli retrieve \
  --task "Bootstrap a Python CLI MVP without losing scope" \
  --task-type project_bootstrap \
  --repo-signal python \
  --repo-signal cli \
  --tag mvp
```

### 轨迹会产出什么

成功轨迹会产出：

- `skill_draft`：从任务中提炼出的可复用执行步骤。
- `checklist`：用于相似任务的简洁检查清单。

失败轨迹会产出：

- `anti_pattern`：带有观察信号和修复方式的失败模式。
- `warning_rule`：运行时可注入的风险提醒和恢复建议。

### 运行测试

```bash
python -m pytest
```

如果没有安装 `pytest`，也可以先通过上面的 CLI 示例手动验证核心流程。

## English

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
