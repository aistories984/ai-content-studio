"""The shared, model-independent agent interface. No director approval tool."""
from pathlib import Path
from .store import Store, WORKFLOW, WORKFLOWS, workflow_for, Problem
from .media import inspect_media
from . import production, skill_runner
from .film import FilmService


def database():
    return Store()


def create_production_project(payload: dict) -> dict:
    """Create a Google Flow film from a validated topic, audience, format, duration and style."""
    return production.create_project(database(), payload)


def get_production_handoff(project_id: str, scene_id: str | None = None) -> dict:
    """Read combined skill selection, verified execution receipts and missing production adapters."""
    return production.get_handoff(database(), project_id, scene_id)


def run_youtube_tool(project_id: str, tool_name: str, arguments: list[str], task_id: str, token: str) -> dict:
    """Run a fixed local YouTube helper into leased supporting notes; no approval or stage advance."""
    return skill_runner.run_tool(database(), project_id, tool_name, arguments, task_id, token)


def get_speech_capabilities() -> dict:
    """Read installed temporary speech voices; no synthesis or voice selection."""
    from .audio import get_speech_capabilities as capabilities
    return capabilities()


def render_scratch_audio(project_id: str, scene_id: str, source: dict, task_id: str, token: str) -> dict:
    """Synchronously render measured temporary audio under a live scene audio lease.

    Explicit absolute PCM audio_file imports are allowed. Passing output enters
    human review; no approval, task completion, provider call or spending occurs.
    """
    from .audio import AudioService
    return AudioService(database()).render_scratch_audio(project_id, scene_id, source, task_id, token)


def get_film_state(project_id: str) -> dict:
    """Read film packages, director decisions and credit history; no browser connection implied."""
    return FilmService(database()).get_state(project_id)


def record_film_capability(project_id: str, payload: dict, task_id: str, token: str) -> dict:
    """Save an observed Flow configuration under a live film task; does not inspect a browser."""
    return FilmService(database()).record_capability(project_id, payload, task_id, token)


def prepare_film_package(project_id: str, scene_id: str, payload: dict, task_id: str, token: str) -> dict:
    """Pin approved film sources and exact observed settings for separate director review."""
    return FilmService(database()).prepare_package(project_id, scene_id, payload, task_id, token)


def reserve_film_attempt(package_id: str, task_id: str, token: str) -> dict:
    """Reserve one exact authorized film allowance; never uploads or clicks Generate."""
    return FilmService(database()).reserve_attempt(package_id, task_id, token)


def record_film_result(attempt_id: str, payload: dict, task_id: str, token: str) -> dict:
    """Append an observed result/reconciliation; a reported download is not verified local media."""
    return FilmService(database()).record_result(attempt_id, payload, task_id, token)


def list_projects() -> list[dict]:
    """List film and sprite projects. Never infer approval from a title."""
    return database().list_projects()


def get_project(project_id: str) -> dict:
    """Read direction, scenes, immutable versions, human reviews and agent tasks."""
    return database().project(project_id)


def get_next_action(project_id: str, scene_id: str | None = None) -> dict:
    """Return the next permitted stage, pinned inputs and exact director feedback."""
    return database().next_action(project_id, scene_id)


def claim_task(project_id: str, agent_name: str, scene_id: str | None = None) -> dict:
    """Claim one available stage for 15 minutes. Keep the returned token private."""
    return database().claim(project_id, agent_name, scene_id)


def heartbeat(task_id: str, token: str) -> dict:
    """Renew a live task. Changed upstream inputs invalidate the lease."""
    return database().heartbeat(task_id, token)


def register_artifact(project_id: str, payload: dict, file_paths: list[str] | None = None) -> dict:
    """Create a version against a valid task_id/task_token and pinned inputs.

    payload: title, kind, stage, scene_id, content, prompt, metadata, inputs,
    task_id, task_token. Updates also need artifact_id and expected_version.
    file_paths contains explicit absolute files produced for this project.
    Files are copied into immutable version storage; originals stay in place.
    """
    files = []
    measured = {}
    for item in file_paths or []:
        path = Path(item)
        if not path.is_absolute() or not path.is_file():
            raise Problem("Import paths must be explicit absolute files.")
        files.append((path.name, path))
        if not measured and path.suffix.lower() in (".mp4", ".mov", ".webm", ".mp3", ".wav", ".m4a"):
            measured = inspect_media(path)
    payload = {**payload, "metadata": {**payload.get("metadata", {}), **measured}}
    store = database()
    with store.db() as db:
        claim = store.required(db, "tasks", payload.get("task_id", ""))
    return store.add_version(project_id, payload, files, actor=claim["owner"], enforce_gate=True)


def validate_artifact(version_id: str) -> dict:
    """Run structural, dependency and file-integrity checks. This is not approval."""
    return database().checks(version_id)


def submit_for_review(version_id: str, task_id: str, token: str) -> dict:
    """Put the exact version into the human review queue; do not advance the gate."""
    store = database()
    record = store.get_version(version_id)
    with store.db() as db:
        claim = store._check_claim(db, task_id, token, record["project_id"])
    if record["version"].get("task_id") != task_id:
        raise Problem("This version was not produced by the claimed task.", 409)
    return store.submit(version_id, claim["owner"])


def finish_task(task_id: str, token: str, release: bool = False) -> dict:
    """Complete a submitted handoff, or release a task without a deliverable."""
    return database().finish_claim(task_id, token, release)


def save_scene(project_id: str, payload: dict, scene_id: str | None = None) -> dict:
    """Create or revise scene direction during script planning or a later stage.

    Updates require expected_revision and mark older scene artifacts stale.
    Keep package duration a whole number from 2 to 15 seconds.
    """
    store = database()
    action = store.next_action(project_id, scene_id)
    if action["stage"] in ("premise", "comic", "sprite_brief", "sprite_design"):
        raise Problem("Approve visual design before planning film packages or sprite animations.", 409)
    return {"scene_id": store.save_scene(project_id, payload, scene_id)}


def get_workflow(project_id: str | None = None, workflow_id: str | None = None) -> dict:
    """Read a project's film or game-sprite workflow. No args retains the film default."""
    if project_id:
        return workflow_for(database().project(project_id))
    if workflow_id:
        if workflow_id not in WORKFLOWS:
            raise Problem("Workflow not found.", 404)
        return WORKFLOWS[workflow_id]
    return WORKFLOW


def list_workflows() -> list[dict]:
    """List available workflow modes before choosing a project."""
    return list(WORKFLOWS.values())


def get_artifact(version_id: str) -> dict:
    """Read an exact version and absolute local file paths for its registered assets."""
    store = database()
    result = store.get_version(version_id)
    result["local_files"] = [str(store.file_path(version_id, i)[0]) for i in range(len(result["version"]["files"]))]
    return result


def prepare_generation(project_id: str, scene_id: str) -> dict:
    """Build a Wan multimodal request from approved audio, boards and previs.

    Does not upload media, submit, spend credits or retry. ready_for_api is only
    a package-format check; an agent must still verify hosted media and approval.
    """
    return database().generation_package(project_id, scene_id)


def export_project(project_id: str) -> dict:
    """Export every version, prompt, review, timeline and source file to a ZIP."""
    return {"path": str(database().export_project(project_id))}


def reserve_flow_attempt(project_id: str, scene_id: str, task_id: str, token: str, selected_model: str, credit_cost: float) -> dict:
    """Reserve one approved browser-generation allowance; never clicks Flow or calls an API."""
    return database().reserve_flow_attempt(project_id, scene_id, task_id, token, selected_model, credit_cost)


def record_flow_result(attempt_id: str, task_id: str, token: str, status: str, evidence: str, project_url: str = "") -> dict:
    """Log an observed browser result. Uncertain submissions remain unresolved without a retry."""
    return database().record_flow_result(attempt_id, task_id, token, status, evidence, project_url)


def extract_sprites(project_id: str, scene_id: str, source_version_id: str, settings: dict, task_id: str, token: str) -> dict:
    """Pack an approved downloaded clip locally and register transparent sheet/atlas/preview/QC."""
    return database().pack_sprite_artifact(project_id, scene_id, source_version_id, settings, task_id, token)


def create_research_request(payload: dict) -> dict:
    """Save an active-session public research request before any project exists."""
    from .research import ResearchService
    return ResearchService(database()).create_request(payload)


def list_research_requests() -> list[dict]:
    """Read pending and completed research with retained source evidence."""
    from .research import ResearchService
    return ResearchService(database()).list_requests()


def get_research_request(research_id: str) -> dict:
    """Read exact immutable reports, actual swipe results and selections."""
    from .research import ResearchService
    return ResearchService(database()).get_request(research_id)


def save_research_report(research_id: str, payload: dict) -> dict:
    """Validate public observations/ideas and run fixed swipe.py; never select or approve."""
    from .research import ResearchService
    return ResearchService(database()).save_report(research_id, payload)


TOOLS = {fn.__name__: fn for fn in (create_research_request, list_research_requests, get_research_request, save_research_report, list_projects, get_project, get_next_action, claim_task, heartbeat, register_artifact, validate_artifact, submit_for_review, finish_task, save_scene, get_workflow, list_workflows, get_artifact, prepare_generation, export_project, reserve_flow_attempt, record_flow_result, extract_sprites, create_production_project, get_production_handoff, run_youtube_tool, get_film_state, record_film_capability, prepare_film_package, reserve_film_attempt, record_film_result, get_speech_capabilities, render_scratch_audio)}
