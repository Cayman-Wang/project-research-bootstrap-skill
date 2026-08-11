#!/usr/bin/env python3
"""Create and validate the frozen plan-your-project v2 workspace contract."""
from __future__ import annotations
import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path
from typing import Any

PLAN_NAME, STATUS_NAME = "PLAN.md", "STATUS.md"
TOP_KEYS = {"schema_version", "project_name", "problem", "goal", "success_criteria", "scope", "constraints", "selected_approach", "alternatives_considered", "locked_decisions", "milestones", "risks", "assumptions", "open_questions", "evidence", "next_action", "freeze_readiness"}
OLD_PROMPTS = ("session_start_prompt_zh.md", "session_bootstrap_prompt_zh.md")
class ContractError(ValueError): pass

def parse_date(value: str) -> str:
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        raise argparse.ArgumentTypeError("--date must be an ISO date (YYYY-MM-DD)")
    try: return dt.date.fromisoformat(value).isoformat()
    except ValueError as exc: raise argparse.ArgumentTypeError("--date must be an ISO date (YYYY-MM-DD)") from exc

def parse_args(argv=None):
    p = argparse.ArgumentParser(description="Initialize or validate a frozen plan-your-project v2 workspace.")
    p.add_argument("--workspace-root", required=True, type=Path, help="Workspace containing research/.")
    p.add_argument("--plan-file", metavar="FILE|-", help="Strict JSON frozen plan input; - reads stdin.")
    p.add_argument("--language", choices=("zh", "en"), default="zh")
    p.add_argument("--date", type=parse_date, default=dt.date.today().isoformat(), help="ISO date (YYYY-MM-DD).")
    p.add_argument("--dry-run", action="store_true"); p.add_argument("--force-overwrite", action="store_true")
    p.add_argument("--validate-only", action="store_true"); p.add_argument("--adopt-existing-research-dir", action="store_true")
    p.add_argument("--json", action="store_true"); p.add_argument("--project-slug", help="Deprecated; ignored and does not affect paths.")
    a=p.parse_args(argv)
    if not a.validate_only and not a.plan_file: p.error("--plan-file is required unless --validate-only is used")
    if a.validate_only and a.plan_file: p.error("--plan-file cannot be used with --validate-only")
    if a.validate_only and a.force_overwrite: p.error("--force-overwrite cannot be used with --validate-only")
    return a

def valid_text(value: Any, name: str) -> None:
    if not isinstance(value, str):
        raise ContractError(f"{name} must be a string")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ContractError(f"{name} must be valid UTF-8 text") from exc
    if "\r" in value or "\n" in value:
        raise ContractError(f"{name} must not contain CR or LF")


def nonempty(value, name):
    valid_text(value, name)
    if not value.strip(): raise ContractError(f"{name} must be a non-empty string")
def string_list(value, name, required=False):
    if not isinstance(value, list) or (required and not value):
        raise ContractError(f"{name} must be {'a non-empty ' if required else 'a '}list of non-empty strings")
    for item in value:
        nonempty(item, name)
def exact_object(value, keys, name):
    if not isinstance(value,dict) or set(value)!=set(keys): raise ContractError(f"{name} must contain exactly: {', '.join(keys)}")

def validate_plan(plan: Any):
    if not isinstance(plan,dict) or set(plan)!=TOP_KEYS: raise ContractError("plan JSON has missing or unknown top-level keys")
    valid_text(plan["schema_version"], "schema_version")
    valid_text(plan["freeze_readiness"], "freeze_readiness")
    if plan["schema_version"] != "2.0": raise ContractError("schema_version must be '2.0'")
    if plan["freeze_readiness"] not in ("READY", "READY_WITH_ASSUMPTIONS"): raise ContractError("freeze_readiness must be READY or READY_WITH_ASSUMPTIONS")
    for key in ("project_name","problem","goal","selected_approach","next_action"): nonempty(plan[key], key)
    for key in ("success_criteria","constraints","locked_decisions","assumptions","open_questions","evidence"):
        string_list(plan[key], key, key in ("success_criteria","locked_decisions"))
    exact_object(plan["scope"], ("in","out"), "scope"); string_list(plan["scope"]["in"], "scope.in", True); string_list(plan["scope"]["out"], "scope.out")
    if not isinstance(plan["alternatives_considered"],list) or not plan["alternatives_considered"]: raise ContractError("alternatives_considered must be a non-empty list")
    for item in plan["alternatives_considered"]:
        exact_object(item,("option","tradeoffs"),"alternative"); nonempty(item["option"],"alternative.option"); string_list(item["tradeoffs"],"alternative.tradeoffs")
    alternatives = [item["option"] for item in plan["alternatives_considered"]]
    if plan["selected_approach"] in alternatives:
        raise ContractError("alternative.option must differ from selected_approach")
    if len(alternatives) != len(set(alternatives)):
        raise ContractError("alternative.option values must be unique")
    if not isinstance(plan["milestones"],list) or not plan["milestones"]: raise ContractError("milestones must be a non-empty list")
    ids=[]
    for item in plan["milestones"]:
        exact_object(item,("id","outcome","acceptance"),"milestone"); nonempty(item["id"],"milestone.id"); nonempty(item["outcome"],"milestone.outcome"); string_list(item["acceptance"],"milestone.acceptance",True); ids.append(item["id"])
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", item["id"]): raise ContractError("milestone.id has an invalid format")
    if len(ids)!=len(set(ids)): raise ContractError("milestone.id values must be unique")
    if not isinstance(plan["risks"],list): raise ContractError("risks must be a list")
    for item in plan["risks"]:
        exact_object(item,("risk","mitigation_or_validation"),"risk"); nonempty(item["risk"],"risk.risk"); nonempty(item["mitigation_or_validation"],"risk.mitigation_or_validation")
    if plan["freeze_readiness"] == "READY_WITH_ASSUMPTIONS" and not plan["assumptions"]:
        raise ContractError("READY_WITH_ASSUMPTIONS requires at least one assumption")

def load_plan(source):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ContractError(f"plan JSON contains duplicate key: {key}")
            result[key] = value
        return result
    try:
        if source == "-":
            raw = sys.stdin.buffer.read().decode("utf-8-sig")
        else:
            raw = Path(source).read_text(encoding="utf-8-sig")
        value = json.loads(raw, object_pairs_hook=unique_object)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc: raise ContractError("plan file must contain valid UTF-8 JSON") from exc
    validate_plan(value); return value

def classify_layout(root):
    research=root/"research"
    if not research.exists(): return "empty", []
    if not research.is_dir(): return "invalid", ["research is not a directory"]
    plan,status=research/PLAN_NAME,research/STATUS_NAME
    if any(path.exists() and not path.is_file() for path in (plan, status)):
        return "invalid", ["PLAN.md and STATUS.md must be regular files"]
    plans = research / "plans"
    old = (plans/"ACTIVE_PLAN.md").exists() or any((plans/x).exists() for x in OLD_PROMPTS) or any(plans.glob("*/master_plan_zh.md"))
    if old and (plan.exists() or status.exists()): return "mixed", ["legacy and v2 files are both present"]
    if old: return "v1", ["legacy research workspace detected"]
    if plan.exists() != status.exists(): return "invalid", ["partial v2 workspace: PLAN.md and STATUS.md must both exist"]
    if plan.exists(): return "v2", []
    return ("empty",[]) if not any(research.iterdir()) else ("unknown",["unrecognized research directory"])

def bullets(xs, empty="None"): return "\n".join("- "+x for x in xs) if xs else "- " + empty
def obj_bullets(xs, fmt, empty="None"): return "\n".join("- "+fmt(x) for x in xs) if xs else "- " + empty
def render_plan(p: dict[str, Any], language: str, date: str, revision: int) -> str:
    h = {"zh": {"problem":"问题","goal":"目标","success_criteria":"成功标准","scope":"范围","constraints":"约束","selected_approach":"选定方案","alternatives_considered":"备选方案","locked_decisions":"冻结决策","milestones":"里程碑","risks":"风险","assumptions":"假设","open_questions":"开放问题","evidence":"证据","next_action":"下一步"}, "en": {k:k.replace("_"," ").title() for k in TOP_KEYS}}[language]
    empty = "无" if language == "zh" else "None"
    in_label, out_label = ("范围内", "范围外") if language == "zh" else ("In", "Out")
    acceptance = "验收" if language == "zh" else "acceptance"
    freeze = "冻结就绪度" if language == "zh" else "Freeze Readiness"
    tradeoffs = "权衡" if language == "zh" else "tradeoffs"
    mitigation = "缓解或验证" if language == "zh" else "mitigation or validation"
    out=["---","workspace_format: plan-your-project/v2","record: PLAN",f"plan_revision: {revision}",f"language: {language}",f"frozen_at: {date}","---",f"# {p['project_name']}"]
    for key in ("problem","goal","selected_approach","next_action"): out += [f"## {h[key]}",p[key]]
    for key in ("success_criteria","constraints","locked_decisions","assumptions","open_questions","evidence"): out += [f"## {h[key]}",bullets(p[key], empty)]
    out += [f"## {h['scope']}",f"### {in_label}",bullets(p['scope']['in'], empty),f"### {out_label}",bullets(p['scope']['out'], empty),f"## {h['alternatives_considered']}",obj_bullets(p['alternatives_considered'],lambda x: f"{x['option']} ({tradeoffs}: {'; '.join(x['tradeoffs']) or empty})",empty),f"## {h['milestones']}",obj_bullets(p['milestones'],lambda x: f"{x['id']} - {x['outcome']} ({acceptance}: {'; '.join(x['acceptance'])})",empty),f"## {h['risks']}",obj_bullets(p['risks'],lambda x: f"{x['risk']} ({mitigation}: {x['mitigation_or_validation']})",empty),f"## {freeze}",p['freeze_readiness']]
    return "\n".join(out[:7])+"\n\n"+"\n\n".join(out[7:])+"\n"
def render_status(
    p: dict[str, Any],
    language: str,
    date: str,
    revision: int,
    preserved: dict[str, Any] | None = None,
) -> str:
    heading="状态" if language=="zh" else "Status"
    next_action, blockers, must_read, empty = ("下一步", "阻塞", "必读", "无") if language == "zh" else ("Next Action", "Blockers", "Must Read", "None")
    preserved = preserved or {}
    milestone_ids = {item["id"] for item in p["milestones"]}
    current = preserved.get("current_milestone")
    if current not in milestone_ids:
        current = p["milestones"][0]["id"]
    state = preserved.get("state", "planned")
    blocker_text = preserved.get("blockers_body") or f"- {empty}"
    must_read_text = preserved.get("must_read_body") or "- research/PLAN.md"
    return f"---\nworkspace_format: plan-your-project/v2\nrecord: STATUS\nplan_revision: {revision}\nstate: {state}\ncurrent_milestone: {current}\nlast_updated: {date}\n---\n\n# {heading}\n\n## {next_action}\n{p['next_action']}\n\n## {blockers}\n{blocker_text}\n\n## {must_read}\n{must_read_text}\n"

def metadata(text):
    if not text.startswith("---\n"): raise ContractError("missing metadata")
    end=text.find("\n---\n",4)
    if end<0: raise ContractError("unterminated metadata")
    result={}
    for line in text[4:end].splitlines():
        if ": " not in line: raise ContractError("invalid metadata")
        k,v=line.split(": ",1)
        if k in result: raise ContractError("duplicate metadata")
        result[k]=v
    return result, text[end+5:]


def section_body(body: str, heading: str) -> str | None:
    match = re.search(
        rf"(?ms)^## {re.escape(heading)}\s*\n(.*?)(?=^## |\Z)", body
    )
    return match.group(1).strip() if match else None


def section_items(body: str, heading: str) -> list[str]:
    content = section_body(body, heading)
    if content is None:
        return []
    return [line[2:].strip() for line in content.splitlines() if line.startswith("- ")]


def contains_placeholder(text: str) -> bool:
    allowed_names = {"todo app", "todo application"}
    for line in text.splitlines():
        candidate = re.sub(r"^\s*[-*]\s*", "", line.strip(), count=1)
        if re.match(r"(?i)^(?:TODO|TBD)\b", candidate) and candidate.lower() not in allowed_names:
            return True
    patterns = (
        r"(?im):\s*(?:TODO|TBD)\b.*$",
        r"<[^>\r\n]+>",
        r"(?i)\[(?:待填写[^\]]*|fill in[^\]]*)\]",
        r"\{\{[^}\r\n]+\}\}",
    )
    return any(re.search(pattern, text) for pattern in patterns)


def read_preserved_status(root: Path, language: str) -> dict[str, Any]:
    text = (root / "research" / STATUS_NAME).read_text(encoding="utf-8")
    status_meta, body = metadata(text)
    blockers = "阻塞" if language == "zh" else "Blockers"
    must_read = "必读" if language == "zh" else "Must Read"
    return {
        "state": status_meta["state"],
        "current_milestone": status_meta["current_milestone"],
        "blockers_body": section_body(body, blockers),
        "must_read_body": section_body(body, must_read),
    }
def valid_iso_date(value: str) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        return False
    try:
        dt.date.fromisoformat(value)
        return True
    except (TypeError, ValueError):
        return False

def validate_v2_content(plan_text: str, status_text: str) -> list[str]:
    errors=[]
    try: pm,pt=metadata(plan_text); sm,st=metadata(status_text)
    except (UnicodeError, ContractError) as exc: return [str(exc)]
    plan_revision = pm.get("plan_revision", "")
    revision_ok = plan_revision.isascii() and plan_revision.isdecimal() and int(plan_revision) >= 1
    if set(pm)!={"workspace_format","record","plan_revision","language","frozen_at"} or pm.get("workspace_format")!="plan-your-project/v2" or pm.get("record")!="PLAN" or not revision_ok or pm.get("language") not in ("zh","en") or not valid_iso_date(pm.get("frozen_at", "")): errors.append("PLAN metadata is invalid")
    if set(sm)!={"workspace_format","record","plan_revision","state","current_milestone","last_updated"} or sm.get("workspace_format")!="plan-your-project/v2" or sm.get("record")!="STATUS" or sm.get("plan_revision")!=plan_revision or sm.get("state") not in ("planned","in_progress","blocked","complete") or not valid_iso_date(sm.get("last_updated", "")): errors.append("STATUS metadata is invalid")
    language = pm.get("language")
    milestone_heading = {"zh": "里程碑", "en": "Milestones"}.get(language)
    milestone_content = section_body(pt, milestone_heading) if milestone_heading else None
    milestones=[]
    for line in (milestone_content or "").splitlines():
        if line.startswith("- ") and " - " in line and ("(acceptance:" in line or "(验收:" in line): milestones.append(line[2:].split(" - ",1)[0])
    if sm.get("current_milestone") not in milestones: errors.append("STATUS current_milestone is absent from PLAN")
    plan_sections = {
        "zh": ("问题", "目标", "选定方案", "下一步", "成功标准", "约束", "冻结决策", "假设", "开放问题", "证据", "范围", "备选方案", "里程碑", "风险", "冻结就绪度"),
        "en": ("Problem", "Goal", "Selected Approach", "Next Action", "Success Criteria", "Constraints", "Locked Decisions", "Assumptions", "Open Questions", "Evidence", "Scope", "Alternatives Considered", "Milestones", "Risks", "Freeze Readiness"),
    }
    status_sections = {
        "zh": ("下一步", "阻塞", "必读"),
        "en": ("Next Action", "Blockers", "Must Read"),
    }
    if language in plan_sections:
        if any(not section_body(pt, heading) for heading in plan_sections[language]):
            errors.append("PLAN body lacks required sections")
        if any(not section_body(st, heading) for heading in status_sections[language]):
            errors.append("STATUS body lacks required sections")
        expected_h1 = "状态" if language == "zh" else "Status"
        if re.findall(r"(?m)^# (.+)$", st) != [expected_h1]:
            errors.append("STATUS must contain exactly one localized H1")
        if re.findall(r"(?m)^## (.+)$", st) != list(status_sections[language]):
            errors.append("STATUS must contain exactly its three localized H2 sections")
        must_read = section_body(st, status_sections[language][2])
        if must_read is None or "- research/PLAN.md" not in {line.strip() for line in must_read.splitlines()}:
            errors.append("STATUS must_read must include research/PLAN.md")
    if not re.search(r"(?m)^# \S.*$", pt):
        errors.append("PLAN body lacks a non-empty project title")
    if contains_placeholder(pt + "\n" + st):
        errors.append("workspace contains an unresolved placeholder")
    return errors


def validate_lazy_records(root: Path) -> list[str]:
    records = root / "research" / "records"
    if not records.exists():
        return []
    if not records.is_dir():
        return ["research/records must be a directory"]
    errors = []
    allowed = {"decisions", "reviews", "retrospectives", "handoffs"}
    children = list(records.iterdir())
    if not children:
        return ["research/records must not be empty"]
    for kind in children:
        if kind.name not in allowed or not kind.is_dir():
            errors.append("research/records contains an unknown kind")
            continue
        entries = list(kind.iterdir())
        if not entries:
            errors.append(f"lazy record directory is empty: {kind.name}")
        for entry in entries:
            if not entry.is_file():
                errors.append(f"lazy record must be a file: {entry.name}")
                continue
            if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9]+(?:-[a-z0-9]+)*\.md", entry.name):
                errors.append(f"lazy record has an invalid filename: {entry.name}")
                continue
            if not valid_iso_date(entry.name[:10]):
                errors.append(f"lazy record has an invalid date: {entry.name}")
            try:
                content = entry.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                errors.append(f"lazy record is not valid UTF-8: {entry.name}")
                continue
            if not content.strip():
                errors.append(f"lazy record is empty: {entry.name}")
            elif contains_placeholder(content):
                errors.append(f"lazy record contains an unresolved placeholder: {entry.name}")
    return errors


def validate_v2(root: Path) -> list[str]:
    research=root/"research"; plan_path,status_path=research/PLAN_NAME,research/STATUS_NAME
    try:
        plan_text = plan_path.read_text(encoding="utf-8")
        status_text = status_path.read_text(encoding="utf-8")
        errors = validate_v2_content(plan_text, status_text)
    except (OSError, UnicodeError) as exc:
        return [str(exc)]
    try:
        plan_meta, _ = metadata(plan_text)
        _, status_body = metadata(status_text)
    except ContractError as exc:
        return errors + [str(exc)] + validate_lazy_records(root)
    must_read_heading = {"zh": "必读", "en": "Must Read"}.get(plan_meta.get("language"))
    must_read = section_body(status_body, must_read_heading) if must_read_heading else None
    if must_read is not None:
        workspace_root = root.resolve()
        for line in must_read.splitlines():
            if not line.strip():
                continue
            match = re.fullmatch(r"- (\S(?:.*\S)?)", line)
            if not match:
                errors.append("STATUS must_read entries must be non-empty list items")
                continue
            value = match.group(1)
            parts = value.split("/")
            if "\\" in value or ":" in value or Path(value).is_absolute() or not parts or any(part in ("", ".", "..") for part in parts):
                errors.append(f"STATUS must_read path is invalid: {value}")
                continue
            try:
                candidate = (workspace_root / Path(*parts)).resolve()
            except (OSError, RuntimeError):
                errors.append(f"STATUS must_read path is invalid: {value}")
                continue
            try:
                candidate.relative_to(workspace_root)
            except ValueError:
                errors.append(f"STATUS must_read path escapes workspace: {value}")
                continue
            if not candidate.is_file():
                errors.append(f"STATUS must_read path is not an existing file: {value}")
    return errors + validate_lazy_records(root)

def validate_v1(root: Path) -> list[str]:
    research = root / "research"
    active = research / "plans" / "ACTIVE_PLAN.md"
    required = ("goal", "current_milestone", "must_read", "locked_decisions", "next_action", "out_of_scope", "latest_retrospective", "last_updated")
    errors = []
    if not (research / "README.md").is_file(): errors.append("missing research/README.md")
    if not active.is_file(): errors.append("missing plans/ACTIVE_PLAN.md")
    elif any(not any(line.startswith(key + ":") for line in active.read_text(encoding="utf-8").splitlines()) for key in required): errors.append("ACTIVE_PLAN.md lacks required keys")
    plans = research / "plans"
    if not any(plans.glob("*/master_plan_zh.md")): errors.append("missing master_plan_zh.md")
    if not any((plans / name).is_file() for name in OLD_PROMPTS): errors.append("missing session prompt")
    retrospectives = research / "retrospectives"
    if not any(retrospectives.glob("*/README.md")) or not any(retrospectives.glob("*/TEMPLATE_retrospective_zh.md")): errors.append("missing retrospective files")
    return errors

def emit(args, layout, status, messages, actions=None):
    actions=actions or []; payload={"layout":layout,"status":status,"messages":messages,"created":[x for x in actions if x.startswith("create ")],"skipped":[x for x in actions if x.startswith("skip ")],"overwritten":[x for x in actions if x.startswith("overwrite ")]}; payload["counts"]={k:len(payload[k]) for k in ("created","skipped","overwritten")}
    print(json.dumps(payload,ensure_ascii=False,sort_keys=True) if args.json else f"layout: {layout}\nstatus: {status}\n"+"\n".join("- "+x for x in messages+actions))

def main(argv=None):
    try:
        args=parse_args(argv); root=args.workspace_root.resolve()
        if args.project_slug: print("warning: --project-slug is deprecated and ignored",file=sys.stderr)
        layout,messages=classify_layout(root)
        if args.validate_only:
            if layout=="v1":
                errors = validate_v1(root)
                emit(args, layout, "valid" if not errors else "invalid", messages + ["legacy workspace: read-only"] + errors)
                return 0 if not errors else 1
            errors=validate_v2(root) if layout=="v2" else messages or [f"workspace layout is {layout}, not v2"]
            emit(args,layout,"valid" if not errors else "invalid",errors); return 0 if not errors else 1
        if layout in ("v1","mixed","invalid") or (layout=="unknown" and not args.adopt_existing_research_dir): emit(args,layout,"refused",messages or ["use --adopt-existing-research-dir"]); return 1
        if layout == "unknown" and args.adopt_existing_research_dir:
            lazy_errors = validate_lazy_records(root)
            if lazy_errors:
                emit(args, layout, "refused", lazy_errors)
                return 1
        if layout=="v2" and validate_v2(root): emit(args,layout,"refused",["existing v2 workspace is invalid; refusing writes"]); return 1
        if args.force_overwrite and layout!="v2": emit(args,layout,"refused",["--force-overwrite is only valid for an existing valid v2 workspace"]); return 1
        revision = 1
        preserved = None
        if layout == "v2" and args.force_overwrite:
            current, _ = metadata((root / "research" / PLAN_NAME).read_text(encoding="utf-8"))
            revision = int(current["plan_revision"]) + 1
            preserved = read_preserved_status(root, current["language"])
        p=load_plan(args.plan_file); files={root/"research"/PLAN_NAME:render_plan(p,args.language,args.date,revision),root/"research"/STATUS_NAME:render_status(p,args.language,args.date,revision,preserved)}; actions=[]
        try:
            for content in files.values():
                content.encode("utf-8")
        except UnicodeEncodeError as exc:
            raise ContractError("generated workspace content must be valid UTF-8") from exc
        if any(contains_placeholder(content) for content in files.values()):
            raise ContractError("generated workspace content contains an unresolved placeholder")
        rendered_errors = validate_v2_content(files[root/"research"/PLAN_NAME], files[root/"research"/STATUS_NAME])
        if rendered_errors:
            raise ContractError("generated workspace violates contract: " + "; ".join(rendered_errors))
        for path,content in files.items():
            action="overwrite" if path.exists() and args.force_overwrite else "skip" if path.exists() else "create"; actions.append(f"{action} {path.relative_to(root)}")
            if action!="skip" and not args.dry_run: path.parent.mkdir(parents=True,exist_ok=True); path.write_text(content,encoding="utf-8")
        emit(args,layout,"dry-run" if args.dry_run else "initialized",[],actions); return 0
    except ContractError as exc:
        try: emit(args, layout if "layout" in locals() else "invalid", "invalid", [str(exc)])
        except UnboundLocalError: print(f"error: {exc}",file=sys.stderr)
        return 1
if __name__=="__main__": raise SystemExit(main())
