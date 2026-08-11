---
name: plan-your-project
description: Plan and maintain software or research projects with a decision-first DISCUSS, FREEZE, GENERATE, and MAINTAIN protocol. Use for project discovery, research or engineering scoping, plan tradeoffs and milestones, freezing or generating a minimal planning workspace, reporting or explicitly updating project status, and requested decision, review, retrospective, or handoff records. Do not use for immediate coding fixes, one-off implementation with settled scope, or generic scaffolding without planning.
---

# Plan Your Project

Run the state machine `DISCUSS -> FREEZE -> GENERATE -> MAINTAIN`. Keep discussion and workspace records separate: discussion is conversational; records exist only after explicit authorization.

## Select The State

- Enter `DISCUSS` for a new, ambiguous, or materially changed project. Read-only inspection and research are allowed; do not write workspace files.
- Enter `FREEZE` only when the decision set is coherent. Present the complete Discussion Brief and ask for confirmation. Read-only verification is allowed; do not write workspace files.
- Enter `GENERATE` only after the user explicitly authorizes creating the frozen workspace, for example “生成计划文件”, “initialize the plan workspace”, or “按冻结方案落盘”. Never infer authorization from approval of the brief.
- When asked only for current status, read `PLAN.md` and `STATUS.md`, report the answer, and do not write.
- Enter writable `MAINTAIN` only when the user explicitly requests a status update, decision record, review, retrospective, or handoff. Read the two core records first.

Read [references/discussion_protocol_zh.md](references/discussion_protocol_zh.md) before conducting `DISCUSS` or `FREEZE`. Read exactly one lens when shaping a domain: [references/software_lens_zh.md](references/software_lens_zh.md) for software/product/system work, or [references/research_lens_zh.md](references/research_lens_zh.md) for research/experiment work. Read [references/file_contract_zh.md](references/file_contract_zh.md) before `GENERATE` or `MAINTAIN`.

## Generate The Minimal Workspace

After explicit authorization, inspect the target before writing.

- Create only `research/PLAN.md` and `research/STATUS.md` by default, using the strict payload in the file contract.
- Create a lazy record only when explicitly requested, at the dated slug path defined by the file contract; create only that record. Copy a retrospective template only for a requested retrospective. Do not create indexes, prompts, guides, placeholders, or unrelated record directories.
- Treat a workspace containing v1 paths or a mixture of v1 and v2 records as read-only. Report the detected layout and refuse to write; v2 does not provide migration.
- Preserve existing v2 files unless the user explicitly authorizes the requested maintenance change. Do not overwrite a frozen PLAN merely to update progress.
- Use `scripts/init_research_workspace.py` as the v2 GENERATE entrypoint with its strict JSON `--plan-file` input. Use `scripts/bootstrap_research_workspace.py` only for deprecated compatibility; it is not a v2 entrypoint.

## Maintain Records

Update `STATUS.md` for observed progress, current milestone, next action, blockers, and timestamps only after explicit maintenance intent. For a major direction change, return to `DISCUSS` and `FREEZE`; show the revised Discussion Brief, obtain re-freeze confirmation, then separately obtain explicit authorization to write the PLAN revision. Keep the previous locked decisions visible in the new brief and identify each changed decision.

## Verify

After a permitted write, verify that exactly the authorized v2 records were created or changed, both payloads satisfy the contract, STATUS links to PLAN, both records use the same plan revision, and STATUS names a PLAN milestone. Report created, updated, and skipped paths plus any authorization or layout boundary encountered.
