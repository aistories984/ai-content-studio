# Research → ideas Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax.

**Goal:** Finish the active-session research → saved sourced ideas → human selection → Director Studio brief connection, not continuous monitoring.
**Architecture:** Immutable research requests and append-only reports live in the same SQLite database as Studio. Agents use their available public web research tools to collect evidence, then a shared ResearchService validates/stores it and runs the existing yt-viral swipe.py. Only a director HTTP selection creates a project with an immutable source link in one transaction. Production handoff and export retain the exact report and selected idea. A dashboard research workspace works before any project exists.
**Tech Stack:** Existing Python/SQLite/FastAPI, fixed Python helper, React/TypeScript, Playwright; no new dependencies.
**Spec:** Existing approved R1 design docs/superpowers/specs/2026-11-03-flow-video-r1-design.md, R1-006 in docs/sdlc/02-PO-BACKLOG.md, and user-adopted leftoverwork.md item 1 finish checklist.
**Execution authorization:** User explicitly requested finishing this existing R1 connection, preserving active-session agents and human review. Continue existing local feature branch; no new approval flow for these reversible changes.

## Global Constraints

- Preserve all twelve Director Studio obligations. Google Flow replaces Wan only. New researched projects start at premise with no approved stages, scenes or spending allowance.
- Read director-studio and yt-viral and the eleven-skill catalog. Save actual required helper outputs, source hashes and downstream evidence; title formula is lexical observation, not causal explanation.
- Support one niche or broad categories. No forced permanent niche, API key, credential collection, scraping/login or automatic publication.
- Research runs through the active agent's available public web tools. Dashboard saves requests/reports and selections; it does not launch a background AI worker. State this in UI/docs.
- At least four unique comparable videos per channel/format for channel-sample medians. Missing views are null and excluded, never zero imputation. Reject negative/nonfinite/bool metrics, duplicate video identity (including watch/shorts aliases), malformed URLs/timestamps/oversize requests.
- Sourced suggestions are authored by the active agent; never generate canned fictional trends or claim measurements verified by the local validator. Preserve capture dates, sample limitations and source evidence. Research observations do not promise reach/revenue.
- Project selection is director-only, exact-report/idea and retry-idempotent. New reports never rewrite old selections. Reject conflicting retries or wrong IDs; fail closed on changed research/tool sources.
- No stage/paid approval, no source fetch or shell from submitted JSON. No agent selection/approval operation.
- Preserve user projects; use disposable DIRECTOR_DATA in tests. Leave all changes local, unstaged and uncommitted. Keep both leftoverwork.md copies and PROJECT_STATUS.md aligned.

## Review Focus

1. Empty/partial/missing-metric research must remain readable and explicitly unranked, never become claimed viral evidence.
2. Same video via URL aliases and mixed short/long channel samples cannot inflate median support.
3. Double-click/retry/concurrent selection cannot create duplicate/orphan projects or bind wrong report.
4. Tampered saved report or changed helper/skill resources cannot count as current downstream evidence.
5. Pending research and selected project survive reload and desktop/mobile UI without accidental creative approval.

### Task 1: Durable shared research service, APIs and downstream pins

Files: create studio/research.py, tests/test_research.py, tests/test_research_api.py; modify studio/store.py, studio/production.py, studio/app.py, studio/agent_tools.py, tests/test_agent_mcp.py.

Interfaces (binding):
- ResearchService(store).create_request(payload) -> request state: id, query, categories, language, time_window, created, reports (newest first), selections; get_request(research_id); list_requests().
- create payload: query(required), categories(list of strings, can be empty for broad), language(required), time_window(required). Bound JSON <=1MB, query/timewindow <=2000, language<=80, categories<=12.
- save_report(research_id,payload) -> full updated request state. Payload: expected_report_id (null for first, exact latest id subsequently), sampling_note(required), shared_pattern(required), limitations(required), collected(list<=500), ideas(list<=5, zero allowed).
- Each collected row: channel, channel_url(public YouTube channel URL), title, url(public YouTube video URL), category, format(short|long), views(nonnegative finite integer or null), duration(nonnegative finite number or null), observed_at(ISO8601 timezone-aware <=now+5min), evidence_url(public https source), evidence_note(required); optional published_at. All fields retained in normalized immutable report.
- Ideas: title, original_angle, source_urls(nonempty list referencing collected URLs), feasibility, format(short|long), target_seconds(2..14400), optional audience. Server assigns idea ids. Derived evidence labels, ranking/formulas/insufficient-data notes come from actual swipe result, not client claims.
- Reports have id, sha256, created, collected, ideas, tool execution/result and selected skill provenance. Store exact request source too. Immutable tables/triggers and content hash validation on reads.
- Run fixed swipe.py subprocess with validated temporary collected.json, --min 2.0 --json, bounded timeout/output and source hashes. Group by canonical channel_url + format, retaining readable channel labels in output. Unknown counts never satisfy four-video rule.
- select_idea(research_id,report_id,idea_id,payload) -> created/existing project dict. HTTP director only; payload audience/style required, optional creator_voice; use idea title/original_angle/format/duration for validated immutable brief. Allow optional explicit topic/format/target_seconds adjustments validated as brief and recorded in immutable selection; never accept settings/research pins from caller. Atomic create+link+selection using an internal transaction-aware Store creation helper. One selection/project per report idea; exact retry returns same project, conflicting payload409.
- project_research(project_id) -> exact request/report/idea/selection or null, integrity checked. get_production_handoff adds research field, truthful yt-viral evidence state. Export includes research.json. Sources independently accessible from UI and agent handoff; not just a metadata name.
- Shared agent operations: create_research_request(payload), list_research_requests(), get_research_request(research_id), save_research_report(research_id,payload). No agent select_idea.
- HTTP GET/POST /api/research, GET /api/research/{id}, POST /api/research/{id}/reports, POST /api/research/{id}/select with strict body {report_id,idea_id,payload}. Existing director-session middleware on all writes.
- Updating an already selected report adds a new immutable report; earlier selection remains pinned. New selection using superseded report rejects unless exact retry of previous selection. Research records predate projects and do not need fabricated project leases.

Steps:
- [x] Write meaningful RED tests for stored request/reopen, actual ranking/skill hashes, partial/empty evidence, duplicates/mixed formats, exact selection, wrong IDs/currentness/idempotency/concurrency, tampering/source change and export/production handoff.
- [x] Observe expected failures before implementing service.
- [x] Implement service and minimal internal Store transaction support without altering ordinary create behavior.
- [x] Wire shared APIs/agent operations, update tool-count expectation and test session security/CLI JSON/MCP presence/no selection authority, envelope validation.
- [x] Run focused tests and full Python regression; save report and self-review. No commits.

### Task 2: Research dashboard and end-to-end browser evidence

Files: create src/ResearchPanel.tsx, scripts/check_research.cjs; modify src/main.tsx, src/styles.css; documentation docs/youtube/RESEARCH.md, docs/AGENT_INTERFACE.md.
Consumes: Task1 exact HTTP API and returned state. Inspect actual service shape; do not guess.
Produces: visible Research → ideas workspace independent of current project, pending requests and reports readable after reload, sourced suggestions and director selection form, selected project opens normal full Studio.

Steps:
- [x] Write browser RED for opening empty research workspace, creating broad request, pending/active-session boundary, agent/API supplied report, source links and ranking/insufficient notes, selection with audience/style, duplicate retry, reload and correct project handoff. Verify no stage approved and all twelve mapping obligations.
- [x] Implement accessible responsive panel with request form/history/refresh, report cards (source/capture/metrics/limitations and original angle/feasibility/format/duration), exact report/idea selection and open existing project.
- [x] Display research in production handoff with source/report link and clear unranked context; no stale async response overwrites after selecting another request.
- [x] Add explicit optional JSON report import for operator convenience, bounded/error-safe, without pretending dashboard itself researched the web.
- [x] Run production build + isolated research browser check desktop/mobile, source reload/currentness, no pageerrors; save screenshots.
- [x] Write plain operator usage including active-session tools and human selection. Run relevant prior browsers for regressions.

### Task 3: Live public research proof, final verification and status

Files: docs/youtube/RESEARCH.md, PROJECT_STATUS.md, leftoverwork.md, REMAINING_BUILD_PLAN.md, WORK_LOG.md, THOUGHTS_AND_PLANS.md, docs/COMBINED_VALIDATION.md; outer checklist/continuity copies.
- [x] Use available public web research to capture at least one real example batch with honest source dates/available metrics; save as an example in ignored .tools or local runtime data, distinguish demo/fixture from observed web data. Missing metric/baseline remains unranked. Do not invent current viral evidence.
- [x] Verify live batch stores and survives reads; do not choose an idea/create a user production project or approve anything on user's behalf.
- [x] Run full Python tests/build/relevant browser checks once final code stable; independent review of complete changes and focused fixes if required.
- [x] Update both user trackers with exact scope/evidence and remaining limits. Only mark item1 Done for working active-session research-to-selection handoff; continuous monitoring/later production remain Pending.
- [x] Leave local unstaged/uncommitted on current feature branch; preserve review ledgers.


**Completion:** November 8, 2026. All three tasks complete for active-session scope. Independent backend/UI/final reviews PASS; two UI findings fixed with real RED/GREEN and scoped signoff. No full-video, background-monitoring or publishing acceptance. Changes remain local/uncommitted.
