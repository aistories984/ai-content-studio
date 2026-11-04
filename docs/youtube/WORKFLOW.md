# Using both sources together

Open **this repository root** in the agent, so `.agents/skills/` exposes all 13 skills. No global Claude plugin installation is required for this Codex checkout. The pasted Claude installation commands apply to Claude, not to the local Python service.

Read `WORK_LOG.md` for the development handoff. For a content request, select the applicable YouTube skills and read `director-studio` when working on a Studio film. Use `flow-sprite-studio` only for sprite projects. Keep the supplied film diagram and human review controls.

## Skill selection and artifacts

| Purpose | Skill | Artifact / prerequisite |
| --- | --- | --- |
| Standout research | `yt-viral` | Public video data, URLs, channel-relative ranking; at least four videos/channel |
| Schedule | `yt-plan` | Available hours, existing work, calendar |
| Script | `yt-script` | Creator context, scored hooks, script with on-screen directions |
| Title/thumbnail | `yt-package` | Title checks, thumbnail text and visual brief |
| Edit guidance | `yt-edit` | Real timed transcript → cut suggestions |
| Shorts | `yt-shorts` | Long-form transcript → candidate spans, new openings, framing notes |
| Chapters | `yt-chapters` | Timed transcript → validated chapter boundaries and draft titles |
| Search text | `yt-seo` | Description, relevant tags, target queries |
| Replies | `yt-comment` | Supplied comments → draft replies/pin suggestion |
| Retention | `yt-retention` | Supplied CSV and optional timed transcript → leak report |
| Channel review | `yt-audit` | Channel context → priority fix and supporting evidence |

Many writing skills require `~/.codex/youtube/voice.md`. Fill `templates/youtube/voice.md` with real creator examples before copying it there. Do not invent your voice or channel results.

## Flow film intake and local execution

The dashboard's New project form defaults to Google Flow film. Enter a topic, audience, visual style, Short/long format, and target seconds. This creates a `comic-to-flow` project that preserves the required film stages. Existing Wan film and sprite projects remain available explicitly.

The Production handoff panel shows the eligible stage, selected skills, the full eleven-skill catalog with deferral reasons, and current/historical output receipts. A tool output does not complete a creative stage. Flow film generation intentionally reports an unimplemented-adapter error rather than falling back to Wan.

New shared CLI/MCP operations:

- `create_production_project(payload)` creates validated intake. Required payload fields: `topic`, `audience`, `style`, `format` (`short`/`long`), `target_seconds` (2–14400). Optional title, creative brief, creator voice/context, research request and aspect ratio are retained as documented by the service. No demo bypass is permitted.
- `get_production_handoff(project_id, scene_id=None)` reads the brief, current step, applicable skills/hashes, recorded evidence and remaining blockers.
- `run_youtube_tool(project_id, tool_name, arguments, task_id, token)` runs a fixed local helper under a live task claim. Allowed IDs: `hookscore`, `title`, `deadair`, `chapters`, `retention`, `swipe`. Use explicit absolute paths for files. Inputs/sources are capped at 1 MB, output processing at 2 MB, execution at 60 seconds. Supported tool options mirror the helper's documented flags; no arbitrary commands are accepted.

Use the existing `claim_task` first, then validate/submit the saved artifact and finish the task as appropriate. Tool execution saves draft notes and does not submit, approve, or finish the task automatically. Store structured request JSON containing a private lease only under an ignored location such as `.tools/`; never commit it. All clients must point to the same `DIRECTOR_DATA`.

HTTP equivalents: POST `/api/production/projects`, GET `/api/projects/{id}/production`, and POST `/api/projects/{id}/youtube-tool`. Existing director-session write protection applies. No account login, credit spending or upload occurs through these operations.

## Director Studio handoff

Use `.venv/bin/python` on macOS/Linux; Windows uses `.venv/Scripts/python.exe`.

1. `python -m studio.cli list_projects`, then `get_project` and `get_next_action` with the intended project ID. All clients must share the same `DIRECTOR_DATA` directory.
2. Read the selected skill instructions, approved source versions, and feedback. Record the selected skills, inputs, intended outputs, and review gates. Do not start blocked stages.
3. `claim_task`, run the relevant tool or creative task, and save its deliverables. Do not put lease tokens in saved artifacts.
4. `register_artifact` with the task ID/token, exact prompt, source pins, metadata identifying the selected skills, and absolute paths. Research/tool reports may use `kind: notes` at the currently eligible stage. A film script must meet the full film contract and cannot skip the comic stage.
5. `validate_artifact`, `submit_for_review`, and `finish_task`. Supporting notes appear in review but **do not complete the required production artifact or advance its gate**. Approval is a human action.
6. Standalone YouTube tasks without a Studio project save output files and do not claim Studio review state.

Use JSON argument files as described in `docs/AGENT_INTERFACE.md`; no automatic background agent is installed. The repeatable cross-repository handoff test is `test_skill_output_roundtrips_through_studio_without_approval` in `tests/test_youtube_tools.py`.

## Current boundary

Existing Wan film mode still exports Wan packages. New Flow film mode has intake/handoff/local-tool execution only. Existing Google Flow reservations/execution receipts remain sprite-specific. A Flow film/YouTube adapter, rendered Shorts, automatic publishing, and autonomous scheduling are not implemented. Follow the planned diagram adaptation before using Flow for films; do not treat passing local tests as provider validation or spending permission.

Scratch speech synthesis uses Windows voices. On macOS/Linux use supported recorded audio (`audio_file`) for timing; the timing tests verify this path. Synthetic test fixtures are not approved creative output or proof of audience performance.
