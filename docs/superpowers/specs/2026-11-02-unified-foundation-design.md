# Unified content automation foundation

Status: proposed design for user review. Layout A selected by the user. Implementation not started.

## Intent and business goal

Provider clarification: the user selected Google Flow for video generation. Preserve the supplied diagram as the source reference, but adapt its Wan-specific package/execution nodes to a deliberately designed Flow film/YouTube handoff. Do not silently execute Wan. Current Flow code supports sprite projects only. The foundation import remains useful, but the film Flow adapter needs its own implementation design and validation; no provider/model capability is established by this document.

Combined-system acceptance: every content task must consider both the Director Studio contracts and YouTube skill catalog and identify the applicable skills, pinned inputs, outputs, and approval gates in its handoff. Selecting relevant skills is required; executing every unrelated skill or rereading all source files is not. Google Flow credit-efficiency requirements include reviewed prompts/references/timing, an explicit credit/attempt allowance, preserved original results/evidence, and reconciliation before retrying unknown outcomes. Do not claim zero waste, guaranteed reach, or guaranteed revenue.

Latest user clarification: the desired product helps earn money through trend research, standout-video analysis, strong YouTube videos and Shorts, posting workflows, and audience growth. Every task must select and follow the relevant available skills from both repositories. The required film diagram remains the production backbone. Reach and revenue are measured objectives, not guarantees. This foundation is the first integration milestone toward that product; it does not yet implement the complete creation/posting loop.

Combine Director Studio and the YouTube skill pack into one repository so agents can use a common set of instructions, tools, production records, and review gates. The eventual business outcome is a revenue-generating product or service supported by content production and marketing. The paid offer and audience are not yet selected; this foundation does not validate demand or generate revenue by itself.

## Selected approach

The user chose A: keep Director Studio's application structure and Git history, and add the skill pack. B, separate studio/skills packages under a new parent, would preserve package boundaries but require more path/configuration work. Do not replace upstream film or sprite workflows.

## Foundation scope

Use `architect-repo/` as the unified Git project. The outer folder remains the original source/reference copy; it is not a second application. Start a feature branch in the fresh clone; do not push or change its remote. Bring complete `yt-*` directories into `.agents/skills/` alongside `director-studio` and `flow-sprite-studio`. Include all Python/JSON references, and place the voice template under `templates/youtube/voice.md`. Copy the original skill-pack license into `licenses/youtube-skills-LICENSE`; retain upstream LICENSE unchanged and document provenance/source commit.

Merge our mission/continuity rules with upstream AGENTS.md. Keep upstream human approval and paid-generation rules. Copy our current notes/overview/review into the unified root, with corrected relative links. Preserve the original skill-pack README as `docs/youtube/SKILL_PACK_README.md`, adjusting relative links. Add navigation and current-vs-planned capabilities to the Director Studio README. The unified project's notes become authoritative for future implementation; the outer WORK_LOG points to that project and records the handoff.

Provide `docs/youtube/WORKFLOW.md` as the integration playbook. It maps each skill to required inputs, resulting files, and where its output can be registered. Research/calendar/SEO/comment/analytics work can initially be registered as `notes` with a relevant existing project stage, using the shared agent lease/register/validate/submit flow. This is a supporting-artifact bridge, not a new enforced YouTube workflow. It must not claim that approving a notes artifact advances a production stage; only the stage's required artifact kind can do that. Scripts must meet the existing film script contract when submitted as film scripts. YouTube scripts do not bypass comic gates in film mode.

All 11 skills remain available for direct tasks without a Director Studio project. These tasks save deliverables as files and do not claim Studio review state. The playbook must distinguish standalone tasks from project-stage work, and explain that existing gate-ineligible artifacts are not to be forced into a project.

The voice profile template remains optional setup until a voice-dependent skill requests it. Do not fabricate a profile. Preserve each skill's required prompts/tools and relative cross-skill references. Correct copied README statements about all skills reading the profile, and do not alter tool scoring behavior in this milestone.

## Explicit limits and next product milestone

### User-required diagram and YouTube integration

The user explicitly supplied the film diagram and requires the combined system to follow it. Preserve the supplied JSON at `docs/design/user-required-workflow.json`; it defines the intended film path, including controls and future integrations. The YouTube skills support this path, not replace it. Do not silently introduce a shorter film workflow. A separate non-film workflow would require a later explicit user decision.

| Diagram steps | YouTube contribution | Contract to preserve |
| --- | --- | --- |
| 01 Brief, 02 Premise | `yt-viral` researches standout patterns; `yt-plan` plans realistic work; `yt-script` supports hook options | Research informs original premises; user selects the idea. Retain audience, style, runtime, budget, evidence, and creator voice. |
| 03 Comic, 04 Screenplay | `yt-script` supports hooks, beat structure, on-screen intent, and payoff; `yt-package` aligns the title/thumbnail promise | Keep the approved 10-page comic and complete screenplay requirements. YouTube scripts must be adapted to film contracts. A word-count estimate is not measured audio timing. |
| 05 Audio, 06 Boards, 07 Blender | Script/on-screen directions inform existing production tools | Skills do not synthesize final audio, generate boards, or animate Blender. Measure rendered audio, keep stable cast IDs, clean inputs and labeled boards, and review each stage. |
| 08 Pinned package, 09 Spend approval, 10 Wan, 11 Take review | Existing Director Studio tools and selected future adapters perform these jobs | Exact version/source pins, approved allowance, durable task IDs, no silent retries, and human creative review. YouTube skill scores grant no approvals. |
| 12 Edit and delivery | `yt-edit` suggests cuts; `yt-shorts` plans derivative clips; `yt-chapters` drafts chapters; `yt-seo` prepares publishing text; `yt-package` finalizes packaging | Work from actual transcripts/approved source media. Suggested cuts must preserve approved story/timing or trigger revision. Editing instructions are not rendered media. Publishing remains a separate action. |
| After release / next brief | `yt-comment`, `yt-retention`, `yt-audit` feed measured feedback into the next plan | Save supplied comments/analytics and proposed improvements. Do not rewrite historical approvals or invent results. |

All four diagram controls apply throughout: one project record, leased agent handoffs, preserved revisions with stale dependencies, and no silent approvals/retries. Existing code groups some diagram steps within stages/tools; diagram nodes are not all separately enforced dashboard stages today.

Add acceptance traceability: verify the preserved diagram's 11 required edges and brief-to-edit path; map all 11 YouTube skills to the table above; confirm imports do not alter the existing film stage order or weaken its controls. Mark provider execution and mastered rendering unverified until actually implemented and tested.

This milestone does not add a new dashboard mode, autonomous agent scheduler, web scraper, media generator, Short renderer, cloud hosting, paid generation, account integration, publishing, or customer billing. Existing Director Studio film and sprite modes remain functional. A second design will add a genuine YouTube workflow with stage contracts and chosen production adapters after selecting a demonstration output. Record those gaps plainly, not as delivered automation.

## Platform and data constraints

Python 3.11+ and Node.js 20.19+ or 22+ are upstream requirements. Discover installed runtimes first. Install dependencies in a project-local environment only when compatible runtimes are available; network sandbox failures require normal escalation. Do not silently use Python 3.9 or modify global client settings. Scratch synthesis currently needs Windows System.Speech; on macOS mark synthesis unavailable unless supplied audio is used. A cross-platform TTS adapter is outside this milestone.

Preserve `studio-data/` and `outputs/`; all automated test records use temporary directories. SQLite is the production-state authority, Markdown is development continuity. Do not add approval tools or fabricate user reviews. No paid/cloud operations are part of validation.

## Acceptance and SDET verification

1. Unified project contains 13 discoverable skill directories, with complete imported files and intact cross-skill references; both source notices are preserved.
2. Mission, current state, and file navigation agree; all relative documentation links introduced by the integration resolve.
3. All six YouTube tools pass meaningful representative fixtures: hook panel, title/thumbnail checks, transcript cuts, chapters, retention analysis, and channel-relative outliers. Include invalid/insufficient inputs where supported. Record exact commands/results.
4. Upstream Python tests pass with a supported interpreter and isolated test data; frontend production build passes. Report baseline failures separately from regressions.
5. Exercise the artifact bridge through the shared interface against temporary data: discover project/action, claim task, register a supporting notes artifact with pinned inputs, validate/submit/finish, and confirm no downstream stage advance or creative approval occurs. A required stage artifact still waits for human review. Include stale-source and expired-lease regression checks from upstream suite.
6. Verify film/sprite workflow definitions and production code have not been changed by skill import. CLI/MCP continue to use the same service.
7. Manual dashboard smoke check if supported browser tools are available: project listing, artifact text/prompt preview, and review queue. If browser execution or compatible runtimes are unavailable, report the exact unverified checks and do not call the whole app verified.

## Builder choices

Proposed by the architect: `.agents/skills/` as the canonical imported skill location; `architect-repo/` as the working unified project; in-place feature branch in the already separate fresh clone; no additional worktree; standalone/supporting-artifact bridge before a new dashboard mode. These keep the first integration small and preserve upstream behavior.

## Remaining user decisions

Approve this foundation scope; select the first demonstration workflow in the next product milestone. Audience/offer, chosen production services, and any paid allowances remain user decisions. Ask when an unresolved choice changes architecture or delivered behavior; settle routine reversible implementation details and record them.
