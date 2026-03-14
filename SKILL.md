---
name: plan-your-project
description: "Plan a software or research project through DISCUSS, FREEZE, and GENERATE phases, and initialize the research workspace only after an explicit generate trigger."
---

# Plan Your Project

## Overview
Build and maintain a standardized `research/` workspace for project planning, reviews, handoffs, and milestone retrospectives.
Run a strict three-phase protocol: `DISCUSS -> FREEZE -> GENERATE`.

## Run Phase Protocol
1. Enter `DISCUSS` when the user starts a new project or asks for planning support.
- Clarify goal, milestones, success criteria, constraints, and out-of-scope.
- Do not create or edit files.

2. Enter `FREEZE` after the user confirms the plan direction.
- Output a compact frozen summary containing:
  - `Goal`
  - `Milestones`
  - `Next Action`
  - `Out of Scope`
- Do not create or edit files.

3. Enter `GENERATE` only after explicit trigger phrases from the user.
- Accept triggers such as:
  - `开始初始化 research 工作区`
  - `按冻结方案生成 research 目录`
  - `落盘 research 工作区`
- Create files only in this phase.

## Generate Workspace Skeleton
Run the deterministic workspace initialization script:

```bash
python scripts/init_research_workspace.py \
  --workspace-root <workspace_root> \
  --project-slug <project_slug>
```

Legacy compatibility:

```bash
python scripts/bootstrap_research_workspace.py \
  --workspace-root <workspace_root> \
  --project-slug <project_slug>
```

Optional flags:

```bash
--dry-run
--force-overwrite
--date YYYY-MM-DD
```

## Enforce Idempotency and Safety
- Preserve existing files by default; fill missing files only.
- Overwrite existing files only when explicitly requested and `--force-overwrite` is set.
- Keep runtime artifacts out of `research/`; store them in project runtime output paths.
- Use Chinese markdown defaults (`*_zh.md`) unless the user requests another language.

## Required Skeleton Outputs
Create or ensure the following paths:
- `research/README.md`
- `research/plans/ACTIVE_PLAN.md`
- `research/plans/<project_slug>/master_plan_zh.md`
- `research/plans/session_start_prompt_zh.md`
- `research/guides/README.md`
- `research/reviews/README.md`
- `research/handoffs/README.md`
- `research/retrospectives/<project_slug>/README.md`
- `research/retrospectives/<project_slug>/TEMPLATE_retrospective_zh.md`
- `research/artifacts/tmp/.gitkeep`

## Verify After Generation
1. Confirm all required paths exist.
2. Report `created` vs `skipped` counts.
3. Confirm `ACTIVE_PLAN.md` contains required keys:
- `goal`
- `current_milestone`
- `must_read`
- `locked_decisions`
- `next_action`
- `out_of_scope`
- `latest_retrospective`
- `last_updated`

## References
- Read [references/workflow_zh.md](references/workflow_zh.md) for phase definitions and trigger policy.
- Read [references/file_contract_zh.md](references/file_contract_zh.md) for file contract and acceptance checklist.
