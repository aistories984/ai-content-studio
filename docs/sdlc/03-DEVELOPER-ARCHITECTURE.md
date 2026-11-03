# Developer architecture proposal

Date: November 3, 2026. Status: proposed design, not implementation or a provider execution report. R1 is a plain-language brief progressing through combined YouTube skills and the required film process to an original Google Flow download and human review. Uploading to YouTube remains manual. Future channel/account support and automatic publishing must remain separable from R1.

## Evidence and present limits

Inspected `studio/store.py`, `studio/agent_tools.py`, workflow definitions, the supplied diagram, `docs/SPRITE_WORKFLOW.md`, the Director Studio skill, the combined YouTube catalog and relevant research/script/packaging skill instructions. The handoff reports **56 baseline tests green**; this architecture task did not run them. Those tests establish local behavior, not working film generation.

Today `workflow_for` selects a workflow from project settings; `_next`, task leases, immutable artifact versions, dependency checks and human review are useful foundations. `generation_package` branches only for `sprite-to-flow`; all other projects prepare a Wan request using approved audio, boards and Blender artifacts. `flow_package` rejects films, and `reserve_flow_attempt` requires a `sprite_flow` task and approved sprite board. `record_flow_result` records observations without external execution. `agent_tools.py` exposes these shared store methods through CLI/MCP and exposes no human approval operation. Supporting YouTube notes do not complete production gates.

No-change operation therefore requires a person/agent to select skills, create external assets, coordinate tools and carry handoffs manually. It cannot turn a brief into a Flow film. Changing provider text in a prompt, reusing sprite scenes, or renaming a Wan package would leave film input validation, timing, allowances and receipts incorrect. Real orchestration needs a film workflow, capability checks, executable stage runners and recovery, alongside the existing store rules.

## Two feasible approaches

| Approach | Operation | Benefits | Costs and limits |
| --- | --- | --- | --- |
| A: session-assisted visible browser | A capable agent reads Studio state through CLI/MCP, runs permitted local stage tools, and uses a supported visible browser tool for Flow. Studio persists every handoff and attempt. Humans handle authentication and approvals. | Smallest extension of current agent contract; tests actual browser/account capabilities early; supports R1 without a new service. | Requires an active agent session and browser capability. Session loss pauses execution; records must permit safe resumption. It is assisted automation, not an unattended background service. |
| B: durable local worker | A local worker owns a persistent queue and invokes configured language/image/local-render tools plus a supported visible browser driver. Dashboard resumes review-blocked jobs. | Scheduled/resumable orchestration, bounded concurrency and clearer operations as projects grow. | Requires worker lifecycle, model/tool integration, browser ownership, secret/session isolation, durable cancellation and more failure testing. Persistent queue does not make browser generation exactly once. |

**User selected A for R1: active-session agents, signed-in browser and saved progress**, with durable package/attempt contracts shared by both approaches. Collect Short/long format and duration for each project request. Prove one complete approved film path and original download before building B. B is a later implementation option, not an already selected deployment. Neither approach uses a hidden Flow API, scraped authentication cookies or an undocumented provider endpoint.

## Workflow and skill routing

Add a film-specific `comic-to-flow` workflow rather than modifying existing sprite semantics or migrating existing Wan projects silently. Preserve `docs/design/user-required-workflow.json` as source evidence; add a clearly labeled Flow adaptation with identical required stage ordering and controls. Its Wan node maps to Flow in the adaptation. Do not claim that the original diagram already describes Flow.

| Required step | Contract and runner responsibility |
| --- | --- |
| 01 Brief | Persist audience, purpose, style, runtime, format, budget and creative locks. Normalize a plain-language request into a proposed brief; unresolved required fields produce a visible input request. |
| 02 Premise | Research when requested/relevant using `yt-viral`, retain dated public sources and channel-relative ranking; propose hook, cast, conflict and payoff. Human selects the premise. |
| 03 Ten-page comic | Calibrate a visual sample, then produce ten actual readable pages, stable character IDs and clean character references. Human approves visual direction. Text descriptions alone fail this gate. |
| 04 Screenplay | Apply `yt-script` hook scoring and on-screen beats, then satisfy the fuller film contract: dialogue, shots, continuity and package plan. Human approves script and timing plan. |
| 05 Scratch audio/timing | Produce or import real audio, measure it, preserve full overruns, stems and cue sheet. Human approves measured timing; no timing inferred only from word count. |
| 06 Boards/references | Produce labeled visual boards and separately pinned clean upload inputs, exact prompt and ordered reference roles. Human reviews them together. |
| 07 Blender previs | Produce editable `.blend`, camera/blocking data, character-to-dummy map and actual picture-only render. Human approves framing and motion. |
| 08 Pin package | Validate exact approved script/audio/board/previs inputs, timing, file hashes and current Flow capability compatibility. Package preparation uploads nothing. |
| 09 Paid request approval | Human approves the immutable package hash, reference-upload permission, exact model/settings, output count and maximum attempts/credits. A changed package requires renewed approval. |
| 10 Flow creation | Browser runner inspects live controls, reserves locally immediately before one Generate click, observes the same result and saves original download plus receipt. Test shot precedes any separately approved batch. |
| 11 Take review | Full playback, neighboring continuity, actual measured duration and original download available to the human. Reject/revise/accept exact take version; local QC cannot accept art. |
| 12 Edit/deliver | Assemble approved usable ranges, final audio, captions/credits and portable archive; human approves final cut. Do not advertise R1 complete merely because a generated scene exists. |

The store need not represent all twelve as twelve creative artifact stages: brief, package preparation, spend approval and take review may be explicit control records around existing stages. The UI and state machine must expose all twelve obligations and their blockers. No shortcut from script directly to generation is permitted.

The router records `selected_skills`, skill paths/version hashes, required inputs, outputs, gate and tool results per task. Consider both repositories on every content request. Use `yt-package` for linted title/thumbnail pairs and `yt-seo` for manual upload text when requested; use `yt-plan` with real capacity/calendar inputs. Select `yt-edit`, `yt-shorts`, `yt-chapters` only with real timed transcripts; Shorts writing is not a rendered Short. Select `yt-comment`, `yt-retention`, `yt-audit` with actual comments, analytics/channel evidence. These feedback stages do not replace film stages. Read each selected skill deeply and run its required tools during execution. Creator voice prerequisites must be supplied rather than fabricated. This document selects architecture analysis; no content skill or media generation was executed here.

## Proposed persistent contracts

Reuse immutable versions, optimistic revision checks and human-only reviews. Add schema migration and versioned contracts rather than relying on free-text evidence alone:

* `ProductionRequest`: request ID, original brief, workflow ID/version, project ID, profile reference, intended outputs, unresolved inputs and route decision. A channel profile is optional for an unpublished demo.
* `CapabilitySnapshot`: tool identity/version, availability probe timestamp, requested and observed provider model, observed supported input modes/durations/output settings, browser upload/download support, unresolved limitations and evidence. Treat stale observations as requiring recheck before spend.
* `GenerationPackage`: schema version, project/scene/package IDs and revision, direction hash, ordered source version/file/hash/role pins, exact prompt, planned timeline and provider settings, upload permission and capability snapshot. Canonical serialization yields `package_hash`.
* `SpendApproval`: human review ID, exact package hash, selected model/settings, allowed generations/outputs, credit cap and scope. Track total project budget alongside per-package allowance so approving a revised package cannot silently reset the project cap. No invented prices or account quotas.
* `GenerationAttempt`: attempt ID, package hash, task provenance, logical execution owner, observed cost/output count/settings, reserved amount, timestamps, external generation ID/project URL when visible, transition history and evidence hashes. Persist browser intent before clicking. Never store lease/session secrets in receipts.
* `TakeReceipt`: attempt ID, original provider filename/identifier where exposed, local immutable file hash, measured metadata, selected model/settings and UI evidence. Store original bytes before making review proxies. Receipt claims and local media evidence remain distinguishable.
* `RenderManifest`: approved source pins and usable ranges, integer timeline frames/timebase, audio offsets/gain, captions, output profiles, command/tool versions and output hashes. `ManualUploadBundle` adds approved title, thumbnail, description, chapters when applicable and rights/credits notes; it grants no publishing permission.

Revalidate source versions, hashes, direction, model, allowance and current lease atomically when reserving. Recheck immediately before the external click; upstream changes pause rather than submitting stale inputs. Reservations bound cooperative execution, not Google's own UI. Protect the queue with transactional ownership, and allow only one runner to control an account/project browser operation at a time.

## Tool and browser prerequisites

| Capability | Required proof before declaring stage executable |
| --- | --- |
| Language/research | Configured agent/model access, public research access when needed, source retention and successful local skill CLIs. Studio itself is not a language-model orchestrator. |
| Images/comic/boards | Explicit configured image tool/model or user-supplied actual images; consistent character reference workflow, ten-page composition/export, readable typography and human visual review. An image generator alone does not supply page layout or continuity. No default model or paid image allowance is assumed. |
| Scratch/final audio | Recorded audio works for timing; Windows speech code does not establish macOS TTS. Choose/validate voice tool and usage permissions if synthesis is needed. Final voice/music/mix support remains separate from temporary timing. |
| Blender | Installed tested Blender executable, versioned scene builder/templates, asset paths, fonts, rendering capability and an actual render. Existing `.blend` attachment support is not automatic scene generation. |
| Flow | Authenticated user-selected account, supported visible browser inspection/control, approved local file upload and original-file download, current observed model/settings/cost and matching approved package. Existing sprite documentation is design precedent, not current film/account verification. |
| Delivery | ffmpeg/ffprobe and compatible codecs/fonts, stable render plan, caption generation from real timing, complete playback. Rough-cut persistence/export is not a finished mastering pipeline. |

Use a browser adapter interface with inspect, navigate, upload approved local file, perform observed action, observe generation/history and download original. Bind only an installed supported browser capability whose documented session model has been verified; R1 must surface a blocker if none is available. Project-local Playwright/Chromium exists for Studio UI tests; this does not establish an authenticated Flow session or working provider automation. Do not assume generic shell Playwright can control the user's logged-in browser. A user-owned persistent browser profile can be an option only where the supported driver permits it. Keep its authentication outside artifact/export directories, restricted locally. The human signs in and resolves account challenges; never ask the app to capture passwords, bypass challenges or export cookies. Stop on ambiguous account/project identity. New browser automation dependencies require an explicit capability spike before selecting them for production.

Do not copy the sprite workflow's documented model label or duration list into the film contract as current provider truth. At implementation and execution, check current official provider documentation and the actual account UI. The diagram's 2–15 whole-second, 30-fps package convention is the planning/edit timeline; Flow input/output durations may differ. If incompatible, propose an explicit reviewed subdivision/usable-range plan with continuity, audio and updated previs, or block. Never truncate dialogue, stretch media, select another model/provider or silently change duration. Keep audio/previs pinned for planning even where Flow cannot ingest them; if a required control cannot be reproduced by the supported input mode, disclose the fidelity limitation and require a revised approved plan or leave the stage blocked.

## Recovery and credit accounting

States: prepared → awaiting approval → reserved → submitted → downloaded → awaiting take review. `failed` closes only an observed failure; `unknown` and unresolved `reserved/submitted` block another attempt for the same scope. Crash after reservation but before a visible confirmation is uncertain, including the case where it is unclear whether the click happened. Reconcile the existing Flow project/history; absence of a locally recorded external ID does not prove no submission. If the UI cannot resolve it, leave it blocked for human reconciliation.

Lease expiration authorizes a new lease to inspect/reconcile the same attempt, never a new paid click. Preserve initial task provenance and append reconciliation owner/evidence. Failed results retain consumed reservation/observed charges; failure is not a refund. Reconcile reserved versus observed cost separately and do not infer credits returned. Exhausted or changed allowances return to human review. Cancellation before submission stops work locally; after submission it means stop further work and reconcile the existing external result. Downloads can be retried against the same observed asset without regenerating; verify identity and preserve originals. No distributed exactly-once claim is possible for a UI Generate click.

## Deterministic local processing and export

Use integer frame ranges at the approved 30-fps film timebase and measured audio offsets, with explicit resampling rules. Freeze rendering tool versions, fonts, codec settings and input hashes; write to a new run directory and atomically register complete outputs. Separate downloaded source fps/duration from timeline fps and usable range. Preserve overruns and failed render logs. Compare decoded duration/frame count, audio presence, caption bounds and output inventory to the manifest, then require human playback.

Determinism applies to the local plan and reproducible processing under pinned tools; it does not promise identical generative media or bit-identical encodes across hardware. Export original takes, approved final MP4, audio stems, captions, editable timeline/Blender files, prompts, references, receipts, reviews, allowance ledger and source hashes. Exclude credentials and lease tokens. Manual upload is the R1 boundary.

## Phased component/file map

These are proposed edits/new modules, not existing features.

| Phase | Files/components | Exit evidence |
| --- | --- | --- |
| 0: capability and contract proof | New `docs/FLOW_FILM_WORKFLOW.md`, Flow-adapted diagram, `workflows/comic-to-flow-v1.json`, capability/contract fixtures | Required controls map to all twelve steps; supported browser/tool/account observations and explicit gaps; no spend during capability inspection. |
| 1: shared state | `studio/store.py`, proposed `studio/generation.py`, `studio/contracts.py`; workflow routing and SQLite migrations | Film-specific package/approval/attempt records; changed inputs stale dependencies; transactional bounded reservations; existing film/sprite records still load. Audit current film-default checks before enabling third workflow. |
| 2: task orchestration | `studio/agent_tools.py`, CLI/MCP exposure, proposed `studio/orchestration.py` and capability adapters | Request → selected skills → next permitted task with pinned inputs; pause/resume on review or missing capabilities; no agent approval endpoint. |
| 3: executable production | Proposed image/page-layout, audio, Blender and supported browser runner adapters; keep store authoritative | Real staged outputs, then one human-authorized test generation, original download and review. Browser adapter cannot submit before reservation; unknown outcome cannot trigger duplicate click. |
| 4: review/delivery | `studio/app.py`, `src/main.tsx`, proposed `studio/rendering.py`, existing media/export helpers | Exact package comparison/spend review, original playback, take selection, reproducible final-cut/manual upload bundle and portable archive. |
| 5: later operations | Proposed durable worker and channel profile/account bindings; future publishing adapter | Operational supervision and account isolation before multiple profiles; publishing requires separately designed OAuth permissions, target channel confirmation, approved upload content, idempotency and result reconciliation. No R1 auto-post behavior. |

Future channel profiles should version audience/voice/style/format defaults without storing account secrets. Bind a project to an explicit profile version and external account reference; keep Flow identity distinct from YouTube channel identity. Current single creator voice-file behavior needs a profile-aware resolution strategy before multi-channel claims. Do not infer a default destination channel from a logged-in browser.

## Decisions and handoff

User-selected engineering approach: session-assisted R1 with shared durable records; no paid provider or new dependency has been selected or exercised here. Decisions still required: first video and creator inputs; image/page tooling and allowance; voice/audio rights and tools; Blender execution capability; supported browser integration and account; exact live Flow model/input mode; duration mapping; approved test package/budget; final delivery profile. Missing capabilities must produce a prepared handoff and specific blocker, not placeholder media.

Official Flow references, checked by the coordinating agent November 3, 2026: [creation and controls](https://support.google.com/flow/answer/16353334), [downloads](https://support.google.com/flow/answer/16935308), [model features](https://support.google.com/flow/answer/16352836), [credits](https://support.google.com/flow/answer/16526234). These document product behavior, not this user's account availability, authenticated session or an observed generation. Record live model, duration, aspect, output count and displayed cost at execution; do not hard-code a price.

Implementation follows design approval, an execution plan, relevant engineering skills and meaningful regression/SDET checks. The next design review should evaluate the R1 requirements and test document alongside this proposal. Preserve existing baseline behavior while proving real stage execution; local test success alone is insufficient to claim an end-to-end production system, channel growth or revenue.
