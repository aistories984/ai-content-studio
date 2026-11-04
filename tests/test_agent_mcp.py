import json
import os
import sys
import tempfile
import unittest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from studio.store import Store, ROOT


class McpIntegrationTests(unittest.IsolatedAsyncioTestCase):
    async def test_real_stdio_handoff_registers_a_review_without_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            store = Store(directory)
            project = store.create_project({"title": "MCP integration"})["id"]
            env = {**os.environ, "DIRECTOR_DATA": directory, "PYTHONPATH": str(ROOT)}
            server = StdioServerParameters(command=sys.executable, args=["-m", "studio.mcp_server"], env=env)
            async with stdio_client(server) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    names = {tool.name for tool in tools.tools}
                    self.assertEqual(names, {"list_projects", "get_project", "get_next_action", "claim_task", "heartbeat",
                                            "register_artifact", "validate_artifact", "submit_for_review", "finish_task", "save_scene",
                                            "get_workflow", "list_workflows", "get_artifact", "prepare_generation", "export_project",
                                            "reserve_flow_attempt", "record_flow_result", "extract_sprites", "create_production_project",
                                            "get_production_handoff", "run_youtube_tool"})
                    self.assertFalse(any("approv" in name or "review" in name and name != "submit_for_review" for name in names))

                    async def call(name, arguments):
                        result = await session.call_tool(name, arguments)
                        self.assertFalse(result.isError, result.content)
                        return json.loads(result.content[0].text)

                    action = await call("get_next_action", {"project_id": project})
                    self.assertEqual(action["stage"], "premise")
                    claim = await call("claim_task", {"project_id": project, "agent_name": "Test writer"})
                    result = await call("register_artifact", {"project_id": project, "payload": {"title": "Test premise", "kind": "premise", "stage": "premise", "content": "A courier chooses to return a lost letter and changes her route home.", "prompt": "Write a concise original premise.", "inputs": [], "task_id": claim["task_id"], "task_token": claim["token"]}})
                    await call("submit_for_review", {"version_id": result["version_id"], "task_id": claim["task_id"], "token": claim["token"]})
                    await call("finish_task", {"task_id": claim["task_id"], "token": claim["token"]})
                    action = await call("get_next_action", {"project_id": project})
                    self.assertEqual(action["state"], "awaiting_review")
                    self.assertEqual(store.get_version(result["version_id"])["version"]["status"], "in_review")

                    flow = await call("create_production_project", {"payload": {"topic": "A robot learns gardening", "audience": "Curious adults", "format": "short", "target_seconds": 24, "style": "Illustrated"}})
                    claim = await call("claim_task", {"project_id": flow["id"], "agent_name": "MCP YouTube test"})
                    saved = await call("run_youtube_tool", {"project_id": flow["id"], "tool_name": "hookscore", "arguments": ["--hook", "You waste 3 hours editing: what if one cut fixed it?"], "task_id": claim["task_id"], "token": claim["token"]})
                    handoff = await call("get_production_handoff", {"project_id": flow["id"]})
                    self.assertEqual(handoff["evidence"][0]["version_id"], saved["version_id"])
                    self.assertEqual(handoff["next_action"]["stage"], "premise")
                    self.assertEqual(handoff["next_action"]["state"], "ready")
                    receipt = store.file_path(saved["version_id"], 0)[0].read_text()
                    self.assertNotIn(claim["token"], receipt)
                    self.assertNotIn(claim["token"], json.dumps(handoff))


if __name__ == "__main__":
    unittest.main()
