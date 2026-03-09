# research 工作区文件契约

## 必须存在的目录
- `research/plans/`
- `research/guides/`
- `research/reviews/`
- `research/handoffs/`
- `research/retrospectives/`
- `research/artifacts/tmp/`

## 必须存在的核心文件
- `research/README.md`
- `research/plans/ACTIVE_PLAN.md`
- `research/plans/<project_slug>/master_plan_zh.md`
- `research/plans/session_bootstrap_prompt_zh.md`
- `research/retrospectives/<project_slug>/README.md`
- `research/retrospectives/<project_slug>/TEMPLATE_retrospective_zh.md`

## ACTIVE_PLAN 字段契约
以下键必须存在：
- `goal`
- `current_milestone`
- `must_read`
- `locked_decisions`
- `next_action`
- `out_of_scope`
- `latest_retrospective`
- `last_updated`

## 复盘模板契约
`TEMPLATE_retrospective_zh.md` 必须包含章节：
1. 问题
2. 思路
3. 实现
4. 验证
5. 局限
6. 下一步
7. 借鉴关系与实现边界

## 验收清单
1. 文件完整性：核心路径都存在。
2. 幂等性：重复执行不覆盖已有内容（除非强制覆盖）。
3. 运行产物隔离：`research/` 不存放训练或回放产物。
4. 会话继承：`session_bootstrap_prompt_zh.md` 可引导新对话正确读取计划。
