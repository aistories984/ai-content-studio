# Integration review

## Download and sources

Architect: https://github.com/Perfectz/ai-approval-workflow-dash.git, cloned with available Git history into `` at commit `cb522d8`. There are 58 tracked files, including diagram PNG/JSON; no submodules were listed. External services, private project data, and generated production assets are not included. Both source trees have MIT license files; preserve both notices. The outer skills folder is not a Git working tree.

## Architecture and fit

Director Studio provides a React/TypeScript/Vite dashboard, Python FastAPI service, SQLite project state, immutable versioned assets, approval gates, dependency tracking, task leases, exports, and 18 shared CLI/MCP operations.

Its film process is premise → 10-page comic → screenplay → scratch audio → boards → Blender preview → Wan package/takes → edit. A separate Google Flow sprite workflow is also included. Preserve both modes.

Our 11 skills supply YouTube research, calendars, hooks/scripts, titles/thumbnail briefs, transcript cut suggestions, Shorts candidates, chapters, descriptions, comment drafts, retention analysis, and audits. They should produce versioned artifacts managed by the existing service. SQLite remains the production-state authority; Markdown records development and business planning.

## Gaps

- Director Studio prepares Wan packages and accepts Blender output; automatic Blender creation, paid Wan submission, reference hosting, and mastered-film rendering are not implemented. Flow execution needs separate browser/computer control and authenticated access.
- Shorts skills suggest clips; actual exported Shorts require media processing.
- The app is local and single-user, not a hosted multi-user product.
- Upstream setup targets Windows and uses Windows System.Speech for scratch synthesis. This workspace is macOS; a synthesis alternative needs design. Supplied audio is supported upstream.
- Upstream requires Python 3.11+ and Node 20.19+ or 22+. This shell reports Python 3.9.6; node/npm commands are unavailable. Other installed runtimes have not yet been inventoried. No dependencies installed or baseline tests/build run.
- Some upstream documents describe historical proposals; resolve discrepancies against current code and workflow contracts.

## Layout choices

**A — Director Studio as the unified repository (recommended).** Preserve its Git history and application structure; add complete YouTube skills/resources and our planning notes, merge instructions, and retain both licenses. Then add explicit YouTube workflow stages and skill-to-artifact contracts. This builds on the existing coordination system, but copying skills alone does not integrate execution.

**B — One repository with separate studio and skills packages.** Preserve both directory layouts and put orchestration above them. Clear package boundaries, but more path/configuration and coordination work before the first useful workflow.

The user selected A. The nested clone is the intended unified project; the merge is not implemented yet. Proposed foundation scope: `docs/superpowers/specs/2026-11-02-unified-foundation-design.md`.

## Proposed sequence

1. Select the layout and document the concrete design/implementation plan.
2. Prepare a working branch, preserve licenses, import complete skills/resources and continuity notes, and merge instructions without overwriting upstream rules.
3. Find compatible runtimes, install isolated dependencies, and establish baseline tests/build with temporary project data.
4. Define YouTube stage/artifact contracts and skill routing. Preserve the film diagram for films; avoid forcing every YouTube video through a comic and Blender.
5. Implement one requested workflow and verify its actual output; connect selected production tools where needed. Keep human approvals and paid-generation allowances intact.
6. Add post-release feedback and business measurement, expanding based on actual use.

First demonstration output, production tool choices, audience, and paid offer remain open. No paid generation, upload, publication, creative approvals, runtime-data edits, or remote repository changes occurred in this review.
