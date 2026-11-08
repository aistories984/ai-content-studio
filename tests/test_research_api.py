"""Research HTTP/session, CLI and shared agent boundaries use one service."""
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
from studio import agent_tools
from studio.store import ROOT, Store
from tests.test_research import REQUEST, DIRECTION, report_payload


class ResearchApiTests(unittest.TestCase):
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
        response = self.client.post("/api/research", json=REQUEST, headers=self.headers)
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_public_reads_director_writes_and_exact_envelope_selection(self):
        self.assertEqual(self.client.post("/api/research", json=REQUEST).status_code, 403)
        request = self.create()
        route = f"/api/research/{request['id']}"
        self.assertEqual(self.client.get(route).json(), request)
        self.assertEqual(self.client.get("/api/research").json(), [request])
        self.assertEqual(self.client.post(route + "/reports", json=report_payload()).status_code, 403)
        saved = self.client.post(route + "/reports", json=report_payload(), headers=self.headers)
        self.assertEqual(saved.status_code, 200, saved.text)
        report = saved.json()["reports"][0]
        envelope = {"report_id": report["id"], "idea_id": report["ideas"][0]["id"], "payload": DIRECTION}
        self.assertEqual(self.client.post(route + "/select", json=envelope).status_code, 403)
        for bad in ({**envelope, "research_id": "wrong"}, {**envelope, "payload": {**DIRECTION, "settings": {}}}, {"report_id": report["id"], "idea_id": report["ideas"][0]["id"]}):
            self.assertEqual(self.client.post(route + "/select", json=bad, headers=self.headers).status_code, 400)
        selected = self.client.post(route + "/select", json=envelope, headers=self.headers)
        self.assertEqual(selected.status_code, 200, selected.text)
        self.assertEqual(self.client.post(route + "/select", json=envelope, headers=self.headers).json()["id"], selected.json()["id"])
        handoff = self.client.get(f"/api/projects/{selected.json()['id']}/production").json()
        self.assertEqual(handoff["research"]["report"]["id"], report["id"])

    def test_malformed_nonfinite_oversized_and_wrong_envelopes_fail_safely(self):
        for raw in ('[]', '{bad', '{"query": NaN}', ' ' * (1024 * 1024 + 1), '{"query": 1e999}'):
            response = self.client.post("/api/research", content=raw, headers={**self.headers, "content-type": "application/json"})
            self.assertEqual(response.status_code, 400, response.text)
        self.assertEqual(self.client.get("/api/research/missing").status_code, 404)
        self.assertEqual(self.client.post("/api/research", json={**REQUEST, "project_id": "wrong"}, headers=self.headers).status_code, 400)
        self.assertEqual(self.client.post("/api/research", json=REQUEST, headers={**self.headers, "origin": "https://evil.test"}).status_code, 403)
        self.assertEqual(self.store.list_projects(), [])

    def test_agent_and_cli_research_precede_projects_without_selection_authority(self):
        expected = {"create_research_request", "list_research_requests", "get_research_request", "save_research_report"}
        self.assertTrue(expected <= agent_tools.TOOLS.keys(), "Research shared agent operations missing")
        self.assertFalse(any("select" in name for name in agent_tools.TOOLS))
        request = agent_tools.create_research_request(REQUEST)
        state = agent_tools.save_research_report(request["id"], report_payload())
        self.assertEqual(agent_tools.get_research_request(request["id"]), state)
        path = Path(self.temp.name) / "read.json"
        path.write_text(json.dumps({"research_id": request["id"]}))
        result = subprocess.run([sys.executable, "-m", "studio.cli", "get_research_request", "--json-file", str(path)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), state)
        self.assertEqual(agent_tools.list_research_requests(), [state])
        self.assertEqual(self.store.list_projects(), [])
