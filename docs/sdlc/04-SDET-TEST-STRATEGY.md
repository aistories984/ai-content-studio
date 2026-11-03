# SDET test strategy — R1 combined YouTube production

Date: November 3, 2026. Status: proposed verification plan, not implementation or execution evidence.

## Release claim and present evidence

R1 succeeds when a plain-language brief routes through relevant skills from both sources and the required film diagram, produces a real Google Flow video, preserves the original download, and delivers playable media with provenance and human creative review. Posting is manual. A script, supporting artifact, simulated receipt, browser smoke, or sprite workflow is insufficient evidence of R1 completion.

The recorded baseline in `docs/COMBINED_VALIDATION.md` is 56 Python tests with no skips, production frontend build, six YouTube CLI fixtures, real stdio MCP handoff, and isolated Chromium desktop/mobile smoke. That is historical local integration evidence, not a fresh execution in this planning task. No tests, installs, browser automation, provider calls, generation, or approvals were performed for this document. The film adapter for Flow remains unimplemented; current film export targets Wan and Flow controls currently target sprites.

Read as the test basis: `AGENTS.md`, `WORK_LOG.md`, `docs/COMBINED_VALIDATION.md`, `docs/youtube/WORKFLOW.md`, both Director Studio skill contracts, `tests/test_youtube_tools.py`, `tests/test_sprite_workflow.py`, `tests/test_agent_mcp.py`, and `docs/design/user-required-workflow.json`. The YouTube catalog and applicable `yt-script`/`yt-package` instructions informed the planning gates. No content skill was executed.

## Scope and ownership

The software SDLC reviewer assesses requirements, architecture, code, safety controls, test evidence, defects, and release readiness. The human creative approver decides whether exact creative versions, references, prompt, takes, and final delivery are acceptable, and authorizes any exact paid allowance. A software sign-off, successful test, QC result, or agent submission cannot supply creative approval or paid authorization. The agent surface must continue to lack approval operations.

All automated app/approval tests use disposable projects and an explicit temporary `DIRECTOR_DATA`; test approvals may exist only in those fixtures. Never mutate actual user approvals, production records, or account state during regression testing. Live creative approvals are real user decisions, separately recorded, never test assertions that manufacture consent. Ordinary CI has no provider credentials, no paid actions, no cloud upload, and no publication.

Future multi-account YouTube/TikTok/Instagram publishing is a separate release scope. R1 provides manual posting files and clear account-independent handoff; it must not imply scheduled posting or connected profiles exist.

R1 uses active-session agents. Test explicit pause at review/missing inputs and safe resumption in a later active session from durable project/attempt state; do not claim an unattended worker or persistent scheduler exists. Background worker lifecycle/scheduling acceptance belongs to a future release.

## Skill and workflow traceability

Required combined-flow check: inspect actual tool receipts or authored deliverables, their pinned input/output versions, and the downstream stage that consumes each relevant skill output. Catalog presence and selected names alone fail this check. Verify the full applicable chain in the pilot, from researched brief/hooks through approved production artifacts and manual-upload packaging. Chapter/Shorts applicability depends on format and source transcript; comments/retention/audits require real post-release data and remain a later feedback gate for an unpublished pilot. Record reasons for exclusions rather than manufacturing irrelevant outputs.
Every content task must persist a handoff containing selected skills with reasons, required/provided/missing inputs, intended output types and paths, exact source versions/hashes, diagram stage, tool requirements, unresolved conflicts, creative gates, and allowance scope. Catalog presence alone is not execution. Do not force every skill into one film.

| Capability | Relevant skills and inputs | Required output / verification |
| --- | --- | --- |
| Brief and orchestration | `director-studio`; audience, style, runtime, constraints, available tools | Stable project identity; explicit missing inputs; stage/lease/pinned-input contract; no invented autonomous capability |
| Research and calendar, when requested | `yt-viral`, `yt-plan`; dated sourced video data, sufficient channel samples, capacity/calendar | Retained sources and channel-relative ranking; feasible plan; no fabricated trend, audience, or income claims |
| Story and packaging | `yt-script`, `yt-package`, `director-studio`; creator voice or three creator examples, brief, sources | Five scored hooks/two shown, beat script and runtime estimate; ten title candidates/top three lint evidence and thumbnail brief; required film artifacts remain distinct |
| Real production | `director-studio`; approved comic, screenplay, measured audio, boards, clean refs, previs, exact Flow package | Actual film media and exact provenance; Flow film adapter must be newly verified. `flow-sprite-studio` supplies reference control patterns only; it is not a film adapter |
| Edit and distribution preparation, when applicable | `yt-edit`, `yt-shorts`, `yt-chapters`, `yt-seo`; actual timed transcript, final cut, target query | Cut decisions, self-contained clip spans, valid chapters and descriptions; text suggestions are not rendered Shorts or publication |
| Feedback after manual posting | `yt-comment`, `yt-retention`, `yt-audit`; actual comments, retention CSV, channel evidence | Draft replies, measured drop analysis, prioritized audit; no invented analytics; not an R1 prerequisite without real inputs |

Applicable skills and their referenced tools/files must be read before the future content run. Required hook/title tools must actually run then; fixture success cannot replace creative-run outputs. Missing creator voice, research, analytics, or transcript must be explicit rather than fabricated.

The required diagram is `docs/design/user-required-workflow.json`: brief → premise → ten-page comic → full screenplay → scratch audio/timing → boards/references → Blender previs → pinned generation package → paid authorization → generation → take review → edit/delivery. Preserve its 11 ordered main edges, required brief-to-edit path, and four controls: shared project record, leased handoff, stale dependent work after revision, and no silent approvals/retries. Keep the supplied diagram immutable as evidence. An explicitly designed Flow mapping replaces the original `wan` provider node for execution, preserving its gate positions; passing the old Wan path does not satisfy Flow acceptance.

## Requirement-to-test coverage

Proposed IDs below are test obligations, not claims of existing automated coverage. U = unit, C = contract, I = local integration, B = browser, P = real provider E2E.

| ID / requirement | Levels and positive coverage | Negative/recovery coverage and evidence |
| --- | --- | --- |
| R1-01 Brief routing across both sources | U/C selection schema; I persist/reload handoff; B display selected skills and missing inputs | Ambiguous project, absent voice/tool/input, unrelated skill and unsupported automation produce explicit block; inspect handoff and artifact linkage |
| R1-02 Diagram and stage order | U/C compare required path/edges and four controls; I gate every transition | Supporting notes cannot complete a film stage; premature script/generation rejected; sprite mode cannot satisfy film stages; archived graph mapping |
| R1-03 Versioned handoff | U/C task token, lease, expected version, source pins; I CLI/MCP/HTTP parity | Expired lease, concurrent agents, obsolete version, wrong project/scene rejected; tokens absent from logs/prompts/exports; no approval tool introduced |
| R1-04 Timing and creative references | U/C 2–15 whole-second film packages at 30 fps, audio measurement, reference order and stable IDs; I pin approved inputs | Preserve overrun evidence; reject incomplete references, unapproved/stale inputs, altered source bytes and mismatched hashes; do not inherit sprite duration rules into film |
| R1-05 Flow film handoff | C adapter represents approved prompt, model, timing, resolution, aspect, refs and output count; B visible UI agreement; P real execution | Missing browser/file upload/download capability, login expired, model unavailable, unsupported timing/options, changed UI or cost all block before submission; no Wan/API fallback |
| R1-06 Allowance and spending | U/I exact allowance identity, caps, upload authorization and atomic reservation; B dry run verifies Generate is unreachable when blocked | Zero/missing/expired allowance, wrong package/model/account, increased output count/cost, concurrent reservations and exhausted attempts rejected; audit log/click count proves no duplicate submission |
| R1-07 Attempt lifecycle and recovery | U/I persisted intent, attempt ID, provider correlation, observed state and receipts; P one authorized attempt | Timeout after Generate, lost result, crash/restart, expired lease and delayed completion stay pending/unknown; reconcile same provider job/history before retry; reservations never silently refunded |
| R1-08 Original download | I/B download completion event, file exists, nonzero expected size and stable size after completion, original bytes/hash, provider correlation; P original saved | Cancelled/truncated/zero-byte download, HTML/login page renamed MP4, wrong take, duplicate filename, missing disk space, hash mismatch, absent duration/streams and decode failure cannot pass |
| R1-09 Take and final review | I exact version submitted; B prompt/refs/media visible together; P human reviews entire take and final neighboring cuts | Technical validation does not advance review; revised source invalidates affected approval; deleted/corrupt preview blocked; no agent autoapproval |
| R1-10 Playable delivery | I FFprobe metadata + full FFmpeg decode; B play delivered file; P human end-to-end playback | Check expected duration/frame rate/dimensions/audio streams against approved contract, captions/audio sync and missing assets; ZIP extraction paths resolve and manifest hashes match; edit cannot overwrite original |
| R1-11 Manual posting boundary | C/I export final MP4, captions, audio/stems, prompts, sources/decisions and posting text; B downloadable delivery | No publish/schedule calls or claim of posting; missing derivative is labeled missing rather than delivered; manual posting acknowledgement is optional external evidence |
| FUT-01 Account isolation | Future U/C/I/B account/profile IDs explicitly bound to tasks, allowances, uploads and publishing; provider sandboxes where available | Wrong/changed account, expired/revoked auth, insufficient scope, stale profile and cross-account artifact/cache leakage rejected; no real publishing without explicit future scope |
| FUT-02 Publish idempotency | Future C/I/P draft → review → authorized publish receipt per platform/profile | Retries, delayed receipts, duplicate schedules, partial multi-platform success and cancellation reconcile per destination; never replay successful destinations blindly |

Approved source-version edits and on-disk hash changes are separate tests: an approved revision makes dependent work stale; mutation of approved bytes is an integrity failure even if the version ID is unchanged. Recheck immediately before upload/Generate and before final packaging, not just when constructing the package.

## Layer boundaries and baseline regressions

Unit tests cover pure routing, timing, validation, allowance arithmetic, state transitions and hashing using deterministic fixtures. Contract tests cover artifact/receipt schemas, API/CLI/MCP parity, diagram mapping, version compatibility, and prohibited agent operations. Local integration uses a real temporary database/filesystem, real stdio MCP, subprocess CLIs, media tools and restart/concurrency fault injection; provider behavior is explicitly simulated.

Browser integration covers local Studio UI using temporary data and an isolated browser. A provider UI fixture can validate selectors/failure paths but is labeled simulated. Only a supported browser with an authenticated real Flow session, actual approved inputs and exact allowance can establish provider E2E. Local Chromium smoke does not demonstrate access to the user's authenticated Flow browser.

Before any release claim, run the entire existing Python suite with FFmpeg/FFprobe available, production build, shell syntax check, and isolated desktop/mobile dashboard smoke as documented in `docs/COMBINED_VALIDATION.md`, plus all new tests for changed capabilities. A skipped required media test is a blocked gate, not a full pass. Preserve existing film/Wan export behavior as regression coverage without using it as R1 provider acceptance.

Existing targeted regressions to retain:

- `tests/test_youtube_tools.py`: six real CLI paths, title three-word threshold, list/object transcript parsing, supporting artifact roundtrip that leaves premise incomplete.
- `tests/test_agent_mcp.py`: real stdio transport, tool inventory, registration/submission, pending human review and no agent approval operation. If intentional tools are added, review the inventory change rather than blindly retaining the current count of 18.
- `tests/test_sprite_workflow.py`: pinned mode, no cross-mode gates, sprite/film duration separation, no API handoff, capped attempts, unresolved retry blocking, upload permission, stale sources, reference integrity, lease recovery, concurrent packaging, portable atlas/media export. Its generated test video and simulated downloaded receipt are not Google Flow evidence.
- Remaining suite: leases, reviews, timing, source versions, rough cuts, exports and application business rules; changed Flow film code must not regress sprite processing or user data preservation.

## Staged acceptance and release gates

| Gate | Required execution and retained evidence | Pass condition |
| --- | --- | --- |
| G0 Design/test readiness | Approved R1 requirements and Flow diagram mapping; capability matrix; reviewer findings and resolution; mapped test IDs | Flow adapter scope and every required control specified; missing user inputs listed |
| G1 Offline verification | Full-suite command/environment/output, test counts/skips, frontend build, syntax and local media checks; isolated-data proof | All required tests pass; no required skips; zero paid/network publishing calls; no production approval mutation |
| G2 Studio browser verification | Desktop/mobile UI evidence, console/server errors, artifact/source/prompt and pending review views, media playback/download checks | No material UI faults; exact data visible; technical pass cannot approve art |
| G3 Provider readiness, no Generate | Supported tool and authenticated account confirmed; visible actual model/settings/cost, immutable package and refs hashes, upload permission and exact human allowance | Every live prerequisite present and matches approved package; otherwise BLOCKED, preserving prepared work |
| G4 One real Flow test shot | Authorized reservation before click; timestamped single submission/correlation, visible result/history, charged/reserved credits, original download receipt and hash, probe/decode report | One real Flow result traced to approved inputs; no unresolved duplicate risk; complete original saved. Unknown outcome remains BLOCKED pending reconciliation |
| G5 Creative review and delivery | Human take decision on exact version; final edits if required; human complete-playback decision; delivery manifest/archive, playable file, captions/stems/prompts/decisions | Required human decisions recorded by authorized human; playback and archive checks pass; posting clearly manual |
| G6 R1 release decision | SDLC reviewer assesses G0–G5 evidence and open defects; explicit release claim/scope | No open critical/high integrity, spend, data-loss, approval, or delivery defects; all R1 required gates passed |

Batch generation is allowed only after the test shot's review and its separate exact allowance. No automatic retry is an acceptance step. Do not provoke live paid failures to test failure handling: inject them offline. Live retries, downloads requiring extra payment, or additional outputs require remaining valid exact allowance and reconciliation of previous attempts.

G3/G4/G5 may honestly be BLOCKED when session, browser tools, model access, approved creative inputs or allowance are unavailable. Mark the specific unmet prerequisite and owner; do not convert it to PASS, substitute a fixture, skip it in a passing total, or claim R1 complete. Software-only readiness may be reported separately from completed R1 acceptance.

## Recovery and nonduplication protocol to verify

Persist the attempt reservation before the paid action. Simulate crashes (1) before reservation, (2) after reservation/before click, (3) during click/response, (4) after provider result/before download, and (5) during download/registration. On restart, load durable state, reconcile the existing provider history/job with account and package correlation, resume observation/download as appropriate, and preserve old provenance. A new lease can reconcile an old attempt without rewriting its original owner or restoring consumed allowance. If correlation cannot prove whether a click occurred, keep the attempt unresolved and block another Generate. Test multiple workers and repeated recovery requests; only one paid submission may win. A failed generation may still consume credits; record observed charges independently of technical outcome.

Session expiry before Generate must block; expiry afterward must preserve unknown/pending attempt identity. Missing browser controls or model must report actionable missing capability while keeping prepared inputs. Tests must verify no implicit provider, model, account, reference or timing substitution.

## Evidence templates

Every evidence item links to immutable files or version IDs; screenshots alone are insufficient for media completeness. Redact credentials/session cookies/lease tokens; retain relevant account identifiers safely.

```text
Test/run ID and requirement IDs:
Commit, date/time/timezone, operator/reviewer:
Environment/tool versions; temporary data/browser location:
Layer: unit | contract | integration | Studio browser | simulated provider | real Flow
Preconditions and exact input/version/hash manifest:
Command/procedure; expected result; actual result:
Status: PASS | FAIL | BLOCKED | NOT RUN
Logs, screenshots, reports, artifacts and SHA-256 manifest paths:
Failures/skips/blocker owner and next action:
Production records untouched; paid actions/publication count:
```

```text
Live attempt ID; project/scene/package/version; Flow account/project correlation:
Human authorization reference; exact model/settings/output count:
Prompt hash; ordered reference names/version IDs/hashes; timing/audio/previs pins:
Maximum attempts/credits; visible per-attempt cost; remaining allowance:
Reserved/submitted/observed/downloaded timestamps; provider job/history evidence:
State and uncertainty; actual/unknown charge; reconciliation evidence:
Original filename/path/bytes/SHA-256; download completion evidence:
FFprobe report; complete decode result; human playback/review version and decision:
Derived delivery paths/hashes; archive integrity; final approver and decision:
No retry performed, or separate valid retry authorization and reconciliation link:
```

## Remaining user and environment inputs

R1 needs the selected first video brief (audience, niche, intended runtime/aspect/style, creative constraints), creator voice/examples, source rights and clean approved references, actual stage approvals, available audio/previs/finishing tools, supported authenticated Flow browser access with upload/download, actual accessible model/settings/cost, exact upload and generation allowance, and a chosen delivery location. Confirm any provider-supported timing conflict before generation; preserve the film timing controls and require a reviewed adaptation rather than silently dropping stages. Account/profile targets and publishing permissions are future inputs, not a reason to block manual delivery.

Current user decisions: Short/long format and target seconds are supplied per project; the first paid demo has not been selected. The user logs in personally in a dedicated browser; passwords must not be collected in chat. Local Playwright availability does not establish an authenticated Flow session or supported agent control of it. No authenticated Flow E2E or spend allowance is available in this planning record. Root checked official Flow documentation today; actual feature availability, model, supported duration, output count and credit cost still require live UI confirmation for the selected account and exact package. Do not freeze a model or cost into acceptance fixtures as a universal provider guarantee.

No test can establish guaranteed revenue or virality. Future growth validation requires actual posting IDs, dated analytics and defined measurement windows; distinguish those business observations from software acceptance.
