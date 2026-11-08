# Combined repository validation

## Research → ideas verification — November 8, 2026

| Check | Result |
| --- | --- |
| Full Python suite | 192 PASS, zero failures/skips, 25.531 sec; `.tools/2026-11-08-research-final-tests.log` |
| Production build | TypeScript/Vite PASS; root final build and UI ordering-fix build logs retained |
| Five isolated browser flows | Research, dashboard, Flow intake/helpers, film package/spend and actual native audio PASS; `.tools/2026-11-08-research-ui-{green,dashboard,production,film,audio}.log` |
| Review regression | Delayed pre-save GET hiding a saved report/request reproduced RED; epoch/loading fix and full Research browser GREEN; `.tools/2026-11-08-research-ui-ordering-{red,green,build}.log` |
| Scoped independent reviews | Backend PASS; UI PASS after same-reviewer ordering-fix signoff |
| Final integration review | PASS after scoped optional-voice fix signoff; `.superpowers/sdd/2026-11-08-research-to-ideas/final-review.md`; no open Important/Critical findings |
| Live public observation | Five dated secondary-listed Shorts, actual helper output and two original ideas saved/reopened; `.tools/2026-11-08-live-research/` |
| Running Studio | Restarted after zero-active-job check, preserving two projects and no seeding; HTTP200,32agent operations, one saved example/two ideas/no selection |

The real browser flow begins with zero projects, persists a broad research request, saves an actual helper report through the shared agent operation, inspects source links/metrics, selects an exact idea with audience/style, opens the correct Google Flow project and verifies all twelve named obligations remain unapproved. Exact retries reuse one project. Research and ordinary artifact receipts render together. Reload, old/new reports, unknown views, request switching and delayed responses retain the correct evidence. Screenshots `.tools/research-{desktop,mobile,project-desktop}.png` and `.tools/research-live-{desktop,mobile}.png` are retained; root inspected live desktop and technical mobile layouts.

Both final UI fixes (response ordering and omission of blank optional creator voice) changed UI only; the full Research browser and production build were rerun after each. Blank and populated voice selection plus exact retries pass. The backend remained unchanged from the recorded192-test run. Tests use disposable data, not the user's production projects. The live example is explicitly a technical integration example using [a public secondary listing](https://trari.com/en/c/epicgardening/), captured November8 at17:48:57UTC. Direct YouTube pages were unreadable; counts are not independently verified, age-adjusted or a full-channel baseline. The saved example created no production project/selection/approval. No Google login, paid generation, upload or finished-video acceptance occurred.

This verifies the selected active-session coordination path. The dashboard does not run a background researcher or independently measure views. Research/selection is separate from authoring and approving the premise/comic/screenplay. Image/boards/Blender, Flow film execution/downloads, final rendering and real-video acceptance remain unfinished.

## Latest verification — November 8, 2026: native temporary audio

| Check | Result |
| --- | --- |
| Full Python suite | 178 PASS, zero failures/skips,23.319sec; `.tools/2026-11-08-native-audio-tests.log` |
| Frontend production build | TypeScript/Vite PASS |
| Four isolated browser checks | Dashboard, Flow intake/helpers, film package/spend and actual native audio PASS; `.tools/2026-11-08-native-audio-browsers.log` |
| Native audio path | Explicit installed voice, blank scene-sized source, real speech/mix/stems/SRT/cues and measured duration; passing output remains in_review |
| Independent reviews | Native adapter, shared service, UI and final integration PASS; all four recorded findings fixed and re-reviewed |
| Updated local Studio | HTTP200; voice endpoint200/macOS say/184voices/temporary_only true;28agent tools; restarted after zero-active-job check |

The audio service rechecks screenplay/source/file/direction/scene/lease/target state before rendering and atomically on registration/submission. Agent CLI rendering is synchronous; director HTTP stays asynchronous. Supplied recordings are bound to verified read-only captured copies and recorded original/runtime/import evidence. Alias changes cannot substitute unvalidated audio; rendered-line hashes also detect changed-then-restored copies. Source/lease tokens never become saved job/evidence fields. Overrun speech remains intact and unapproved. Flow versions exclude the standalone legacy Wan plan; old Wan/standalone behavior is preserved.

Tests include20speech and26audio-service cases plus the existing132 baseline. Mac native speech was exercised directly and through the actual browser/HTTP pipeline, using only disposable technical fixtures. Windows System.Speech boundaries are mocked; actual Windows runtime was not available. Image/page/board/Blender production, final audio casting, real Flow execution/original downloads/final film rendering and real-video acceptance remain unfinished. No paid request, Google account operation, cloud upload or final creative approval occurred.

Review report: `.tools/2026-11-06-native-audio-integration-review.md` (November8 fix-wave signoff); adapter report `.tools/2026-11-06-native-audio-task1-review.md`. Screenshots: `.tools/audio-form-{desktop,mobile}.png` and `.tools/audio-{desktop,mobile}.png`; mobile form inspected. Prior dated results below remain historical.

## Latest verification — November 6, 2026

Offline film packages and credit controls are implemented locally and independently reviewed; full video automation remains unfinished.

| Check | Result |
| --- | --- |
| Full Python suite | 132 PASS, zero failures/skips, 16.715sec; `.tools/2026-11-06-final-tests.log` |
| Frontend production build | TypeScript/Vite PASS after final scope-copy correction |
| Existing dashboard browser | `scripts/check_dashboard.cjs` PASS on final stable build |
| Flow intake/helper/direction browser | `scripts/check_production.cjs` PASS; immutable intake preserved, credit cap save works |
| Film package/spend browser | `scripts/check_film.cjs` PASS: exact prompt/ref review, separate package/allowance decisions, conservative unknown commitment, Refresh/reload, desktop/mobile, no Generate/page errors |
| Independent reviews | Foundation, financial service, integration/re-review and whole-branch PASS; no outstanding findings |
| Live Studio | HTTP200 at127.0.0.1:8767; three workflows/new film state route verified, no test records seeded |

New service covers immutable observations/packages/decisions/allowances/attempts/results, current approved source/file/lease checks, atomic project/account reservations, cumulative scene/project ceilings across revisions, observed-cost overruns without assumed refunds and fresh-lease reconciliation. Five new agent-safe operations bring total CLI/MCP tools to26; human approvals and caps remain outside agent TOOLS. ZIP exports retain safe `film-production.json` history.

Tests/reviews found and fixed Flow direction-save rejection, stale film state after dashboard Refresh and ignored conflicting HTTP envelope identity fields. Source-integrity cross-component probe confirms an upstream helper receipt is pinned into the film package; tampering invalidates handoff/package and blocks reservation with zero commitment. A failed browser repeat during a concurrent rebuild was repeated successfully against the stable build; usage-limit interruption was resolved on user resume. Do not substitute old failure/pending status for final results above.

All test projects use temporary data; fake observed account/model values and placeholder Blender bytes are technical fixtures. No real Flow login/generation, credits, upload, original download, actual Blender production or final render were verified. A reported downloaded state explicitly sets local verification false. Production asset/browser/download/render adapters and real-video acceptance remain unfinished. English24-second illustrated robot-gardening pilot is selected; audience/voice/production tools and actual creative/spend approvals remain open.

Repeat film browser check with ffmpeg/ffprobe on PATH and the existing local browser dependencies:

```bash
PLAYWRIGHT_BROWSERS_PATH="$PWD/.tools/browsers" node scripts/check_film.cjs
```

Reports/screenshots/logs remain ignored under `.tools/`; execution ledger is under `.superpowers/sdd/2026-11-06-flow-film-state-and-credit-controls/`. No agent Git publication. Historical results below describe earlier milestones.

## Original foundation verification — November 3

## What was checked

The consolidated sources now run locally on this ARM Mac. This validates the app, imported tools, and supporting-artifact handoff; it does not establish end-to-end autonomous film production.

| Check | Result |
| --- | --- |
| Python environment | Python 3.12.16; 32 locked packages installed, dependency compatibility check passes |
| Frontend environment | Official Node.js 22.23.4 ARM Mac archive, SHA-256 verified against Node's published sums; npm lock installed |
| Application + combined tests | 56 tests passed, zero failures/errors/skips |
| Frontend build | TypeScript + Vite production build passed |
| Six YouTube tools | Real CLI fixtures exercise hooks, titles, transcript cuts, chapters, retention, channel-relative outliers |
| Cross-repository handoff | Hook-scoring JSON registered as a Studio supporting artifact; copied file roundtrips intact; validation/submission succeed, required film stage remains incomplete |
| Shared agent interface | Upstream real stdio MCP test passes; 18 tools; no agent approval tool |
| Media path | FFmpeg/FFprobe installed project-locally; previously skipped sprite extraction/export tests now run and pass |
| Real dashboard | Chromium: create film through UI, register agent notes into temporary data, display artifact/prompt and pending review; no page errors; desktop and 390px mobile layouts checked |
| User records | All test projects use temporary directories; no real production reviews changed, no paid generation/cloud upload performed |

## Fixes backed by failures

- macOS install failed because `pywin32==312` had no compatible wheel. Added the Windows platform marker; the same locked install then succeeded.
- The title tool allowed four thumbnail words despite its three-word contract. Added a boundary regression test, observed failure, changed the threshold, and reran successfully.
- The transcript parser crashed on a JSON segment list by calling `.get` on a list. Reproduced the exception, fixed list/object dispatch, and tested both forms. The parser now closes its source file as well.

Added `tests/test_youtube_tools.py` (nine checks), `START_STUDIO.sh`, and `docs/youtube/WORKFLOW.md` for repeatable combined use. Existing film/sprite stage definitions and approval rules were preserved.

## Repeat the checks

Run from the repository root with a supported Python environment, Node/npm on PATH, and FFmpeg/FFprobe on PATH:

```bash
.venv/bin/python -m unittest discover -s tests -v
npm run build
sh -n START_STUDIO.sh
```

For this prepared Mac checkout:

```bash
export PATH="$PWD/.tools/node/bin:$PWD/.tools/media/node_modules/@ffmpeg-installer/darwin-arm64:$PWD/.tools/media/node_modules/@ffprobe-installer/darwin-arm64:$PATH"
.venv/bin/python -m unittest discover -s tests -v
npm run build
```

Browser smoke test (optional test tooling, not an application dependency):

```bash
npm install --prefix .tools/browser playwright@1.64.1
PLAYWRIGHT_BROWSERS_PATH="$PWD/.tools/browsers" node .tools/browser/node_modules/playwright/cli.js install chromium
PLAYWRIGHT_BROWSERS_PATH="$PWD/.tools/browsers" node scripts/check_dashboard.cjs
```

The smoke test launches an isolated browser and temporary app data, chooses a free localhost port, and removes its temporary data afterward. Screenshots and server log stay under ignored `.tools/`. It never clicks Approve or Generate. Runtime binaries, caches, dependencies, and personal project data are excluded from Git.

## Remaining product work

- Google Flow film/YouTube generation adapter: not implemented. Current Flow reservation/receipt functions are sprite-specific; current film mode still exports Wan packages.
- Automatic agent selection/execution, rendered Shorts, mastered final cuts, account connections, and YouTube publishing: not implemented by this validation work.
- Windows speech synthesis: unavailable on macOS. Recorded compatible WAVs work for timing and are exercised in tests; no alternative TTS service was selected.
- Creator voice, target audience, niche, paid offer, and actual channel analytics still need real user inputs. These fixtures do not demonstrate viral reach or revenue.

Source files coexisting is not the same as autonomous production. The verified integration today is the skill/tool workflow plus shared Studio artifact/review storage described in `docs/youtube/WORKFLOW.md`.

## Local Flow intake/runner slice — November 3, 2026

On local branch `feature/flow-video-automation`, unstaged and uncommitted for user review:

- New Flow film workflow preserves the original film artifact kinds/scopes and diagram mapping; raw source diagram unchanged. Demo bypass rejected. Flow preparation fails explicitly until its provider adapter exists.
- Intake validates per-project topic, audience, style, format and duration and persists the normalized brief. Handoffs show all relevant skill instructions/hashes and defer unsupported work honestly.
- Six allowlisted helpers execute through shared HTTP/CLI/MCP with lease/pin checks before and during registration, fixed script/dependency hashes, input hashes and strict JSON receipts. Changed inputs, malformed output, failed processes, stale claims or unknown tools cannot register success.
- Evidence distinguishes current/latest outputs from superseded/history and changed-source receipts. Recorded output stays draft until reviewed; required production stages do not advance automatically.
- Full suite: **102 tests passed, zero skips/failures**, including real six-tool fixtures, new HTTP/CLI contracts and a real 21-tool stdio MCP session. Production TypeScript/Vite build passed. Existing dashboard browser regression passed. Flow browser check covers default selection, Short/long intake, saved state, actual hook receipt and mobile layout; latest rerun is recorded in local review notes.
- Tests exposed and fixed superseded-evidence status, extreme duration overflow, nonfinite stored JSON receipts and a missing invocation prompt. Browser RED/green exposed the missing initial Flow UI and an inaccessible exact video-format label.

Independent review: Task1 received a fresh SDET review and approved fix re-review. The Developer sub-agent hit its usage limit during Task2; coordinator completed remaining changes and automated verification inline. **Fresh independent review of Tasks2/3 and the whole branch remains pending**. This is local implementation evidence, not R1 provider acceptance or merge approval.

Run the Flow browser check with the same local test dependencies as the existing smoke:

```bash
PLAYWRIGHT_BROWSERS_PATH="$PWD/.tools/browsers" node scripts/check_production.cjs
```

No Google Flow account session, real generation, credits, cloud uploads or publication were used. Actual stage-asset creation, credit/attempt controls, provider generation/download, final rendering and publishing remain later tickets.
