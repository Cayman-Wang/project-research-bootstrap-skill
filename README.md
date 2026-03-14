# plan-your-project

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

## 生成结果骨架（标准树状图）

脚本会在目标工作区生成如下 `research/` 结构（模板）：

```text
research/
├── README.md
├── plans/
│   ├── ACTIVE_PLAN.md
│   ├── session_bootstrap_prompt_zh.md
│   └── <project_slug>/
│       └── master_plan_zh.md
├── guides/
│   └── README.md
├── reviews/
│   └── README.md
├── handoffs/
│   └── README.md
├── retrospectives/
│   └── <project_slug>/
│       ├── README.md
│       └── TEMPLATE_retrospective_zh.md
└── artifacts/
    └── tmp/
        └── .gitkeep
```

## research 目录与文件作用

| 路径 | 类型 | 作用 | 何时更新 |
| --- | --- | --- | --- |
| `research/README.md` | 文件 | 说明整个 research 工作区的用途与边界。 | 初始化后按需更新。 |
| `research/plans/` | 目录 | 存放计划入口、主计划和阶段计划。 | 每次阶段切换或计划调整时更新。 |
| `research/plans/ACTIVE_PLAN.md` | 文件 | 当前阶段唯一入口；新会话优先读取。 | 每次里程碑切换、`must_read` 变化时更新。 |
| `research/plans/<project_slug>/master_plan_zh.md` | 文件 | 项目长期主计划（目标、里程碑、验收标准）。 | 方向变化或里程碑重排时更新。 |
| `research/plans/session_bootstrap_prompt_zh.md` | 文件 | 跨平台新会话启动模板。 | 会话协议调整时更新。 |
| `research/guides/README.md` | 文件 | 指南目录入口；用于放运行手册和操作指南。 | 新增指南文档时同步更新。 |
| `research/reviews/README.md` | 文件 | 审查目录入口；用于放审查报告和修复提示词。 | 产出审查材料时同步更新。 |
| `research/handoffs/README.md` | 文件 | 交接目录入口；用于跨会话交接文档。 | 会话交接流程变化时更新。 |
| `research/retrospectives/<project_slug>/README.md` | 文件 | 复盘索引，按里程碑记录复盘列表。 | 每次新增阶段复盘后更新。 |
| `research/retrospectives/<project_slug>/TEMPLATE_retrospective_zh.md` | 文件 | 阶段复盘模板（问题/思路/实现/验证/局限/下一步/借鉴边界）。 | 模板规范变化时更新。 |
| `research/artifacts/tmp/.gitkeep` | 文件 | 保留临时产物目录结构。 | 一般不需更新。 |

## 维护建议（最小流程）

1. `讨论项目方案`：先讨论目标、里程碑、边界，不改文档。  
2. `冻结当前方案`：生成冻结摘要，锁定 `Goal / Milestones / Next Action / Out of Scope`。  
3. `开始初始化 research 工作区`：只在此阶段落盘更新 `research/`。  
4. 阶段完成后写 retrospective：同步更新 `ACTIVE_PLAN.md` 的 `latest_retrospective` 与 `must_read`。  

维护规则：
- `ACTIVE_PLAN.md` 是当前阶段唯一入口文件。
- 运行产物不写入 `research/`，统一放到项目运行目录（如 `outputs/`）。

## 安装说明

### 1) 克隆到 Codex skills 目录（推荐）

```bash
mkdir -p ~/.codex/skills
git clone git@github.com:Cayman-Wang/plan-your-project-skill.git \
  ~/.codex/skills/plan-your-project
```

如果你使用 HTTPS：

```bash
git clone https://github.com/Cayman-Wang/plan-your-project-skill.git \
  ~/.codex/skills/plan-your-project
```

### 2) 更新到最新版本

```bash
cd ~/.codex/skills/plan-your-project
git pull
```

### 3) 重新加载 Skill

- 新开一个 Codex 对话，或重启当前会话环境。
- 然后直接使用触发语句：`讨论项目方案` / `冻结当前方案` / `开始初始化 research 工作区`。

### 4) 让 AI 自动安装（skill-installer）

在新机器上，你可以直接对 AI 发送下面这段话，让它自动调用 `skill-installer`：

```text
使用 skill-installer 安装这个 skill：
repo=Cayman-Wang/plan-your-project-skill
path=.
name=plan-your-project
安装后提醒我重启/新开 Codex 会话。
```

如果你的环境里未启用 `skill-installer`，让 AI 回退到 shell 安装：

```bash
mkdir -p ~/.codex/skills
git clone git@github.com:Cayman-Wang/plan-your-project-skill.git \
  ~/.codex/skills/plan-your-project
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
ls -la ~/.codex/skills/plan-your-project
find ~/.codex/skills/plan-your-project -maxdepth 2 -type f | sort
```

应至少包含：`SKILL.md`、`agents/openai.yaml`、`scripts/bootstrap_research_workspace.py`、`references/*`。

### 2) 运行结构校验（可选）

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  ~/.codex/skills/plan-your-project
```

预期输出包含：`Skill is valid!`。

### 3) 运行 dry-run 冒烟测试

```bash
tmpdir=$(mktemp -d)
python ~/.codex/skills/plan-your-project/scripts/bootstrap_research_workspace.py \
  --workspace-root "$tmpdir" \
  --project-slug demo_project \
  --dry-run
```

预期输出包含：`created: 10`。

### 4) 运行幂等测试（连续两次）

```bash
tmpdir=$(mktemp -d)
script=~/.codex/skills/plan-your-project/scripts/bootstrap_research_workspace.py
python "$script" --workspace-root "$tmpdir" --project-slug demo_project
python "$script" --workspace-root "$tmpdir" --project-slug demo_project
```

预期第二次输出包含：`created: 0` 且 `skipped: 10`。

## 验证建议

1. 结构完整性：树状图中的路径都能在生成结果中找到。
2. 角色清晰性：可快速指出“当前阶段入口是 `ACTIVE_PLAN.md`，复盘模板是 `TEMPLATE_retrospective_zh.md`”。
3. 幂等性：连续运行两次，第二次应主要为 `skipped`。
4. 会话继承：新对话先读 `ACTIVE_PLAN.md`，再读 `must_read`，首条输出 `Goal / Current Milestone / Next Action`。

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
