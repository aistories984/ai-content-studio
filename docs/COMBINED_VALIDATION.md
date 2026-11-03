# Combined repository validation — November 3, 2026

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
