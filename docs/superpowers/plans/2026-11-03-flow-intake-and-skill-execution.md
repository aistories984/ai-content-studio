# Flow intake and skill execution implementation plan

> For agentic workers: use superpowers:subagent-driven-development task by task. User override: do not stage, commit, push, open a PR, or merge. Leave the local feature branch for user review.

**Goal:** Make a selectable Flow film project collect a real brief, expose a durable combined-skill handoff, and run the existing YouTube tools into versioned Studio review artifacts.

**Architecture:** Preserve the existing shared Store rules and both upstream workflow modes. Add an explicit Flow film preset plus production-intake/handoff and allowlisted local-tool execution modules. Active agents execute the handoff; no autonomous LLM backend is implied.

**Tech stack:** Python 3.12/FastAPI/SQLite/CLI/MCP; existing React/TypeScript/Vite; unittest and isolated browser fixtures.

**Spec:** `docs/superpowers/specs/2026-11-03-flow-video-r1-design.md`; tickets R1-001 and R1-002 plus intake-related R1-003 contracts. This is a working first slice, not full R1 or all first-sprint tickets. Package spending/recovery, provider browser execution, asset generation, rendering and publishing remain later tickets.

## Global constraints

- Work on local `feature/flow-video-automation` from master; no staging/commits/push/PR/merge. User reviews and owns Git publication.
- Preserve all twelve diagram obligations and human approvals; preserve existing Wan/sprite records and behavior.
- New Flow film requests never fall back to Wan. Generation must explicitly report the unimplemented adapter.
- Use `.agents/skills/` as canonical skill root; read actual files and hash instructions/tools. Installed names are not execution.
- Python 3.11+ and Node 22; no new runtime dependencies. No paid generation, auth changes, uploads or publication.
- All automated tests use temporary DIRECTOR_DATA and preserve real studio-data/outputs.
- Shared CLI/MCP/HTTP business rules; no agent approval operation.

## Review focus

- Missing/invalid/boolean/nonfinite duration and empty audience/style: intake must reject rather than manufacture defaults (Task 1 tests).
- Existing projects and new workflow: unchanged gate semantics; no silent Wan fallback (Task 1 tests).
- A handoff must survive reopening Store and distinguish selected skills from actual versioned tool output (Tasks 1/2 tests).
- Unknown tools, expired/wrong project/scene claims, changed sources or failed subprocesses must never create a successful artifact (Task 2 tests).
- Browser creation and handoff display must show true readiness/limits and preserve existing mode selection (Task 3 tests).

### Task 1: Flow workflow, validated intake and combined-skill handoff

**Files:** create `workflows/comic-to-flow-v1.json`, `studio/production.py`, `tests/test_production.py`; modify `studio/store.py` only for create_project/settings validation and fail-closed generation routing. No app/UI or agent_tools edits in this task.

**Interfaces produced:**
- `normalize_brief(payload: dict) -> dict`: validates topic, audience, format (`short` or `long`), target_seconds (finite numeric, 2..14400), style as nonempty strings/numeric. Reject bool and extra-invalid types. Optional creator_voice/context and research_requested bool may be captured; never invent missing content.
- `create_project(store: Store, payload: dict) -> dict`: uses normal Store.create_project with workflow_id `comic-to-flow`; settings contain normalized `production_brief`. `Store.create_project` also applies this validation for direct HTTP use. runtime_minutes derives from target_seconds; permit the 2-second minimum for Flow projects only while preserving existing mode bounds; aspect ratio supplied explicitly/default inferred from declared format (short9:16,long16:9), not a provider guarantee. Brief intake must be immutable or editable only through version-aware project update; reject attempts to silently change production fields via existing generic update.
- `get_handoff(store: Store, project_id: str, scene_id: str | None = None) -> dict`: only Flow film projects; returns `project_id`, `workflow_id`, `brief`, Store `next_action`, `skills` (selected applicable stage entries with name/path/sha256/status not_run), `catalog` (all eleven YouTube skills and applicability/deferred reasons), `evidence` (registered artifact/version IDs identifying executed tools), `blockers` and `automation` with browser/generation/render/publish readiness false. Evidence must be derived from actual project artifacts, not user-supplied selected names. Tool runner contract: metadata.youtube_execution = {tool_name, skill_name, skill_sha256, script_sha256, input_files, argv, status: succeeded}. Require a registered JSON receipt file and matching immutable file integrity; do not treat name-only metadata as execution. Include artifact/version IDs and review/staleness status.
- Workflow has premise/comic/script/audio/boards/blender/flow/edit with existing artifact kinds and original film scopes, plus diagram_mapping for the twelve source responsibilities. Google Flow browser_ui provider, no frozen model or prices. Stage instructions name applicable skills without bypassing stage deliverables. Source diagram JSON unchanged.

- [ ] Write tests first: missing each required field rejects; invalid duration rejects; valid short24sec persists over Store reopen and settings derive0.4min/9:16; long maps16:9; optional flags validated; existing modes unchanged.
- [ ] Add workflow/gate tests: new project next action premise, old film remains Wan; early script/flow cannot get approval; new generation route raises Problem explicitly for missing Flow film adapter rather than returning Wan.
- [ ] Add handoff tests: all eleven considered with reasons; selected instruction files exist/hashes match; no execution evidence before actual artifact output; waiting review preserved; unsupported project/foreign scene rejected.
- [ ] Run focused test and capture expected failures, implement minimal functions/hooks, rerun focused plus full suite. Record evidence in task report, no commit.

### Task 2: Run real YouTube tools and expose shared agent/HTTP handoffs

**Files:** create `studio/skill_runner.py`, `tests/test_skill_runner.py`, `tests/test_production_api.py`; modify `studio/agent_tools.py`, `studio/app.py`, `tests/test_agent_mcp.py` (replace fixed tool count with explicit expected additions/preserved no approval surface). No UI edits. Minimal production.py receipt-resource verification and corresponding fixture updates are authorized for fixed dependency provenance.

**Interfaces consumed:** Task1 `production.create_project/get_handoff`; existing `Store._check_claim`, Store.next_action/add_version and immutable file copy/import.

**Interfaces produced:**
- `skill_runner.run_tool(store: Store, project_id: str, tool_name: str, arguments: list[str], task_id: str, token: str) -> dict`: allowlist `hookscore`, `title`, `deadair`, `chapters`, `retention`, `swipe` mapped to fixed scripts. No shell execution or arbitrary script/cwd. Validate bounded list/text args, tool-specific supported flags/arity, input files explicit absolute paths where needed; capture supplied input file hashes. Append/use --json. Use current Python executable, subprocess timeout60s and bounded output processing. Validate JSON result and nonzero return before registering anything. Enforce valid matching stage/project/scene lease before running, and again during artifact registration to handle expiry/source changes. Write unique receipt/result JSON under store.root/work then import into immutable `notes` artifact at eligible stage with exact pins. Metadata includes `youtube_execution` per Task1 with tool_name/skill_name, skill_sha256/script_sha256, input_files, argv (no task tokens), status `succeeded`, and `resource_hashes` for fixed known dependencies (hooks.json for hookscore/swipe; deadair.py for chapters/retention). Validate these before/after execution and in later handoffs; arbitrary metadata paths must never be read. Content summarizes JSON, raw file preserved. Does not approve, submit, finish task or advance the required stage. Return registered IDs plus result.
- CLI/MCP tools add `create_production_project(payload: dict)`, `get_production_handoff(project_id: str, scene_id: str | None=None)`, `run_youtube_tool(project_id, tool_name, arguments, task_id, token)`, all wrappers over shared functions.
- HTTP POST `/api/production/projects` ->create; GET `/api/projects/{project}/production` ->handoff; POST `/api/projects/{project}/youtube-tool` ->run. Existing session token protects writes. Avoid route shadowing by existing catch-all frontend route.

- [ ] TDD: actual hook/title subprocess result saved with hashes and visible in later handoff; reopening Store preserves IDs; no stage approval/advance.
- [ ] TDD: unknown tool, relative/missing files, malformed arguments, nonzero output, expired/wrong project/scene token reject with no successful artifact. Stale source/claim on registration cannot save success. No shells or agent approval ops.
- [ ] HTTP tests: token required; valid create/handoff roundtrip; invalid intake400; unknown project404; service parity. Extend real MCP test to discover and call new tools without storing lease tokens in evidence.
- [ ] Focused red/green, full suite, report. No stage/commit/push.

### Task 3: Dashboard intake/handoff and SDET verification

**Files:** modify `src/main.tsx`, minimal `src/styles.css` only if needed; extend `scripts/check_dashboard.cjs` or new `scripts/check_production.cjs`; update README, validation report, backlog progress and WORK_LOG. No new provider integration.

**Interfaces consumed:** new shared API and `comic-to-flow` preset.

- [ ] Add a third project choice labeled Google Flow film, distinct from existing film and sprites. Default new-project selection to Google Flow film (the user-selected provider); preserve explicit access to old Film production (Wan) and Game sprites. Required topic/audience/style/Short-long/target-seconds fields in Flow mode; show meaningful validation. Submit via production API and preserve existing modes.
- [ ] Display combined-skill handoff for Flow project: current eligible step, selected skills, real tool-evidence status, and explicit unsupported generation/rendering/publishing status. Do not present installed catalog as completed automation.
- [ ] Flow generation preparation controls must not label model as Wan or expose sprite generation allowances; show missing adapter clearly. Existing Wan/sprite controls still work. No paid button is added.
- [ ] SDET independently checks API/backend regressions and isolated browser: create short24s Flow project with required fields, see relevant selected skill/status, reload state; run hookscore through shared interface, refresh to show linked evidence, and confirm production stage still awaits required creative work. Existing dashboard smoke still passes.
- [ ] Full56+new tests, frontend build, browser checks, doc/whitespace checks. Fresh branch review after task review. Preserve master SHA and empty index; leave all changes unstaged/uncommitted and present review paths to user.
