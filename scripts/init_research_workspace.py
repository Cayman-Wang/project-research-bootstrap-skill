#!/usr/bin/env python3
"""Initialize a reusable research workspace skeleton with idempotent behavior."""

from __future__ import annotations

import argparse
import datetime as dt
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass(frozen=True)
class WriteResult:
    path: Path
    status: str  # created | overwritten | skipped


def normalize_slug(raw: str) -> str:
    slug = raw.strip().lower()
    slug = re.sub(r"[^a-z0-9_\-]+", "_", slug)
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "project_plan"


def render_research_readme() -> str:
    return """# Research Workspace Layout

`research/` stores project planning and execution knowledge for reusable collaboration.

## Directory Layout
- `research/plans/`: active pointer, master plan, milestone plans, session start prompt.
- `research/guides/`: operation guides and runbooks.
- `research/reviews/`: audit reports and fix prompts.
- `research/handoffs/`: session handoff notes.
- `research/retrospectives/`: milestone retrospectives.
- `research/artifacts/tmp/`: optional temporary artifacts that can be regenerated.

## Retention Rule
- Keep runtime outputs outside `research/` (for example `outputs/`).
- Keep only decision records and reusable process documents in `research/`.
"""


def render_active_plan(slug: str, today: str) -> str:
    return f"""# ACTIVE_PLAN

goal: [待填写：项目总目标]
current_milestone: M1 规划阶段（待确认）
must_read:
  - research/plans/{slug}/master_plan_zh.md
locked_decisions:
  - [待填写：已冻结关键决策]
next_action: [待填写：下一步可执行动作]
out_of_scope:
  - [待填写：本阶段不做内容]
latest_retrospective: none
last_updated: {today}
"""


def render_master_plan(slug: str, today: str) -> str:
    return f"""# {slug} 主计划（中文）

- 创建日期：{today}
- 负责人：[待填写]

## 一、目标
- [待填写：一句话目标]

## 二、背景与问题定义
- [待填写：现状、痛点、约束]

## 三、方案总览
- [待填写：总体方案]

## 四、里程碑
- M1: [待填写]
- M2: [待填写]
- M3: [待填写]

## 五、验收标准
- [待填写：可验证指标]

## 六、风险与对策
- [待填写]

## 七、默认假设
- 默认中文文档
- 默认按“讨论 -> 冻结 -> 生成”执行
"""


def render_session_start_prompt() -> str:
    return """# 新对话启动模板（跨平台通用）

> 用法：新建任意 AI 对话后，把本文件内容整体粘贴为第一条消息，再补你的具体任务。

```text
请先读取以下计划文件，再回答我的问题：

workspace_path=<workspace_path>
main_plan=<main_plan>
active_plan=<active_plan>

执行顺序要求：
1) 先读取 active_plan。
2) 再读取 main_plan。
3) 再按 active_plan 中 must_read 列表读取其余必读文件。

在你的第一条回复中，先输出 Intent Digest（三行）：
Goal: <从计划中提炼的一句话目标>
Current Milestone: <当前里程碑>
Next Action: <下一步可执行动作>

如果任何必读文件缺失、路径无效或计划冲突，请先明确报错并给出修复建议，不要直接开始实现。
```
"""


def render_simple_readme(title: str, bullets: List[str]) -> str:
    lines = [f"# {title}", ""]
    for bullet in bullets:
        lines.append(f"- {bullet}")
    lines.append("")
    return "\n".join(lines)


def render_retrospective_readme(slug: str) -> str:
    return f"""# {slug} 阶段复盘索引

本目录用于存放里程碑复盘文档（论文素材/工程复盘）。

## 索引
| Milestone | Date | File | Status |
| --- | --- | --- | --- |
| M1 | - | - | Pending |

## 固定结构（每篇复盘必须包含）
1. 问题
2. 思路
3. 实现
4. 验证
5. 局限
6. 下一步
7. 借鉴关系与实现边界
"""


def render_retrospective_template() -> str:
    return """# YYYY-MM-DD_mX_retrospective_zh

- 日期：YYYY-MM-DD
- 里程碑：MX
- 对应主计划：[master_plan_zh.md](../../plans/<project_slug>/master_plan_zh.md)

## 1. 问题
- [待填写]

## 2. 思路
- [待填写]

## 3. 实现
- [待填写]

## 4. 验证
- [待填写]

## 5. 局限
- [待填写]

## 6. 下一步
- [待填写]

## 7. 借鉴关系与实现边界
### 7.1 借鉴层级
- [待填写]

### 7.2 来源映射表
| 借鉴来源 | 借鉴到的思路 | 本项目落点 | 当前状态 |
| --- | --- | --- | --- |
| [待填写] | [待填写] | [待填写] | [待填写] |

### 7.3 独立实现证据
- [待填写]
"""


def write_file(path: Path, content: str, force: bool, dry_run: bool) -> WriteResult:
    if path.exists() and not force:
        return WriteResult(path=path, status="skipped")

    status = "overwritten" if path.exists() else "created"
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return WriteResult(path=path, status=status)


def touch_file(path: Path, force: bool, dry_run: bool) -> WriteResult:
    if path.exists() and not force:
        return WriteResult(path=path, status="skipped")

    status = "overwritten" if path.exists() else "created"
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
    return WriteResult(path=path, status=status)


def build_file_map(root: Path, slug: str, today: str) -> Dict[Path, str]:
    return {
        root / "research" / "README.md": render_research_readme(),
        root / "research" / "plans" / "ACTIVE_PLAN.md": render_active_plan(slug, today),
        root / "research" / "plans" / slug / "master_plan_zh.md": render_master_plan(slug, today),
        root / "research" / "plans" / "session_start_prompt_zh.md": render_session_start_prompt(),
        root / "research" / "guides" / "README.md": render_simple_readme(
            "Guides", ["放置运行指南、操作手册、参数说明。"]
        ),
        root / "research" / "reviews" / "README.md": render_simple_readme(
            "Reviews", ["放置审查报告、修复提示词、审计结论。"]
        ),
        root / "research" / "handoffs" / "README.md": render_simple_readme(
            "Handoffs", ["放置跨会话交接文档。"]
        ),
        root / "research" / "retrospectives" / slug / "README.md": render_retrospective_readme(slug),
        root
        / "research"
        / "retrospectives"
        / slug
        / "TEMPLATE_retrospective_zh.md": render_retrospective_template(),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Initialize a reusable research workspace skeleton."
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path.cwd(),
        help="Target workspace root directory.",
    )
    parser.add_argument(
        "--project-slug",
        type=str,
        required=True,
        help="Project slug used under research/plans and research/retrospectives.",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=dt.date.today().isoformat(),
        help="Date string used in template metadata (YYYY-MM-DD).",
    )
    parser.add_argument(
        "--force-overwrite",
        action="store_true",
        help="Overwrite existing files instead of skipping them.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned changes without writing files.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    workspace_root = args.workspace_root.resolve()
    slug = normalize_slug(args.project_slug)
    today = args.date

    file_map = build_file_map(workspace_root, slug, today)
    results: List[WriteResult] = []

    for path, content in file_map.items():
        results.append(write_file(path, content, args.force_overwrite, args.dry_run))

    gitkeep_path = workspace_root / "research" / "artifacts" / "tmp" / ".gitkeep"
    results.append(touch_file(gitkeep_path, args.force_overwrite, args.dry_run))

    created = sum(1 for r in results if r.status == "created")
    overwritten = sum(1 for r in results if r.status == "overwritten")
    skipped = sum(1 for r in results if r.status == "skipped")

    print("Research workspace initialization complete")
    print(f"- workspace_root: {workspace_root}")
    print(f"- project_slug: {slug}")
    print(f"- dry_run: {args.dry_run}")
    print(f"- created: {created}")
    print(f"- overwritten: {overwritten}")
    print(f"- skipped: {skipped}")

    for result in results:
        print(f"  [{result.status}] {result.path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
