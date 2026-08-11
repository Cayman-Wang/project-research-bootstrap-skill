import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "init_research_workspace.py"
BOOTSTRAP = ROOT / "scripts" / "bootstrap_research_workspace.py"
SPEC = importlib.util.spec_from_file_location("init_research_workspace", SCRIPT)
INIT = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(INIT)


def plan(**changes):
    value = {
        "schema_version": "2.0",
        "project_name": "Unicode 研究计划",
        "problem": "A concrete problem",
        "goal": "验证 Unicode input",
        "success_criteria": ["Tests pass"],
        "scope": {"in": ["implementation"], "out": ["training output"]},
        "constraints": [],
        "selected_approach": "Use stdlib",
        "alternatives_considered": [{"option": "Dependency", "tradeoffs": ["More setup"]}],
        "locked_decisions": ["Use stdlib"],
        "milestones": [{"id": "M1", "outcome": "Working CLI", "acceptance": ["Tests pass"]}],
        "risks": [{"risk": "Schema drift", "mitigation_or_validation": "Unit tests"}],
        "assumptions": [], "open_questions": [], "evidence": [],
        "next_action": "Implement", "freeze_readiness": "READY",
    }
    value.update(changes)
    return value


class InitResearchWorkspaceTests(unittest.TestCase):
    def run_cli(self, directory, *args, stdin=None):
        return subprocess.run([sys.executable, str(SCRIPT), "--workspace-root", str(directory), *args], input=stdin, text=True, capture_output=True, check=False)

    def write_plan(self, directory, value=None):
        path = Path(directory) / "plan.json"
        path.write_text(json.dumps(value or plan(), ensure_ascii=False), encoding="utf-8")
        return path

    def test_initializes_exactly_two_v2_files_and_unicode(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = self.write_plan(root)
            result = self.run_cli(root, "--plan-file", str(source), "--date", "2026-08-11")
            self.assertEqual(result.returncode, 0, result.stderr)
            research = root / "research"
            self.assertEqual({p.name for p in research.iterdir()}, {"PLAN.md", "STATUS.md"})
            self.assertIn("Unicode 研究计划", (research / "PLAN.md").read_text(encoding="utf-8"))
            self.assertIn("plan_revision: 1", (research / "PLAN.md").read_text(encoding="utf-8"))
            status = (research / "STATUS.md").read_text(encoding="utf-8")
            self.assertIn("research/PLAN.md", status)
            self.assertNotIn("验证 Unicode", status)

    def test_english_and_stdin(self):
        with tempfile.TemporaryDirectory() as raw:
            result = self.run_cli(raw, "--plan-file", "-", "--language", "en", stdin=json.dumps(plan()))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("# Unicode 研究计划", (Path(raw) / "research" / "PLAN.md").read_text(encoding="utf-8"))
            self.assertIn("# Status", (Path(raw) / "research" / "STATUS.md").read_text(encoding="utf-8"))

    def test_stdin_uses_utf8_bytes_with_optional_bom(self):
        for prefix in (b"", b"\xef\xbb\xbf"):
            with self.subTest(bom=bool(prefix)), tempfile.TemporaryDirectory() as raw:
                payload = prefix + json.dumps(plan(), ensure_ascii=False).encode("utf-8")
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), "--workspace-root", raw, "--plan-file", "-"],
                    input=payload,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
                self.assertIn("验证 Unicode input", (Path(raw) / "research" / "PLAN.md").read_text(encoding="utf-8"))

    def test_invalid_stdin_utf8_is_zero_write_contract_error(self):
        with tempfile.TemporaryDirectory() as raw:
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--workspace-root", raw, "--plan-file", "-", "--json"],
                input=b"{\"goal\": \xff}",
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            payload = json.loads(result.stdout.decode("utf-8"))
            self.assertIn("UTF-8", " ".join(payload["messages"]))
            self.assertFalse((Path(raw) / "research").exists())

    def test_plan_schema_rejects_unknown_missing_and_wrong_types(self):
        with tempfile.TemporaryDirectory() as raw:
            for value in (plan(extra="no"), {"project_name": "x"}, plan(locked_decisions="bad")):
                source = self.write_plan(raw, value)
                result = self.run_cli(raw, "--plan-file", str(source))
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((Path(raw) / "research").exists())

    def test_invalid_date_and_dry_run_do_not_write(self):
        with tempfile.TemporaryDirectory() as raw:
            source = self.write_plan(raw)
            self.assertNotEqual(self.run_cli(raw, "--plan-file", str(source), "--date", "2026-2-3").returncode, 0)
            result = self.run_cli(raw, "--plan-file", str(source), "--dry-run")
            self.assertEqual(result.returncode, 0)
            self.assertFalse((Path(raw) / "research").exists())

    def test_strict_dates_and_duplicate_json_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = self.write_plan(root)
            self.assertNotEqual(self.run_cli(root, "--plan-file", str(source), "--date", "20260811").returncode, 0)
            source.write_text(json.dumps(plan())[:-1] + ', "goal": "overridden"}', encoding="utf-8")
            self.assertNotEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            self.assertFalse((root / "research").exists())
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = self.write_plan(root)
            self.assertEqual(self.run_cli(root, "--plan-file", str(source), "--date", "2026-08-11").returncode, 0)
            plan_path = root / "research" / "PLAN.md"
            plan_path.write_text(plan_path.read_text(encoding="utf-8").replace("frozen_at: 2026-08-11", "frozen_at: 20260811"), encoding="utf-8")
            self.assertNotEqual(self.run_cli(root, "--validate-only").returncode, 0)

    def test_idempotency_and_force(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = self.write_plan(root)
            self.assertEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            original = (root / "research" / "PLAN.md").read_text(encoding="utf-8")
            source.write_text(json.dumps(plan(goal="changed")), encoding="utf-8")
            self.assertEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            self.assertEqual(original, (root / "research" / "PLAN.md").read_text(encoding="utf-8"))
            self.assertEqual(self.run_cli(root, "--plan-file", str(source), "--force-overwrite").returncode, 0)
            current = (root / "research" / "PLAN.md").read_text(encoding="utf-8")
            self.assertIn("changed", current)
            self.assertIn("plan_revision: 2", current)
            self.assertEqual(self.run_cli(root, "--validate-only").returncode, 0)

    def test_initial_commit_failure_leaves_no_core_files_or_temps(self):
        with tempfile.TemporaryDirectory() as raw:
            research = Path(raw) / "research"
            files = {
                research / "PLAN.md": "new plan\n",
                research / "STATUS.md": "new status\n",
            }
            original_replace = INIT._replace

            def fail_status_commit(source, destination):
                if source.suffix == ".tmp" and destination.name == "STATUS.md":
                    raise OSError("injected STATUS commit failure")
                original_replace(source, destination)

            with mock.patch.object(INIT, "_replace", side_effect=fail_status_commit):
                with self.assertRaises(INIT.ContractError):
                    INIT.commit_core_files(files, overwrite=False)
            self.assertFalse((research / "PLAN.md").exists())
            self.assertFalse((research / "STATUS.md").exists())
            self.assertEqual(list(research.glob(".*.tmp")), [])
            self.assertEqual(list(research.glob(".*.bak")), [])

    def test_force_second_commit_failure_restores_original_core_bytes_and_revision(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = self.write_plan(root)
            self.assertEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            research = root / "research"
            plan_path, status_path = research / "PLAN.md", research / "STATUS.md"
            before_plan, before_status = plan_path.read_bytes(), status_path.read_bytes()
            before_revision = INIT.metadata(before_plan.decode("utf-8"))[0]["plan_revision"]
            files = {plan_path: "replacement plan\n", status_path: "replacement status\n"}
            original_replace = INIT._replace

            def fail_status_commit(source, destination):
                if source.suffix == ".tmp" and destination == status_path:
                    raise OSError("injected STATUS commit failure")
                original_replace(source, destination)

            with mock.patch.object(INIT, "_replace", side_effect=fail_status_commit):
                with self.assertRaises(INIT.ContractError):
                    INIT.commit_core_files(files, overwrite=True)
            self.assertEqual(plan_path.read_bytes(), before_plan)
            self.assertEqual(status_path.read_bytes(), before_status)
            self.assertEqual(INIT.metadata(plan_path.read_text(encoding="utf-8"))[0]["plan_revision"], before_revision)
            self.assertEqual(list(research.glob(".*.tmp")), [])
            self.assertEqual(list(research.glob(".*.bak")), [])

    def test_force_restore_failure_retains_original_backup_and_reports_path(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = self.write_plan(root)
            self.assertEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            research = root / "research"
            plan_path, status_path = research / "PLAN.md", research / "STATUS.md"
            before_plan, before_status = plan_path.read_bytes(), status_path.read_bytes()
            files = {plan_path: "replacement plan\n", status_path: "replacement status\n"}
            original_replace = INIT._replace

            def fail_status_commit_and_plan_restore(source, destination):
                if source.suffix == ".tmp" and destination == status_path:
                    raise OSError("injected STATUS commit failure")
                if source.suffix == ".bak" and destination == plan_path:
                    raise OSError("injected PLAN restore failure")
                original_replace(source, destination)

            with mock.patch.object(INIT, "_replace", side_effect=fail_status_commit_and_plan_restore):
                with self.assertRaises(INIT.ContractError) as raised:
                    INIT.commit_core_files(files, overwrite=True)
            retained = list(research.glob(".PLAN.md.*.bak"))
            self.assertEqual(len(retained), 1)
            self.assertEqual(retained[0].read_bytes(), before_plan)
            self.assertIn("injected PLAN restore failure", str(raised.exception))
            self.assertIn(str(retained[0]), str(raised.exception))
            self.assertEqual(status_path.read_bytes(), before_status)
            self.assertEqual(list(research.glob(".*.tmp")), [])
            self.assertEqual(list(research.glob(".STATUS.md.*.bak")), [])

    def test_json_validate_and_deprecated_slug(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = self.write_plan(root)
            result = self.run_cli(root, "--plan-file", str(source), "--project-slug", "ignored", "--json")
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)["status"], "initialized")
            self.assertIn("deprecated", result.stderr)
            result = self.run_cli(root, "--validate-only", "--json")
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)["status"], "valid")

    def test_layout_refusals_and_adoption_have_zero_write_guards(self):
        for old_prompt in ("session_start_prompt_zh.md", "session_bootstrap_prompt_zh.md"):
            with self.subTest(old_prompt=old_prompt), tempfile.TemporaryDirectory() as raw:
                root = Path(raw); old = root / "research" / "plans" / old_prompt; old.parent.mkdir(parents=True); old.write_text("legacy")
                source = self.write_plan(root)
                result = self.run_cli(root, "--plan-file", str(source))
                self.assertNotEqual(result.returncode, 0); self.assertFalse((root / "research" / "PLAN.md").exists())
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); research = root / "research"; research.mkdir(); (research / "notes.txt").write_text("keep")
            source = self.write_plan(root)
            self.assertNotEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            self.assertFalse((research / "PLAN.md").exists())
            self.assertEqual(self.run_cli(root, "--plan-file", str(source), "--adopt-existing-research-dir").returncode, 0)
            self.assertEqual((research / "notes.txt").read_text(), "keep")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); research = root / "research"; research.mkdir(); (research / "PLAN.md").write_text("partial")
            source = self.write_plan(root)
            self.assertNotEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            self.assertEqual((research / "PLAN.md").read_text(), "partial")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); research = root / "research"; research.mkdir(); (research / "PLAN.md").write_text("x"); (research / "plans").mkdir()
            (research / "plans" / "ACTIVE_PLAN.md").write_text("legacy")
            source = self.write_plan(root)
            self.assertNotEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            self.assertFalse((research / "STATUS.md").exists())

    def test_force_requires_existing_v2_and_bootstrap_warns(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = self.write_plan(root)
            self.assertNotEqual(self.run_cli(root, "--plan-file", str(source), "--force-overwrite").returncode, 0)
            result = subprocess.run([sys.executable, str(BOOTSTRAP), "--workspace-root", str(root), "--plan-file", str(source)], text=True, capture_output=True)
            self.assertEqual(result.returncode, 0); self.assertIn("deprecated", result.stderr)

    def test_invalid_layout_and_malformed_v2_are_read_only(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); (root / "research").write_text("not a directory")
            source = self.write_plan(root)
            result = self.run_cli(root, "--plan-file", str(source))
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((root / "research").read_text(), "not a directory")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); research = root / "research"; research.mkdir()
            (research / "PLAN.md").write_text("bad")
            (research / "STATUS.md").write_text("bad")
            result = self.run_cli(root, "--validate-only")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((research / "PLAN.md").read_text(), "bad")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); research = root / "research"; (research / "PLAN.md").mkdir(parents=True); (research / "STATUS.md").mkdir()
            result = self.run_cli(root, "--validate-only", "--json")
            self.assertEqual(json.loads(result.stdout)["layout"], "invalid")

    def test_nested_schema_duplicate_milestones_and_rich_rendering(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            bad = plan(scope={"in": ["x"], "out": [], "extra": []})
            source = self.write_plan(root, bad)
            self.assertNotEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            duplicate = plan(milestones=[{"id": "M1", "outcome": "one", "acceptance": ["a"]}, {"id": "M1", "outcome": "two", "acceptance": ["b"]}])
            source = self.write_plan(root, duplicate)
            self.assertNotEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            rich = plan(assumptions=["Network exists"], evidence=["Paper A"], alternatives_considered=[{"option": "Alt", "tradeoffs": ["Slow"]}])
            source = self.write_plan(root, rich)
            self.assertEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            text = (root / "research" / "PLAN.md").read_text(encoding="utf-8")
            self.assertIn("Network exists", text); self.assertIn("Paper A", text); self.assertIn("Alt (权衡: Slow)", text)

    def test_localized_generated_labels_validate_in_both_languages(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = self.write_plan(root)
            self.assertEqual(self.run_cli(root, "--plan-file", str(source), "--language", "zh").returncode, 0)
            zh_plan = (root / "research" / "PLAN.md").read_text(encoding="utf-8")
            zh_status = (root / "research" / "STATUS.md").read_text(encoding="utf-8")
            for label in ("范围内", "范围外", "冻结就绪度", "验收:", "- 无"):
                self.assertIn(label, zh_plan)
            self.assertNotIn("### In", zh_plan); self.assertNotIn("Freeze Readiness", zh_plan)
            self.assertIn("## 下一步", zh_status); self.assertIn("## 阻塞", zh_status); self.assertIn("## 必读", zh_status)
            self.assertEqual(self.run_cli(root, "--validate-only").returncode, 0)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = self.write_plan(root)
            self.assertEqual(self.run_cli(root, "--plan-file", str(source), "--language", "en").returncode, 0)
            en_plan = (root / "research" / "PLAN.md").read_text(encoding="utf-8")
            en_status = (root / "research" / "STATUS.md").read_text(encoding="utf-8")
            self.assertIn("### In", en_plan); self.assertIn("Freeze Readiness", en_plan)
            self.assertIn("## Next Action", en_status); self.assertEqual(self.run_cli(root, "--validate-only").returncode, 0)

    def test_stricter_freeze_invariants_fail_without_core_writes(self):
        cases = (
            plan(milestones=[{"id": "bad id", "outcome": "x", "acceptance": ["a"]}]),
            plan(alternatives_considered=[]),
            plan(alternatives_considered=[{"option": "Use stdlib", "tradeoffs": []}]),
            plan(alternatives_considered=[{"option": "Alt", "tradeoffs": []}, {"option": "Alt", "tradeoffs": []}]),
            plan(freeze_readiness="READY_WITH_ASSUMPTIONS", assumptions=[]),
            plan(next_action="Work\n## 阻塞"),
        )
        for value in cases:
            with self.subTest(value=value), tempfile.TemporaryDirectory() as raw:
                root = Path(raw); source = self.write_plan(root, value)
                result = self.run_cli(root, "--plan-file", str(source), "--json")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(json.loads(result.stdout)["status"], "invalid")
                self.assertFalse((root / "research").exists())

    def test_lone_surrogate_is_contract_error_with_zero_core_files(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = root / "plan.json"
            source.write_text(json.dumps(plan(goal="\ud800"), ensure_ascii=True), encoding="ascii")
            result = self.run_cli(root, "--plan-file", str(source), "--json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("UTF-8", " ".join(json.loads(result.stdout)["messages"]))
            self.assertFalse((root / "research").exists())

    def test_placeholder_payload_is_zero_write_but_todo_app_is_valid(self):
        placeholders = ("TODO: define goal", "TODO define goal", "TODO find owner", "TBD choose baseline", "TBD pending review", "TODO clarify scope", "TBD confirm owner", "TODO verify output", "TODO review results", "TODO replace asset", "TODO fix test", "TODO later", "TODO investigate failure", "TBD specify owner", "TODO resolve blocker", "<project goal>", "[待填写目标]", "[Fill in goal]")
        for goal in placeholders:
            with self.subTest(goal=goal), tempfile.TemporaryDirectory() as raw:
                root = Path(raw); source = self.write_plan(root, plan(goal=goal))
                result = self.run_cli(root, "--plan-file", str(source), "--json")
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((root / "research").exists())
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = self.write_plan(root, plan(project_name="TODO app"))
            self.assertEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            self.assertEqual(self.run_cli(root, "--validate-only").returncode, 0)

    def test_must_read_paths_exist_and_remain_inside_workspace(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = self.write_plan(root)
            self.assertEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            research = root / "research"; status = research / "STATUS.md"; notes = research / "NOTES.md"
            notes.write_text("Reference notes", encoding="utf-8")
            original = status.read_text(encoding="utf-8")
            status.write_text(original.replace("- research/PLAN.md", "- research/PLAN.md\n- research/NOTES.md"), encoding="utf-8")
            self.assertEqual(self.run_cli(root, "--validate-only").returncode, 0)
            status.write_text(original.replace("- research/PLAN.md", "- research/PLAN.md\n- research/MISSING.md"), encoding="utf-8")
            self.assertNotEqual(self.run_cli(root, "--validate-only").returncode, 0)
            status.write_text(original.replace("- research/PLAN.md", "- research/PLAN.md\n- ../outside.md"), encoding="utf-8")
            self.assertNotEqual(self.run_cli(root, "--validate-only").returncode, 0)

    def test_unknown_plans_directory_is_not_legacy(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); (root / "research" / "plans").mkdir(parents=True)
            source = self.write_plan(root)
            result = self.run_cli(root, "--plan-file", str(source), "--json")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)["layout"], "unknown")

    def test_validate_rejects_missing_sections_and_placeholders(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = self.write_plan(root)
            self.assertEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            plan_path = root / "research" / "PLAN.md"
            plan_path.write_text(plan_path.read_text(encoding="utf-8").replace("## 问题", "## Removed"), encoding="utf-8")
            self.assertNotEqual(self.run_cli(root, "--validate-only").returncode, 0)
            plan_path.write_text(plan_path.read_text(encoding="utf-8").replace("## Removed", "## 问题") + "\nTODO\n", encoding="utf-8")
            self.assertNotEqual(self.run_cli(root, "--validate-only").returncode, 0)
            text = plan_path.read_text(encoding="utf-8").replace("\nTODO\n", "\n")
            plan_path.write_text(text.replace("# Unicode 研究计划", "# "), encoding="utf-8")
            self.assertNotEqual(self.run_cli(root, "--validate-only").returncode, 0)

    def test_status_shape_and_lazy_records_are_strictly_validated(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = self.write_plan(root)
            self.assertEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            research = root / "research"; status = research / "STATUS.md"
            status.write_text(status.read_text(encoding="utf-8") + "\n## 风险\nCopied plan content\n", encoding="utf-8")
            self.assertNotEqual(self.run_cli(root, "--validate-only").returncode, 0)
            status.write_text(status.read_text(encoding="utf-8").replace("\n## 风险\nCopied plan content\n", "\n"), encoding="utf-8")
            good = research / "records" / "decisions" / "2026-08-11-ship-it.md"; good.parent.mkdir(parents=True); good.write_text("Decision recorded", encoding="utf-8")
            self.assertEqual(self.run_cli(root, "--validate-only").returncode, 0)
            good.rename(good.with_name("2026-08-11-Bad.md"))
            self.assertNotEqual(self.run_cli(root, "--validate-only").returncode, 0)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = self.write_plan(root)
            self.assertEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            records = root / "research" / "records"; (records / "reviews").mkdir(parents=True)
            self.assertNotEqual(self.run_cli(root, "--validate-only").returncode, 0)
            (records / "reviews").rmdir(); (records / "unknown").mkdir()
            self.assertNotEqual(self.run_cli(root, "--validate-only").returncode, 0)
            (records / "unknown").rmdir(); bad = records / "handoffs" / "2026-08-11-next.md"; bad.parent.mkdir(); bad.write_text("TODO define handoff", encoding="utf-8")
            self.assertNotEqual(self.run_cli(root, "--validate-only").returncode, 0)
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = self.write_plan(root)
            self.assertEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            record = root / "research" / "records" / "retrospectives" / "2026-08-11-template.md"; record.parent.mkdir(parents=True)
            record.write_text((ROOT / "assets" / "TEMPLATE_retrospective_zh.md").read_text(encoding="utf-8"), encoding="utf-8")
            self.assertNotEqual(self.run_cli(root, "--validate-only").returncode, 0)
            record.write_text("Ordinary {braces} are valid.", encoding="utf-8")
            self.assertEqual(self.run_cli(root, "--validate-only").returncode, 0)

    def test_adopt_validates_existing_lazy_records_before_core_writes(self):
        invalid_builders = (
            lambda research: (research / "records" / "reviews").mkdir(parents=True),
            lambda research: (research / "records" / "decisions" / "bad.md").parent.mkdir(parents=True) or (research / "records" / "decisions" / "bad.md").write_text("record", encoding="utf-8"),
            lambda research: (research / "records" / "handoffs" / "2026-08-11-next.md").parent.mkdir(parents=True) or (research / "records" / "handoffs" / "2026-08-11-next.md").write_text("{{owner}}", encoding="utf-8"),
        )
        for build in invalid_builders:
            with self.subTest(build=build), tempfile.TemporaryDirectory() as raw:
                root = Path(raw); research = root / "research"; build(research); source = self.write_plan(root)
                result = self.run_cli(root, "--plan-file", str(source), "--adopt-existing-research-dir", "--json")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(json.loads(result.stdout)["layout"], "unknown")
                self.assertFalse((research / "PLAN.md").exists()); self.assertFalse((research / "STATUS.md").exists())
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); research = root / "research"; record = research / "records" / "reviews" / "2026-08-11-accepted.md"; record.parent.mkdir(parents=True); record.write_text("Reviewed and accepted.", encoding="utf-8")
            source = self.write_plan(root)
            self.assertEqual(self.run_cli(root, "--plan-file", str(source), "--adopt-existing-research-dir").returncode, 0)
            self.assertEqual(self.run_cli(root, "--validate-only").returncode, 0)

    def test_force_preserves_status_progress_and_unrelated_records(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = self.write_plan(root)
            self.assertEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            research = root / "research"; status = research / "STATUS.md"
            status_text = status.read_text(encoding="utf-8")
            status_text = status_text.replace("state: planned", "state: in_progress")
            status_text = status_text.replace("## 阻塞\n- 无", "## 阻塞\nWaiting for review\nOwner: team")
            status_text = status_text.replace("## 必读\n- research/PLAN.md", "## 必读\n- research/PLAN.md\n- research/NOTES.md")
            status.write_text(status_text, encoding="utf-8")
            notes = research / "NOTES.md"; notes.write_text("unchanged", encoding="utf-8")
            record = research / "records" / "decisions" / "2026-08-11-record.md"; record.parent.mkdir(parents=True); record.write_text("record", encoding="utf-8")
            source.write_text(json.dumps(plan(next_action="Ship it")), encoding="utf-8")
            self.assertEqual(self.run_cli(root, "--plan-file", str(source), "--force-overwrite").returncode, 0)
            updated = status.read_text(encoding="utf-8")
            self.assertIn("state: in_progress", updated); self.assertIn("current_milestone: M1", updated)
            self.assertIn("Waiting for review\nOwner: team", updated); self.assertIn("research/NOTES.md", updated); self.assertIn("Ship it", updated)
            self.assertEqual(notes.read_text(encoding="utf-8"), "unchanged"); self.assertEqual(record.read_text(encoding="utf-8"), "record")
            self.assertEqual(self.run_cli(root, "--validate-only").returncode, 0)
            replacement = plan(
                milestones=[{"id": "M2", "outcome": "Release", "acceptance": ["Published"]}],
                next_action="Release",
            )
            source.write_text(json.dumps(replacement), encoding="utf-8")
            self.assertEqual(self.run_cli(root, "--plan-file", str(source), "--force-overwrite").returncode, 0)
            updated = status.read_text(encoding="utf-8")
            self.assertIn("state: in_progress", updated); self.assertIn("current_milestone: M2", updated)

    def test_legacy_validation_and_v2_metadata_consistency(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); legacy = root / "research" / "plans"; legacy.mkdir(parents=True)
            (root / "research" / "README.md").write_text("old")
            (legacy / "ACTIVE_PLAN.md").write_text("\n".join(f"{key}: x" for key in ("goal", "current_milestone", "must_read", "locked_decisions", "next_action", "out_of_scope", "latest_retrospective", "last_updated")))
            project = legacy / "old"; project.mkdir(); (project / "master_plan_zh.md").write_text("old")
            (legacy / "session_start_prompt_zh.md").write_text("old")
            retro = root / "research" / "retrospectives" / "old"; retro.mkdir(parents=True); (retro / "README.md").write_text("old"); (retro / "TEMPLATE_retrospective_zh.md").write_text("old")
            result = self.run_cli(root, "--validate-only", "--json")
            self.assertEqual(result.returncode, 0); self.assertEqual(json.loads(result.stdout)["layout"], "v1")
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = self.write_plan(root)
            self.assertEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            status = root / "research" / "STATUS.md"
            status.write_text(status.read_text(encoding="utf-8").replace("plan_revision: 1", "plan_revision: 2"), encoding="utf-8")
            self.assertNotEqual(self.run_cli(root, "--validate-only").returncode, 0)
            status.write_text(status.read_text(encoding="utf-8").replace("plan_revision: 2", "plan_revision: 1").replace("state: planned", "state: in_progress"), encoding="utf-8")
            self.assertEqual(self.run_cli(root, "--validate-only").returncode, 0)
            status.write_text(status.read_text(encoding="utf-8").replace("current_milestone: M1", "current_milestone: M9"), encoding="utf-8")
            self.assertNotEqual(self.run_cli(root, "--validate-only").returncode, 0)

    def test_force_invalid_payload_reports_existing_v2_layout(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = self.write_plan(root)
            self.assertEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            source.write_text('{"broken": true}', encoding="utf-8")
            result = self.run_cli(root, "--plan-file", str(source), "--force-overwrite", "--json")
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout)["layout"], "v2")

    def test_cross_validation_uses_milestone_section_and_exact_must_read_line(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = self.write_plan(root)
            self.assertEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            plan_path = root / "research" / "PLAN.md"
            text = plan_path.read_text(encoding="utf-8")
            text = text.replace("- M1 - Working CLI (验收: Tests pass)", "No declared milestone")
            plan_path.write_text(text + "\n- M1 - Forged outside section (验收: x)\n", encoding="utf-8")
            result = self.run_cli(root, "--validate-only", "--json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("current_milestone", " ".join(json.loads(result.stdout)["messages"]))
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw); source = self.write_plan(root)
            self.assertEqual(self.run_cli(root, "--plan-file", str(source)).returncode, 0)
            status = root / "research" / "STATUS.md"
            status.write_text(status.read_text(encoding="utf-8").replace("- research/PLAN.md", "- research/PLAN.md.bak"), encoding="utf-8")
            result = self.run_cli(root, "--validate-only", "--json")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must_read", " ".join(json.loads(result.stdout)["messages"]))


if __name__ == "__main__":
    unittest.main()
