# Remaining build plan

Last updated: November 3, 2026. Read this with the **Current handoff** in `WORK_LOG.md` to resume. Detailed ticket requirements remain in `docs/sdlc/02-PO-BACKLOG.md`.

## Goal and operating rules

Combine Director Studio and the YouTube skills into a working brief-to-video system following the full supplied film diagram. Use Google Flow for video generation. Release 1 ends with real downloaded takes, an accepted final video and a portable delivery bundle; the user uploads manually. Multi-account publishing is a later release. Growth and revenue are measured goals, not guaranteed outcomes.

- Current local branch: `feature/flow-video-automation`, based on master `2cf5f5e`. The current work is unstaged and uncommitted.
- Do not stage, commit, push, create a PR, merge, discard, or overwrite the user's work. User owns Git review/publication unless they explicitly authorize a particular action later.
- Continue with active-session agents and durable saved state. An unattended worker is not implemented.
- Preserve all twelve diagram obligations and human creative/spending gates. Select the relevant YouTube skills and retain actual outputs, receipts and downstream links.
- Keep tests isolated from real project data. No live paid generation without approved creative versions and the exact allowance. The user signs in directly; no passwords or session secrets in notes/Git.

## Already implemented — do not rebuild

- [x] Consolidated Director Studio, both original skills and eleven YouTube skills, resources and licenses.
- [x] Installed local runtimes/dependencies and fixed the verified Mac setup and original helper issues.
- [x] Added `comic-to-flow` film preset, validated per-project Short/long intake and persisted brief.
- [x] Added combined-skill handoff with source hashes, reasons for deferred skills and current/historical receipt tracking.
- [x] Added allowlisted execution of six real local YouTube tools, strict argument/file/JSON checks, task/source revalidation, receipts and shared HTTP/CLI/MCP operations.
- [x] Added Flow project intake and evidence UI, retaining existing Wan/sprite modes and explicit missing-adapter status.
- [x] Verified this local slice: 102 Python tests with no skips, frontend production build and both isolated browser checks. This is recorded evidence from November 3, not a claim that future edits or real Flow execution have passed.

Review evidence: `docs/sdlc/05-LOCAL-REVIEW.md` and `docs/COMBINED_VALIDATION.md`. Implementation locations: `studio/production.py`, `studio/skill_runner.py`, `studio/store.py`, `studio/agent_tools.py`, `studio/app.py`, `src/main.tsx`, and the associated tests.

## Next action

1. Inspect the current branch/diff and the handoff without repeating the repository audit or overwriting local work.
2. Complete the pending independent review of the runner/UI and whole branch; fix any confirmed findings with regression checks. Initial intake review was completed, but later independent review was interrupted by the sub-agent usage limit. Do not report that review as passed.
3. Resolve the outstanding portions of R1-001/002 against their acceptance criteria, then implement **R1-003: film-specific durable state/contracts**, followed by R1-004 credit/attempt controls. Software work can proceed without a Google login; live provider work cannot.
4. Respect the user's local review/commit/PR workflow throughout. If the user has merged changes in the meantime, inspect actual Git state before choosing the next feature branch; never assume the recorded base is still current.

## Remaining Release 1 work

The order below follows dependencies. Existing supporting pieces are reused rather than rebuilt. No entire R1 ticket is declared accepted merely because a portion works.

| Ticket | Current state | What remains |
| --- | --- | --- |
| R1-001 — Flow mapping/contracts | Partial | Finish executable provider/capability/package contracts and acceptance traceability; preserve the existing Flow preset and original diagram. |
| R1-002 — Brief/skill handoff | Partial | Complete authored-output and downstream-consumption coverage as production stages are connected; finish independent review. Intake, local tool execution and receipts already work. |
| R1-003 — Durable film state | Not implemented beyond intake | Add versioned film packages, capability snapshots, allowances, attempts and receipts with migrations, project isolation, source pins and interface parity. |
| R1-004 — Credit/recovery controls | Film implementation pending | Exact package/account/model/settings approval, project credit cap, atomic reservations, attempt/output limits, unknown-outcome reconciliation and crash recovery. Sprite controls are a reference, not a film implementation. |
| R1-005 — Package/spend review UI | Basic handoff UI exists | Add exact generation package/reference/settings comparison, explicit spending decisions, allowance status and actionable blockers. |
| R1-006 — Research/story/comic/script | Helpers exist; production automation pending | Connect sourced trend research and original premise selection; produce real ten-page comic and screenplay artifacts using configured tools and relevant skills, with approvals and provenance. |
| R1-007 — Audio/boards/references | Existing recorded-audio timing supported | Choose/configure actual audio generation or supplied recordings; produce measured mix/stems/cues, real boards and ordered clean references; preserve overruns and revision invalidation. |
| R1-008 — Blender previs | Existing import/review path exists | Connect and verify real Blender execution or explicit supplied `.blend`/preview handoff against approved timing, cameras and character IDs. |
| R1-009 — Flow capability preflight | Live verification pending | Verify supported visible browser control, direct user login, upload/download, actual model/reference/duration/output support and displayed credit cost; resolve compatibility with the approved film package. |
| R1-010 — Flow execution | Not implemented for films | Connect the guarded visible-browser runner to reservations, single submission, observation/evidence, safe pause/resume and reconciliation. No hidden API or silent provider substitution. |
| R1-011 — Original downloads | Not implemented for films | Download the actual selected take; reject incomplete/wrong/non-video files; measure/decode/hash originals and register immutable files with provider correlation. |
| R1-012 — Final video assembly | Rough-cut review/export exists | Render a complete usable MP4 from approved takes/ranges, audio, captions and credits; check playback/sync/continuity and export a verified delivery archive. |
| R1-013 — Manual-upload assets | Writing skills exist | Connect reviewed titles/thumbnail brief, description, applicable chapters and optional rendered Shorts to the actual finished video and delivery bundle. Draft Short candidates are not exported clips. |
| R1-014 — Real pilot/release acceptance | Blocked on preceding work and live inputs | Run the full diagram with real approved assets and authorized Flow execution; save original downloads, review the complete final film and retain SDET evidence. Local fixtures cannot satisfy this gate. |

## Inputs needed only before dependent work

- First real project's topic, audience, Short/long format, target duration, style and quality requirements.
- Creator voice/examples or an agreed new voice direction; authorized references and any supplied assets.
- Selected/available image, audio and Blender tools and any associated permissions or cost limits.
- Supported visible Flow browser and direct user login, observed model/features and explicit upload/attempt/credit allowance for the exact package.
- Final output specifications and delivery location.

Missing inputs pause the dependent production stage, not unrelated software work. Never invent evidence, credentials, spending authorization or provider success.

## Later releases — outside the manual-upload R1 boundary

- [ ] Versioned profiles with different audiences, styles, voices and formats per channel/account.
- [ ] Multiple authorized YouTube, TikTok and Instagram accounts, with strict destination/account isolation.
- [ ] Publishing/scheduling adapters with actual supported platform permissions, receipts, duplicate-post prevention and recovery.
- [ ] Ongoing trend monitoring, calendars and actual post-release comment/retention/audit feedback.
- [ ] Business measurements: accepted output cost, time, reach, conversions and attributable revenue.
- [ ] Unattended worker/scheduling/notifications, if explicitly chosen after the active-session workflow is proven.

## Resume instruction

When the user says **“continue what remains,” “build the remaining automation,” “read where we left off,”** or similar:

1. Read `WORK_LOG.md` Current handoff and this file first.
2. Inspect branch/status and preserve existing changes; confirm the actual code state before selecting the next unfinished item.
3. Continue the first actionable unfinished item with BA/PO/Developer/SDET discipline and relevant skills. Read its ticket, targeted code and tests only as needed.
4. Do not redo completed intake/runner/UI work or interpret “again” as a request to rebuild everything unless the user explicitly asks for a reset/rebuild.
5. Update this checklist, ticket progress, verification evidence and the work log after meaningful changes. Keep implementation, verification, independent review and real-provider acceptance separate.

This file is development continuity; Studio's SQLite records remain the authority for actual production tasks, artifacts, approvals and attempts.
