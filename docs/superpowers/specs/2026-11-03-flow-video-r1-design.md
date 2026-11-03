# R1 design: brief to reviewed Google Flow video

Date: November 3, 2026. Status: concrete proposal for user review; implementation not started. Supersedes the original foundation-only scope for the next product milestone.

## Intent

Build the missing production connections so the user can give a video request, supply its audience/format/duration, and receive a reviewed video made through Google Flow with the original takes and a portable project bundle. Use Director Studio's architecture and the relevant YouTube skills together. R1 ends with local delivery and manual upload. Growth and revenue remain the business objectives, measured after release rather than promised.

## Decisions already made by the user

- Director Studio is the unified repository foundation.
- Follow the supplied 12-step film diagram and its human creative/spending gates; Google Flow replaces the Wan-specific execution step.
- Use active-session agents first: agents execute during the user's active session and personally authenticated browser, saving state for later resume. A persistent unattended worker is future scope.
- Ask Short or long video, topic/audience, style and desired seconds/minutes per project; no fixed global video length has been selected.
- Use BA → PO → Developer → SDET for development. Different production tasks select applicable skills from both sources. The four development roles are not automatically running application services.
- Manual upload is acceptable now. Multi-account YouTube/TikTok/Instagram publishing and account-specific formats are later releases.

## Approaches considered

**A, selected:** session-assisted execution with durable Studio state and a dedicated visible browser. This uses existing CLI/MCP handoffs and proves provider integration before introducing scheduling infrastructure. An active capable agent and browser session are needed; saved records permit recovery, not unattended execution after the session ends.

**B, deferred:** persistent local worker from the start. This adds deployment, model backend, queue, scheduling, browser ownership, monitoring, and recovery before the first real output. Durable production contracts from A should support it later.

## Proposed architecture

1. **Request and skill routing:** normalize user intent to a stored request with explicit missing inputs. A small routing layer identifies the applicable skill paths/hashes, stage, tools, required sources and expected outputs. Reading a skill is not itself execution; record actual tool results and creative artifacts. In R1 the active agent invokes its available creative/local/browser tools; the local router supplies structured plans and handoffs and does not imply an installed autonomous model backend.
2. **Flow film workflow:** introduce a new versioned `comic-to-flow` preset and explicit provider identity; keep existing film/Wan and sprite projects untouched. Audit film-default assumptions before enabling a third mode. Existing stages can group diagram operations, but all twelve diagram responsibilities and approvals remain traceable.
3. **Production adapters:** invoke configured tools for ten-page comic/layout, screenplay, real measured audio, boards/references, and Blender previs. Tools produce actual reviewable files with stable identities, source pins and prompts. Missing adapters stop the dependent stage rather than create placeholder success. No image, voice, Blender, or browser provider is silently selected.
4. **Flow preparation and capability inspection:** create a film-specific package with ordered approved references, source hashes, exact prompt and desired settings. Use live browser observations to resolve model/reference/duration/output support. The diagram's timing conventions do not establish Flow compatibility; split/retime shot packages only through a reviewed adaptation.
5. **Spending and execution:** obtain exact-version package/settings/credit/attempt approval. Transactionally reserve the observed allowance immediately before Generate. Persist the intent and correlation/evidence, use visible browser controls, then observe the same generation. An unresolved click/result blocks another generation; failure does not imply refunded credits.
6. **Download and review:** capture actual original downloads, verify completion, decode/probe media, retain original bytes and hashes, register takes/receipts, and submit for human review. Provider evidence and local media checks are distinct.
7. **Delivery:** assemble approved take ranges with the approved audio, captions/credits and requested output format. Validate full decoding, duration, continuity and audio sync; human reviews full playback. Export final MP4, originals, applicable captions/stems, prompt/source/decision records, cost ledger and a manifest/archive. Unsupported or absent optional assets are explicitly identified.

Studio's SQLite records remain authoritative. Add typed package, capability, allowance, attempt and receipt contracts plus migrations for durable evidence; do not introduce separate JSON status authority. CLI, MCP and UI use the same business rules. Secrets/session state stay outside artifacts, tickets, exports and Git.

The detailed component/file map and failure states are in `docs/sdlc/03-DEVELOPER-ARCHITECTURE.md`. BA requirements and acceptance IDs are in `docs/sdlc/01-BA-REQUIREMENTS.md`. The PO backlog is the implementation order; detailed implementation steps are written after this design is approved.

## Required automation flow

Brief → sourced research and relevant skill selection → approved premise → approved ten-page comic → approved screenplay/shot plan → measured audio → approved boards/clean references → approved Blender previs → pinned Flow-compatible package → approved spending allowance → one Flow test shot, then authorized batches → original downloads and take review → final assembly/playback approval → downloadable delivery/manual-upload package.

Every revision preserves prior versions and invalidates only affected downstream work. Technical checks and SDET acceptance never fabricate human creative approval. Real Flow access may require a human login/account challenge and explicitly authorized asset uploads.

## Release sequence

1. Define intake, capability preflight, skill-selection handoff and a Flow film workflow contract; no generation required.
2. Implement shared package/version/approval/attempt state and recovery rules, with isolated negative tests.
3. Wire real production asset adapters and reviewable outputs to the preserved diagram.
4. Verify a supported visible Flow browser/session path and an approved complete test package; inspect controls without spending.
5. Perform one real director-authorized generation, download original media and verify it. Stop and reconcile unknown outcomes.
6. Complete accepted scenes, assemble/review final delivery and export the production bundle.
7. SDET checks local regression, browser behavior, recovery and actual provider evidence; release only the scope demonstrated.

## Verification and definition of done

- Required combined-flow evidence: for each applicable YouTube skill, retain the skill identity/version, actual tool execution or authored output, pinned input/output artifact IDs, and its downstream consumer. A selected skill name or installed folder alone does not count as execution. SDET verifies the chain from skill output into the next production/delivery stage; every omission is justified by format, missing prerequisites, or future-release scope. Use all eleven across their appropriate lifecycle, not indiscriminately in every video. Post-release comment/retention/audit work requires actual audience data and does not block an unpublished R1 pilot.
- Keep the existing baseline suite/build green; add requirement-driven tests for changed behavior.
- Verify missing inputs/capabilities, source changes, stale/expired leases, allowance exhaustion, changed settings, race conditions and interruption points. Tests use temporary project data and do not spend credits.
- Browser fixtures prove local adapter behavior; they never count as provider E2E.
- R1 requires an actual approved Flow result, original download/receipt, playable final video, exact provenance and user creative acceptance. A raw clip alone is a test-shot milestone, not the whole final-film release.
- Store traceable SDET evidence for requirements BA-A01–BA-A07. Mark absent live access, tools, creative inputs or allowance BLOCKED rather than PASS.
- No open critical/important correctness, spend, approval, data-loss or delivery defects at release.

Full gates and evidence templates: `docs/sdlc/04-SDET-TEST-STRATEGY.md`.

## Out of R1 scope

Automatic publishing, multiple connected social accounts, persistent scheduling, autonomous operation when the active session is absent, customer billing, and automatic analytics ingestion. Later releases add versioned channel profiles and account-isolated publishing adapters with real platform permissions/receipts. Do not claim a platform supports an operation before checking its official interface.

## Inputs needed before dependent live work

First actual video brief and acceptable quality rubric; real creator voice/examples or a declared new voice direction; authorized images/reference assets; available image/layout/audio/Blender tools; supported browser control with user-signed-in Flow account; actual model/feature compatibility; exact generation/upload allowance and credit ceiling; delivery requirements/location. The user offered to supply inputs. Passwords and login codes must be entered by the user directly in the browser, never pasted into project notes.

## What design approval permits

Planning/implementing the software tickets and isolated tests described here. It does not approve a creative artifact, authenticate an account, authorize a paid generation, or authorize publication. Those decisions remain tied to their concrete project versions and operations.
