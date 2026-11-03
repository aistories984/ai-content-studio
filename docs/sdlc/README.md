# SDLC agenda: brief to downloaded Google Flow video

## Mission and release boundary

Build a working content-production system using both Director Studio and the YouTube skills. The user supplies a project idea, whether it is a Short or long video, and the desired duration. Agents select relevant skills, follow the supplied film-production diagram, prepare approved assets, create video in Google Flow, download the original output, and deliver a reviewed local video/bundle. Manual upload is acceptable for Release 1.

Popularity, trends, audience growth, and revenue are objectives evaluated using real results. The system must retain research sources and distinguish verified data from creative proposals. A scoring heuristic is not evidence of future popularity.

## The requested four roles

These are roles in the development team, not four already-installed autonomous services. Agents were dispatched to prepare the artifacts below. Persistent application-side orchestration is part of the future implementation.

| Role | Owns | Handoff / gate |
| --- | --- | --- |
| BA | User needs, release scope, requirements, unresolved inputs | `01-BA-REQUIREMENTS.md` reviewed for accurate intent |
| PO | Prioritized epics/tickets, dependencies, acceptance criteria | `02-PO-BACKLOG.md`; tickets become Ready only when inputs/design are sufficient |
| Software Developer | Architecture, adapters, implementation, recovery | `03-DEVELOPER-ARCHITECTURE.md`; implements Ready tickets with tests and exact artifacts |
| SDET | Requirement coverage, regression tests, real end-to-end evidence | `04-SDET-TEST-STRATEGY.md`; verifies each ticket and release, reports blocked live checks honestly |

The human director retains creative and spending approvals in the diagram. Developer or SDET success does not approve creative content or credit spend. Routine code changes do not require film-stage approval.

## Automation flow

1. Intake the project-specific topic/audience, Short/long format, target duration, voice/style, channel profile, and available resources.
2. Select relevant skills from both source sets and save the plan, research sources, chosen tools, and expected artifacts.
3. Develop research-informed premise options and title/hook promises; wait for selection/revision.
4. Follow the required comic, screenplay, measured audio, boards, and Blender previs stages with exact version pins and human review.
5. Build a Flow-compatible request package from approved assets. Inspect live model/reference/duration/output capabilities. Adapt shot boundaries without silently skipping approved story or timing.
6. Show exact package, settings, original downloads destination, and credit/attempt allowance for director approval.
7. Use the visible authenticated Flow session; reserve the authorized attempt before Generate. Record observed evidence and reconcile unknown outcomes before considering another attempt.
8. Download original takes, check file integrity/decodability and actual durations, register immutable artifacts, and review identity, performance, timing, and continuity.
9. Assemble accepted clips where needed; review the complete output and export video, captions/audio as available, prompts, source pins, receipts, and project archive. Produce Shorts/chapters/SEO/packaging where relevant.
10. User manually uploads in Release 1. Record feedback and results when supplied.

No implementation may claim this entire flow works merely because mocked browser jobs or local fixtures pass. A real approved Flow generation and downloaded usable video are required release evidence.

## Phased SDLC agenda

| Phase | Deliverable | Exit condition |
| --- | --- | --- |
| Discovery | BA requirements and capability assessment | Required workflow, release boundary, and decisions explicit |
| Product planning | PO backlog and acceptance matrix | Small ordered tickets with dependencies, owners, and test evidence |
| Design | Developer architecture and chosen first approach | Concrete design reviewed; missing tool/account prerequisites exposed |
| Implementation | Ticket-sized changes to workflow, service, browser adapter, assets, and delivery | Relevant tests plus independent review; no fabricated approvals |
| Verification | SDET regression, recovery, browser, media, and real-provider checks | Actual approved video downloaded and reviewed; evidence linked |
| Release | Runbook, known limits, handoff, and reproducible demo | Ready for manual upload; no unresolved critical/important failures |
| Improvement | Real audience/business feedback and measured costs | Next work targets a demonstrated bottleneck |

## Selected approach

**A — Session-assisted automation (selected by the user).** Agents act during an active session, using the existing shared service and a dedicated visible browser after the user logs in. Persist tasks, artifacts, approvals, and receipts so work resumes safely. Fastest route to a real verified download, but an active agent/browser session is needed.

**B — Unattended local worker from the first release.** Add a persistent runner, model execution backend, scheduling, job recovery, browser ownership, and notifications immediately. Stronger unattended operation, but adds considerable infrastructure before proving provider execution and media quality.

The user selected A for Release 1. B is deferred. Both preserve human creative/spending gates and the full production diagram. Neither means a hidden Flow API or unlimited retries. A later worker can build on A's durable records.

## Per-project information and access

- The user clarified that Short/long format and seconds/minutes are supplied for each project. There is no fixed global clip/video length. The first real pilot topic and exact duration remain open.
- User signs in directly in a dedicated browser. Do not put passwords, login codes, cookies, session exports, or tokens in chat, tickets, Git, or generated media.
- Real browser access, supported selected model, approved creative inputs, local production tools, and explicit allowance are prerequisites. If unavailable, report the precise blocked ticket.
- The source diagram's 2–15 second package conventions are not proof that Flow accepts identical references or durations. Validate the live provider capabilities before generation; record any adaptation for review.

## Later releases

- Multiple channel profiles: each account has its own audience, content types, voice/style, format, schedule, approval rules, and analytics identifiers.
- Authorized publishing adapters for multiple YouTube, TikTok, and Instagram accounts, with account isolation, draft previews, idempotent posting, receipts, and recovery, subject to actual supported platform capabilities.
- Trend monitoring, content calendars, per-account derivatives, and feedback loops. Monetization/marketing experiments track revenue and production cost separately from views.

These are future scope; no accounts have been connected or uploads authorized by this document.

## Provider research used for planning

Checked official Google Flow documentation on November 3, 2026:

- Create video and choose settings: https://support.google.com/flow/answer/16353334
- Download generated media: https://support.google.com/flow/answer/16935308
- Models and feature compatibility: https://support.google.com/flow/answer/16352836
- Credit accounting: https://support.google.com/flow/answer/16526234

Do not hardcode a credit price from a planning document. Actual availability/settings/cost must be checked in the user's live account. This research is not evidence that the account has been connected or a provider generation completed.
