# Plan Your Project

`plan-your-project` is a Codex skill for planning and maintaining software or research projects with explicit tradeoffs, milestones, and durable handoffs.

`plan-your-project` 是一个 Codex Skill，用于规划和维护需要明确方案取舍、里程碑和长期交接的软件或科研项目。

## Workflow / 工作流

- **DISCUSS**: explore the goal, evidence, constraints, alternatives, risks, and milestone boundaries. No workspace files are written.
- **FREEZE**: turn the agreed direction into a concise, reviewable plan. No workspace files are written.
- **GENERATE**: create the durable planning baseline only after explicit user authorization.
- **MAINTAIN**: only after an explicit request, update status or create the requested decision, review, retrospective, or handoff record. A revised plan returns to DISCUSS and FREEZE before a separately authorized write.

正式的状态、授权和维护行为以 [SKILL.md](SKILL.md) 为准；生成文件、输入与校验契约以 [references/file_contract_zh.md](references/file_contract_zh.md) 为准。

## Workspace / 工作区

The default baseline contains only two files:

```text
research/
├── PLAN.md      # frozen goal, decisions, milestones, and acceptance criteria
└── STATUS.md    # current milestone, next action, blockers, and required reading
```

For an existing v2 workspace, start with `STATUS.md`, then read every path in `must_read`. Additional records are created only when explicitly requested under `research/records/{decisions,reviews,retrospectives,handoffs}`. No empty record directories, indexes, or placeholders are created.

Runtime outputs belong in the project's normal output locations, not in `research`. 运行产物应留在项目的常规输出目录，而不是 `research/`。

v2 工作区从 `STATUS.md` 开始；再读取 `must_read` 中列出的所有路径。决策、评审、复盘和交接记录只在明确请求时按需创建；不会预建空目录、索引或占位文件。

## Install / 安装

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/Cayman-Wang/plan-your-project-skill.git \
  ~/.codex/skills/plan-your-project
```

The default branch installs from `main`. The v2 workflow will be available from `main` once the `v2.0.0` release changes are merged; until then, propose development work through a pull request rather than treating it as an installed v2 release.

安装后重启或新建 Codex 任务，再使用 `$plan-your-project` 开始项目规划。

## CLI / 命令行

The v2 initializer requires a workspace root and a frozen plan payload:

```bash
python scripts/init_research_workspace.py \
  --workspace-root <dir> \
  --plan-file <FILE|->
```

`--plan-file` is the validated frozen payload; use `-` to read it from standard input. Use `--help` for available options, including `--validate-only` and `--dry-run`; see the [file contract](references/file_contract_zh.md) for the payload schema, validation rules, and workspace behavior.

## v2.0.0 Breaking Changes / 破坏性变更

- The default contract is `research/PLAN.md` and `research/STATUS.md`, replacing the v1 fixed multi-directory layout.
- Planning records are lazy rather than scaffolded as a required file set.
- v1 workspaces remain readable. v2 does not promise automatic migration or rewrite existing v1 workspaces.
- `scripts/bootstrap_research_workspace.py` is deprecated compatibility support. Use `scripts/init_research_workspace.py` with `--workspace-root` and `--plan-file` for v2.

## License

MIT
