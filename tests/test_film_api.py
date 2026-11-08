"""Director-only film decisions and shared agent/HTTP contracts, with isolated data."""
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from fastapi.testclient import TestClient
from studio import agent_tools, production
from studio.store import ROOT, Store

BRIEF = {"topic": "A robot learns gardening", "audience": "Curious adults", "format": "short", "target_seconds": 24, "style": "Illustrated"}
FILM_TOOLS = {"record_film_capability", "prepare_film_package", "get_film_state", "reserve_film_attempt", "record_film_result"}


class FilmApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.enterContext(patch.dict(os.environ, {"DIRECTOR_DATA": self.temp.name, "DIRECTOR_NO_SEED": "1"}))
        self.module = importlib.import_module("studio.app")
        self.store = Store(self.temp.name)
        self.enterContext(patch.object(self.module, "store", self.store))
        self.client = self.enterContext(TestClient(self.module.app))
        self.headers = {"x-director-token": self.module.DIRECTOR_TOKEN}
        self.project = production.create_project(self.store, BRIEF)["id"]

    def test_empty_film_state_matches_agent_and_cli_without_claiming_execution(self):
        response = self.client.get(f"/api/projects/{self.project}/film")
        self.assertEqual(response.status_code, 200, response.text)
        state = response.json()
        self.assertEqual(state, agent_tools.get_film_state(self.project))
        self.assertEqual(state["packages"], [])
        self.assertEqual(state["attempts"], [])
        self.assertTrue(state["blockers"])
        self.assertFalse(any(state["automation"].values()))
        request = Path(self.temp.name) / "read.json"
        request.write_text(json.dumps({"project_id": self.project}))
        result = subprocess.run([sys.executable, "-m", "studio.cli", "get_film_state", "--json-file", str(request)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), state)

    def test_budget_is_a_director_decision_and_not_an_agent_tool(self):
        route = f"/api/projects/{self.project}/film/budget"
        payload = {"max_credits": 100, "note": "Offline explicit test cap"}
        self.assertEqual(self.client.post(route, json=payload).status_code, 403)
        response = self.client.post(route, json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 200, response.text)
        state = self.client.get(f"/api/projects/{self.project}/film").json()
        self.assertEqual(state["budget"]["max_credits"], 100)
        self.assertTrue(FILM_TOOLS <= agent_tools.TOOLS.keys())
        self.assertFalse(any("approv" in name or "budget" in name or name == "review_film_package" for name in agent_tools.TOOLS))

    def test_film_routes_reject_wrong_workflow_and_protect_human_decisions(self):
        old = self.store.create_project({"title": "Legacy film"})["id"]
        response = self.client.get(f"/api/projects/{old}/film")
        self.assertEqual(response.status_code, 409, response.text)
        self.assertEqual(self.client.get("/api/projects/missing/film").status_code, 404)
        for suffix in ("capabilities", "packages", "budget"):
            self.assertEqual(self.client.post(f"/api/projects/{self.project}/film/{suffix}", json={}).status_code, 403)
        for route in ("/api/film/packages/missing/review", "/api/film/packages/missing/allowance", "/api/film/packages/missing/reserve", "/api/film/attempts/missing/result"):
            self.assertEqual(self.client.post(route, json={}).status_code, 403)
        claim = self.store.claim(self.project, "api-test")
        cap = self.client.post(f"/api/projects/{self.project}/film/capabilities", json={"payload": {}, "task_id": claim["task_id"], "token": claim["token"]}, headers=self.headers)
        self.assertIn(cap.status_code, (400, 409))
        self.assertEqual(self.store.project(self.project)["stage_status"][0]["complete"], False)

    def test_exact_package_decisions_reservation_and_recovery_share_the_service(self):
        from tests.test_film import FilmTests, future
        from studio.film import FilmService
        FilmTests.setUpClass()
        self.addCleanup(FilmTests.tearDownClass)
        helper = FilmTests()
        helper.store = self.store
        helper.service = FilmService(self.store)
        helper.p, helper.scene, helper.claim, helper.board = helper.fixture()
        claim = {"task_id": helper.claim["task_id"], "token": helper.claim["token"]}
        envelope = {"scene_id": helper.scene, "payload": helper.payload(), **claim}
        mismatched = self.client.post(f"/api/projects/{helper.p}/film/packages", json={**envelope, "project_id": "different-project"}, headers=self.headers)
        self.assertEqual(mismatched.status_code, 400, mismatched.text)
        response = self.client.post(f"/api/projects/{helper.p}/film/packages", json=envelope, headers=self.headers)
        self.assertEqual(response.status_code, 200, response.text)
        package = response.json()
        route = f"/api/film/packages/{package['id']}"
        self.assertNotIn(claim["token"], json.dumps(package))
        self.assertEqual(self.client.post(route + "/review", json={}).status_code, 403)
        review = {"package_hash": "changed", "expected_current": True, "decision": "approved", "note": "Offline test review"}
        self.assertEqual(self.client.post(route + "/review", json=review, headers=self.headers).status_code, 409)
        review["package_hash"] = package["hash"]
        self.assertEqual(self.client.post(route + "/review", json=review, headers=self.headers).status_code, 200)
        budget = self.client.post(f"/api/projects/{helper.p}/film/budget", json={"max_credits": 20, "note": "Offline project cap"}, headers=self.headers)
        self.assertEqual(budget.status_code, 200, budget.text)
        allowance = {"package_hash": package["hash"], "upload_authorized": True, "max_attempts": 2, "max_credits": 10, "expires_at": future(), "note": "Offline exact allowance"}
        approved = self.client.post(route + "/allowance", json=allowance, headers=self.headers)
        self.assertEqual(approved.status_code, 200, approved.text)
        mismatched = self.client.post(route + "/reserve", json={**claim, "package_id": "different-package"}, headers=self.headers)
        self.assertEqual(mismatched.status_code, 400, mismatched.text)
        attempt = agent_tools.reserve_film_attempt(package["id"], **claim)
        mismatched = self.client.post(f"/api/film/attempts/{attempt['id']}/result", json={"attempt_id": "different-attempt", "payload": {"status": "failed", "evidence": "Wrong scope"}, **claim}, headers=self.headers)
        self.assertEqual(mismatched.status_code, 400, mismatched.text)
        result = self.client.post(f"/api/film/attempts/{attempt['id']}/result", json={"payload": {"status": "unknown", "evidence": "Simulated interrupted submission"}, **claim}, headers=self.headers)
        self.assertEqual(result.status_code, 200, result.text)
        self.assertFalse(result.json()["local_download_verified"])
        blocked = self.client.post(route + "/reserve", json=claim, headers=self.headers)
        self.assertEqual(blocked.status_code, 409, blocked.text)
        state = self.client.get(f"/api/projects/{helper.p}/film").json()
        self.assertEqual(state, agent_tools.get_film_state(helper.p))
        self.assertEqual(state["budget"]["committed_credits"], 5)
        self.assertEqual(state["attempts"][0]["status"], "unknown")
        self.assertNotIn(claim["token"], json.dumps(state))

    def test_export_retains_film_budget_evidence_without_private_lease(self):
        claim = self.store.claim(self.project, "export-test")
        self.client.post(f"/api/projects/{self.project}/film/budget", json={"max_credits": 100, "note": "Offline export test cap"}, headers=self.headers)
        with zipfile.ZipFile(self.store.export_project(self.project)) as archive:
            self.assertIn("film-production.json", archive.namelist())
            state = json.loads(archive.read("film-production.json"))
            self.assertEqual(state["budget"]["max_credits"], 100)
            self.assertEqual(len(state["budget"]["history"]), 1)
            self.assertFalse(any(state["automation"].values()))
            self.assertNotIn(claim["token"], archive.read("film-production.json").decode())
            self.assertNotIn(claim["token"], archive.read("project.json").decode())
