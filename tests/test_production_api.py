"""HTTP/CLI contracts use the same isolated production service as active agents."""
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from studio import production
from studio.store import ROOT, Store

BRIEF = {"topic": "A robot learns gardening", "audience": "Curious adults", "format": "short", "target_seconds": 24, "style": "Illustrated"}


class ProductionApiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.enterContext(patch.dict(os.environ, {"DIRECTOR_DATA": self.temp.name, "DIRECTOR_NO_SEED": "1"}))
        self.module = importlib.import_module("studio.app")
        self.store = Store(self.temp.name)
        self.enterContext(patch.object(self.module, "store", self.store))
        self.client = self.enterContext(TestClient(self.module.app))
        self.headers = {"x-director-token": self.module.DIRECTOR_TOKEN}

    def create(self):
        response = self.client.post("/api/production/projects", json=BRIEF, headers=self.headers)
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_production_writes_keep_session_boundary(self):
        for route in ["/api/production/projects", "/api/projects/unknown/youtube-tool"]:
            response = self.client.post(route, json=BRIEF)
            self.assertEqual(response.status_code, 403)
        response = self.client.post("/api/production/projects", json=BRIEF, headers={**self.headers, "origin": "https://elsewhere.example"})
        self.assertEqual(response.status_code, 403)

    def test_http_create_and_handoff_match_service_and_survive_reopen(self):
        project = self.create()
        response = self.client.get(f"/api/projects/{project['id']}/production")
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json(), production.get_handoff(Store(self.temp.name), project["id"]))
        self.assertEqual(response.json()["next_action"]["stage"], "premise")
        self.assertFalse(response.json()["automation"]["generation_ready"])
        self.assertEqual(project["settings"]["runtime_minutes"], .4)

    def test_invalid_intake_and_demo_bypass_are_rejected(self):
        for payload in [{}, {**BRIEF, "audience": ""}, {**BRIEF, "target_seconds": True}, {**BRIEF, "demo": True}]:
            with self.subTest(payload=payload):
                response = self.client.post("/api/production/projects", json=payload, headers=self.headers)
                self.assertEqual(response.status_code, 400, response.text)
        self.assertEqual(self.store.list_projects(), [])

    def test_unknown_project_and_foreign_scene_errors_are_json(self):
        response = self.client.get("/api/projects/missing/production")
        self.assertEqual(response.status_code, 404)
        self.assertIn("detail", response.json())
        project = self.create()["id"]
        response = self.client.get(f"/api/projects/{project}/production?scene_id=foreign")
        self.assertEqual(response.status_code, 400)

    def test_http_tool_saves_actual_result_and_rejects_bad_lease_or_arguments(self):
        project = self.create()["id"]
        claim = self.store.claim(project, "http-test")
        payload = {"tool_name": "hookscore", "arguments": ["--hook", "You waste 3 hours editing: what if one cut fixed it?"],
                   "task_id": claim["task_id"], "token": claim["token"]}
        response = self.client.post(f"/api/projects/{project}/youtube-tool", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 200, response.text)
        saved = response.json()
        handoff = self.client.get(f"/api/projects/{project}/production").json()
        self.assertEqual(handoff["evidence"][0]["version_id"], saved["version_id"])
        self.assertEqual(handoff["next_action"]["stage"], "premise")
        self.assertNotIn(claim["token"], json.dumps(handoff))
        for fields, status in [({"tool_name": "arbitrary"}, 400), ({"token": "wrong"}, 409), ({"arguments": "--hook no"}, 400)]:
            response = self.client.post(f"/api/projects/{project}/youtube-tool", json={**payload, **fields}, headers=self.headers)
            self.assertEqual(response.status_code, status, response.text)
        self.assertEqual(len(self.store.project(project)["artifacts"]), 1)

    def test_cli_create_run_and_handoff_use_the_same_evidence(self):
        request = Path(self.temp.name) / "request.json"
        def call(name, payload):
            request.write_text(json.dumps(payload))
            result = subprocess.run([sys.executable, "-m", "studio.cli", name, "--json-file", str(request)],
                                    cwd=ROOT, env={**os.environ, "DIRECTOR_DATA": self.temp.name}, text=True, capture_output=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            return json.loads(result.stdout)
        project = call("create_production_project", {"payload": BRIEF})["id"]
        claim = self.store.claim(project, "cli-test")
        saved = call("run_youtube_tool", {"project_id": project, "tool_name": "title", "arguments": ["--title", "3 editing mistakes"],
                                         "task_id": claim["task_id"], "token": claim["token"]})
        handoff = call("get_production_handoff", {"project_id": project})
        self.assertEqual(handoff["evidence"][0]["version_id"], saved["version_id"])
        self.assertEqual(handoff["next_action"]["stage"], "premise")


if __name__ == "__main__":
    unittest.main()
