# Native scratch audio implementation plan

> For agentic workers: use superpowers:subagent-driven-development or executing-plans task by task. User override: preserve current feature/flow-video-automation and all existing edits; no staging/commit/push/PR/merge. Do not redo completed film package/credit work.

**Status:** Completed local temporary-audio scope November 8, 2026.178tests/build/four browsers and independent reviews passed; real Mac speech exercised. Actual Windows execution, final casting and full video/Flow acceptance remain unverified or unfinished. No Git publication.

**Goal:** Produce real temporary dialogue on this Mac, expose explicit installed-voice selection, and register measured audio/stems/cues through the preserved film approval rules.

**Architecture:** Add a platform-native speech adapter used by the existing deterministic scratch timeline tool. Share guarded audio orchestration between director HTTP jobs and a synchronous leased agent operation. The UI makes users select a voice and enter real screenplay dialogue; no Windows demo voice/text is silently used on Mac.

**Tech stack:** Existing Python standard library, native macOS `/usr/bin/say`, Windows System.Speech, FastAPI/React; no cloud service, new runtime dependency or paid operation.

**Spec:** Existing approved R1 design `docs/superpowers/specs/2026-11-03-flow-video-r1-design.md`, R1-007 and the full twelve-obligation workflow. User has explicitly resumed implementation. Native temporary speech is platform parity with existing Windows scratch audio, not a selected final voice provider.

## Global constraints

- Preserve required premise/comic/screenplay/audio/boards/Blender/package/spend/generation/take/edit obligations and human approval. No creative approval tool.
- Use actual supplied or synthesized audio and measured timing. Never trim/stretch/lose overrun dialogue; existing recorded-input and timing regression tests stay green.
- Explicit installed voice required; no fallback to a different voice/provider. Native voices are temporary timing audio, not final creative acceptance.
- Native speech output must be nonempty, nonsilent mono48kHz16bitPCM; process exit0 alone is insufficient. Local sandbox may prevent synthesis without reporting an error; retain clear failure instead of fake success.
- Shell=False/fixed executable vectors, bounded input/timeouts, text supplied through UTF8 file/stdin rather than shell/voice flags. No credentials, network or paid speech calls.
- Windows existing rate[-10,10] remains unchanged. macOS rate0 uses native default; nonzero Windows rates reject on macOS with explicit instruction. Optional `rate_wpm` (integer40..600) selects actual native words/minute; Windows rejects this foreign rate option rather than ignoring it.
- Linux/unsupported platform: supply PCM recordings or configure a later engine; do not silently select/install another provider.
- Tests use temporary data. Preserve all existing source edits and real studio-data/outputs. All new work stays unstaged/uncommitted.

## Review focus

- Voice names containing spaces/parentheses and unavailable/malformed voices must not become shell/options (Task1).
- Empty/silent output with exit0, timeout and missing local speech availability must fail before successful artifact registration (Tasks1/2).
- Existing audio_file timing/overrun behavior, Windows behavior and supplied recordings must remain valid (Task1).
- Agent jobs cannot survive CLI via daemon assumptions: agent operation is synchronous under a live audio lease, revalidated after rendering and on registration; no lease secrets in jobs/artifacts/results (Task2).
- Approved screenplay/source revisions and project/scene changes during synthesis block stale success; unknown source files and task scope reject (Task2).
- Template/voice UI matches selected scene duration, never installs/picks voices or treats demo dialogue as real content; UI timing success is separate from human approval (Task3).

### Task 1: Native speech adapter and deterministic CLI integration

**Files:** create `scripts/speech.py`, `tests/test_speech.py`; modify `scripts/scratch_audio.py`, `scripts/synthesize.ps1` only for voice discovery compatibility if needed. No studio service/API/UI edits.

**Interfaces:**
- `get_speech_capabilities()` -> `{platform,engine,available,voices:[{id,name,language}],issues,temporary_only:true}`. macOS discovers with fixed `/usr/bin/say -v ?`; parse multiword/parenthesized names and locale. Windows queries installed enabled System.Speech voices via fixed script. Unsupported platforms return clear unavailable + recorded-input alternative. Discovery success is not a synthesis guarantee.
- `synthesize_requests(requests, work_dir)` -> `{engine,...}` for list of `{text,voice,rate,output,rate_wpm?}` from validated source. macOS uses `say -v <exact installed voice> -o <dest> --file-format=WAVE --data-format=LEI16@48000 --channels=1 -f <UTF8 file>`; resolve fixed tool only, timeout180s per batch with bounded lines/text. Verify exact PCM output and nonzero samples. Windows retains existing PowerShell requests, no rate conversion.
- Scratch render chooses native speech only for missing audio_file lines, propagates `rate_wpm`, records actual engine/provenance (including mixed recorded/native where applicable), preserves output files/reports and all no-upload/approval limits. Both standalone script and package imports work.

- [x] Write RED tests with mocked subprocess/native inventories: multiword voice names, exact argument vectors/file text, unknown voices, unsupported rate/platform, empty/silent/nonPCM output, process failure/timeout and supplied-recording behavior.
- [x] Implement minimal adapter/CLI changes, focused GREEN; run existing timing tests unchanged. Test Windows adapter through controlled process observations (actual Windows execution unavailable).
- [x] Run actual native speech smoke outside sandbox if needed, render complete WAV/stems/timing/SRT and verify_audio; no paid/provider operations or approved pilot claims. Retain output under ignored .tools/ only.
- [x] Write `.tools/2026-11-06-native-audio-task1-report.md` with exact interfaces/commands, RED/GREEN and limits. Independent scoped review, no commits.

### Task 2: Shared guarded audio service and agent operations

**Files:** create `studio/audio.py`, `tests/test_audio_service.py`; adapt existing run_audio/audio routes in studio/app.py to shared logic; add `get_speech_capabilities` and `render_scratch_audio` wrappers in agent_tools.py and update MCP discovery tests.

**Interfaces:**
- Service voice discovery GET `/api/audio-voices`; no account/secrets or synthesized playback side effect.
- `render_scratch_audio(project_id,scene_id,source,task_id,token)` synchronous agent-safe operation returns registered artifact/version IDs and measured timing. Requires live matching ready audio-stage scene claim and pinned approved premise/comic/script; validates before synthesis and after completion/at registration. Saves temporary audio/report/stems/cues and actual engine, submits passing structural output for human review only. Does not approve or finish task automatically.
- Existing director POST `/api/projects/{project}/audio` remains asynchronous using jobs and shared service (no agent lease fabricated). Reject sprite/premature stages, malformed source, missing explicit voices, source duration mismatch and dashboard audio_file paths. Preserve safe failure/needs_changes and original overrun outputs. Revalidate direction/scene AND current approved upstream version IDs/hashes after synthesis so old scripts cannot be registered/submitted as current.
- Native source collection and registration use immutable Store versions; task tokens remain ephemeral arguments, not saved source/metadata/job JSON. Registration/source failures never record successful jobs.

Additional binding details: the leased agent operation may import explicitly supplied absolute PCM audio_file paths (hash/check before and after); the director HTTP route still rejects local recording paths. Current approved premise/comic/script versions and attached hashes are fingerprinted, not project revision alone. A fresh render revises the existing generated temporary-audio artifact with expected_version rather than accumulating unrelated primary audio artifacts. Target is chosen/rechecked under execution so queued work cannot overwrite a newer version. Add a minimal Store.create_job duplicate-active guard for scratch_audio if necessary, preserving sprite behavior. Capture scratch.render's stdout inside the service so the CLI emits only its single JSON result. Return job_id/artifact_id/version_id/timing_passed/actual_duration and retain failed/overrun output directories without claiming success. Voice validation happens before starting a synthesis job; no voice fallback. HTTP route wrappers and agent wrappers share this service, not two copies of registration logic.

- [x] RED tests for real measured recorded fixture orchestration (mock only actual speech when needed), unsupported stage/workflow, expired/wrong claims, changed screenplay/direction/scene during generation, empty output, director vs agent parity and no secret/approval leak.
- [x] Implement shared service preserving existing job API status shape; focused/full tests GREEN and real stdio MCP discovery (28 tools, no approvals).
- [x] Independent review; retain exact interface/report `.tools/2026-11-06-native-audio-task2-report.md`.

### Task 3: Explicit installed voices and usable scene-sized audio UI

**Files:** AudioForm in src/main.tsx (or focused extracted component), minimal CSS, isolated browser test; documentation/status updates.

- [x] Load `/api/audio-voices`, show actual platform/temporary-only status, explicit character voice dropdowns with blank initial selection; unknown/unavailable voices show blockers. No model/provider switch.
- [x] Starter source is scene-sized30fps with one narrator, one shot/job and blank dialogue; user enters actual approved-script words. Voice remains blank until chosen. Selecting a different scene updates timing scaffold only before user-authored edits; preserve/confirm edited source changes instead of silently erasing them. Advanced JSON remains available.
- [x] Native rate_wpm control is explicitly labeled; do not apply Windows rate scale on Mac. Preview form contains no hidden synthesis request or automatic paid action.
- [x] Browser verifies form defaults, available voice selection, selected scene duration, guarded submission and actual measured audio job/version where host supports it; invalid timing yields needs_changes/no approval. Fixture projects isolate all temporary creative reviews.
- [x] Full suite/build/existing browser checks plus actual native audio smoke. Independent integration/final review, fix confirmed findings, update PROJECT_STATUS.md/remaining plan/WORK_LOG and report actual scope. Preserve no-commit policy and full required diagram. No final video/Flow/provider success claimed.
