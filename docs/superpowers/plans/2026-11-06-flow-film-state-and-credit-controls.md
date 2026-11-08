# Flow film state and credit controls implementation plan

> For agentic workers: use superpowers:subagent-driven-development task by task. User override: no staging, commits, push, PR or merge. Preserve existing local documentation edits; continue feature/flow-video-automation in place.

**Status:** Offline scope completed and independently reviewed November 6, 2026;132 tests/build/three browser checks passed. Live production/provider/delivery remain outside this completed slice. No commits or publication.

**Goal:** Build durable exact-version film packages, bounded credit/attempt accounting and human review screens needed before any Google Flow film execution.

**Architecture:** Extend the existing authoritative SQLite Store with a focused film service. Preserve old Wan/sprite semantics; film operations use separate tables/contracts, current source/lease checks and shared HTTP/CLI/MCP rules. A stored browser observation is evidence supplied by an active operator, not proof this application has a connected browser.

**Tech stack:** Existing Python/FastAPI/SQLite/React/TypeScript; no new dependencies.

**Spec:** `docs/superpowers/specs/2026-11-03-flow-video-r1-design.md`; existing BA/PO/SDET docs, tickets R1-003/004 and package/spend part of R1-005. Existing user instruction to finish/resume authorizes this software work. No paid request or creative approval is authorized.

## Global constraints

- Preserve all twelve diagram obligations and actual relevant YouTube skill output evidence; do not bypass any upstream stage.
- No agent approval tools, provider API, paid call, authentication capture or account upload. No live provider truth, model, prices or supported durations hardcoded.
- Keep SQLite authoritative with additive/idempotent schema initialization, immutable records and exact package hashes. Existing Wan/sprite workflows/tests remain unchanged.
- Active-session operation, not an unattended worker. All tests use disposable data. No tests alter real studio-data or outputs.
- Human spending decisions are HTTP/dashboard-only under existing director-session protection. Agents may prepare, reserve and report observed results but cannot grant or alter allowances/project caps.
- Use current approved source version/file hashes, direction, scene revision and a live matching flow-stage lease. Never expose private lease tokens in records/exports.
- Generation UI remains explicitly disconnected; reservations do not click Generate. New packages/allowances cannot erase project spending or unresolved attempts.

## Review focus

- Sources changed after preparation/approval: reserve rejects stale versions, wrong project/scene, changed bytes or revoked approvals (Task1).
- Concurrent requests cannot reserve twice against one scope/account or exceed caps (Task1).
- Unknown/reserved/submitted outcomes block new attempts even across package/allowance revisions, Store reopen or lease expiry (Task1).
- Failure/timeout never refunds credits; observed costs are separate and higher observed costs consume project budget (Task1).
- Dashboard shows exact immutable prompt/pins/settings/account/capability/allowance and true missing-browser state; agents have no approval operation (Task2).

### Task 1: Durable packages, capability observations and spend/recovery ledger

**Files:** create `studio/film.py`, `tests/test_film.py`; minimal Store initialization hook in `studio/store.py`. A separate contracts file only if useful; avoid generic abstractions. Do not edit app/UI/agent_tools in this task.

**Interface:** `FilmService(store)` with methods:
- `record_capability(project_id, payload, task_id, token)` -> immutable record. Payload includes nonsecret account_ref, visible model, input_mode, observed duration/aspect/output count, displayed credit cost, browser upload/download observations, observed evidence and expiry. This is a package-specific supported-settings observation, not invented provider capabilities. Validate finite values and bounded text; outputs=1 for first release. Evidence is retained, `observed_at` assigned locally. Expiry max24h; upload/download must be true for a usable snapshot. Record only for matching flow-stage lease. No cookies/tokens/session secrets accepted as fields.
- `prepare_package(project_id, scene_id, payload, task_id, token)` -> immutable package. Payload names capability_id, exact settings and ordered refs `{version_id,file_index,role}` (ingredient/first_frame/last_frame), and exact prompt. Require flow next-action ready and matching lease; all prior diagram artifacts approved, current and integrity checked (including audio and Blender files). Prompt must equal approved boards or previs prompt. Sources from get_next_action pins. Clean still refs must be current approved/pinned files; forbid GIF/labeled boards unless explicitly clean file mapping. Keep audio/previs pinned as planning assets, not claims Flow ingests them. Enforce selected observed duration/aspect/outputs exactly match approved scene/project for this slice; unsupported timing adaptations block instead of truncating. Settings/model/account/input_mode bind capability. Canonical JSON SHA256 excludes generated IDs/timestamps. Return id/hash/data, status/readiness blockers and no external action.
- `get_state(project_id)` -> safe records for capabilities, packages, human decisions, attempts and project credit cap with consumed/reserved totals, remaining budget and blockers. Recompute package currentness from live pins/hashes, never just stored booleans. No lease secrets or arbitrary metadata paths.
- `set_budget(project_id, payload)` -> human-only project credit cap, audited. Cap may be explicitly raised by human; cannot drop below commitments or reset on revision.
- `review_package(package_id, payload)` -> human-only immutable approved/rejected decision with exact package_hash, expected currentness and note. Separate creative package review from spending allowance. A later rejection blocks future reservations, never rewrites attempts.
- `approve_allowance(package_id, payload)` -> human-only approved exact package/hash/account/model/settings, upload_authorized=true, max_attempts (1..100), max_credits (0..100000), expiry. Requires current human-approved package and project cap. Append allowance version; previous reservations continue counting against package totals (new approval is a cumulative ceiling, not a reset). Expose explicit revocation through a decision if needed.
- `reserve_attempt(package_id, task_id, token)` -> transactionally reserve one observed cost and output under current exact package/approval/allowance/capability/live claim. Validate all sources inside write transaction. Block any unresolved project/scene attempt and unresolved same account across projects. Persist original task identity, estimated/reserved cost, exact scope/settings, history; never tokens. Enforce per-package cumulative attempt/credit ceiling plus project cap, including failed/resolved/unknown attempts. Return attempt ID and no_external_action=true.
- `record_result(attempt_id, payload, task_id, token)` -> append observed transition/evidence under matching current flow-scene claim; a fresh lease can reconcile same attempt after expiry/revisions without authorizing new generation. States reserved -> submitted/unknown/failed; submitted/unknown -> observed/unknown/failed; observed -> downloaded/unknown; downloaded terminal. Unknown may reconcile back to submitted with concrete evidence. No backward reset, no arbitrary terminal rewrites. Track observed_credits separately (finite nonnegative); conservative commitment=max(reserved,observed), never automatic refunds. Evidence required; provider identity optional but immutable once set. Status downloaded is an observation only and must not claim local file verification/creative approval. Real download registration is later work.

**Steps:**
- [x] Write requirement-driven tests and run RED before implementation: old database reopen; all twelve upstream obligations remain; prepare before approvals rejects; package hashes stable for same inputs and change on meaningful inputs; exact settings/reference roles; file mutation/revoked/stale sources; lease expiry/wrong scope; no tokens.
- [x] Implement minimum state/contracts; verify focused GREEN.
- [x] Add RED tests for project and cumulative package caps across revised approvals; unresolved scene/account attempts across packages/projects/restarts; concurrent competing reservations; cost overrun and failure no refund; expiry; fresh-lease recovery and state transition rejection.
- [x] Implement transactional spend/recovery and run focused/full suites. Record exact commands/counts, limits and no provider execution. Leave unstaged. Write `.tools/2026-11-06-film-task1-report.md`.

### Task 2: Shared interfaces and exact package/spend dashboard

**Files:** `studio/agent_tools.py`, `studio/app.py`, `studio/production.py`, `src/main.tsx`, minimal CSS, API/MCP tests and isolated browser smoke.

**Interfaces:** consume Task1 FilmService. Expose agent tools `record_film_capability`, `prepare_film_package`, `get_film_state`, `reserve_film_attempt`, `record_film_result`; never approval/budget operations. HTTP equivalents scoped to project/package/attempt, plus director-only budget/package-review/allowance endpoints. Validate shared errors and mismatched URL/body identity. Preserve old sprite operations distinctly.

- [x] RED tests: shared agent/API parity, director token required, wrong workflow/scope rejected, no approval tools in CLI/MCP, secrets absent.
- [x] Wire API and agent tools; generation_package can provide saved package state explicitly without any external execution, or retain clear missing execution-adapter blocker. Do not label readiness as live browser ready based on stored observations alone.
- [x] Dashboard shows packages, exact prompts/ordered pin names/hashes, account/model/settings, capability age/evidence, separate package review and allowance form, project cap, commitment and unresolved attempt blockers. No Generate button; clear live execution/download/render adapters still absent. User must explicitly check exact review/upload authorization and enter budget/limits; no automatic approval or invented prices.
- [x] Build and isolated desktop/mobile browser checks: real disposable approved fixture package displayed; human package/spend approval and cap persist; unknown reservation remains visible; reload preserves state; no browser execution is falsely claimed.
- [x] Review, fix confirmed findings, run full suite/build/browser regressions. Update README/interfaces/remaining plan and WORK_LOG with actual completed/remaining boundaries.

### Task 3: Independent acceptance and resume handoff

- [x] Fresh independent review of Task1 and Task2 (each scoped diff/report), fix important findings with regression tests.
- [x] Full tests and frontend build; existing dashboard/Flow browser checks and new package/spend check. Keep real data untouched.
- [x] Record completed R1-003/004/005 portions and remaining live/media/download/render requirements honestly. Identify precise missing tool/user inputs for real production; never claim full R1 or fabricated live E2E.
- [x] Keep every change local/unstaged/uncommitted. User owns commit/PR/merge. Preserve ledger and reports for review/resume.
