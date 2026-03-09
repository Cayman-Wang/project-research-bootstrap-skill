# 工作流约束（DISCUSS / FREEZE / GENERATE）

## 目标
在新项目中复用 `research/` 工作区方法，先讨论、再冻结、后落盘，避免“边想边改导致结构漂移”。

## 阶段定义
1. `DISCUSS`
- 收集并确认：目标、里程碑、验收标准、范围边界、约束。
- 输出讨论结论，不写文件。

2. `FREEZE`
- 输出冻结摘要：
  - Goal
  - Milestones
  - Next Action
  - Out of Scope
- 仍不写文件。

3. `GENERATE`
- 仅在用户显式触发后执行。
- 触发短语示例：
  - `开始初始化 research 工作区`
  - `按冻结方案生成 research 目录`
  - `落盘 research 工作区`
- 执行脚本生成骨架并回报创建结果。

## 触发守卫
- 若用户未显式触发 GENERATE：禁止落盘。
- 若项目已存在 `research/`：默认幂等补齐，非强制覆盖。
- 若用户要求覆盖：再次确认并使用 `--force-overwrite`。

## 默认值
- 默认文档语言：中文。
- 默认目录名：`research/`。
- 默认先产出可讨论版本，再产出冻结版本。
