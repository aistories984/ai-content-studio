# Release 1 product backlog

November 3, 2026 · Planning baseline for design review. No ticket below is implemented or accepted by this document.

R1 delivers one original, reviewed final film containing real Google Flow output, its original download and a portable manual-upload bundle. Every project collects topic, audience, Short/long format and target duration. Agents operate during an active session (selected approach A), preserving state for later resume. Manual upload is the release boundary. Revenue and audience growth are measured objectives, never promised results.

Director Studio and the supplied complete film diagram are the selected source architecture. The `comic-to-flow` workflow, new schemas, adapters and file locations in the developer proposal remain detailed implementation proposals requiring review. The diagram's Wan execution node must be explicitly mapped to Flow while retaining all stages and controls. Existing sprite Flow support and the reported 56 passing tests/local browser smoke do not prove film generation. No authenticated Flow session, selected pilot or paid allowance exists in this record.

## Working agreement and gates

These are concrete **local tickets**, identified below; no external issue tracker or persistent worker is implied. P0 means release-critical/control integrity; P1 means required production/delivery work after foundations; P2 means deferred exploration. All R1 tickets start **Draft/design-review**, except explicitly **Blocked** live work. Draft tickets are proposals, not Ready work or authorization to code.

**Ready:** requirements and acceptance criteria understood; exact scope/design reviewed; prerequisite contracts accepted or available as pinned fixtures for explicitly offline work; responsible owner and SDET checks identified; necessary tools/inputs available. Live work additionally needs genuine creative decisions, authenticated supported browser capability, upload permission and exact generation allowance. A software design approval does not supply those approvals.

**Done for a software ticket:** changes reviewed; checkable criteria and mapped SDET evidence pass at the stated layer; relevant regression/build/browser checks run with isolated `DIRECTOR_DATA`; no critical/important unresolved defects; paths, commands/results and limits retained. Fixtures must be labeled simulated. A blocked live gate cannot be counted as passing or replaced by a mock. Done software tickets do not imply R1 release acceptance.

**Done for R1:** SDET G0–G6 passed, BA-A01–07 satisfied, actual Flow output downloaded and used in final film, exact takes and complete final playback approved by the human, archive integrity verified and manual-upload boundary explicit. No critical/high integrity, spending, approval, data-loss or delivery defects remain. Ordinary agent tools must continue to lack human approval operations.

Dependencies below are completion dependencies unless a stated offline contract fixture allows earlier development. Owners are accountable roles, not currently running services. Developer owns implementation; SDET owns independent verification; PO owns prioritization/readiness; human director owns creative/spend decisions.

## Ordered tickets

### R1-001 — Approve Flow film mapping and executable contracts

**P0 · Draft/design-review · Owner: Developer, with PO/BA · Depends: none**

Story: As director, I can see how the selected source film process becomes Flow production without losing its gates.

- [ ] Add a separately labeled Flow adaptation; preserve the immutable source diagram, all 12 obligations, 11 main edges and four cross-cutting controls.
- [ ] Review workflow/schema/browser boundaries, timing adaptation rules and migration compatibility; record unresolved capability/tool choices without pretending they are implemented.
- [ ] Prohibit sprite/film substitution, hidden Flow API/provider assumptions and silent Wan fallback; specify explicit blockers for unsupported controls.
- [ ] Link every R1 ticket to BA and SDET obligations and record design review decision before implementation readiness.

Trace: BA-F03/F06/F13, BA-A01; SDET R1-02/04/05, G0. Evidence: reviewed mapping, contract fixtures, decision/findings record. No login or generation required.

### R1-002 — Persist brief and combined-skill task handoff

**P0 · Draft/design-review · Owner: Developer · Depends: R1-001**

Story: As creator, I describe a project and receive the next permissible task and precise missing inputs.

- [ ] Persist topic/audience, purpose, Short/long format, duration, style/constraints; require each project's format/runtime rather than global defaults. Channel profile is optional in R1.
- [ ] Consider both catalogs; record selected skill paths/hashes, reasons, required/provided/missing inputs, outputs, tools, source pins and creative/spend gates. Do not select irrelevant skills merely to fill a list.
- [ ] Expose missing voice/examples, research, media/tools and unsupported automation; block only dependent tasks and never fabricate these inputs.
- [ ] Reload the same handoff and next action after active-session interruption; no unattended scheduler claim.

Trace: BA-F01/F02/F13; SDET R1-01/03. Evidence: intake/handoff roundtrip, missing-input/routing tests, browser display. Content execution later reads applicable skills and references deeply.

### R1-003 — Add film-specific durable state and migration

**P0 · Draft/design-review · Owner: Developer · Depends: R1-001**

Story: As operator, I preserve project history and approved inputs across revisions and interruption.

- [ ] Introduce reviewed versioned film package, capability, allowance, attempt and receipt contracts with stable project/scene identity and canonical package hash.
- [ ] Existing Wan and sprite projects still load and retain their semantics; no implicit migration/provider switch.
- [ ] Lease/version/source-hash checks reject stale, expired, wrong-project and concurrent writes; source revision stales dependents and byte mutation independently fails integrity.
- [ ] CLI/MCP/HTTP expose consistent supported operations; lease/session secrets absent from outputs; agent approval operation remains absent.

Trace: BA-F05/F10/F13, BA-A05/06; SDET R1-02/03/04. Evidence: migration, contract/parity, concurrency and stale/hash tests using temporary data.

### R1-004 — Build exact allowance and attempt recovery rules

**P0 · Draft/design-review · Owner: Developer · Depends: R1-003**

Story: As budget owner, I bound attempts and reconcile uncertainty before another paid action.

- [ ] Human approval binds package hash, account/model/settings, upload permission, output count, attempts/credits and project cap; revision cannot reset the project cap.
- [ ] Reserve atomically before submission; zero/expired/exhausted/wrong-scope allowance and competing reservations cannot submit.
- [ ] Persist reserved/submitted/unknown/observed/downloaded transitions and actual/estimated/unknown cost separately; failure never implies a refund.
- [ ] Inject crashes before/after reservation, around click, after result and during download. Resume/reconcile the same attempt after lease expiry; ambiguous outcomes block new Generate.

Trace: BA-F07/F08/F09/F13, BA-A05/06; SDET R1-06/07, recovery protocol. Evidence: offline fault injection, ledger/concurrency results, no paid calls. Browser integration follows in R1-010.

### R1-005 — Implement package/spend review and blocker views

**P0 · Draft/design-review · Owner: Developer · Depends: R1-002/003/004**

Story: As director, I review exact versions, references and financial scope before deciding.

- [ ] Show all required stage obligations, next action/blocker, exact prompt, ordered clean references, audio/previs pins, settings and allowance identity.
- [ ] Human review through the supported dashboard records exact creative versions and separate spending decisions; technical validation cannot approve either.
- [ ] Revision invalidates affected decisions; missing/corrupt previews block review; account or settings changes require renewed scope.
- [ ] Isolated desktop/mobile checks verify pending/revised states, media display and no material layout/console faults.

Trace: BA-F07/F10, BA-A01/05; SDET R1-06/09, G2. Evidence: browser/review tests; no actual user approvals fabricated.

### R1-006 — Produce research, premise, comic and screenplay handoffs

**P1 · Draft/design-review · Owner: Developer; human creative director · Depends: R1-002/003/005**

Story: As director, I select an original researched premise and review real visual/story artifacts.

- [ ] Configure or accept explicit supplied image/page tools; absent tooling/allowance blocks media production instead of generating placeholder completion.
- [ ] Relevant `yt-viral` work retains dated sources and channel-relative evidence; `yt-script` uses supplied creator context and required hook tools. Preserve selections and real tool outputs.
- [ ] Runner/import path registers actual readable ten-page comic with stable identities and a distinct full screenplay/shot/package plan; text notes do not satisfy comic completion.
- [ ] Stage-order tests reject screenplay/generation bypass; pilot must record premise, comic and screenplay human decisions sequentially.

Trace: BA-F02/F03/F04/F05, BA-A01; SDET R1-01/02/04. Evidence: offline actual artifact/import checks and tool tests; live pilot creative decisions in R1-014.

### R1-007 — Measure audio and prepare boards/references

**P1 · Draft/design-review · Owner: Developer; human creative director · Depends: R1-006**

Story: As director, I approve actual timing and clean, reconstructable visual inputs.

- [ ] Validate configured recording/synthesis path and rights; recorded audio supported without assuming Windows TTS is cross-platform final voice.
- [ ] Persist measured real mix/stems/cues, preserve overruns, and express 2–15 whole-second packages at 30 fps without substituting word-count estimates.
- [ ] Register labeled boards separately from clean upload references, with ordered roles, character/prop IDs and pinned hashes.
- [ ] Timing/board revisions invalidate dependents; require human timing and board/prompt decisions before subsequent stages.

Trace: BA-F03/F05/F06/F10; SDET R1-02/04/09. Evidence: measured-media and invalidation tests; actual pilot artifacts/decisions later.

### R1-008 — Validate Blender previs runner/import contract

**P1 · Draft/design-review · Owner: Developer · Depends: R1-007**

Story: As director, I inspect editable staging and a real preview before generation.

- [ ] Explicitly configure/probe Blender version, asset/font paths and rendering; missing capability blocks this stage.
- [ ] Produce or import editable `.blend`, picture-only rendered preview, camera/blocking data and character-to-dummy map pinned to approved boards/audio.
- [ ] Validate files/render and expose human framing/blocking review; generic attachment or text plan cannot complete previs.
- [ ] Preserve actual timings/overruns and require rebuilt affected previs after approved upstream revision.

Trace: BA-F03/F05/F06/F10, BA-A01; SDET R1-02/04/09. Evidence: actual local Blender/open/render smoke and pin checks; no claim of fidelity guaranteed by previs.

### R1-009 — Verify supported Flow browser and film package compatibility

**P0 · Blocked: no authenticated supported session · Owner: Developer; user signs in · Depends: R1-001/003; production package also R1-008**

Story: As operator, I know whether the actual account and browser can execute the exact planned shot.

- [ ] Offline interface tests cover inspect/upload/observe/download; separately verify an installed supported visible browser's documented session/control model. Local Studio Playwright smoke is insufficient proof.
- [ ] User signs in personally; record safe account/project correlation and live model/input/reference/duration/aspect/output-count/cost evidence without credentials or cookies.
- [ ] Recheck official documentation and actual UI; no hard-coded universal model, duration list or price.
- [ ] Prepare immutable package without uploading; unsupported timing requires reviewed subdivision/usable ranges plus continuity/audio/previs updates, or explicit block. Disclose any Flow input fidelity limit.

Trace: BA-F05/F06/F07/F08, BA-A02/05; SDET R1-04/05/06, G3. Evidence: capability matrix and inspected settings; this ticket permits no Generate or unapproved upload. Offline interface work can be split out after design review without login.

### R1-010 — Connect guarded single-submit and reconciliation browser runner

**P0 · Draft/design-review · Owner: Developer · Depends: R1-004/005/009**

Story: As operator, I execute only the exact authorized request and recover observation safely.

- [ ] Match approved account/package/settings immediately before action; recheck hashes/lease/allowance, reserve, then permit one observed Generate action.
- [ ] UI drift, missing controls, expired auth, changed cost/model or ambiguous identity stops submission; no API/Wan fallback.
- [ ] Persist intent, timestamps and visible provider correlation/results; interrupted action remains unresolved until same job/history is reconciled.
- [ ] Simulated browser failures prove no duplicate action; session loss pauses active-session work with resumable records. Do not induce paid failures for tests.

Trace: BA-F07/F08/F09/F13, BA-A05/06; SDET R1-05/06/07. Evidence: simulated action counts/recovery plus real pilot trace in R1-014. Offline completion cannot establish provider success.

### R1-011 — Download and validate immutable originals

**P0 · Draft/design-review · Owner: Developer · Depends: R1-003/010**

Story: As reviewer, I can play the complete original and trace it to its authorized take.

- [ ] Observe download completion and stable nonzero file; retain original filename/correlation/bytes/hash before derivatives and register immutable receipt.
- [ ] Probe metadata and fully decode; reject HTML/login pages, truncation, wrong take, duplicate-path overwrite, missing streams and integrity mismatch.
- [ ] Resume download of the same known result without regeneration; disk/download failure preserves attempt identity and ledger.
- [ ] Present original with prompt/refs and measured timing; only human can accept/reject exact take.

Trace: BA-F08/F09/F10, BA-A02/03; SDET R1-08/09, G4/G5. Evidence: fault/media fixtures plus actual original download in R1-014.

### R1-012 — Assemble final cut and portable delivery archive

**P1 · Draft/design-review · Owner: Developer · Depends: R1-007/008/011**

Story: As creator, I receive a complete reviewed video rather than only an isolated generated clip.

- [ ] Render accepted usable ranges, approved final audio, captions/credits using a pinned frame-based manifest; preserve originals, stems, source timing and failed render logs.
- [ ] Check approved duration/format tolerances, full decode, audio/caption alignment and neighboring cuts; human must approve entire final playback.
- [ ] Archive final MP4, originals/takes, captions/stems, editable timeline/Blender sources, prompts/refs, provenance, decisions and cost ledger with manifest hashes.
- [ ] Extract archive in a fresh directory and verify linked paths/media; omit secrets and never report missing derivatives as delivered.

Trace: BA-F11, BA-A01/03/04; SDET R1-09/10/11, G5. Evidence: real local media render/archive tests; actual pilot playback decision later.

### R1-013 — Prepare reviewed manual-upload assets

**P1 · Draft/design-review · Owner: Developer/content operator · Depends: R1-002/012**

Story: As creator, I can manually upload the delivered film with usable reviewed packaging.

- [ ] Read/run relevant `yt-package` and `yt-seo` instructions/tools with genuine creator/query inputs; retain title/thumbnail pairing, lint outputs and search text.
- [ ] Use real timed final transcript for applicable `yt-edit`/`yt-chapters`; validate chapter rules. Omit inapplicable chapters explicitly, not as a failed Short requirement.
- [ ] `yt-shorts` applies only with suitable long-form source; candidate spans are labeled drafts. Any rendered derivative requires a separate approved output contract and real media verification.
- [ ] Include review status/rights/credits and manual upload instructions; no publish/schedule action or posting claim.

Trace: BA-F02/F12, BA-A07; SDET R1-01/11. Evidence: actual packaging/tool outputs and bundle inventory, no external posting calls.

### R1-014 — Run approved real pilot and release acceptance

**P0 · Blocked: pilot, stage decisions, supported session and exact allowance absent · Owner: SDET coordinates; human director approves · Depends: R1-001–013**

Story: As product owner, I accept R1 only when real provider media becomes the reviewed delivered film.

- [ ] User supplies first topic/audience/format/runtime, voice/references/rights, delivery specifications and quality/timing tolerances; all 12 stage decisions/pins are traceable.
- [ ] G0–G3 evidence passes; exact test-shot package/upload permission and cost/attempt allowance approved by human. No planning document itself grants spend.
- [ ] One real Flow submission yields correlated receipt, ledger and original downloaded media with probe/full-decode evidence; unknown outcome stays Blocked pending reconciliation.
- [ ] Human reviews exact test take before any separately authorized batch, then reviews complete assembled final playback. Final film uses actual downloaded Flow output; a raw test clip alone fails acceptance.
- [ ] BA-A01–07 and SDET G0–G6 evidence linked; full regression/build/syntax/isolated browser checks pass without required skips. State actual cost, limits, unresolved defects and manual-upload handoff.

Trace: all BA acceptance IDs; SDET R1-01–11, G0–G6. Evidence: real provider media/receipts plus separate creative decisions and software sign-off. No fixture can satisfy this ticket.

## Recommended first sprint: software independent of login

Proposed sprint goal: make intake, exact Flow film contracts and spending/recovery rules demonstrably safe offline. First obtain design approval through R1-001, then implement R1-003 → R1-004 and R1-002; add the review/blocker slice of R1-005 if capacity permits. No estimate/capacity is agreed, so this is an ordered recommendation, not a committed sprint or permission to implement.

Use deterministic fixtures, temporary databases and local browser evidence; retain the existing 56-test baseline and add meaningful migration, contract, stale-input, allowance/concurrency and restart checks. Keep production approvals/data untouched. The sprint exit is software-only readiness with explicit live blockers. It does not deliver R1, spend credits or depend on provider login. A later supported-browser capability spike is necessary before selecting the production driver; it must not be silently inferred from local Playwright.

## Future candidates, not adopted release commitments

| Candidate | Priority/status/owner | Dependency and discovery acceptance |
| --- | --- | --- |
| R2-001 Versioned channel profiles and account isolation | P2 · Proposed · PO/Developer | After R1 evidence; define audience/voice/format defaults, explicit project profile version, separate Flow versus destination identity; verify no cross-account artifact/auth leakage (SDET FUT-01). |
| R2-002 Platform feasibility and authorized publishing | P2 · Proposed · Developer/SDET | After R2-001 and platform/access decisions; establish actual YouTube/TikTok/Instagram supported tools/APIs, scopes and account confirmation; design draft/review/publish receipts, idempotency, partial-success recovery and cancellation before live posting (FUT-01/02). No capability promise or upload authorization. |
| R2-003 Real feedback and business measurement | P2 · Proposed · PO/content operator | Actual manual post/account IDs and analytics; select `yt-comment`, `yt-retention`, `yt-audit` with real comments/CSV/channel evidence; `yt-plan` requires real capacity/calendar. Retain dated observations, cost and measurement window; no invented results or guaranteed revenue. |
| R2-004 Unattended operations and derivatives | P2 · Proposed · Developer/PO | Separate operating-model decision; deployed workers, monitoring/recovery and account-bound scheduling acceptance. Account-specific rendered Shorts/ads require approved formats and verified media, not only textual suggestions. |

## Decisions and conflicts to resolve

No contradictory user selection remains: A is selected; B is deferred; Flow is selected; upload is manual in R1. Remaining technical tensions must not be hidden: source Wan semantics versus new Flow execution; 2–15 second/30-fps planning versus actual provider-supported timing; pinned audio/previs controls versus supported Flow inputs; existing attachment coordination versus executable comic/audio/Blender/finishing tools. R1-001/009 resolve or explicitly block these before spend. Test-shot-before-batch is present in the required diagram; its concrete enforcement and cumulative project cost ceiling are proposed R1 design requirements awaiting approval. Neither grants an actual generation allowance.

Missing inputs are owned by the human director (pilot/voice/rights/creative decisions/budget/export needs), with Developer responsible for supported local tool/browser capability proof and SDET responsible for honest evidence/blocker classification. The complete workflow cannot be declared ready merely because the user agreed in principle to provide inputs.
