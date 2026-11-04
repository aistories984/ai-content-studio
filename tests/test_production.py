"""Flow intake/handoff contracts against isolated real Store records."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from studio.store import Problem, ROOT, Store

BRIEF = {"topic": "A small robot learns to garden", "audience": "Curious adults", "format": "short", "target_seconds": 24, "style": "Warm illustrated story"}


class ProductionTests(unittest.TestCase):
    def setUp(self):
        # A missing implementation is an expected assertion failure during RED.
        spec = importlib.util.find_spec("studio.production")
        self.assertIsNotNone(spec, "Flow production intake/handoff is not implemented")
        from studio import production
        self.production = production
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(self.temp.name)

    def create(self, **changes):
        return self.production.create_project(self.store, {**BRIEF, **changes})

    def test_missing_each_required_field_rejects(self):
        for field in BRIEF:
            with self.subTest(field=field):
                payload = dict(BRIEF)
                del payload[field]
                with self.assertRaises(Problem):
                    self.production.normalize_brief(payload)

    def test_invalid_duration_rejects_bool_nonfinite_wrong_type_and_bounds(self):
        for value in (True, False, None, "24", [], {}, float("nan"), float("inf"), -1, 0, 1.99, 14400.01):
            with self.subTest(value=value), self.assertRaises(Problem):
                self.production.normalize_brief({**BRIEF, "target_seconds": value})

    def test_invalid_text_format_and_optional_fields_reject(self):
        for field in ("topic", "audience", "style"):
            for value in (None, True, 123, [], {}, "", "  "):
                with self.subTest(field=field, value=value), self.assertRaises(Problem):
                    self.production.normalize_brief({**BRIEF, field: value})
        for field, value in (("format", "Short"), ("format", []), ("context", {}), ("creator_voice", True), ("research_requested", "yes"), ("research_requested", 1)):
            with self.subTest(field=field), self.assertRaises(Problem):
                self.production.normalize_brief({**BRIEF, field: value})
        for value in ([], None, "brief"):
            with self.assertRaises(Problem):
                self.production.normalize_brief(value)

    def test_short_persists_normalized_brief_and_derives_runtime_and_ratio(self):
        p = self.create(topic="  A small robot learns to garden  ", creator_voice="Measured and curious", context="An original fiction", research_requested=False)
        reopened = Store(self.temp.name).project(p["id"])
        self.assertEqual(reopened["workflow_id"], "comic-to-flow")
        self.assertEqual(reopened["settings"]["runtime_minutes"], .4)
        self.assertEqual(reopened["settings"]["aspect_ratio"], "9:16")
        self.assertEqual(reopened["settings"]["production_brief"]["topic"], BRIEF["topic"])
        self.assertEqual(reopened["settings"]["production_brief"]["creator_voice"], "Measured and curious")
        self.assertFalse(reopened["settings"]["production_brief"]["research_requested"])

    def test_long_defaults_landscape_and_explicit_ratio_is_preserved(self):
        self.assertEqual(self.create(format="long")["settings"]["aspect_ratio"], "16:9")
        self.assertEqual(self.create(aspect_ratio="1:1")["settings"]["aspect_ratio"], "1:1")
        with self.assertRaises(Problem):
            self.create(aspect_ratio="cinema")

    def test_flow_duration_edges_and_existing_modes_keep_original_minimum(self):
        self.assertAlmostEqual(self.create(target_seconds=2)["settings"]["runtime_minutes"], 2/60)
        self.assertEqual(self.create(target_seconds=14400)["settings"]["runtime_minutes"], 240)
        for workflow in ("comic-to-wan", "sprite-to-flow"):
            with self.subTest(workflow=workflow), self.assertRaises(Problem):
                self.store.create_project({"title": "Existing", "workflow_id": workflow, "runtime_minutes": 2/60})
            p = self.store.create_project({"title": "Existing", "workflow_id": workflow})
            self.assertEqual(p["settings"]["runtime_minutes"], 2)

    def test_direct_store_creation_enforces_brief_and_derived_settings(self):
        with self.assertRaises(Problem):
            self.store.create_project({"title": "Missing", "workflow_id": "comic-to-flow"})
        p = self.store.create_project({"title": "Direct", "workflow_id": "comic-to-flow", "production_brief": BRIEF, "runtime_minutes": 80})
        self.assertEqual(p["settings"]["runtime_minutes"], .4)
        self.assertEqual(p["settings"]["aspect_ratio"], "9:16")

    def test_generic_updates_cannot_silently_change_intake_fields(self):
        p = self.create()
        for field, value in (("production_brief", {**BRIEF, "topic": "Other"}), ("target_seconds", 12), ("audience", "Other"), ("runtime_minutes", 3), ("aspect_ratio", "16:9"), ("settings", {"production_brief": BRIEF})):
            with self.subTest(field=field), self.assertRaises(Problem):
                self.store.update_project(p["id"], {"expected_revision": 1, field: value})
        self.assertEqual(self.store.project(p["id"])["revision"], 1)
        revised = self.store.update_project(p["id"], {"expected_revision": 1, "title": "New title"})
        self.assertEqual(revised["revision"], 2)

    def test_flow_workflow_preserves_diagram_deliverables_scopes_and_gates(self):
        p = self.create()
        self.assertEqual(self.store.next_action(p["id"])["stage"], "premise")
        workflow = p["workflow"]
        self.assertEqual([(s["id"], s["kind"], s["scope"]) for s in workflow["stages"]], [
            ("premise", "premise", "project"), ("comic", "comic", "project"), ("script", "script", "project"), ("audio", "audio", "scene"), ("boards", "storyboard", "scene"), ("blender", "previs", "scene"), ("flow", "video", "scene"), ("edit", "edit", "project")])
        self.assertEqual(set(workflow["diagram_mapping"]), {"brief", "premise", "comic", "script", "audio", "boards", "blender", "package", "spend", "wan", "takes", "edit"})
        self.assertEqual(workflow["provider"], "Google Flow")
        self.assertEqual(workflow["execution"], "browser_ui")
        self.assertNotIn("model", workflow)
        old = self.store.create_project({"title": "Old film"})
        self.assertIn("wan", [s["id"] for s in old["workflow"]["stages"]])
        for stage, kind in (("script", "script"), ("flow", "video")):
            result = self.store.add_version(p["id"], {"title": "Too early", "stage": stage, "kind": kind, "content": "Early fixture"})
            with self.assertRaises(Problem):
                self.store.review(result["version_id"], "approved")
        self.assertEqual(self.store.next_action(p["id"])["stage"], "premise")

    def test_flow_generation_fails_closed_with_explicit_missing_adapter(self):
        p = self.create()
        scene = self.store.save_scene(p["id"], {"title": "First"})
        with self.assertRaisesRegex(Problem, "Flow film adapter") as caught:
            self.store.generation_package(p["id"], scene)
        self.assertEqual(caught.exception.status, 409)

    def test_flow_intake_cannot_enable_legacy_demo_gate_bypass(self):
        with self.assertRaises(Problem):
            self.create(demo=True)
        with self.assertRaises(Problem):
            self.store.create_project({"title": "Direct demo bypass", "workflow_id": "comic-to-flow", "production_brief": BRIEF, "demo": True})

    def test_handoff_considers_all_skills_with_real_paths_hashes_and_no_execution(self):
        p = self.create(research_requested=True)
        handoff = self.production.get_handoff(Store(self.temp.name), p["id"])
        self.assertEqual(handoff["brief"]["topic"], BRIEF["topic"])
        self.assertEqual(handoff["next_action"]["stage"], "premise")
        self.assertEqual({s["name"] for s in handoff["catalog"]}, {"yt-viral", "yt-plan", "yt-script", "yt-package", "yt-edit", "yt-shorts", "yt-chapters", "yt-seo", "yt-comment", "yt-retention", "yt-audit"})
        self.assertTrue(all(s["reason"] for s in handoff["catalog"]))
        self.assertIn("yt-viral", {s["name"] for s in handoff["skills"]})
        self.assertIn("director-studio", {s["name"] for s in handoff["skills"]})
        for selected in handoff["skills"]:
            path = ROOT / selected["path"]
            self.assertTrue(path.is_file())
            self.assertEqual(selected["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
            self.assertEqual(selected["status"], "not_run")
            self.assertTrue(selected["required_inputs"])
            self.assertTrue(selected["intended_outputs"])
            self.assertTrue(selected["approval_gates"])
        self.assertEqual(handoff["evidence"], [])
        self.assertTrue(handoff["blockers"])
        self.assertEqual(handoff["automation"], {"browser_ready": False, "generation_ready": False, "render_ready": False, "publish_ready": False})

    def test_handoff_preserves_waiting_review_and_rejects_other_modes_and_foreign_scene(self):
        p = self.create()
        saved = self.store.add_version(p["id"], {"title": "Premise", "kind": "premise", "stage": "premise", "content": "An original fixture story"})
        self.store.submit(saved["version_id"])
        h = self.production.get_handoff(self.store, p["id"])
        self.assertEqual(h["next_action"]["state"], "awaiting_review")
        self.assertEqual(h["next_action"]["review_versions"], [saved["version_id"]])
        other = self.store.create_project({"title": "Other"})
        scene = self.store.save_scene(other["id"], {"title": "Foreign"})
        with self.assertRaises(Problem):
            self.production.get_handoff(self.store, other["id"])
        with self.assertRaises(Problem):
            self.production.get_handoff(self.store, p["id"], scene)

    def receipt(self, p, *, metadata=None, receipt=None, with_file=True):
        skill = ROOT / ".agents/skills/yt-script"
        execution = metadata if metadata is not None else {
            "tool_name": "hookscore", "skill_name": "yt-script", "skill_sha256": hashlib.sha256((skill / "SKILL.md").read_bytes()).hexdigest(),
            "script_sha256": hashlib.sha256((skill / "hookscore.py").read_bytes()).hexdigest(), "input_files": [], "argv": ["--hook", "You can grow a garden in 3 steps", "--json"],
            "resource_hashes": {".agents/skills/yt-script/hooks.json": hashlib.sha256((skill / "hooks.json").read_bytes()).hexdigest()}, "status": "succeeded"}
        result = json.loads(subprocess.run([sys.executable, str(skill / "hookscore.py"), "--hook", "You can grow a garden in 3 steps", "--json"], check=True, text=True, capture_output=True).stdout)
        body = receipt if receipt is not None else {"youtube_execution": execution, "result": result}
        uploads = [("receipt.json", json.dumps(body).encode())] if with_file else None
        return self.store.add_version(p["id"], {"title": "Tool receipt fixture", "kind": "notes", "stage": "premise", "metadata": {"youtube_execution": execution}, "content": "Real local fixture tool output; no creative approval."}, uploaded=uploads)

    def test_names_or_metadata_without_registered_receipt_never_count_as_execution(self):
        p = self.create()
        self.store.add_version(p["id"], {"title": "Names", "kind": "notes", "metadata": {"skills": ["yt-script"]}, "content": "Names only"})
        self.receipt(p, with_file=False)
        self.receipt(p, metadata={"tool_name": "hookscore", "skill_name": "yt-script", "status": "succeeded"})
        self.assertEqual(self.production.get_handoff(self.store, p["id"])["evidence"], [])

    def test_registered_execution_evidence_survives_reopen_and_carries_review_status(self):
        p = self.create()
        saved = self.receipt(p)
        self.store.submit(saved["version_id"])
        h = self.production.get_handoff(Store(self.temp.name), p["id"])
        self.assertEqual(len(h["evidence"]), 1)
        evidence = h["evidence"][0]
        self.assertEqual(evidence["artifact_id"], saved["artifact_id"])
        self.assertEqual(evidence["version_id"], saved["version_id"])
        self.assertEqual(evidence["tool_name"], "hookscore")
        self.assertEqual(evidence["status"], "in_review")
        self.assertFalse(evidence["stale"])
        self.assertEqual(next(s for s in h["skills"] if s["name"] == "yt-script")["status"], "has_evidence")
        self.assertEqual(h["next_action"]["stage"], "premise")
        self.assertFalse(self.store.project(p["id"])["stage_status"][0]["complete"])

    def test_changed_missing_or_mismatched_receipt_is_rejected_without_crashing_handoff(self):
        for failure in ("changed", "missing", "mismatched", "bad_result"):
            with self.subTest(failure=failure):
                p = self.create()
                receipt = {"youtube_execution": {}, "result": []} if failure == "mismatched" else None
                saved = self.receipt(p, receipt=receipt)
                path, _ = self.store.file_path(saved["version_id"], 0)
                if failure == "changed":
                    path.write_text('{"result": []}')
                elif failure == "missing":
                    path.unlink()
                elif failure == "bad_result":
                    p2 = self.create()
                    old = json.loads(path.read_text())
                    old.pop("result")
                    self.receipt(p2, receipt=old)
                    p = p2
                h = self.production.get_handoff(self.store, p["id"])
                self.assertEqual(h["evidence"], [])
                self.assertTrue(any("receipt" in b.lower() for b in h["blockers"]))

    def test_stale_tool_evidence_is_historical_and_does_not_mark_current_skill_executed(self):
        p = self.create()
        self.receipt(p)
        self.store.update_project(p["id"], {"expected_revision": 1, "creative_locks": "Rework the protagonist"})
        h = self.production.get_handoff(self.store, p["id"])
        self.assertTrue(h["evidence"][0]["stale"])
        self.assertEqual(h["evidence"][0]["effective_status"], "needs_update")
        self.assertEqual(next(s for s in h["skills"] if s["name"] == "yt-script")["status"], "not_run")

    def test_superseded_receipt_is_historical_and_cannot_mark_current_execution(self):
        p = self.create()
        saved = self.receipt(p)
        self.store.add_version(p["id"], {"title": "Replacement", "artifact_id": saved["artifact_id"],
            "expected_version": saved["version_id"], "content": "Previous output withdrawn", "metadata": {}, "inherit_files": False})
        h = self.production.get_handoff(Store(self.temp.name), p["id"])
        self.assertEqual(next(s for s in h["skills"] if s["name"] == "yt-script")["status"], "not_run")
        self.assertEqual(len(h["evidence"]), 1)
        self.assertEqual(h["evidence"][0]["version_id"], saved["version_id"])
        self.assertFalse(h["evidence"][0]["is_current"])
        self.assertTrue(h["evidence"][0]["historical"])

    def test_current_verified_receipt_is_explicitly_current(self):
        p = self.create()
        self.receipt(p)
        h = self.production.get_handoff(self.store, p["id"])
        self.assertIs(h["evidence"][0].get("is_current"), True)
        self.assertIs(h["evidence"][0].get("historical"), False)

    def test_receipts_with_nonfinite_result_or_unrecognized_resource_paths_are_invalid(self):
        for failure in ("nonfinite", "resource"):
            p = self.create()
            saved = self.receipt(p)
            record = self.store.get_version(saved["version_id"])
            execution = record["version"]["metadata"]["youtube_execution"]
            if failure == "resource":
                execution["resource_hashes"]["/etc/passwd"] = "0" * 64
            body = {"youtube_execution": execution, "result": {"value": float("nan") if failure == "nonfinite" else 1}}
            other = self.create()
            self.receipt(other, metadata=execution, receipt=body)
            self.assertEqual(self.production.get_handoff(self.store, other["id"])["evidence"], [])

    def test_huge_integer_duration_is_a_validation_problem(self):
        try:
            with self.assertRaises(Problem):
                self.production.normalize_brief({**BRIEF, "target_seconds": 10**1000})
        except OverflowError:
            self.fail("Oversized numeric input must raise Problem rather than OverflowError")

    def test_requested_research_is_honestly_deferred_after_premise(self):
        p = self.create(research_requested=True)
        saved = self.store.add_version(p["id"], {"title": "Premise", "kind": "premise", "stage": "premise", "content": "Original fixture story"})
        self.store.review(saved["version_id"], "approved")
        h = self.production.get_handoff(self.store, p["id"])
        self.assertEqual(h["next_action"]["stage"], "comic")
        research = next(entry for entry in h["catalog"] if entry["name"] == "yt-viral")
        self.assertEqual(research["applicability"], "deferred")
        self.assertNotIn("not requested", research["reason"].lower())
        self.assertIn("premise", research["reason"].lower())


if __name__ == "__main__":
    unittest.main()
