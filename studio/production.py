"""Validated Flow film intake and durable, read-only production handoffs.

Selection describes work to perform. Only registered, integrity-checked tool
receipts count as execution evidence; neither selection nor execution approves art.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re
from typing import TYPE_CHECKING

from .store import ROOT, Problem, numeric, text

if TYPE_CHECKING:
    from .store import Store

FLOW_WORKFLOW = "comic-to-flow"
BRIEF_FIELDS = {"topic", "audience", "format", "target_seconds", "style", "creator_voice", "context", "research_requested"}
TOOL_SOURCES = {
    "hookscore": ("yt-script", "hookscore.py"),
    "title": ("yt-package", "title.py"),
    "deadair": ("yt-edit", "deadair.py"),
    "chapters": ("yt-chapters", "chapters.py"),
    "retention": ("yt-retention", "retention.py"),
    "swipe": ("yt-viral", "swipe.py"),
}
TOOL_RESOURCES = {
    "hookscore": (".agents/skills/yt-script/hooks.json",),
    "title": (), "deadair": (),
    "chapters": (".agents/skills/yt-edit/deadair.py",),
    "retention": (".agents/skills/yt-edit/deadair.py",),
    "swipe": (".agents/skills/yt-script/hooks.json",),
}


def load_finite_json(raw):
    """Reject nonstandard JSON constants and overflowing numeric values."""
    def reject(value):
        raise ValueError(f"Nonfinite JSON value: {value}")

    def number(value):
        result = float(value)
        if not math.isfinite(result):
            reject(value)
        return result

    try:
        return json.loads(raw, parse_constant=reject, parse_float=number)
    except (ValueError, UnicodeError, RecursionError) as error:
        raise Problem("Tool input/output must contain valid finite JSON.") from error


def normalize_brief(payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise Problem("Production brief must be an object.")
    brief = {field: text(payload.get(field), field, 10000, True) for field in ("topic", "audience", "style")}
    format_name = payload.get("format")
    if not isinstance(format_name, str) or format_name not in ("short", "long"):
        raise Problem("Production format must be short or long.")
    brief["format"] = format_name
    duration = payload.get("target_seconds")
    # Bound integers before numeric() attempts a float conversion for finiteness.
    if isinstance(duration, int) and not 2 <= duration <= 14400:
        raise Problem("Target seconds must be between 2 and 14400.")
    brief["target_seconds"] = numeric(duration, "Target seconds", 2, 14400)
    for field in ("creator_voice", "context"):
        if field in payload:
            brief[field] = text(payload[field], field, 10000, True)
    if "research_requested" in payload:
        if not isinstance(payload["research_requested"], bool):
            raise Problem("research_requested must be a boolean.")
        brief["research_requested"] = payload["research_requested"]
    return brief


def create_project(store: Store, payload: dict) -> dict:
    if not isinstance(payload, dict):
        raise Problem("Production request must be an object.")
    brief = normalize_brief(payload.get("production_brief", payload))
    return store.create_project({**payload, "title": payload.get("title", brief["topic"][:120]),
                                 "brief": payload.get("brief", brief["topic"]),
                                 "workflow_id": FLOW_WORKFLOW, "production_brief": brief})


def _skill(name, required_inputs, intended_outputs, approval_gates):
    path = ROOT / ".agents" / "skills" / name / "SKILL.md"
    return {"name": name, "path": path.relative_to(ROOT).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "status": "not_run",
            "required_inputs": required_inputs, "intended_outputs": intended_outputs,
            "approval_gates": approval_gates}


def _catalog(brief, stage):
    # All eleven skills are considered at their appropriate lifecycle stage.
    # Missing transcripts/channel data remain visible prerequisites, never fabricated.
    definitions = [
        ("yt-viral", ("premise",), bool(brief.get("research_requested")), "Research is requested; collect public listings with at least four videos per channel.", "Research was requested and belongs to the premise stage; review its evidence before downstream use." if brief.get("research_requested") else "Research was not requested in this brief.", ["Public video listings, views and URLs; four videos/channel"], ["Ranked channel-relative outliers and source URLs"]),
        ("yt-plan", (), False, "", "Upload scheduling requires capacity, existing work and a calendar; this is one production brief.", ["Creator capacity and calendar"], ["Feasible upload plan"]),
        ("yt-script", ("premise", "script"), True, "Scored hooks support premise selection; screenplay adaptation still requires the approved comic.", "Hook/script work belongs to premise or screenplay, preserving the comic gate.", ["Brief, real creator voice/examples, approved sources at the eligible stage"], ["Five scored hooks, top two panels, beat script and runtime estimate"]),
        ("yt-package", ("premise", "boards", "edit"), True, "Develop the click promise and lint the title/thumbnail pairing against approved creative sources.", "Packaging is revisited at premise, visual references and delivery.", ["Audience, topic, real creator voice/examples and approved creative sources"], ["Scored titles, thumbnail text and visual brief"]),
        ("yt-edit", ("edit",), True, "Editing guidance requires an actual timestamped transcript and footage; acquire those before running.", "Deferred to edit with a real timed transcript; no timing is invented.", ["Actual timed transcript and footage"], ["Timecoded cut suggestions reviewed against footage"]),
        ("yt-shorts", (), False, "", "Requires a supplied long-form transcript for repurposing; a Short brief alone is not that input.", ["Long-form transcript and source media"], ["Self-contained Short spans, hooks and framing notes"]),
        ("yt-chapters", ("edit",) if brief["format"] == "long" else (), brief["format"] == "long", "Long-form chapters require the final timed transcript and boundary validation.", "Deferred until a long-form final transcript; chapters are not selected for a Short.", ["Final long-form timed transcript"], ["Validated chapter boundaries and titles"]),
        ("yt-seo", ("edit",), True, "Prepare search-facing delivery text from the actual approved content and target queries.", "Deferred to delivery after the actual video content exists.", ["Approved video/script, creator voice and target queries"], ["Description, relevant tags and three query checks"]),
        ("yt-comment", (), False, "", "Post-release replies require real supplied comments; no comments are available from intake.", ["Actual viewer comments and creator voice"], ["Triaged draft replies and pin suggestion"]),
        ("yt-retention", (), False, "", "Post-release diagnosis requires a real audience-retention export.", ["Actual retention CSV, duration and optional timed transcript"], ["Leak report and specific pacing changes"]),
        ("yt-audit", (), False, "", "Channel audit requires a real channel context and evidence; this project intake supplies neither.", ["Channel URL, public videos and channel context"], ["Channel priorities with supporting evidence"]),
    ]
    result = []
    for name, stages, enabled, active_reason, deferred_reason, inputs, outputs in definitions:
        applicable = enabled and stage in stages
        result.append({**_skill(name, inputs, outputs, ["Human review of the exact output; no publication authorization"]),
                       "stages": list(stages), "applicability": "applicable" if applicable else "deferred",
                       "reason": active_reason if applicable else deferred_reason})
    return result


def _execution_valid(execution):
    if not isinstance(execution, dict):
        return False
    tool = execution.get("tool_name")
    if not isinstance(tool, str) or tool not in TOOL_SOURCES:
        return False
    skill, _ = TOOL_SOURCES[tool]
    if execution.get("skill_name") != skill or execution.get("status") != "succeeded":
        return False
    if any(not isinstance(execution.get(key), str) or not re.fullmatch(r"[0-9a-f]{64}", execution[key]) for key in ("skill_sha256", "script_sha256")):
        return False
    if not isinstance(execution.get("argv"), list) or not execution["argv"] or not all(isinstance(v, str) for v in execution["argv"]):
        return False
    files = execution.get("input_files")
    resources = execution.get("resource_hashes")
    return (isinstance(resources, dict) and set(resources) == set(TOOL_RESOURCES[tool]) and
            all(isinstance(v, str) and re.fullmatch(r"[0-9a-f]{64}", v) for v in resources.values()) and
            isinstance(files, list) and all(isinstance(f, dict) and isinstance(f.get("path"), str) and Path(f["path"]).is_absolute() and isinstance(f.get("sha256"), str) and re.fullmatch(r"[0-9a-f]{64}", f["sha256"]) for f in files))


def _evidence(store, project, scene_id):
    evidence, blockers = [], []
    for artifact in project["artifacts"]:
        if scene_id and artifact["scene_id"] not in (None, scene_id):
            continue
        for version in artifact["versions"]:
            execution = version.get("metadata", {}).get("youtube_execution")
            if execution is None:
                continue
            verified_receipt = None
            if _execution_valid(execution):
                # A receipt must be a registered immutable file, not loose metadata.
                # Inspect every attachment to prevent a valid receipt hiding tampering.
                intact = True
                for index, info in enumerate(version["files"]):
                    try:
                        path, _ = store.file_path(version["id"], index)
                        raw = path.read_bytes()
                        if hashlib.sha256(raw).hexdigest() != info["sha256"]:
                            intact = False
                            break
                        if path.suffix.lower() == ".json" and len(raw) <= 5 * 1024 * 1024:
                            receipt = load_finite_json(raw)
                            if isinstance(receipt, dict) and receipt.get("youtube_execution") == execution and isinstance(receipt.get("result"), (dict, list)):
                                verified_receipt = {"file_index": index, "sha256": info["sha256"]}
                    except (Problem, OSError, ValueError, UnicodeError):
                        intact = False
                        break
                if not intact:
                    verified_receipt = None
            if verified_receipt is None:
                blockers.append(f"Tool receipt is missing or invalid for version {version['id']}.")
                continue
            skill, script = TOOL_SOURCES[execution["tool_name"]]
            folder = ROOT / ".agents" / "skills" / skill
            try:
                sources_changed = (hashlib.sha256((folder / "SKILL.md").read_bytes()).hexdigest() != execution["skill_sha256"] or
                                   hashlib.sha256((folder / script).read_bytes()).hexdigest() != execution["script_sha256"] or
                                   any(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != execution["resource_hashes"][name]
                                       for name in TOOL_RESOURCES[execution["tool_name"]]))
            except OSError:
                sources_changed = True
            stale = version["stale"] or sources_changed
            is_current = artifact["latest"]["id"] == version["id"] and not stale
            evidence.append({**execution, "artifact_id": artifact["id"], "version_id": version["id"],
                             "stage": artifact["stage"], "scene_id": artifact["scene_id"], "inputs": version["inputs"],
                             "status": version["status"], "execution_status": "succeeded", "stale": stale,
                             "effective_status": "needs_update" if stale else version["effective_status"],
                             "sources_changed": sources_changed, "is_current": is_current,
                             "historical": not is_current, "receipt": verified_receipt})
    return evidence, blockers


def get_handoff(store: Store, project_id: str, scene_id: str | None = None) -> dict:
    project = store.project(project_id)
    if project["workflow_id"] != FLOW_WORKFLOW:
        raise Problem("Production handoff requires a Google Flow film project.")
    next_action = store.next_action(project_id, scene_id)
    brief = normalize_brief(project["settings"].get("production_brief"))
    catalog = _catalog(brief, next_action["stage"])
    skills = [_skill("director-studio", ["Current project, exact approved source versions and review feedback"],
                     [next_action.get("deliverable", "Reviewed delivery and production record")],
                     ["Human creative review at every required stage", "Exact package and spending allowance before any generation"])]
    skills.extend(dict(entry) for entry in catalog if entry["applicability"] == "applicable")
    evidence, blockers = _evidence(store, project, scene_id)
    for selected in skills:
        if any(item["skill_name"] == selected["name"] and item["is_current"] for item in evidence):
            selected["status"] = "has_evidence"
    blockers.extend([
        "Flow film adapter is not implemented; visible browser capability inspection and signed-in session are still required.",
        "Image/layout, voice/audio and Blender production adapters must provide real stage deliverables.",
        "Final rendering/delivery and publishing automation are not implemented; R1 upload is manual.",
    ])
    if not brief.get("creator_voice"):
        blockers.append("Creator voice/examples are missing from intake; read an available real voice profile or obtain creator examples before writing.")
    if next_action["state"] == "awaiting_review":
        blockers.append("The exact submitted version is awaiting human review; do not advance the stage.")
    return {"project_id": project_id, "workflow_id": FLOW_WORKFLOW, "brief": brief,
            "next_action": next_action, "skills": skills, "catalog": catalog, "evidence": evidence,
            "blockers": blockers, "automation": {"browser_ready": False, "generation_ready": False, "render_ready": False, "publish_ready": False}}
