"""Local execution, provenance and lease failures against disposable Store records."""
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from studio import production
from studio.store import Problem, ROOT, Store

BRIEF = {"topic": "A robot learns gardening", "audience": "Curious adults", "format": "short", "target_seconds": 24, "style": "Illustrated"}
HOOK = "You waste 3 hours editing: what if one cut fixed it?"


class SkillRunnerTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec("studio.skill_runner"), "Allowlisted YouTube execution is not implemented")
        from studio import skill_runner
        self.runner = skill_runner
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.store = Store(self.folder / "data")
        self.project = production.create_project(self.store, BRIEF)["id"]
        self.claim = self.store.claim(self.project, "runner-test")

    def run_tool(self, tool="hookscore", args=None, **kw):
        return self.runner.run_tool(self.store, kw.pop("project_id", self.project), tool,
                                    args if args is not None else ["--hook", HOOK],
                                    kw.pop("task_id", self.claim["task_id"]), kw.pop("token", self.claim["token"]))

    def transcript(self):
        path = self.folder / "captions.srt"
        path.write_text("\n\n".join(f"{i+1}\n00:00:{i*10:02d},000 --> 00:00:{i*10+5:02d},000\n{line}" for i, line in enumerate([
            "Your opening makes a concrete promise.", "Um", "Your opening makes a concrete promise with proof.",
            "Camera framing shows the reference character.", "Editing joins the approved scene takes.", "Credits identify the production sources."])))
        return path

    def assert_no_artifacts(self):
        self.assertEqual(self.store.project(self.project)["artifacts"], [])

    def test_real_hook_and_title_receipts_survive_reopen_without_advancing(self):
        hook = self.run_tool()
        title = self.run_tool("title", ["--title", "3 editing mistakes", "--thumb", "EDITING MISTAKES", "--json"])
        self.assertEqual(hook["result"][0]["hook"], HOOK)
        self.assertEqual(len(hook["result"][0]["properties"]), 5)
        self.assertIn("duplicate", [issue[0] for issue in title["result"][0]["issues"]])
        reopened = Store(self.folder / "data")
        handoff = production.get_handoff(reopened, self.project)
        self.assertEqual({item["version_id"] for item in handoff["evidence"]}, {hook["version_id"], title["version_id"]})
        self.assertTrue(all(item["is_current"] and not item["historical"] for item in handoff["evidence"]))
        self.assertEqual(handoff["next_action"]["stage"], "premise")
        self.assertEqual(handoff["next_action"]["state"], "ready")
        for result, skill, script in [(hook, "yt-script", "hookscore.py"), (title, "yt-package", "title.py")]:
            record = reopened.get_version(result["version_id"])
            version = record["version"]
            self.assertEqual(record["artifact"]["kind"], "notes")
            self.assertEqual(version["status"], "draft")
            self.assertEqual(version["inputs"], [])
            receipt = json.loads(reopened.file_path(result["version_id"], 0)[0].read_text())
            self.assertEqual(set(receipt), {"youtube_execution", "result"})
            self.assertEqual(receipt["result"], result["result"])
            metadata = receipt["youtube_execution"]
            self.assertEqual(metadata, version["metadata"]["youtube_execution"])
            self.assertEqual(metadata["status"], "succeeded")
            self.assertEqual(metadata["skill_name"], skill)
            for field, filename in [("skill_sha256", "SKILL.md"), ("script_sha256", script)]:
                self.assertEqual(metadata[field], hashlib.sha256((ROOT / ".agents/skills" / skill / filename).read_bytes()).hexdigest())
            self.assertIn("--json", metadata["argv"])
            self.assertNotIn(self.claim["token"], json.dumps(receipt))
        p = reopened.project(self.project)
        self.assertFalse(p["stage_status"][0]["complete"])
        self.assertEqual(p["tasks"][0]["status"], "claimed")

    def test_tool_invocation_is_shown_in_saved_prompt(self):
        saved = self.run_tool()
        version = self.store.get_version(saved["version_id"])["version"]
        self.assertIn("hookscore", version["prompt"])
        self.assertIn(HOOK, version["prompt"])
        self.assertNotIn(self.claim["token"], version["prompt"])

    def test_file_modes_capture_exact_hashes_for_all_six_tools(self):
        transcript = self.transcript()
        csv = self.folder / "retention.csv"
        csv.write_text("position,retention\n" + "\n".join(f"{i*10},{100-i*5}" for i in range(11)))
        videos = self.folder / "videos.json"
        videos.write_text(json.dumps([{"channel": "fixture", "title": "3 editing mistakes", "views": v} for v in [100, 100, 100, 1000]]))
        hooks = self.folder / "hooks.txt"
        hooks.write_text(HOOK)
        cases = [("hookscore", [str(hooks)], [hooks]), ("title", [str(hooks), "--thumb", "SAVE TIME"], [hooks]),
                 ("deadair", [str(transcript), "--floor", ".35"], [transcript]),
                 ("chapters", [str(transcript), "--target", "3"], [transcript]),
                 ("retention", [str(csv), "--duration", "100", "--transcript", str(transcript)], [csv, transcript]),
                 ("swipe", [str(videos), "--min", "2"], [videos])]
        for tool, args, inputs in cases:
            with self.subTest(tool=tool):
                result = self.run_tool(tool, args)
                meta = self.store.get_version(result["version_id"])["version"]["metadata"]["youtube_execution"]
                self.assertEqual(meta["input_files"], [{"path": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in inputs])
                if tool == "deadair":
                    self.assertEqual({c["kind"] for c in result["result"]["cuts"]}, {"FILLER", "DEAD", "REPEAT"})
                elif tool == "chapters":
                    self.assertTrue(result["result"]["valid"])
                elif tool == "retention":
                    self.assertEqual(result["result"]["hook_leak"], 15)
                elif tool == "swipe":
                    self.assertEqual(result["result"]["outliers"][0]["multiple"], 10)

    def test_rejects_unknown_flags_bad_arity_and_unbounded_values_before_execution(self):
        transcript = str(self.transcript())
        cases = [("python", []), ("hookscore", []), ("hookscore", ["--hook"]), ("hookscore", ["--hook", "ok", "extra"]),
                 ("hookscore", ["--hook", "ok", "--json", "--json"]), ("hookscore", ["--hook", "ok", "--evil"]),
                 ("hookscore", "--hook text"), ("hookscore", [True]), ("hookscore", ["--hook", "x" * 20001]),
                 ("title", ["--thumb", "alone"]), ("title", ["--title", "ok", "--title", "other"]),
                 ("deadair", [transcript, "--floor", "NaN"]), ("deadair", [transcript, "--floor", "-1"]),
                 ("chapters", [transcript, "--target", "3.5"]), ("chapters", [transcript, "--target", "100000"]),
                 ("retention", [transcript, "--duration", "Infinity"]), ("retention", [transcript, "--duration", "0"]),
                 ("swipe", [transcript, "--min", "-1"]), ("hookscore", ["--hook", self.claim["token"]])]
        for tool, args in cases:
            with self.subTest(tool=tool, args=str(args)[:100]), patch.object(self.runner.subprocess, "run", side_effect=AssertionError("invalid request executed")):
                with self.assertRaises(Problem):
                    self.run_tool(tool, args)
                self.assert_no_artifacts()

    def test_relative_missing_oversized_and_directory_input_files_reject(self):
        large = self.folder / "large.txt"
        large.write_bytes(b"a" * (5 * 1024 * 1024 + 1))
        for value in ["relative.srt", str(self.folder / "missing.srt"), str(self.folder), str(large)]:
            with self.subTest(value=value), self.assertRaises(Problem):
                self.run_tool("deadair", [value])
        self.assert_no_artifacts()

    def test_invalid_json_input_rejects_nonfinite_values(self):
        path = self.folder / "whisper.json"
        for raw in ['{"segments": [], "value": NaN}', '{"value": 1e999}', '[Infinity]', '[']:
            path.write_text(raw)
            with self.subTest(raw=raw), self.assertRaises(Problem):
                self.run_tool("deadair", [str(path)])
        self.assert_no_artifacts()

    def test_bad_wrong_project_and_expired_leases_never_execute(self):
        other = production.create_project(self.store, BRIEF)["id"]
        for changes in [{"token": "wrong"}, {"project_id": other}]:
            with patch.object(self.runner.subprocess, "run", side_effect=AssertionError("invalid lease executed")), self.assertRaises(Problem):
                self.run_tool(**changes)
        with self.store.db(True) as db:
            db.execute("UPDATE tasks SET expires=0 WHERE id=?", (self.claim["task_id"],))
        with patch.object(self.runner.subprocess, "run", side_effect=AssertionError("expired lease executed")), self.assertRaises(Problem):
            self.run_tool()
        self.assert_no_artifacts()

    def test_wrong_scene_lease_cannot_execute_or_register(self):
        foreign = production.create_project(self.store, BRIEF)["id"]
        scene = self.store.save_scene(foreign, {"title": "Foreign"})
        with self.store.db(True) as db:
            db.execute("UPDATE tasks SET scene_id=? WHERE id=?", (scene, self.claim["task_id"]))
        with patch.object(self.runner.subprocess, "run", side_effect=AssertionError("wrong scene executed")), self.assertRaises(Problem):
            self.run_tool()
        self.assert_no_artifacts()

    def test_nonzero_actual_subprocess_does_not_create_artifact(self):
        empty = self.folder / "empty.srt"
        empty.write_text("not a transcript")
        with self.assertRaises(Problem):
            self.run_tool("deadair", [str(empty)])
        self.assert_no_artifacts()

    def fake_process(self, stdout=b'{}', stderr=b'', code=0, change=None):
        def run(argv, **kwargs):
            self.assertIsInstance(argv, list)
            self.assertNotIn(self.claim["token"], argv)
            self.assertFalse(kwargs.get("shell", False))
            self.assertEqual(kwargs["timeout"], 60)
            kwargs["stdout"].write(stdout)
            kwargs["stderr"].write(stderr)
            if change:
                change()
            return subprocess.CompletedProcess(argv, code)
        return run

    def test_malformed_nonfinite_scalar_and_oversized_output_never_register(self):
        for raw in [b'not JSON', b'{"x":NaN}', b'[Infinity]', b'{"x":1e999}', b'7', b'{"x":"' + b'a' * (5 * 1024 * 1024) + b'"}']:
            with self.subTest(raw=raw[:25]), patch.object(self.runner.subprocess, "run", side_effect=self.fake_process(raw)), self.assertRaises(Problem):
                self.run_tool()
            self.assert_no_artifacts()

    def test_timeout_and_os_errors_become_problem_without_registration(self):
        for error in [subprocess.TimeoutExpired("fixed tool", 60), OSError("process unavailable")]:
            with patch.object(self.runner.subprocess, "run", side_effect=error), self.assertRaises(Problem):
                self.run_tool()
        self.assert_no_artifacts()

    def test_input_mutation_during_execution_never_registers(self):
        path = self.folder / "hooks.txt"
        path.write_text(HOOK)
        with patch.object(self.runner.subprocess, "run", side_effect=self.fake_process(change=lambda: path.write_text("changed"))), self.assertRaises(Problem):
            self.run_tool(args=[str(path)])
        self.assert_no_artifacts()

    def test_expired_or_changed_direction_before_registration_never_saves(self):
        def expire():
            with self.store.db(True) as db:
                db.execute("UPDATE tasks SET expires=0 WHERE id=?", (self.claim["task_id"],))
        with patch.object(self.runner.subprocess, "run", side_effect=self.fake_process(change=expire)), self.assertRaises(Problem):
            self.run_tool()
        self.assert_no_artifacts()

    def test_store_registration_rechecks_claim_after_runner_preflight(self):
        add = self.store.add_version
        def expire_then_add(*args, **kwargs):
            with self.store.db(True) as db:
                db.execute("UPDATE tasks SET expires=0 WHERE id=?", (self.claim["task_id"],))
            return add(*args, **kwargs)
        with patch.object(self.store, "add_version", side_effect=expire_then_add), self.assertRaises(Problem):
            self.run_tool()
        self.assert_no_artifacts()

    def test_next_stage_pins_approved_versions_and_changed_direction_blocks_save(self):
        self.store.finish_claim(self.claim["task_id"], self.claim["token"], release=True)
        premise = self.store.add_version(self.project, {"title": "Fixture premise", "kind": "premise", "stage": "premise", "content": "An original gardening robot story."})
        self.store.review(premise["version_id"], "approved")
        self.claim = self.store.claim(self.project, "comic-support")
        saved = self.run_tool()
        record = self.store.get_version(saved["version_id"])
        self.assertEqual(record["artifact"]["stage"], "comic")
        self.assertEqual(record["version"]["inputs"], [premise["version_id"]])
        def change_direction():
            self.store.update_project(self.project, {"expected_revision": 1, "creative_locks": "Rework the main character"})
        with patch.object(self.runner.subprocess, "run", side_effect=self.fake_process(change=change_direction)), self.assertRaises(Problem):
            self.run_tool()
        self.assertEqual(len(self.store.project(self.project)["artifacts"]), 2)

    def test_wrong_scene_during_registration_rolls_back_success(self):
        add = self.store.add_version
        foreign = production.create_project(self.store, BRIEF)["id"]
        scene = self.store.save_scene(foreign, {"title": "Foreign"})
        def change_then_add(*args, **kwargs):
            with self.store.db(True) as db:
                db.execute("UPDATE tasks SET scene_id=? WHERE id=?", (scene, self.claim["task_id"]))
            return add(*args, **kwargs)
        with patch.object(self.store, "add_version", side_effect=change_then_add), self.assertRaises(Problem):
            self.run_tool()
        self.assert_no_artifacts()

    def test_private_token_in_tool_output_never_becomes_a_receipt(self):
        raw = json.dumps({"text": self.claim["token"]}).encode()
        with patch.object(self.runner.subprocess, "run", side_effect=self.fake_process(raw)), self.assertRaises(Problem):
            self.run_tool()
        self.assert_no_artifacts()
        self.assertEqual(list((self.store.root / "work").glob("youtube-*.json")), [])

    def test_source_and_dependency_mutation_reject_then_marks_prior_receipt_historical(self):
        saved = self.run_tool()
        receipt = self.store.get_version(saved["version_id"])["version"]["metadata"]["youtube_execution"]
        resources = receipt.get("resource_hashes", {})
        self.assertIn(".agents/skills/yt-script/hooks.json", resources)
        real_open = Path.open
        for suffix in ["yt-script/SKILL.md", "yt-script/hookscore.py", "yt-script/hooks.json"]:
            def changed(path, *args, target=suffix, **kwargs):
                source = real_open(path, *args, **kwargs)
                if str(path).endswith(target) and (args[0] if args else kwargs.get("mode")) == "rb":
                    with source:
                        return io.BytesIO(source.read() + b" ")
                return source
            with patch.object(self.runner.subprocess, "run", side_effect=self.fake_process(change=lambda: None)):
                # Change begins after preflight, at the actual subprocess boundary.
                original = self.runner.subprocess.run
                def mutate_after(*args, **kwargs):
                    result = original(*args, **kwargs)
                    mutation.start()
                    return result
                mutation = patch.object(Path, "open", changed)
                try:
                    with patch.object(self.runner.subprocess, "run", side_effect=mutate_after), self.assertRaises(Problem):
                        self.run_tool()
                finally:
                    mutation.stop()
            with patch.object(Path, "open", changed):
                evidence = production.get_handoff(self.store, self.project)["evidence"][0]
                self.assertTrue(evidence["historical"])
                self.assertTrue(evidence["sources_changed"])
                self.assertFalse(evidence["is_current"])
        self.assertEqual(len(self.store.project(self.project)["artifacts"]), 1)


if __name__ == "__main__":
    unittest.main()
