# project-research-bootstrap

一个可复用的 Codex Skill，用于在新项目中初始化标准化 `research/` 工作区，并强制执行：

- `DISCUSS`：讨论阶段，不落盘
- `FREEZE`：冻结方案摘要，不落盘
- `GENERATE`：仅在显式指令后初始化文件骨架

## 核心能力

1. 固化新项目研究工作区结构（plans/guides/reviews/handoffs/retrospectives/artifacts）。
2. 提供统一的计划入口 `ACTIVE_PLAN.md`，支持跨会话继承上下文。
3. 生成阶段复盘模板，便于持续沉淀论文和工程素材。
4. 默认幂等：重复执行只补缺失文件，不覆盖你已编辑内容（除非显式强制）。

## 目录结构（Skill 本体）

- `SKILL.md`：技能触发规则与执行流程
- `agents/openai.yaml`：UI 元信息
- `scripts/bootstrap_research_workspace.py`：初始化脚本
- `references/workflow_zh.md`：DISCUSS/FREEZE/GENERATE 工作流约束
- `references/file_contract_zh.md`：文件契约与验收清单

## 生成结果骨架

脚本会在目标工作区下生成：

- `research/README.md`
- `research/plans/ACTIVE_PLAN.md`
- `research/plans/<project_slug>/master_plan_zh.md`
- `research/plans/session_bootstrap_prompt_zh.md`
- `research/guides/README.md`
- `research/reviews/README.md`
- `research/handoffs/README.md`
- `research/retrospectives/<project_slug>/README.md`
- `research/retrospectives/<project_slug>/TEMPLATE_retrospective_zh.md`
- `research/artifacts/tmp/.gitkeep`

## 使用方法

### 1) 对话协议（给 AI 的触发语义）

- `讨论项目方案` -> 进入 DISCUSS
- `冻结当前方案` -> 进入 FREEZE
- `开始初始化 research 工作区` -> 进入 GENERATE

### 2) 脚本初始化（手动执行）

```bash
python scripts/bootstrap_research_workspace.py \
  --workspace-root <workspace_root> \
  --project-slug <project_slug>
```

常用参数：

- `--dry-run`：只预览，不写文件
- `--force-overwrite`：覆盖已有文件
- `--date YYYY-MM-DD`：指定模板日期

## 验证建议

1. 结构完整性：确认目标骨架文件全部生成。
2. 幂等性：连续运行两次，第二次应主要为 `skipped`。
3. 会话继承：新对话先读 `ACTIVE_PLAN.md`，再读 `must_read`，首条输出 `Goal / Current Milestone / Next Action`。

## 约束与约定

- 默认中文文档（`*_zh.md`）。
- 运行产物不要写入 `research/`，应放在项目运行目录（如 `outputs/`）。
- `ACTIVE_PLAN.md` 必含字段：
  - `goal`
  - `current_milestone`
  - `must_read`
  - `locked_decisions`
  - `next_action`
  - `out_of_scope`
  - `latest_retrospective`
  - `last_updated`

## License

MIT
