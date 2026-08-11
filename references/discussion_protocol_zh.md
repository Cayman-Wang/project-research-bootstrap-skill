# 讨论与冻结协议

## 深度选择

默认使用 `Standard`：覆盖问题、现状、成功标准、约束、至少两条合理路径及主要风险。

遇到高成本或不可逆决策、跨团队依赖、安全或合规风险、科研可行性未知，或用户明确要求深入时，使用 `Deep`。在 Standard 基础上增加证据核验、假设优先级排序和 pre-mortem；不要用更多问题代替验证。

用户请求“直接冻结”时，先做一次 Standard 完整性审计。若材料已覆盖全部 Discussion Brief 字段，可直接进入 `CONVERGE` / `FREEZE`；若有缺口，只追问会改变范围、方案、验收或风险判断的高价值决策，不机械重走六个阶段。

## DISCUSS

按以下顺序推进；每轮只处理一个决策簇，提出 1 至 3 个可回答的问题。

1. `INTAKE`：确认问题、期望结果、受众和交付物。
2. `CONTEXT`：确认现状、已有证据、约束、依赖和不可变边界。
3. `SHAPE`：定义成功标准、范围、里程碑和至少两条合理路径。
4. `EXPLORE`：比较选项、取舍、证据、成本和假设。
5. `STRESS TEST`：检查主要风险、失败模式和验收漏洞；Deep 执行 pre-mortem。
6. `CONVERGE`：形成 Discussion Brief，明确推荐项、开放决策和冻结就绪度。

若同一决策簇连续两轮仍未收敛，采用可逆的合理默认值，或提出一个最小验证消除关键不确定性。记录默认值及理由，不要无限追问。

## Discussion Brief

```text
Problem:
Outcomes:
Evidence:
Scope:
Constraints:
Options:
Tradeoffs:
Assumptions:
Risks:
Recommendation:
Open Decisions:
Freeze Readiness: READY | READY_WITH_ASSUMPTIONS | NOT_READY
Milestones and Acceptance:
Next Action:
Change Log (re-freeze only):
```

Standard 的 Options 至少包含推荐路径和一个合理 alternative，并在 Tradeoffs 中逐项比较。Deep 标出已核验的证据、按影响和不确定性排序的假设，以及 pre-mortem 结果。

## FREEZE

仅接受 `READY` 或 `READY_WITH_ASSUMPTIONS`。后者必须列出非空 assumptions，并由用户明确接受；否则保持 `NOT_READY`，继续 DISCUSS 或执行最小验证。

冻结摘要必须明确目标、成功标准、范围、约束、选定方案、锁定决策、里程碑及验收、风险及其验证、剩余假设和下一动作。要求用户确认冻结摘要；该确认不等于 `GENERATE` 写入授权。

把未知项标为 Open Decision 或 Assumption，不要伪造确定性。re-freeze 时保留先前 locked decisions，并在 Change Log 中逐项说明保留、替换或废弃的决定。
