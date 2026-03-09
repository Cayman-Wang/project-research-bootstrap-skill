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

## 安装说明

### 1) 克隆到 Codex skills 目录（推荐）

```bash
mkdir -p ~/.codex/skills
git clone git@github.com:Cayman-Wang/project-research-bootstrap-skill.git \
  ~/.codex/skills/project-research-bootstrap
```

如果你使用 HTTPS：

```bash
git clone https://github.com/Cayman-Wang/project-research-bootstrap-skill.git \
  ~/.codex/skills/project-research-bootstrap
```

### 2) 更新到最新版本

```bash
cd ~/.codex/skills/project-research-bootstrap
git pull
```

### 3) 重新加载 Skill

- 新开一个 Codex 对话，或重启当前会话环境。
- 然后直接使用触发语句：`讨论项目方案` / `冻结当前方案` / `开始初始化 research 工作区`。

### 4) 让 AI 自动安装（skill-installer）

在新机器上，你可以直接对 AI 发送下面这段话，让它自动调用 `skill-installer`：

```text
使用 skill-installer 安装这个 skill：
repo=Cayman-Wang/project-research-bootstrap-skill
path=.
name=project-research-bootstrap
安装后提醒我重启/新开 Codex 会话。
```

如果你的环境里未启用 `skill-installer`，让 AI 回退到 shell 安装：

```bash
mkdir -p ~/.codex/skills
git clone git@github.com:Cayman-Wang/project-research-bootstrap-skill.git \
  ~/.codex/skills/project-research-bootstrap
```

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

## 自检方法（安装后 1 分钟）

### 1) 检查 Skill 文件是否完整

```bash
ls -la ~/.codex/skills/project-research-bootstrap
find ~/.codex/skills/project-research-bootstrap -maxdepth 2 -type f | sort
```

应至少包含：`SKILL.md`、`agents/openai.yaml`、`scripts/bootstrap_research_workspace.py`、`references/*`。

### 2) 运行结构校验（可选）

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  ~/.codex/skills/project-research-bootstrap
```

预期输出包含：`Skill is valid!`。

### 3) 运行 dry-run 冒烟测试

```bash
tmpdir=$(mktemp -d)
python ~/.codex/skills/project-research-bootstrap/scripts/bootstrap_research_workspace.py \
  --workspace-root "$tmpdir" \
  --project-slug demo_project \
  --dry-run
```

预期输出包含：`created: 10`。

### 4) 运行幂等测试（连续两次）

```bash
tmpdir=$(mktemp -d)
script=~/.codex/skills/project-research-bootstrap/scripts/bootstrap_research_workspace.py
python "$script" --workspace-root "$tmpdir" --project-slug demo_project
python "$script" --workspace-root "$tmpdir" --project-slug demo_project
```

预期第二次输出包含：`created: 0` 且 `skipped: 10`。

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
