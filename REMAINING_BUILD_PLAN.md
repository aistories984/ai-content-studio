# Remaining build plan

Last updated: November 8, 2026. Read this with the **Current handoff** in `WORK_LOG.md` to resume. Detailed ticket requirements remain in `docs/sdlc/02-PO-BACKLOG.md`.

Use both the [simple daily checklist](leftoverwork.md) and [detailed project status](PROJECT_STATUS.md). **Item 1, Research → ideas, is Done for active-session use. Next item 2, Comic and screenplay, is Pending.** Work on one numbered item at a time and update both files at session end. No real-video or unattended-monitoring completion is implied.

## Goal and operating rules

Combine Director Studio and the YouTube skills into a working brief-to-video system following the full supplied film diagram. Use Google Flow for video generation. Release 1 ends with real downloaded takes, an accepted final video and a portable delivery bundle; the user uploads manually. Multi-account publishing is a later release. Growth and revenue are measured goals, not guaranteed outcomes.

- Current branch: `feature/flow-video-automation`, based on master `2cf5f5e`. Latest November 8 checklist inspection: user HEAD `b731fc8` (New Update), clean before this session's documentation edits. Remote/PR/merge state not checked. Inspect actual Git state on resume.
- Do not stage, commit, push, create a PR, merge, discard, or overwrite the user's work. User owns Git review/publication unless they explicitly authorize a particular action later.
- Continue with active-session agents and durable saved state. An unattended worker is not implemented.
- Preserve all twelve diagram obligations and human creative/spending gates. Select the relevant YouTube skills and retain actual outputs, receipts and downstream links.
- Keep tests isolated from real project data. No live paid generation without approved creative versions and the exact allowance. The user signs in directly; no passwords or session secrets in notes/Git.

## Full intended flow — quick resume overview

**Multi-channel scope:** user wants one shared system supporting different niches, audiences, languages, styles and formats across channels. A request for broad discovery is valid without choosing one permanent niche. Research can compare opportunities across categories, retaining category-specific sources, dates, available metrics, original angles, production effort/cost considerations and possible channel fit. Channel-relative outliers are not a universal cross-niche virality score or revenue forecast. Before producing a selected idea, establish its specific project/channel audience, voice, style, format and duration. Preserve the same twelve-obligation Director Studio process and relevant skills across these content types. Automatic monitoring, saved multi-channel profiles and multi-account publishing remain future work; finish the first end-to-end production path before claiming broad automated coverage.

**User-facing request path:** “Find promising current ideas in my niche” → active-session public research with `yt-viral` → five sourced examples/ideas, observed metrics and capture dates, channel-relative multiples when sufficient data exists, original angles, feasibility and suggested format/duration → user selects an idea → create/save the production brief → follow all twelve obligations below with relevant skill outputs and director approvals. Compare at least four videos per channel for the helper's ranking; insufficient data is labeled, never invented. Title formula labels are observations, not causal proof. On-demand assisted research is available; the local helper analyzes supplied data and does not itself discover or continuously monitor YouTube. Recurring monitoring/notifications and automated media production remain unfinished. No live trend research was performed for this clarification; first niche/audience is pending.

1. **Brief:** capture topic, audience, Short/long format, duration, style and resources.
2. **Premise:** use sourced `yt-viral` research when requested, `yt-script` hook options and `yt-package` title/thumbnail promises; director selects the idea.
3. **Ten-page comic:** produce the actual pages and approve story/visual direction.
4. **Screenplay:** adapt the approved comic into dialogue, shots and timed packages using `yt-script`.
5. **Scratch audio:** create or import voices, measure actual timing, retain stems/cues and review.
6. **Boards/references:** produce labeled boards and clean character/prop reference files; review exact prompts and files together.
7. **Blender previs:** produce editable `.blend` and playable preview; approve framing, blocking and timing.
8. **Pinned package:** freeze approved prompt/reference/audio/previs versions; check the live Flow model can support the package.
9. **Spend approval:** director approves the exact package/settings and credit/attempt allowance.
10. **Google Flow generation:** reserve an authorized attempt, generate a test take, record the observed outcome and reconcile uncertainty before any retry.
11. **Take review:** download and verify original video; director accepts or requests revisions for identity, action, timing and continuity.
12. **Final edit/delivery:** assemble accepted takes, audio, captions and credits; use `yt-edit`, `yt-package` and `yt-seo`, plus `yt-chapters`/`yt-shorts` for eligible real long-form material. Review full playback and export the MP4 and project archive.

**After delivery:** user uploads manually in R1. Use `yt-plan` with actual capacity/calendar; use `yt-comment`, `yt-retention` and `yt-audit` with real channel/audience inputs. Later releases add automatic multi-account publishing and continuous feedback. These are intended integrations, not claims that all skill workflows are already automated.

**Finish in reviewable milestones:** (1) independent review and remaining contract gaps; (2) durable film package/credit state and review UI; (3) connected research/story/comic/script/audio/boards/Blender production; (4) live Flow preflight, guarded generation and original downloads; (5) final assembly/upload assets; (6) real twelve-obligation SDET pilot. Reuse completed intake/helper/UI work. For each milestone use BA requirements → PO acceptance criteria → Developer changes → SDET evidence, with user-owned Git review. Software work can proceed before login; live compatibility should be checked early enough to avoid designing around unsupported Flow inputs.

**First concrete restart task:** item 1 is completed and independently reviewed. Continue **item 2, Comic and screenplay**: original premise review, real readable ten-page comic production, approved-comic screenplay adaptation and timed shot packages (remaining R1-006). Resolve image/page tooling and dependent creative inputs. Do not rebuild research, temporary audio, intake, helpers or credit controls. The research plan `docs/superpowers/plans/2026-11-08-research-to-ideas.md` is complete;192tests/build/five browser flows and final review PASS. The selected real-video pilot remains the English24-second illustrated robot-gardening Short; creative/spend approvals remain open. Live Flow/download/render/real-video acceptance remain later checklist items.

## Golden rule — required SOP and skill evidence

User reaffirmed November 3: this diagram is the production contract. Preserve all twelve obligations, including for Shorts. Google Flow replaces Wan as provider; this does not authorize removing any other obligation. The engine groups them into eight stages; a mapping or written instruction does not prove that the corresponding automation exists.

| Diagram obligation | Current implementation and remaining proof |
| --- | --- |
| 01 Project brief | Validated, persisted Short/long brief and handoff implemented. |
| 02 Premise and ideas | Stage and review gate exist; sourced research and authored premise adapter remain. |
| 03 Ten-page comic | Required stage/deliverable retained; real page creation and visual approval remain. |
| 04 Full screenplay | Required stage retained; actual approved-comic adaptation and shot packages remain. |
| 05 Scratch audio and timing | Native temporary-speech/recording adapter, explicit voice UI, measured mix/stems/SRT/cues and guarded registration connected. Actual pilot dialogue/timing and final voice still require creative approval. |
| 06 Boards and references | Existing versioned artifact/review contract retained; real boards and clean-reference production remain. |
| 07 Blender previs | Required stage and editable-file/preview contract retained; real Blender production/verification remain. |
| 08 Pin generation package | Immutable exact prompt/settings/source/file package snapshots and operator capability records implemented; live browser capability verification remains. |
| 09 Approve paid request | Separate human package/spend decisions, project/scene cumulative caps, atomic reservations and conservative recovery ledger implemented/tested offline; live browser execution/recovery proof remains. Generation is blocked. |
| 10 Generate video | Google Flow browser provider selected; film browser execution adapter remains. No silent Wan fallback. |
| 11 Review scene takes | Review obligation retained; original Flow download, provider trace and actual take acceptance remain. |
| 12 Edit and deliver | Existing edit/review contracts retained; final render, captions/audio, manifest and real delivery acceptance remain. |

Cross-cutting obligations: one authoritative project record, exact-version approvals, leased agent handoffs, old-version preservation, stale dependent work after revisions, and no silent approvals/retries. Existing Store/lease/receipt tests verify the built foundations; film provider/spend recovery still needs implementation and tests.

YouTube integration: the handoff considers all eleven skills and the runner executes six real helper tools with integrity-checked receipts. Read and follow each applicable `SKILL.md`; retain authored outputs as well as tool results, pin their sources and demonstrate downstream use. Scheduling, long-form repurposing, comments, retention and audits still require their actual inputs/lifecycle integrations. Deferred means unfinished or inapplicable with a stated reason, never completed. Do not run irrelevant skills just to fill a checklist.

Before calling R1 complete, SDET must verify:

- [ ] A real project traverses all twelve obligations with approved exact versions, original files and retained review evidence.
- [ ] Applicable skills produce real outputs used by the next stages; deferred skills have explicit reasons and prerequisites.
- [ ] Changed inputs invalidate dependent approvals; expired leases and stale pins block saves/submissions.
- [ ] Generate cannot run without the approved package and remaining allowance; unknown outcomes cannot trigger duplicate paid retries.
- [ ] An authorized real Flow test produces original downloadable, decodable video and a reviewed final delivery bundle.
- [ ] Independent branch review and real-video acceptance are recorded separately from local automated tests.

Verification November 3: full Python suite **102 passed, no skips** (`.tools/golden-rule-tests.log`); production build passed. Existing tests cover the twelve mapping keys/stage order, early-stage approval rejection, demo-bypass rejection, all eleven skill entries, actual helper execution, receipt integrity/history and no automatic approval/advancement. This is local integration evidence, not full SOP/provider acceptance. No production video was generated in this audit.

## Already implemented — do not rebuild

- [x] Active-session Research → ideas workspace: durable public-source requests/reports, actual swipe outputs/provenance, original suggestions, human selection and immutable research-to-brief/handoff/export pins.32agent operations; no agent selection/approval.192tests/no skips, build, five browser flows and independent reviews PASS; ordering and optional-voice UI findings fixed/rereviewed. A dated secondary-source example is saved without selecting/approving a production project.
- [x] Consolidated Director Studio, both original skills and eleven YouTube skills, resources and licenses.
- [x] Installed local runtimes/dependencies and fixed the verified Mac setup and original helper issues.
- [x] Added `comic-to-flow` film preset, validated per-project Short/long intake and persisted brief.
- [x] Added combined-skill handoff with source hashes, reasons for deferred skills and current/historical receipt tracking.
- [x] Added allowlisted execution of six real local YouTube tools, strict argument/file/JSON checks, task/source revalidation, receipts and shared HTTP/CLI/MCP operations.
- [x] Added Flow project intake and evidence UI, retaining existing Wan/sprite modes and explicit missing-adapter status.
- [x] Added additive immutable film package/capability/decision/allowance/attempt/result tables, source/file/currentness checks and conservative cumulative credit accounting; 25 focused tests and independent service review passed.
- [x] Added five agent-safe film operations (26 total), strict HTTP envelopes, separate director package/spend review, dashboard cap/attempt history and film-production.json audit exports. No Generate button or live readiness claim.
- [x] November6 final verification:132tests/no skips, production build, all3 isolated browser checks and independent whole-branch review PASS. This does not satisfy real-provider acceptance.
- [x] Fixed Flow direction-save regression; isolated browser tests cover unchanged intake, exact package/ref review, spending decisions, unknown commitment after Refresh/reload and desktop/mobile layout.
- [x] Connected real native temporary speech and supplied-recording rendering through shared guarded HTTP/CLI/MCP service, explicit scene-sized voice UI and human review. Final November8:178 tests/no skips, build, four browsers and independent native-audio integration review PASS; no paid/provider operation.
- [x] Verified this local slice: 102 Python tests with no skips, frontend production build and both isolated browser checks. This is recorded evidence from November 3, not a claim that future edits or real Flow execution have passed.

Review evidence: `docs/sdlc/05-LOCAL-REVIEW.md` and `docs/COMBINED_VALIDATION.md`. Implementation locations: `studio/production.py`, `studio/skill_runner.py`, `studio/store.py`, `studio/agent_tools.py`, `studio/app.py`, `src/main.tsx`, and the associated tests.

## Next action

1. Inspect the current branch/diff and the handoff without repeating the repository audit or overwriting local work.
2. Read November8 final native-audio results:178 tests/build/four browser checks and independent reviews passed. Do not repeat completed reviews or implementation unless changes/new evidence justify it. Local speech acceptance is not real Flow release acceptance.
3. Research → ideas is Done. Continue the next checklist item only: premise review, image/page/ten-page comic and screenplay/timed-shot production (remaining R1-006). Read targeted contracts and relevant skills; missing assets/tool access block only dependent work. Boards/Blender/Flow/download/render follow their checklist items; temporary audio is also complete.
4. Respect the user's local review/commit/PR workflow throughout. If the user has merged changes in the meantime, inspect actual Git state before choosing the next feature branch; never assume the recorded base is still current.

## Remaining Release 1 work

The order below follows dependencies. Existing supporting pieces are reused rather than rebuilt. No entire R1 ticket is declared accepted merely because a portion works.

| Ticket | Current state | What remains |
| --- | --- | --- |
| R1-001 — Flow mapping/contracts | Partial | Finish executable provider/capability/package contracts and acceptance traceability; preserve the existing Flow preset and original diagram. |
| R1-002 — Brief/skill handoff | Partial | Intake, helper receipts and independently reviewed selected-research evidence/brief pins work. Complete authored-output/downstream coverage and review for the remaining creative/media stages. |
| R1-003 — Durable film state | Offline package/ledger implemented | Real verified take receipts and downstream adapter integration remain. Additive schema/currentness/isolation/source checks and shared interface evidence are implemented; reported downloaded status is not a verified file. |
| R1-004 — Credit/recovery controls | Offline implemented and independently reviewed | Live browser click/result/crash recovery and real spending acceptance remain for R1-010/014. Exact package/settings approval, cumulative caps, atomic reservations, unknown reconciliation and no-refund accounting are tested locally. |
| R1-005 — Package/spend review UI | Implemented and independently reviewed locally | Real provider controls/media and full production acceptance remain. Exact package/reference/settings, separate human decisions, cumulative allowance/cap/attempt status and Refresh/reload tested in isolated browser. |
| R1-006 — Research/story/comic/script | Research → ideas completed; actual premise/comic/screenplay production pending | Active-session sourced reports, original suggestions and human selection into pinned briefs implemented/verified. Next author/review the actual premise, generate readable ten-page comic and adapt approved comic into screenplay/timed shots with relevant skills/provenance. Research selection is not premise approval. |
| R1-007 — Audio/boards/references | Temporary audio connected and reviewed; boards/reference production pending | Native temporary voices or supplied recordings produce real measured mix/stems/SRT/cues under source/lease/revision guards. Choose final voice/audio and connect actual boards/clean-reference creation; real pilot approval remains. |
| R1-008 — Blender previs | Existing import/review path exists | Connect and verify real Blender execution or explicit supplied `.blend`/preview handoff against approved timing, cameras and character IDs. |
| R1-009 — Flow capability preflight | Live verification pending | Verify supported visible browser control, direct user login, upload/download, actual model/reference/duration/output support and displayed credit cost; resolve compatibility with the approved film package. |
| R1-010 — Flow execution | Not implemented for films | Connect the guarded visible-browser runner to reservations, single submission, observation/evidence, safe pause/resume and reconciliation. No hidden API or silent provider substitution. |
| R1-011 — Original downloads | Not implemented for films | Download the actual selected take; reject incomplete/wrong/non-video files; measure/decode/hash originals and register immutable files with provider correlation. |
| R1-012 — Final video assembly | Rough-cut review/export exists | Render a complete usable MP4 from approved takes/ranges, audio, captions and credits; check playback/sync/continuity and export a verified delivery archive. |
| R1-013 — Manual-upload assets | Writing skills exist | Connect reviewed titles/thumbnail brief, description, applicable chapters and optional rendered Shorts to the actual finished video and delivery bundle. Draft Short candidates are not exported clips. |
| R1-014 — Real pilot/release acceptance | Blocked on preceding work and live inputs | Run the full diagram with real approved assets and authorized Flow execution; save original downloads, review the complete final film and retain SDET evidence. Local fixtures cannot satisfy this gate. |

## Inputs needed only before dependent work

- Pilot selected November 6: a 24-second illustrated Short about a robot learning to garden, in English. Audience/voice, detailed creative direction and quality requirements remain. This is one acceptance example, not a permanent niche; no artifact/upload/spending approval is implied.
- Creator voice/examples or an agreed new voice direction; authorized references and any supplied assets.
- Selected/available image and Blender tools, final audio direction/assets and any associated permissions/cost limits. Native Mac/Windows temporary speech and supplied PCM recording paths are already connected; voices are explicitly selected, never silently substituted.
- Supported visible Flow browser and direct user login, observed model/features and explicit upload/attempt/credit allowance for the exact package.
- Final output specifications and delivery location.

Missing inputs pause the dependent production stage, not unrelated software work. Never invent evidence, credentials, spending authorization or provider success.

## Later releases — outside the manual-upload R1 boundary

- [ ] Versioned profiles with different niches, audiences, languages, styles, voices, formats and monetization objectives per channel/account; keep channel assets/context separate while reusing one production engine.
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
