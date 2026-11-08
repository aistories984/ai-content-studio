"""Research evidence stays reproducible and selection never bypasses Studio gates."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import sqlite3
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from studio import production
from studio.store import Store, ROOT, Problem
try:
    from studio.research import ResearchService
except ImportError:
    ResearchService = None

REQUEST = {"query": "Broad story opportunities", "categories": [], "language": "English", "time_window": "past month"}
DIRECTION = {"audience": "Curious adults", "style": "Illustrated", "creator_voice": "Warm and precise"}


def report_payload():
    rows = [{"channel": "Garden Lab", "channel_url": "https://www.youtube.com/@gardenlab", "title": "I tried gardening" if i == 3 else f"Garden {i}", "url": f"https://www.youtube.com/watch?v=video{i:06d}", "category": "gardening", "format": "short", "views": views, "duration": 24, "observed_at": datetime.now(timezone.utc).isoformat(), "evidence_url": "https://www.youtube.com/@gardenlab/videos", "evidence_note": "Public listing; fixture, not observed research"} for i, views in enumerate([100, 100, 100, 1000])]
    return {"expected_report_id": None, "sampling_note": "Four comparable public listing fixtures", "shared_pattern": "Personal experiment titles", "limitations": "Fixture only; sample median not full channel history", "collected": rows, "ideas": [{"title": "A robot tries gardening", "original_angle": "A tiny robot learns to care for one stubborn seed", "source_urls": [rows[3]["url"]], "feasibility": "One illustrated character and setting", "format": "short", "target_seconds": 24}]}


class ResearchTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(ResearchService, "Durable research service has not been implemented")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(self.temp.name)
        self.service = ResearchService(self.store)
        self.request = self.service.create_request(REQUEST)

    def save(self, payload=None):
        return self.service.save_report(self.request["id"], payload or report_payload())["reports"][0]

    def select(self, report, payload=None):
        return self.service.select_idea(self.request["id"], report["id"], report["ideas"][0]["id"], payload or DIRECTION)

    def test_request_and_exact_ranking_survive_reopen_with_source_hashes(self):
        report = self.save()
        reopened = ResearchService(Store(self.temp.name)).get_request(self.request["id"])
        self.assertEqual(reopened["reports"][0], report)
        self.assertEqual(report["request_source"], REQUEST)
        result = report["tool_execution"]["result"]
        self.assertEqual(result["outliers"][0]["multiple"], 10)
        self.assertEqual(result["outliers"][0]["median"], 100)
        self.assertEqual(report["evidence"]["status"], "ranked")
        self.assertEqual(report["tool_execution"]["input"][0]["channel"], "https://www.youtube.com/@gardenlab | short")
        for name, digest in report["tool_execution"]["source_hashes"].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest)
        self.assertEqual(self.service.list_requests()[0]["id"], self.request["id"])
        self.assertEqual(self.store.list_projects(), [])

    def test_unknown_counts_and_mixed_formats_do_not_inflate_support(self):
        for mutate in (lambda rows: rows[0].update(views=None), lambda rows: rows[0].update(format="long")):
            payload = report_payload()
            mutate(payload["collected"])
            report = self.save(payload)
            self.assertEqual(report["tool_execution"]["result"]["outliers"], [])
            self.assertEqual(report["evidence"]["status"], "unranked")
            self.assertTrue(report["evidence"]["insufficient_data"])
            self.request = self.service.create_request(REQUEST)
        empty = report_payload()
        empty.update(collected=[], ideas=[])
        self.assertEqual(self.save(empty)["evidence"]["status"], "unranked")

    def test_rejects_alias_duplicates_invalid_metrics_sources_dates_and_claims(self):
        cases = [("views", True), ("views", -1), ("views", 1.5), ("views", float("inf")), ("duration", float("nan")), ("url", "file:///tmp/x"), ("url", "https://youtube.com.evil.test/watch?v=video000000"), ("evidence_url", "https://127.0.0.1/private"), ("channel_url", "https://youtube.com/watch?v=video000000"), ("observed_at", "2026-01-01"), ("observed_at", "2999-01-01T00:00:00+00:00")]
        for field, value in cases:
            payload = report_payload()
            payload["collected"][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(Problem):
                self.save(payload)
        duplicate = report_payload()
        duplicate["collected"][1]["url"] = "https://youtu.be/video000000"
        with self.assertRaises(Problem): self.save(duplicate)
        forged = report_payload()
        forged["evidence"] = {"status": "ranked"}
        with self.assertRaises(Problem): self.save(forged)
        forged = report_payload()
        forged["ideas"][0]["source_urls"] = ["https://youtube.com/watch?v=uncollected"]
        with self.assertRaises(Problem): self.save(forged)

    def test_selection_is_atomic_idempotent_validated_and_pinned_after_new_report(self):
        report = self.save()
        with ThreadPoolExecutor(max_workers=4) as pool:
            projects = list(pool.map(lambda _: self.select(report), range(4)))
        self.assertEqual(len({p["id"] for p in projects}), 1)
        project = projects[0]
        self.assertEqual(len(self.store.list_projects()), 1)
        self.assertEqual(project["workflow_id"], "comic-to-flow")
        self.assertEqual(project["settings"]["production_brief"]["topic"], "A robot tries gardening")
        self.assertIn("one stubborn seed", project["settings"]["production_brief"]["context"])
        self.assertFalse(any(s["complete"] for s in project["stage_status"]))
        self.assertEqual(project["scene_count"], 0)
        with self.assertRaises(Problem) as conflict: self.select(report, {**DIRECTION, "style": "Different"})
        self.assertEqual(conflict.exception.status, 409)
        payload = report_payload()
        payload["expected_report_id"] = report["id"]
        newest = self.save(payload)
        self.assertEqual(self.select(report)["id"], project["id"])
        linked = self.service.project_research(project["id"])
        self.assertEqual(linked["report"]["id"], report["id"])
        self.assertEqual(linked["idea"]["id"], report["ideas"][0]["id"])
        handoff = production.get_handoff(self.store, project["id"])
        self.assertEqual(handoff["research"]["report"]["id"], report["id"])
        viral = next(s for s in handoff["skills"] if s["name"] == "yt-viral")
        self.assertEqual(viral["status"], "has_evidence")
        with zipfile.ZipFile(self.store.export_project(project["id"])) as archive:
            self.assertEqual(json.loads(archive.read("research.json"))["report"]["id"], report["id"])
        self.assertNotEqual(newest["id"], report["id"])

    def test_wrong_ids_superseded_report_and_selection_injections_fail_without_projects(self):
        report = self.save()
        other = self.service.create_request(REQUEST)
        for research_id, report_id, idea_id in [(other["id"], report["id"], report["ideas"][0]["id"]), (self.request["id"], "missing", report["ideas"][0]["id"]), (self.request["id"], report["id"], "missing")]:
            with self.assertRaises(Problem): self.service.select_idea(research_id, report_id, idea_id, DIRECTION)
        for bad in ({**DIRECTION, "settings": {}}, {**DIRECTION, "research": {}}, {**DIRECTION, "target_seconds": True}, {"style": "Illustrated"}):
            with self.assertRaises(Problem): self.select(report, bad)
        with self.assertRaises(Problem): self.save()
        payload = report_payload()
        payload["expected_report_id"] = report["id"]
        self.save(payload)
        with self.assertRaises(Problem) as stale: self.select(report)
        self.assertEqual(stale.exception.status, 409)
        self.assertEqual(self.store.list_projects(), [])

    def test_selection_failure_rolls_back_created_project(self):
        report = self.save()
        with self.store.db(True) as db:
            db.execute("CREATE TRIGGER reject_selection BEFORE INSERT ON research_selections BEGIN SELECT RAISE(ABORT,'test insert failure'); END")
        with self.assertRaises(sqlite3.IntegrityError): self.select(report)
        self.assertEqual(self.store.list_projects(), [])

    def test_immutable_records_and_hash_validation_catch_tampering(self):
        report = self.save()
        with self.assertRaises(sqlite3.IntegrityError), self.store.db(True) as db:
            db.execute("UPDATE research_reports SET data='{}' WHERE id=?", (report["id"],))
        with self.store.db(True) as db:
            db.execute("DROP TRIGGER research_reports_no_update")
            db.execute("UPDATE research_reports SET data='{}' WHERE id=?", (report["id"],))
        with self.assertRaises(Problem) as tampered: self.service.get_request(self.request["id"])
        self.assertEqual(tampered.exception.status, 409)

    def test_changed_helper_sources_are_readable_but_never_current_or_selectable(self):
        report = self.save()
        project = self.select(report)
        with patch("studio.research.source_hashes", return_value={}):
            self.assertFalse(self.service.get_request(self.request["id"])["reports"][0]["is_current"])
            with self.assertRaises(Problem): self.select(report)
            handoff = production.get_handoff(self.store, project["id"])
            self.assertFalse(handoff["research"]["is_current"])
            self.assertNotEqual(next(s for s in handoff["skills"] if s["name"] == "yt-viral")["status"], "has_evidence")

    def test_bounds_and_explicit_adjustments_preserve_original_idea(self):
        for payload in ({**REQUEST, "query": "x" * 2001}, {**REQUEST, "categories": ["x"] * 13}, {**REQUEST, "unknown": True}, {**REQUEST, "language": ""}):
            with self.assertRaises(Problem): self.service.create_request(payload)
        payload = report_payload()
        payload["limitations"] = "x" * (1024 * 1024)
        with self.assertRaises(Problem): self.save(payload)
        report = self.save()
        project = self.select(report, {**DIRECTION, "topic": "An adjusted seed story", "format": "long", "target_seconds": 100})
        self.assertEqual(project["settings"]["production_brief"]["target_seconds"], 100)
        self.assertEqual(self.service.project_research(project["id"])["idea"]["target_seconds"], 24)

    def test_exact_payload_retry_rejects_explicit_overrides_even_when_brief_matches(self):
        report = self.save()
        self.select(report)
        with self.assertRaises(Problem) as conflict:
            self.select(report, {**DIRECTION, "target_seconds": 24})
        self.assertEqual(conflict.exception.status, 409)

    def test_channel_host_aliases_share_baseline_and_watch_shorts_aliases_are_duplicates(self):
        payload = report_payload()
        payload["collected"][0]["channel_url"] = "https://m.youtube.com/@GARDENLAB/shorts"
        report = self.save(payload)
        self.assertEqual(len(report["tool_execution"]["result"]["outliers"]), 1)
        self.assertEqual(report["tool_execution"]["result"]["outliers"][0]["multiple"], 10)
        self.request = self.service.create_request(REQUEST)
        payload = report_payload()
        payload["collected"][1]["url"] = "https://m.youtube.com/shorts/video000000"
        with self.assertRaises(Problem): self.save(payload)
