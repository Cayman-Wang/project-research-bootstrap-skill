# v2 工作区契约

## 范围、布局与入口

v2 默认只生成 `research/PLAN.md` 和 `research/STATUS.md`。使用 `scripts/init_research_workspace.py --workspace-root <root> --plan-file <plan.json>` 生成或校验这两个文件；`bootstrap_research_workspace.py` 仅为 deprecated 兼容入口，不属于 v2 流程。

检测到任一真实旧标记时，布局为 v1：`research/plans/ACTIVE_PLAN.md`、`research/plans/<slug>/master_plan_zh.md`、`research/plans/session_start_prompt_zh.md` 或 `research/plans/session_bootstrap_prompt_zh.md`。v1 保持只读；v1 与任一 v2 记录共存时，布局为 mixed，同样拒绝写入。仅有 PLAN 或 STATUS 的 v2 partial layout 为 invalid，拒绝写入。v2 不提供迁移；不要请求迁移决定，也不要在这些布局写入。

## 严格 JSON 输入

`--plan-file`（或 stdin `-`）必须是单个 JSON object，键必须恰好如下。数组项的每个 string 必须非空；`freeze_readiness` 只能是 `READY` 或 `READY_WITH_ASSUMPTIONS`。

```json
{
  "schema_version": "2.0",
  "project_name": "...",
  "problem": "...",
  "goal": "...",
  "success_criteria": ["..."],
  "scope": {"in": ["..."], "out": ["..."]},
  "constraints": ["..."],
  "selected_approach": "...",
  "alternatives_considered": [{"option": "...", "tradeoffs": ["..."]}],
  "locked_decisions": ["..."],
  "milestones": [{"id": "M1", "outcome": "...", "acceptance": ["..."]}],
  "risks": [{"risk": "...", "mitigation_or_validation": "..."}],
  "assumptions": ["..."],
  "open_questions": ["..."],
  "evidence": ["..."],
  "next_action": "...",
  "freeze_readiness": "READY"
}
```

`success_criteria`、`locked_decisions`、`scope.in`、`alternatives_considered` 和 `milestones` 必须各有至少一项；每个 milestone 的 `acceptance` 也必须非空。`scope.out`、`constraints`、`risks`、`assumptions`、`open_questions`、`evidence` 以及 alternative 的 `tradeoffs` 可为空数组；对象一旦存在，其 string 字段必须非空。`READY_WITH_ASSUMPTIONS` 是例外：此时 `assumptions` 必须非空且已获用户接受。

`schema_version` 必须为 `"2.0"`；`scope`、`alternatives_considered`、`milestones` 和 `risks` 中的对象不得有额外或缺失键。每个 milestone `id` 必须匹配 `^[A-Za-z0-9][A-Za-z0-9._-]*$` 且在计划内唯一。Standard 讨论必须把至少一个非选定路径映射为 `alternatives_considered` 项。仍需独立的 GENERATE 写入授权。

## Markdown 输出

生成器将 JSON 映射为 Markdown YAML frontmatter 加正文。frontmatter 是严格 metadata，正文保存可读的冻结计划或动态状态；不要把 JSON 原样嵌入输出。

`PLAN.md` frontmatter 必须恰好包含：

```yaml
workspace_format: plan-your-project/v2
record: PLAN
plan_revision: 1
language: zh
frozen_at: YYYY-MM-DD
```

PLAN 正文必须覆盖 JSON 中的项目名、问题、目标、成功标准、范围、约束、方案、替代项、锁定决策、里程碑及验收、风险、假设、开放问题、证据、下一步与冻结就绪度。`plan_revision` 是正整数。PLAN 只能通过 DISCUSS、FREEZE、用户确认 re-freeze、再获明确写入授权后修改；每次 re-freeze 递增 `plan_revision`。

`STATUS.md` frontmatter 必须恰好包含：

```yaml
workspace_format: plan-your-project/v2
record: STATUS
plan_revision: 1
state: planned
current_milestone: M1
last_updated: YYYY-MM-DD
```

`state` 只能是 `planned`、`in_progress`、`blocked` 或 `complete`。STATUS 正文必须链接 `PLAN.md`，并只包含 `next_action`、`blockers`、`must_read` 等动态执行信息。不得复制 goal 或其他冻结计划内容。只有明确的 MAINTAIN 意图可以更新 STATUS；STATUS 更新不得改变 PLAN 的决策。

## Lazy Records

`research/records/decisions/`、`research/records/reviews/`、`research/records/retrospectives/`、`research/records/handoffs/` 均为 lazy records：仅在用户明确请求对应记录时创建。

- decision：记录 PLAN 之外需要追溯的单项决策、依据与影响。
- review：记录对实现、证据或里程碑结果的审查结论与待办。
- retrospective：记录阶段结果、验证、局限和后续改进。
- handoff：记录下一位执行者所需的当前状态、上下文和下一动作。

每个文件命名为 `research/records/<kind>/YYYY-MM-DD-<slug>.md`；语言由内容决定，不强制写入文件名。不创建 README、索引、占位文件或其他模板。现有复盘模板仅在用户明确请求复盘时按需复制。

## 验收

- 默认 GENERATE 只创建 PLAN 与 STATUS 两个文件。
- JSON 输入、CLI 参数与 PLAN 正文数据一致；两份 Markdown frontmatter 满足各自 metadata 契约。
- STATUS 有效链接到 PLAN，`plan_revision` 与 PLAN 相同，`current_milestone` 是 PLAN 中的里程碑。
- 生成的 PLAN、STATUS 和 lazy record 不含 `TODO`、`TBD` 或 `<placeholder>` 等未解析占位符。
- v1 和 mixed 布局均未被写入。
