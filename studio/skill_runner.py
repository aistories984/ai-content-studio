"""Run fixed, local YouTube helpers into leased, immutable supporting artifacts."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from .production import TOOL_RESOURCES, TOOL_SOURCES, load_finite_json
from .store import ROOT, Problem, Store

MAX_INPUT = 1024 * 1024
MAX_OUTPUT = 2 * 1024 * 1024


def _read(path):
    try:
        if not path.is_file() or path.stat().st_size > MAX_INPUT:
            raise Problem("Tool inputs and sources must be existing files of at most 1 MB.")
        # Bound processing even when a file grows after stat().
        with path.open("rb") as source:
            raw = source.read(MAX_INPUT + 1)
        if len(raw) > MAX_INPUT:
            raise Problem("Tool input exceeds 1 MB.")
        return raw
    except OSError as error:
        raise Problem("Tool input/source file is unavailable.") from error


def _hash(path):
    return hashlib.sha256(_read(path)).hexdigest()


def _arguments(tool, arguments):
    if (not isinstance(arguments, list) or not 1 <= len(arguments) <= 24 or
            any(not isinstance(v, str) or not v.strip() or "\0" in v or len(v) > 10000 for v in arguments) or
            sum(len(v) for v in arguments) > 20000):
        raise Problem("Provide a bounded list of nonempty tool arguments.")
    allowed = {
        "hookscore": {"--hook"}, "title": {"--title", "--thumb"},
        "deadair": {"--floor"}, "chapters": {"--target"},
        "retention": {"--duration", "--transcript"}, "swipe": {"--min"},
    }[tool]
    flags, positional = {}, []
    index = 0
    while index < len(arguments):
        value = arguments[index]
        if value.startswith("-"):
            if value in flags or value not in allowed | {"--json"}:
                raise Problem("Unknown or repeated tool flag.")
            if value == "--json":
                flags[value] = True
            else:
                index += 1
                if index == len(arguments) or arguments[index].startswith("--"):
                    raise Problem("Tool flag is missing its value.")
                flags[value] = arguments[index]
        else:
            positional.append(value)
        index += 1
    inline = "--hook" if tool == "hookscore" else "--title" if tool == "title" else None
    if (inline and inline in flags and positional) or len(positional) != (0 if inline and inline in flags else 1):
        raise Problem("Provide exactly one input file or the supported inline text flag.")
    if "--target" in flags:
        value = flags["--target"]
        if not re.fullmatch(r"[0-9]{1,3}", value) or not 3 <= int(value) <= 100:
            raise Problem("Chapter target must be a whole number between 3 and 100.")
    for flag, low, high in [("--floor", 0, 60), ("--duration", .001, 14400), ("--min", 0, 1000000)]:
        if flag in flags:
            # These helpers use simple decimal filtering to distinguish flags from filenames.
            if not re.fullmatch(r"[0-9]*\.?[0-9]+", flags[flag]):
                raise Problem(f"{flag} must be a finite decimal number.")
            value = float(flags[flag])
            if not math.isfinite(value) or not low <= value <= high:
                raise Problem(f"{flag} is outside the supported bounds.")
    files = positional + ([flags["--transcript"]] if "--transcript" in flags else [])
    for name in files:
        if not Path(name).is_absolute():
            raise Problem("Input files must be explicit absolute paths.")
    # Normalize filename first: legacy helpers infer it from the first nonflag argument.
    argv = list(positional)
    for flag, value in flags.items():
        if flag != "--json":
            argv.extend([flag, value])
    return argv + ["--json"], list(dict.fromkeys(files))


def _claim(store, project_id, task_id, token):
    if not isinstance(task_id, str) or not task_id or not isinstance(token, str) or not token:
        raise Problem("A valid task ID and private lease token are required.", 409)
    with store.db() as db:
        claim = dict(store._check_claim(db, task_id, token, project_id))
        action = store._next(store._project(db, project_id), claim["scene_id"])
        if action["state"] != "ready" or action.get("needs_scene"):
            raise Problem("The claimed stage is not ready for supporting work.", 409)
    return claim, action


def run_tool(store: Store, project_id: str, tool_name: str, arguments: list[str], task_id: str, token: str) -> dict:
    """Execute one allowlisted helper; save notes without submitting or advancing a stage."""
    if not isinstance(tool_name, str) or tool_name not in TOOL_SOURCES:
        raise Problem("Unknown YouTube tool.")
    claim, action = _claim(store, project_id, task_id, token)
    args, filenames = _arguments(tool_name, arguments)
    skill, script_name = TOOL_SOURCES[tool_name]
    folder = ROOT / ".agents" / "skills" / skill
    script = folder / script_name
    argv = [sys.executable, str(script), *args]
    if any(token in value for value in argv):
        raise Problem("Lease tokens must not appear in tool arguments.")
    sources = [folder / "SKILL.md", script, *(ROOT / p for p in TOOL_RESOURCES[tool_name])]
    hashes = {path: _hash(path) for path in sources}
    input_files = []
    for name in filenames:
        path = Path(name)
        raw = _read(path)
        if path.suffix.lower() == ".json":
            load_finite_json(raw)
        input_files.append({"path": name, "sha256": hashlib.sha256(raw).hexdigest()})
    # Temporary files bound stdout/stderr *processing*, avoiding communicate()'s
    # unbounded in-memory capture. Only fixed scripts run, with bounded inputs.
    try:
        with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
            process = subprocess.run(argv, cwd=ROOT, stdin=subprocess.DEVNULL,
                                     stdout=stdout, stderr=stderr, timeout=60, shell=False)
            stdout.seek(0)
            stderr.seek(0)
            raw, errors = stdout.read(MAX_OUTPUT + 1), stderr.read(MAX_OUTPUT + 1)
        if process.returncode != 0:
            raise Problem("YouTube tool failed; no successful artifact was registered.")
        if len(raw) > MAX_OUTPUT or len(errors) > MAX_OUTPUT:
            raise Problem("YouTube tool output exceeds the 2 MB processing limit.")
        result = load_finite_json(raw)
        if not isinstance(result, (dict, list)):
            raise Problem("YouTube tool must return a JSON object or list.")
    except (OSError, subprocess.TimeoutExpired) as error:
        raise Problem("YouTube tool could not finish within its local execution limits.") from error
    if any(_hash(path) != digest for path, digest in hashes.items()) or any(_hash(Path(f["path"])) != f["sha256"] for f in input_files):
        raise Problem("Tool sources or input files changed during execution; refresh before running again.", 409)
    current, latest_action = _claim(store, project_id, task_id, token)
    if current["stage"] != claim["stage"] or current["scene_id"] != claim["scene_id"] or latest_action["inputs"] != action["inputs"]:
        raise Problem("The claimed stage, scene or source pins changed during execution.", 409)
    execution = {"tool_name": tool_name, "skill_name": skill, "skill_sha256": hashes[folder / "SKILL.md"],
                 "script_sha256": hashes[script], "input_files": input_files, "argv": argv,
                 "resource_hashes": {p: hashes[ROOT / p] for p in TOOL_RESOURCES[tool_name]}, "status": "succeeded"}
    receipt = json.dumps({"youtube_execution": execution, "result": result}, ensure_ascii=False, allow_nan=False)
    if token in receipt:
        raise Problem("Tool output contains private lease data; no artifact was registered.")
    work = store.root / "work"
    work.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", prefix=f"youtube-{tool_name}-", dir=work, encoding="utf-8", delete=False) as output:
        output.write(receipt)
        receipt_path = Path(output.name)
    payload = {"title": f"YouTube {tool_name} report", "kind": "notes", "stage": claim["stage"], "scene_id": claim["scene_id"],
               "content": f"Local {tool_name} result for human review.\n" + json.dumps(result, ensure_ascii=False, allow_nan=False)[:12000],
               "prompt": f"Local YouTube tool: {tool_name}\nArguments: " + json.dumps(args, ensure_ascii=False),
               "inputs": action["inputs"], "metadata": {"youtube_execution": execution}, "task_id": task_id, "task_token": token}
    saved = store.add_version(project_id, payload, [(receipt_path.name, receipt_path)], actor=claim["owner"], enforce_gate=True)
    return {**saved, "result": result}
