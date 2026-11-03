# Combined project continuity

- Combined-system rule: for every content creation request, consider both Director Studio's architecture/contracts and the YouTube skill catalog before choosing the applicable skills. Record the selected skills, required inputs, intended outputs, and relevant approval gates in the task handoff. Do not default to only one source. Read the catalog first and the applicable skill/reference files in depth; reread unrelated code only when necessary. Do not force irrelevant skills into a task.
- User selected Google Flow for video generation. Preserve the film diagram's planning, timing, pinned references, review, allowance, and retry controls; adapting its current Wan handoff to Flow is a required design change, not an implemented feature. Existing Flow support is for sprites and is not proof of a film/YouTube adapter. Do not silently substitute Wan or another provider.
- Credit efficiency: prepare and review exact prompts, references, timing, and intended outputs before generation; obtain the required allowance, record each attempt/result, and reconcile uncertain outcomes before any retry. Reduce avoidable waste without promising zero wasted credits or guaranteed viral results.
- Primary user outcome: agents that support earning money through trend research, strong YouTube videos/Shorts, posting workflows, and measurable audience growth. Follow the architect's required diagram and combine both repositories' capabilities. Viral reach and revenue are objectives, never promises.
- For every task, select and follow the relevant available skills from both repositories, including their required tools and inputs. Use skills because they fit the task; do not force all 13 into every action. Identify unsupported steps and missing inputs explicitly. Application engineering and tests also follow applicable engineering skills. A skill draft is not finished media or a published post.
- Mission: combine the AI architect's repository and video-production workflow with this repository's YouTube skills and supporting resources into one working YouTube production system.
- Expanded outcome: one unified repository and agent framework that turns plain-language requests into coordinated content-production and automation workflows. Support a revenue-generating product/business, including marketing, advertising content, and Shorts. These activities are in scope. Revenue is an objective, not a promise. Product, audience, monetization, production tooling, and automation boundaries still need definition.
- The mission includes actively using and strengthening all 11 skills across their appropriate workflow stages: research, planning, scripting, packaging, edit guidance, Shorts, chapters, SEO, comments, retention, and audits. Read the relevant skill instructions and use required tools; retain relevant inputs, sources, outputs, decisions, and results. Flag missing inputs and workflow conflicts. See `THOUGHTS_AND_PLANS.md` for the stage map. Improvements to these skills are in scope even before the architect's repository is supplied.
- Before acting on a new request, check whether it supports this mission. Planning, documenting ideas, inspecting both repositories, integration, and validating the resulting workflow are in scope.
- If a request is unrelated or would replace the mission, say plainly: "This takes us away from this folder's mission: building the combined content and automation framework for a revenue-generating business." Explain the mismatch briefly and ask whether the user intends to expand/change the mission or keep that work separate. Do not start the unrelated changes until the user clarifies. An explicit user decision to change scope takes precedence; record it in both notes files.
- Treat new goals as proposed until the user adopts them. Keep supporting goals connected to the mission; do not silently turn suggestions into project goals.
- Read `WORK_LOG.md` first when starting or resuming work. It is the concise source for the main goal, current state, and next step.
- If the user says "read where we left off" or similar, read the log's Main goal and Current handoff first, summarize the stopping point briefly, and continue the recorded next action. Do not repeat completed audits or read the whole codebase for orientation. Consult linked documents and targeted code only when needed; acknowledge missing context rather than inventing memory.
- Read `THOUGHTS_AND_PLANS.md` when the user's original ideas or decisions need clarification. Avoid rereading unrelated files or old conversation history for context already summarized in the log.
- Read relevant project files as needed to do accurate work; the log does not replace inspecting code before changing it.
- Update `WORK_LOG.md` after each meaningful action and before ending a work session. Use the user's local date (America/New_York), record completed work, results, changed files, and blockers. Group routine reads and checks concisely.
- Keep the goal and current handoff at the top accurate and brief. Append dated activity below; preserve earlier entries.
- Record new user ideas and decisions in `THOUGHTS_AND_PLANS.md` and summarize any resulting change of direction in `WORK_LOG.md`.
- Distinguish proposed work from completed work. Never record an integration, test, or other action as done unless it actually happened.


# Director Studio workspace

This repository contains a local film-production dashboard and a reusable agent workflow. It also retains the standalone scratch-audio tool and its technical demo.

## Work on game sprites

Read `.agents/skills/flow-sprite-studio/SKILL.md` and `docs/SPRITE_WORKFLOW.md`. Query the selected project's workflow (`get_workflow` with `project_id`); sprite scenes represent action/direction animation entries. Use Google Flow's visible browser UI and the approved Omni model, never a video generation API. Reserve the exact approved credit/attempt allowance locally immediately before Generate, and reconcile uncertain results instead of silently retrying. Preserve original downloads, clean reference versions, exact prompts, settings and UI evidence. Only extract sprites from a current approved clip; local QC never approves art.

## Work on a film

Read `.agents/skills/director-studio/SKILL.md` and use the shared CLI/MCP tools in `docs/AGENT_INTERFACE.md`. Query project state before producing a deliverable. Use exact artifact versions, source pins and task leases. The dashboard is where the director reviews prompts and outputs together. Never record an approval merely because a tool ran successfully. The imported audio lab is a sandbox, not an approved creative project.

## Work on the application

Application maintenance does not need film-stage approval. Preserve user data in `studio-data/` and existing media in `outputs/`. Use temporary data directories for automated/browser tests; do not test approval by changing the user's real film records. No paid generation or cloud upload is part of ordinary app validation.

- Shared business rules: `studio/store.py`; agent surface: `studio/agent_tools.py`.
- HTTP/UI: `studio/app.py`, `src/main.tsx`, `src/styles.css`.
- Workflow contracts: `workflows/comic-to-wan-v1.json`, `workflows/sprite-to-flow-v1.json`, `docs/WORKFLOW_SPEC.md`, `docs/SPRITE_WORKFLOW.md`.
- Start: `START_STUDIO.ps1`; app at `http://127.0.0.1:8767`.
- Build: `npm run build`.
- Relevant tests: `.venv/Scripts/python.exe -m unittest discover -s tests -v`.

Keep the CLI, MCP and dashboard on the same rules. Do not add agent approval operations or hidden paid retries. Model changes require checking current provider documentation. Describe local previews and verified provider executions separately.
