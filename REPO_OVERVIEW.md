# What this repository does

This repository is a toolkit of 11 YouTube skills for an AI assistant. Each skill contains instructions for a specific job; some include Python tools. Together they support research, planning, writing, packaging, transcript-based editing guidance, and channel improvement.

It is not a complete video-generation application. It does not itself generate finished video or audio, render edits, create thumbnail image files, upload videos, or post replies. It produces drafts, briefs, reports, and instructions for the creator or another system to use.

## All 11 skills

| Skill | What you provide | What it produces |
| --- | --- | --- |
| `yt-viral` | Niche/channel context and public video listings with view counts | Standout videos ranked against each channel's own median, title patterns, and ideas to adapt. Its tool needs at least four videos per channel. |
| `yt-plan` | Available hours, existing work, and relevant channel context | An upload calendar with formats, working titles, promises, workload estimates, and what to drop if time runs short. |
| `yt-script` | A video idea and creator context | Five opening-hook candidates, the best two with heuristic scores, a spoken script with on-screen directions, and a runtime estimate. Includes 21 hook formulas. |
| `yt-package` | Video idea/content and creator context | Title options, title/thumbnail-text checks, and a thumbnail brief describing text, framing, expression, and background. |
| `yt-edit` | A timestamped transcript: SRT, VTT, or Whisper JSON | Suggested cuts for pauses, filler, and repeated takes, with timecodes. Does not edit the actual footage. |
| `yt-shorts` | A long video's timestamped transcript | Ranked self-contained Short candidates, timecodes, replacement opening lines, on-screen text, loop ideas, and vertical framing notes. Does not export clips. |
| `yt-chapters` | A timestamped transcript | Suggested chapter boundaries and rewritten chapter titles; a tool checks chapter-list constraints. |
| `yt-seo` | Video content, intended audience, and search intent | Description, relevant tags, and three target search queries. |
| `yt-comment` | Comments and creator voice/context | Comments grouped by type, short draft replies, recurring questions, and a suggested comment to pin. Does not post, heart, or pin anything. |
| `yt-retention` | Audience-retention CSV, optionally a transcript and duration | Early losses, steep drops, and gradual decline, plus a prioritized change. Diagnoses are suggestions, not proof of why viewers left. |
| `yt-audit` | Channel information, recent titles/thumbnails/openings, and optional analytics | A channel review with one priority fix, three strengths, and work to defer. |

## Supporting files

- `skills/yt-script/hookscore.py`: scores opening-hook wording using heuristics; scores do not predict views.
- `skills/yt-script/hooks.json`: 21 hook formulas.
- `skills/yt-package/title.py`: checks titles and thumbnail text.
- `skills/yt-edit/deadair.py`: suggests transcript-based cuts.
- `skills/yt-chapters/chapters.py`: suggests and validates chapters.
- `skills/yt-retention/retention.py`: analyzes supplied retention data.
- `skills/yt-viral/swipe.py`: ranks videos against their own channel's median views.
- `templates/voice.md`: template for the creator's audience, speaking style, preferences, and boundaries. Many skills look for a filled profile at `~/.codex/youtube/voice.md`.

The README describes the six Python tools as Python 3 scripts with no third-party dependencies. This overview is based on the README and skill instructions; the tools were not executed for this inventory.

## Connection to our mission

The architect's repository is intended to supply the main video-production workflow. These skills can support its stages: research and planning, scripts and packaging, editing guidance, publishing text, and feedback after release. The exact connections depend on reviewing his repository and diagram, which have not been supplied yet.

To use a skill in this workspace, ask by name, for example: `$yt-script write a script about [idea]`. Skill execution still needs the relevant inputs and access to supporting tools or sources.
