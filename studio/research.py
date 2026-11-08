"""Immutable, public research evidence before a director chooses a production brief.

This service never fetches sources, starts an AI worker or approves production.
"""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
import hashlib
import ipaddress
import json
import math
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .store import ROOT, Problem, encode, ident, now, text
from .production import normalize_brief, load_finite_json

MAX_JSON = 1024 * 1024
SOURCE_PATHS = (".agents/skills/yt-viral/SKILL.md", ".agents/skills/yt-viral/swipe.py", ".agents/skills/yt-script/hooks.json", ".agents/skills/director-studio/SKILL.md")


def initialize_schema(db):
    db.executescript("""
    CREATE TABLE IF NOT EXISTS research_requests(id TEXT PRIMARY KEY,data TEXT NOT NULL,sha256 TEXT NOT NULL,created TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS research_reports(id TEXT PRIMARY KEY,research_id TEXT NOT NULL REFERENCES research_requests(id),data TEXT NOT NULL,sha256 TEXT NOT NULL,created TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS research_selections(id TEXT PRIMARY KEY,research_id TEXT NOT NULL REFERENCES research_requests(id),report_id TEXT NOT NULL REFERENCES research_reports(id),idea_id TEXT NOT NULL,project_id TEXT NOT NULL UNIQUE REFERENCES projects(id),data TEXT NOT NULL,sha256 TEXT NOT NULL,created TEXT NOT NULL,UNIQUE(report_id,idea_id));
    CREATE INDEX IF NOT EXISTS research_report_request ON research_reports(research_id);
    """)
    for table in ("research_requests", "research_reports", "research_selections"):
        for operation in ("UPDATE", "DELETE"):
            db.execute(f"CREATE TRIGGER IF NOT EXISTS {table}_no_{operation.lower()} BEFORE {operation} ON {table} BEGIN SELECT RAISE(ABORT,'Research history is immutable'); END")


def fields(payload, allowed, required=()):
    if not isinstance(payload, dict) or set(payload) - set(allowed) or set(required) - set(payload):
        raise Problem("Research payload has missing or unsupported fields.")
    try:
        raw = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, OverflowError, RecursionError, UnicodeError) as error:
        raise Problem("Research requires finite JSON.") from error
    if len(raw) > MAX_JSON:
        raise Problem("Research JSON must be at most 1 MB.")
    return payload


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def source_hashes():
    try:
        return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCE_PATHS}
    except OSError as error:
        raise Problem("Research helper/skill sources are unavailable.", 409) from error


def public_url(value):
    value = text(value, "Public source URL", 2000, True)
    try:
        parsed = urlsplit(value)
        host = parsed.hostname or ""
        if parsed.scheme != "https" or not host or parsed.username or parsed.password or parsed.port not in (None, 443):
            raise ValueError()
        if not re.fullmatch(r"[A-Za-z0-9.-]+", host) or "." not in host or host.endswith((".local", ".localhost", ".internal")) or host == "localhost":
            raise ValueError()
        try:
            address = ipaddress.ip_address(host)
        except ValueError:
            address = None
        if address is not None and not address.is_global:
            raise ValueError()
        if any(c.isspace() or ord(c) < 32 for c in value) or "\\" in value:
            raise ValueError()
    except ValueError as error:
        raise Problem("Use a public HTTPS source URL.") from error
    return value, parsed


def youtube_url(value, channel=False):
    value, parsed = public_url(value)
    host = parsed.hostname.lower()
    if host not in ("youtube.com", "www.youtube.com", "m.youtube.com", "youtu.be", "www.youtu.be"):
        raise Problem("Use a public YouTube URL.")
    if channel:
        if host.endswith("youtu.be") or not re.fullmatch(r"/(?:@[A-Za-z0-9_.-]+|(?:channel|c|user)/[A-Za-z0-9_.-]+)(?:/(?:videos|shorts|featured))?/?", parsed.path):
            raise Problem("Use a public YouTube channel URL.")
        path = re.sub(r"/(videos|shorts|featured)/?$", "", parsed.path).rstrip("/")
        if path.startswith("/@"):
            path = path.lower()
        return "https://www.youtube.com" + path
    if host.endswith("youtu.be"):
        video = parsed.path.strip("/")
    elif parsed.path == "/watch":
        ids = parse_qs(parsed.query).get("v", [])
        video = ids[0] if len(ids) == 1 else ""
    else:
        match = re.fullmatch(r"/(?:shorts|embed)/([A-Za-z0-9_-]{11})/?", parsed.path)
        video = match[1] if match else ""
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video):
        raise Problem("Use a public YouTube video URL with an eleven-character video ID.")
    return "https://www.youtube.com/watch?v=" + video


def timestamp(value, field):
    value = text(value, field, 80, True)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None or parsed > datetime.now(timezone.utc) + timedelta(minutes=5):
            raise ValueError()
    except (ValueError, OverflowError) as error:
        raise Problem(f"{field} must be a timezone-aware ISO8601 capture date, no later than five minutes in the future.") from error
    return parsed.isoformat()


def metric(value, field, integer=False):
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise Problem(f"{field} must be nonnegative and finite, or null.")
    try:
        if not math.isfinite(value) or value > 10**15 or (integer and int(value) != value):
            raise ValueError()
    except (ValueError, OverflowError) as error:
        raise Problem(f"{field} must be a bounded finite {'integer' if integer else 'number'}.") from error
    return int(value) if integer else value


def format_name(value):
    if not isinstance(value, str) or value not in ("short", "long"):
        raise Problem("Research format must be short or long.")
    return value


def _execute(rows):
    """Fixed subprocess, no caller paths/commands; output and elapsed time bounded."""
    before = source_hashes()
    tool_input = [{"channel": row["channel_url"] + " | " + row["format"], "title": row["title"], "views": row["views"], "url": row["url"], "duration": row["duration"]} for row in rows if row["views"] is not None]
    with tempfile.TemporaryDirectory(prefix="director-research-") as directory:
        base = Path(directory)
        raw = encode(tool_input).encode()
        (base / "collected.json").write_bytes(raw)
        with (base / "stdout").open("wb") as out, (base / "stderr").open("wb") as err:
            argv = [sys.executable, str(ROOT / ".agents/skills/yt-viral/swipe.py"), str(base / "collected.json"), "--min", "2.0", "--json"]
            try:
                process = subprocess.Popen(argv, stdout=out, stderr=err, cwd=ROOT)
            except OSError as error:
                raise Problem("Research helper could not start.", 409) from error
            deadline = time.monotonic() + 10
            try:
                while process.poll() is None:
                    if time.monotonic() > deadline or any((base / name).stat().st_size > 2 * MAX_JSON for name in ("stdout", "stderr")):
                        raise Problem("Research helper exceeded its time/output limit.", 409)
                    time.sleep(.01)
            finally:
                if process.poll() is None:
                    process.kill()
                process.wait()
        if any((base / name).stat().st_size > 2 * MAX_JSON for name in ("stdout", "stderr")):
            raise Problem("Research helper output exceeded its limit.", 409)
        stdout, stderr = [(base / name).read_text(encoding="utf-8") for name in ("stdout", "stderr")]
        if process.returncode:
            raise Problem("Research helper failed; no report was saved.", 409)
    result = load_finite_json(stdout)
    if not isinstance(result, dict) or set(result) != {"outliers", "skipped_thin_channels"} or not isinstance(result["outliers"], list) or not isinstance(result["skipped_thin_channels"], list):
        raise Problem("Research helper returned an invalid result.", 409)
    if before != source_hashes():
        raise Problem("Research sources changed during execution; report was not saved.", 409)
    return {"tool_name": "swipe", "status": "succeeded", "arguments": ["collected.json", "--min", "2.0", "--json"], "input": tool_input, "input_sha256": hashlib.sha256(raw).hexdigest(), "stdout": stdout, "stderr": stderr, "result": result, "source_hashes": before}


class ResearchService:
    def __init__(self, store):
        self.store = store

    def _insert(self, db, table, value, **links):
        raw = encode(value)
        columns = ["id", "data", "sha256", "created", *links]
        values = [value["id"], raw, digest(value), value["created"], *links.values()]
        db.execute(f"INSERT INTO {table}({','.join(columns)}) VALUES({','.join('?' for _ in columns)})", values)

    def _read(self, row):
        try:
            value = load_finite_json(row["data"])
            if not isinstance(value, dict) or digest(value) != row["sha256"] or value["id"] != row["id"] or value["created"] != row["created"]:
                raise ValueError()
            for name in ("research_id", "report_id", "idea_id", "project_id"):
                if name in row.keys() and value.get(name) != row[name]:
                    raise ValueError()
        except (Problem, ValueError, KeyError, TypeError, OverflowError) as error:
            raise Problem("Research content integrity check failed.", 409) from error
        return {**value, "sha256": row["sha256"]}

    def _request(self, db, key):
        row = self.store.required(db, "research_requests", key)
        value = self._read(row)
        reports = [self._read(row) for row in db.execute("SELECT * FROM research_reports WHERE research_id=? ORDER BY rowid DESC", (key,))]
        for report in reports:
            if report["request_source"] != value["source"]:
                raise Problem("Research request pin integrity failed.", 409)
            report["is_current"] = self._sources_current(report)
        selections = [self._read(row) for row in db.execute("SELECT * FROM research_selections WHERE research_id=? ORDER BY rowid DESC", (key,))]
        return {**value, "reports": reports, "selections": selections}

    @staticmethod
    def _sources_current(report):
        try:
            return report["tool_execution"]["source_hashes"] == source_hashes()
        except Problem:
            return False

    def create_request(self, payload):
        fields(payload, {"query", "categories", "language", "time_window"}, {"query", "categories", "language", "time_window"})
        categories = payload["categories"]
        if not isinstance(categories, list) or len(categories) > 12:
            raise Problem("Supply at most twelve research categories.")
        value = {"id": ident("research"), "created": now(), "query": text(payload["query"], "Research query", 2000, True), "categories": [text(v, "Category", 200, True) for v in categories], "language": text(payload["language"], "Language", 80, True), "time_window": text(payload["time_window"], "Time window", 2000, True), "source": deepcopy_json(payload)}
        with self.store.db(True) as db:
            self._insert(db, "research_requests", value)
        return self.get_request(value["id"])

    def get_request(self, research_id):
        with self.store.db() as db:
            return self._request(db, research_id)

    def list_requests(self):
        with self.store.db() as db:
            return [self._request(db, row[0]) for row in db.execute("SELECT id FROM research_requests ORDER BY rowid DESC")]

    def save_report(self, research_id, payload):
        allowed = {"expected_report_id", "sampling_note", "shared_pattern", "limitations", "collected", "ideas"}
        fields(payload, allowed, allowed)
        request = self.get_request(research_id)
        expected = payload["expected_report_id"]
        if expected != (request["reports"][0]["id"] if request["reports"] else None):
            raise Problem("Research report changed; refresh before saving.", 409)
        rows, ideas = payload["collected"], payload["ideas"]
        if not isinstance(rows, list) or len(rows) > 500 or not isinstance(ideas, list) or len(ideas) > 5:
            raise Problem("Supply at most 500 collected rows and five ideas.")
        collected, urls = [], set()
        row_fields = {"channel", "channel_url", "title", "url", "category", "format", "views", "duration", "observed_at", "evidence_url", "evidence_note"}
        for row in rows:
            fields(row, row_fields | {"published_at"}, row_fields)
            clean = {key: text(row[key], key, 4000, True) for key in ("channel", "title", "category", "evidence_note")}
            clean.update(channel_url=youtube_url(row["channel_url"], True), url=youtube_url(row["url"]), format=format_name(row["format"]), views=metric(row["views"], "Views", True), duration=metric(row["duration"], "Duration"), observed_at=timestamp(row["observed_at"], "observed_at"), evidence_url=public_url(row["evidence_url"])[0])
            if "published_at" in row:
                clean["published_at"] = timestamp(row["published_at"], "published_at")
            if clean["url"] in urls:
                raise Problem("Duplicate YouTube video identity in research sample.")
            urls.add(clean["url"])
            collected.append(clean)
        normalized_ideas = []
        idea_fields = {"title", "original_angle", "source_urls", "feasibility", "format", "target_seconds"}
        for idea in ideas:
            fields(idea, idea_fields | {"audience"}, idea_fields)
            clean = {key: text(idea[key], key, 4000, True) for key in ("title", "original_angle", "feasibility")}
            sources = idea["source_urls"]
            if not isinstance(sources, list) or not 1 <= len(sources) <= 500:
                raise Problem("Ideas require collected source URLs.")
            clean["source_urls"] = list(dict.fromkeys(youtube_url(url) for url in sources))
            if not set(clean["source_urls"]) <= urls:
                raise Problem("Every idea source must reference a collected video.")
            validated = normalize_brief({"topic": clean["title"], "audience": "Research audience pending", "style": "Research style pending", "format": idea["format"], "target_seconds": idea["target_seconds"]})
            clean.update(id=ident("idea"), format=validated["format"], target_seconds=validated["target_seconds"])
            if "audience" in idea:
                clean["audience"] = text(idea["audience"], "Audience", 4000, True)
            normalized_ideas.append(clean)
        notes = {name: text(payload[name], name, 10000, True) for name in ("sampling_note", "shared_pattern", "limitations")}
        execution = _execute(collected)
        groups = {}
        for row in collected:
            group = row["channel_url"] + " | " + row["format"]
            groups.setdefault(group, {"group": group, "channel": row["channel"], "channel_url": row["channel_url"], "format": row["format"], "collected": 0, "known_views": 0})
            groups[group]["collected"] += 1
            groups[group]["known_views"] += row["views"] is not None
        result = execution["result"]
        evidence = {"status": "ranked" if result["outliers"] else "unranked", "outliers": result["outliers"], "groups": list(groups.values()), "insufficient_data": [f"{g['channel']} ({g['format']}): {g['known_views']} known counts; at least four unique comparable videos required." for g in groups.values() if g["known_views"] < 4], "gate_line": "ship it, or change it?", "formula_note": "Title formula is a lexical observation, not a causal explanation. Public observations are supplied by the active agent; local validation does not verify source measurements. Reach and revenue are not promised."}
        if not collected:
            evidence["insufficient_data"].append("No public videos collected; no ranking is supported.")
        value = {"id": ident("report"), "created": now(), "research_id": research_id, "request_source": request["source"], **notes, "collected": collected, "ideas": normalized_ideas, "tool_execution": execution, "evidence": evidence, "skills": [{"name": "yt-viral", "path": SOURCE_PATHS[0], "sha256": execution["source_hashes"][SOURCE_PATHS[0]], "required_inputs": ["Public video listings, channel identity, format, views and source capture dates"], "intended_outputs": ["Channel-relative outliers, title formulas, shared structural pattern and feasible original ideas"], "approval_gates": ["Director selects exact idea and production direction; no stage, spending or publication approval"]}, {"name": "director-studio", "path": SOURCE_PATHS[3], "sha256": execution["source_hashes"][SOURCE_PATHS[3]], "required_inputs": ["Exact selected report/idea and director audience/style"], "intended_outputs": ["Pinned production brief preserving all twelve obligations"], "approval_gates": ["Human review at every required production stage"]}]}
        with self.store.db(True) as db:
            latest = db.execute("SELECT id FROM research_reports WHERE research_id=? ORDER BY rowid DESC LIMIT 1", (research_id,)).fetchone()
            if expected != (latest[0] if latest else None):
                raise Problem("Research report changed; refresh before saving.", 409)
            if not self._sources_current(value):
                raise Problem("Research sources changed before save.", 409)
            self._insert(db, "research_reports", value, research_id=research_id)
        return self.get_request(research_id)

    def select_idea(self, research_id, report_id, idea_id, payload):
        fields(payload, {"audience", "style", "creator_voice", "topic", "format", "target_seconds"}, {"audience", "style"})
        with self.store.db(True) as db:
            request = self._request(db, research_id)
            report = next((r for r in request["reports"] if r["id"] == report_id), None)
            idea = next((i for i in report["ideas"] if i["id"] == idea_id), None) if report else None
            if not idea:
                raise Problem("Exact research report/idea not found for this request.", 404)
            if not report["is_current"]:
                raise Problem("Research sources changed; refresh evidence before selection.", 409)
            brief = normalize_brief({"topic": idea["title"], "format": idea["format"], "target_seconds": idea["target_seconds"], **payload, "context": idea["original_angle"], "research_requested": True})
            old = next((s for s in request["selections"] if s["report_id"] == report_id and s["idea_id"] == idea_id), None)
            if old:
                if old["brief"] != brief or old["payload"] != payload:
                    raise Problem("This idea was already selected with different direction.", 409)
                self._check_selection(old, report, idea)
                project_id = old["project_id"]
            else:
                if request["reports"][0]["id"] != report_id:
                    raise Problem("This research report is superseded; select from the newest report.", 409)
                project_id = self.store._create_project(db, {"title": brief["topic"][:120], "brief": brief["topic"], "workflow_id": "comic-to-flow", "production_brief": brief})
                value = {"id": ident("selection"), "created": now(), "research_id": research_id, "report_id": report_id, "idea_id": idea_id, "report_sha256": report["sha256"], "project_id": project_id, "payload": deepcopy_json(payload), "brief": brief}
                self._insert(db, "research_selections", value, research_id=research_id, report_id=report_id, idea_id=idea_id, project_id=project_id)
        return self.store.project(project_id)

    @staticmethod
    def _check_selection(selection, report, idea):
        if selection["report_sha256"] != report["sha256"] or selection["idea_id"] != idea["id"]:
            raise Problem("Research selection pin integrity failed.", 409)

    def project_research(self, project_id):
        with self.store.db() as db:
            self.store.required(db, "projects", project_id)
            row = db.execute("SELECT * FROM research_selections WHERE project_id=?", (project_id,)).fetchone()
            if row is None:
                return None
            selection = self._read(row)
            request = self._request(db, selection["research_id"])
            report = next((r for r in request["reports"] if r["id"] == selection["report_id"]), None)
            idea = next((i for i in report["ideas"] if i["id"] == selection["idea_id"]), None) if report else None
            if not idea:
                raise Problem("Research selection references missing evidence.", 409)
            self._check_selection(selection, report, idea)
            project = self.store.required(db, "projects", project_id)
            if json.loads(project["settings"]).get("production_brief") != selection["brief"]:
                raise Problem("Production brief differs from immutable research selection.", 409)
            return {"request": {k: v for k, v in request.items() if k not in ("reports", "selections")}, "report": report, "idea": idea, "selection": selection, "is_current": report["is_current"]}


def deepcopy_json(value):
    return json.loads(encode(value))
