# Plan Your Project

`plan-your-project` is a Codex skill for planning and maintaining software or research projects that need explicit tradeoffs, milestones, and a durable handoff.

`plan-your-project` 是一个 Codex Skill，用于需要明确方案取舍、里程碑和长期交接的软件或科研项目。

## Workflow / 工作流

- **DISCUSS**: adaptively explore the goal, evidence, constraints, alternatives, risks, and milestone boundaries. No files are written.
- **FREEZE**: turn the agreed direction into a concise, reviewable plan. No files are written.
- **GENERATE**: only after an explicit user request, create the durable planning baseline.
- **MAINTAIN**: make controlled updates as work advances; preserve the plan's history and record only material decisions, milestone changes, risks, and handoffs.

默认生成的基线只有：

```text
research/
├── PLAN.md      # long-lived goal, decisions, milestones, and acceptance criteria
└── STATUS.md    # current milestone, next action, blockers, and required reading
```

Additional records are created lazily in `research/records/{decisions,reviews,retrospectives,handoffs}` when the project needs them; the skill does not create a fixed directory tree up front. Runtime outputs belong in the project's normal output locations, not in `research/`.

额外记录按需写入 `research/records/{decisions,reviews,retrospectives,handoffs}`，不预先生成固定目录树；运行产物应留在项目的常规输出目录，而不是 `research/`。

## Install / 安装

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/Cayman-Wang/plan-your-project-skill.git \
  ~/.codex/skills/plan-your-project
```

Restart or open a new Codex task after installation, then invoke `$plan-your-project` for a project-planning conversation.

安装后重启或新建 Codex 任务，再使用 `$plan-your-project` 开始项目规划。

## CLI / 命令行

The v2 initializer requires a workspace root and a plan-file source:

```bash
python scripts/init_research_workspace.py \
  --workspace-root <dir> \
  --plan-file <FILE|->
```

`--plan-file -` reads the frozen plan from standard input. Optional parameters are `--language zh|en`, `--date YYYY-MM-DD`, `--dry-run`, `--force-overwrite`, `--validate-only`, `--adopt-existing-research-dir`, and `--json`. `--validate-only` validates an existing workspace without requiring `--plan-file`.

`--plan-file` must contain strict JSON with exactly these 17 top-level keys and types:

```json
{
  "schema_version": "2.0",
  "project_name": "Example", "problem": "Manual triage is slow", "goal": "Reduce triage time",
  "success_criteria": ["Median time under 5 minutes"],
  "scope": {"in": ["Triage workflow"], "out": ["Ticket migration"]},
  "constraints": ["Use existing data"], "selected_approach": "Rank candidate owners",
  "alternatives_considered": [{"option": "Rules only", "tradeoffs": ["Lower recall"]}],
  "locked_decisions": ["Human approval remains required"],
  "milestones": [{"id": "M1", "outcome": "Baseline measured", "acceptance": ["Report reviewed"]}],
  "risks": [{"risk": "Sparse labels", "mitigation_or_validation": "Measure coverage"}],
  "assumptions": ["Owners are identifiable"], "open_questions": ["What is the SLA?"],
  "evidence": ["Triage sample"], "next_action": "Measure baseline", "freeze_readiness": "READY"
}
```

Use `--dry-run` to preview changes. After re-freeze and separate write authorization, `--force-overwrite` advances a valid v2 workspace to the next plan revision. It preserves still-valid dynamic `STATUS` values for `state`, `current_milestone`, `blockers`, and `must_read`, while `next_action` comes from the new payload; if the prior milestone no longer exists, STATUS returns to the new plan's first milestone. On a v1 workspace, `--validate-only` performs a read-only legacy check and does not migrate or rewrite it.

## v2.0.0 Breaking Changes / 破坏性变更

- The default contract is now `research/PLAN.md` and `research/STATUS.md`, replacing the v1 fixed multi-directory layout.
- Planning records are lazy rather than a required set of scaffolded files.
- v1 workspaces remain readable. v2 does not promise automatic migration or rewrite existing v1 workspaces.
- `scripts/bootstrap_research_workspace.py` is deprecated and delegates to the v2 initializer. Use `--workspace-root` and `--plan-file`; the legacy `--project-slug` parameter is ignored with a warning.

## License

MIT
