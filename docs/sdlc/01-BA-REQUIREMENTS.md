# Business analysis requirements

Date: November 3, 2026. Status: planning baseline for review; no production implementation or provider validation claimed.

## Business outcome and authority

Turn a plain-language request into an original, reviewed video and a downloadable production bundle by combining Director Studio's film contracts with the applicable YouTube skills. Support audience growth and a revenue-generating business through research, production, packaging and later feedback. Popularity, viral reach and revenue are objectives to measure, never acceptance guarantees.

**User decisions:** Google Flow is the video provider; preserve the supplied full 12-step film diagram and human creative/spending controls. Release 1 ends with an actual downloaded video, final review and production bundle; uploading remains manual. Format (Shorts or long video) and duration are user-supplied per-project brief values, not fixed global settings; the first demonstration topic and length remain unselected. The user selected approach A: agents work during an active session using a personally signed-in visible browser, with saved state for resume. The user will supply necessary inputs. Future scope includes channel profiles, multiple YouTube/TikTok/Instagram accounts, account-specific formats, scheduling/publishing and analytics. This document does not authorize spend or publishing.

**R1 design requirements for approval:** prove one complete video before scaling; use an approved test shot before batches as required by the supplied diagram; enforce a per-project cost ceiling in addition to exact-package allowances; define a short quality rubric before provider execution. Exact ceiling values, quality thresholds, later-release sequencing and metric targets remain user decisions. These controls are requirements of the proposed R1 design, not already granted spending permission.

Sources: `WORK_LOG.md`, `AGENTS.md`, `docs/youtube/WORKFLOW.md`, `docs/design/user-required-workflow.json`, and `.agents/skills/director-studio/SKILL.md`. The supplied diagram remains the source record: its Wan node requires explicit adaptation to Flow, not deletion or silent replacement. Existing sprite Flow support is not a film adapter.

## Personas and stories

| Persona | Need / user story | Observable result |
| --- | --- | --- |
| Creator/director | As director, I describe audience and intent in ordinary language and see what is missing. | Structured brief, explicit gaps and a proposed workflow; no fabricated voice, niche or budget. |
| Creator/director | I compare researched ideas and approve creative versions before costly production. | Sources, scored alternatives, previews and exact version-specific decisions. |
| Budget owner, initially the user | I approve an exact request and allowance before paid actions. | Prompt/reference versions, expected charge basis and attempt ceiling visible before submission. |
| Production operator/agent | I resume the next eligible task using approved inputs. | Shared project state, leases, pins, dependency status and traceable outputs. |
| Reviewer, initially the user | I accept takes and the final film after playback. | Review evidence, requested changes and accepted versions retained. |
| Channel operator, future | I manage different accounts and formats without mixing their identities or permissions. | Explicit destination/profile selection and account-scoped workflow/evidence. |

## Release boundaries

**Release 1:** one selected video project from brief through the full film path, relevant research/writing skills, actual Flow generation, local download, accepted take selection, assembled final video, captions/audio/creative records and manual-upload packaging. The selected operator model is agents during an active Codex session, with human decisions through the supported review mechanism. Human-assisted provider operations must be labeled honestly if automation is unavailable; they must still record exact requests, outputs and spending. A downloaded raw test clip alone does not satisfy the final-film outcome.

**Later releases, not Release 1 acceptance:** persistent per-channel profiles; multiple accounts across YouTube/TikTok/Instagram; format variants per account; authenticated publishing/scheduling; post-publication metrics and feedback loops. Their API/tool feasibility, permissions, token lifecycle and platform-specific rules require separate design and validation. Rendered Shorts require their own approved output contract; draft clip suggestions are not rendered videos.

An active Codex session routing tasks is distinct from a durable unattended worker. Release 1 requires persistent evidence and resumability after interruption, but does not imply a running scheduler, automatic process recovery while Codex is absent, or autonomous posting. Those require explicitly deployed workers, monitoring and operations acceptance in a later scope decision.

## Functional requirements

| ID | Requirement | Verification intent |
| --- | --- | --- |
| BA-F01 | Convert brief into audience, purpose, style, runtime, format, constraints and missing-input list; ask only blocking questions before dependent work. | Incomplete brief cannot become invented creative or financial authorization. |
| BA-F02 | Select skills from both sources per task; record chosen skills, prerequisites, intended outputs and gates; explain relevant unsupported steps. | Task handoff exposes selections and omissions. |
| BA-F03 | Preserve all 12 stages and ordered approval/dependency controls below. | No comic, measured-audio or previs bypass. |
| BA-F04 | Research with cited source records and channel-relative evidence; derive original premises rather than copying successful videos. | Sources and creative transformation retained for review. |
| BA-F05 | Keep stable character/prop identities, continuity, labeled review boards and clean provider references with pinned versions. | Exact generation input can be reconstructed. |
| BA-F06 | Measure actual rendered/recorded audio and retain overruns; keep the diagram's 2–15 whole-second packages at 30 fps and validate actual Flow support. | Unsupported timing/reference combinations block submission and require an approved adaptation. |
| BA-F07 | Show exact generation package and grant scoped spending authorization, including attempt/cost limits, before paid actions. | Changed package/expired or exhausted allowance blocks execution. |
| BA-F08 | Submit once, retain provider identity/receipt and task or equivalent durable evidence; track status and download originals. | Unknown outcomes reconcile before retry; no silent duplicate submissions. |
| BA-F09 | Retain attempts, failures, takes, charges/estimates and reconciliation, including rejected outputs. | Remaining allowance is auditable; unknown cost stays marked unknown. |
| BA-F10 | Support version-specific human review and revision; mark affected downstream artifacts stale without erasing history. | Technical validation never records creative approval. |
| BA-F11 | Assemble accepted takes with final audio, cuts, captions and credits; review full playback and neighboring cuts; deliver MP4 and archive. | Bundle has usable media, manifest and decisions; no raw-clip-only completion. |
| BA-F12 | Export manual-upload title/thumbnail brief, description/tags and applicable chapter drafts, with review status. | Production output is distinct from publication and any later audience result. |
| BA-F13 | Resume eligible work from one project record using task leases and exact approved pins; protect tokens from saved artifacts. | Interruption cannot create accidental duplicate work or spend. |

## Required film path and gates

| Step | Required output | Control |
| --- | --- | --- |
| 01 Brief | Audience, style, runtime, budget and constraints | User inputs and unresolved questions visible |
| 02 Premise and ideas | Hook, cast, conflict, ending | Director selects idea |
| 03 Ten-page comic | Readable story/look/character test | Director approves visual direction |
| 04 Full screenplay | Dialogue, shots and package plan | Director approves script and plan |
| 05 Scratch audio and timing | Measured mix, stems, cue sheets | Director approves measured timing; preserve overruns |
| 06 Boards and references | Labeled boards, clean images, IDs, prompts | Director approves boards and prompt |
| 07 Blender previs | Editable scene and picture preview, camera/blocking metadata | Director approves framing and blocking |
| 08 Pin generation package | Exact prompt, references, audio, previs and supported settings | Validate inputs and Flow capability; pin immutable versions |
| 09 Paid request | Exact package, budget and attempt limit | Explicit director spending authorization |
| 10 Flow video generation | Test shot, then approved batches; originals and receipts | Adapt Wan handoff to Flow; no provider substitution |
| 11 Scene-take review | Identity, action, timing and continuity evaluation | Director accepts take or requests changes |
| 12 Edit and deliver | Complete final cut, MP4, captions, audio stems and archive | Director approves playback and final export |

Cross-cutting controls: one project record; agent lease/pinned-input contract; revisions retain versions and invalidate affected dependencies; no silent approvals or paid retries. Flow capability mismatches must be surfaced and resolved by an explicit reviewed design, not hidden by skipping diagram steps.

## Combined skill handoff

This is requirements planning, not execution of content skills. The catalog was considered alongside Director Studio contracts. Production tasks must read applicable skill instructions and references in depth before execution; this matrix records intended selection, not completed skill runs.

| Stage/use | Selected skill(s) | Required inputs → intended outputs | Approval/boundary |
| --- | --- | --- | --- |
| All film stages | `director-studio` | Project state, approved versions, leases → validated versioned artifacts | Human creative decisions; no agent approval operation |
| Research/ideation | `yt-viral` | Niche, comparable channels/public data; at least four videos/channel → sourced relative-performance research | User selects original premise; no viral prediction guarantee |
| Work planning | `yt-plan` | Capacity, available hours, existing work → realistic upload/work plan | User approves commitments; not an unattended scheduler |
| Script | `yt-script` | Brief, research, actual creator context/voice → scored hooks and spoken script | Must also satisfy full screenplay/comic dependency contract |
| Packaging | `yt-package` | Video intent/script, creator context → checked title/thumbnail pairing and visual brief | Human approval before final delivery |
| Editing | `yt-edit` | Real timed transcript → cut guidance | Guidance must be implemented in actual edit to affect film |
| Derivative candidates | `yt-shorts` | Long-form transcript → self-contained spans/hooks/framing | Optional when source fits; candidates do not equal rendered Shorts |
| Delivery | `yt-chapters`, `yt-seo` | Timed transcript, query/audience context → validated chapters and search text | Apply only when appropriate to format; manual upload |
| Later feedback | `yt-comment`, `yt-retention`, `yt-audit` | Real comments, retention CSV/transcript, channel evidence → replies, leak report and priorities | No invented performance; replies remain drafts absent explicit send authority |

`flow-sprite-studio` is not selected for film production; its sprite-only implementation must not be claimed as a completed Flow film integration. All 11 YouTube skills belong to appropriate lifecycle stages, not every video task.

## Nonfunctional requirements

- **Evidence and recovery:** persist each artifact, source pin, approval, provider attempt and download; interrupted/unknown outcomes remain explicit. Recommendation: a manifest with hashes and a recovery test after submission and after download.
- **Financial control:** block spend outside scoped allowances; reconcile actual/estimated/unknown charges; never claim zero waste. Cost efficiency means avoiding preventable duplicate or unreviewed runs, not guaranteed cheap output.
- **Quality:** structural checks plus user creative review for identity, coherence, timing, continuity, intelligibility and captions. Adopt concrete quality thresholds with the first brief; file validity alone is insufficient.
- **Security and privacy:** no credentials or lease secrets in prompts, logs, exports or Git; preserve user media and keep testing isolated. Retain source provenance and user-confirmed rights for creative assets/voices.
- **Usability:** show next action, blocker, approved version, spend status and download location in understandable terms; do not expose tool mechanics unless needed for a decision.
- **Portability and performance:** identify supported local runtime/audio/Blender/provider paths; declare expected processing time after choosing format and tools. No ungrounded latency or throughput SLA is adopted here.

## Required user inputs and current gaps

Before brief approval: chosen topic/niche and audience, business purpose/offer if relevant, format/aspect ratio, intended runtime, style, factual/brand constraints and success priorities. Before voice-dependent writing/audio: genuine voice examples/profile or explicit approved neutral direction; selected final voice and rights/consent. Before generation: Flow account availability and supported interaction method (user signs in personally in a dedicated visible browser; do not paste passwords), accessible references and rights, exact allowance/currency or credits, retry limit and package approval. Before delivery: desired output specifications, caption/credit requirements and review acceptance. No authenticated provider session or spending allowance is established. Credentials, budget, voice and niche are **not assumed**; the user has agreed to supply necessary inputs, not supplied these values through that agreement.

Current evidence supports local supporting-artifact integration and documented tests/build/browser checks. It does not establish a Flow film adapter, real provider execution, automatic Blender production, final mastered-film automation, rendered Shorts, durable unattended workers, publishing or audience performance. Film currently exports Wan packages; sprite Flow receipts are separate. macOS/Linux timing can use recorded audio; existing Windows scratch synthesis is not a cross-platform final voice solution.

## Measurable acceptance and evidence levels

| ID | Release 1 acceptance | Required evidence |
| --- | --- | --- |
| BA-A01 | One supplied brief reaches final delivery through all 12 steps with required human reviews. | Project timeline links exact stage versions, decisions and dependency pins. |
| BA-A02 | A real authorized Flow execution produces downloaded original media used in the delivered final film. | Account/tool capability record, approved package/allowance, provider/UI receipt or task identity, original file and matching manifest. Fixtures do not satisfy this criterion. |
| BA-A03 | Final MP4 plays fully, has expected streams/runtime/format, and is accepted after complete human playback. | Probe report, review decision and film in bundle; approved brief defines tolerances. |
| BA-A04 | Bundle contains final video, captions, audio stems, prompts/references or documented recoverable links, provenance, takes, cost/attempt ledger and decision archive. | Manifest with file existence/integrity checks; user can locate and download/open it. |
| BA-A05 | Unapproved/stale packages, exhausted allowances and ambiguous prior requests block new paid submission. | Isolated automated negative tests plus documented real-workflow enforcement; no paid duplicate required to test the block. |
| BA-A06 | Restart after a simulated submission uncertainty and after download preserves identity, approval and known costs without blind retry. | Recovery logs/fixtures prove state rules; real run evidence demonstrates actual provider reconciliation separately. |
| BA-A07 | Manual-upload assets are delivered and visibly distinct from posted content. | Reviewed packaging files; no publication claim without a real platform receipt. |

Verification tiers must stay separate: unit/fixture tests establish local rules; integration tests establish tool/artifact contracts; real provider E2E establishes actual Flow generation/download; human creative acceptance establishes final usability. Previous passing local checks satisfy none of the unperformed real-provider or creative-approval gates. Release 1 cannot be declared complete solely from fixture runs or a written skill draft.

## Business measures and ranked questions

Track per project: time from approved brief to accepted delivery, human review time, accepted/rejected takes, generation attempts and cost per accepted minute, reconciliation backlog, and manual-upload readiness. After publication, record content/account/date and available impressions, click-through rate, retention/watch time, engagement, subscriber change, conversions and attributable revenue/cost. Compare against a declared baseline/time window; no numerical growth/revenue targets have been adopted.

1. **P0, before dependent production:** What is the first video's audience, original subject, purpose, format/runtime and definition of an acceptable final cut?
2. **P0, before paid execution:** What Flow account/tool path is available, what capabilities can be verified, and what exact credit/cost and attempt allowance will the user approve?
3. **P0, before voice/reference-dependent work:** Which real voice examples, final audio choice and authorized references will be supplied?
4. **P1, before Release 1 sign-off:** What final export/caption specifications, storage/download location and review turnaround apply?
5. **P1, product prioritization:** Which revenue model and measurable audience/business outcome should later optimization target?
6. **P2, later release planning:** Which accounts, account-specific formats, scheduling/publishing permissions, analytics sources and unattended operating model are required first?

Handoff: PO should prioritize these requirements and resolve scope recommendations; developer should assess the Flow film adapter and media/tool contracts without assuming sprite equivalence; SDET should map BA-A01–07 to evidence tiers and failure/recovery tests. This file changes planning only and grants no production allowance.
