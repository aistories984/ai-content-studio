> Source README preserved for reference. In this combined project, skill folders live in `.agents/skills/`; original install commands below describe the source layout.

# The YouTube agent skill

Eleven Codex skills that help plan, write, and improve YouTube content. The skill pack is MIT-licensed; its bundled Python tools require no API key. Running an AI assistant or external production services may involve separate accounts and costs.

## This workspace's direction

We intend to combine these skills with the AI architect's repository into one agent framework for video production, automation, and marketing, supporting a revenue-generating business. The architect's repository has not been supplied, and that framework has not been built.

- [Work log](../../WORK_LOG.md): read first for the goal, current state, and next step.
- [Thoughts and plan](../../THOUGHTS_AND_PLANS.md): user decisions, workflow, open questions, and proposed business milestones.
- [Repository overview](../../REPO_OVERVIEW.md): current capabilities, inputs, outputs, and limits.
- [Agent instructions](../../AGENTS.md): continuity and mission rules.

One of them writes your script off 21 hook formulas and scores the hook before you waste a take on
it. One lints the title and the thumbnail as a single pairing, because writing them separately is
why half of your click surface says the same thing twice. One reads your audience-retention export
and tells you the exact second people left and what you were saying when they did. One turns a
transcript into an edit decision list. One finds the Shorts already hiding inside a long video. One
goes and finds what is working in your niche and ranks it by how far each video beat its own
channel, not by how big the channel is.

**Nothing gets published until you do it.** These skills write. You upload.

## Install

This checkout exposes its skills to Codex through `.agents/skills` (a link to `skills/`).
Open this folder in Codex and start a new session to load them. Ask for a skill by name,
for example: `$yt-script write a script about my next video idea`.

To install the skills for use across projects:

```bash
mkdir -p ~/.agents/skills
cp -R skills/yt-* ~/.agents/skills/
```

Run these commands from this folder. For another project, copy the skill folders into
that project's `.agents/skills/` instead. The `.codex-plugin/plugin.json` manifest also
packages all eleven skills as a Codex plugin.

Without a local agent, paste a single `SKILL.md` into a chat to use its instructions.
The Python tools require an environment that can run Python 3.

Then spend ten minutes on [`templates/voice.md`](../../templates/youtube/voice.md). Copy it to
`~/.codex/youtube/voice.md` and fill it in, or send Codex three of your own videos and say "write
my voice.md from these". Many skills explicitly read that file. It matters more here than anywhere else,
because you have to say the words out loud.

## The eleven

| command | what it does |
| --- | --- |
| `$yt-script` | One idea into a script. Five hooks off [21 formulas](../../.agents/skills/yt-script/hooks.json), scored, then the spoken script with the retention beats marked. |
| `$yt-package` | Title and thumbnail as one pairing, linted for truncation, duplication and vagueness. |
| `$yt-edit` | A transcript into an edit decision list: dead air, filler cues, retakes, with timecodes. |
| `$yt-comment` | The comment section triaged into four piles, then replies in your voice. Says which one to pin. |
| `$yt-plan` | A week that fits the hours you actually have. One anchor, one cheap one, three Shorts. |
| `$yt-viral` | What is working in your niche, ranked by multiple over each channel's own median. |
| `$yt-retention` | Your retention export read properly: hook leak, the cliffs, the slide, and what to change. |
| `$yt-shorts` | The Shorts already inside a long video, with a new first line written for each. |
| `$yt-seo` | The description, the tags that are worth having, and the three queries this should win. |
| `$yt-chapters` | Chapters from a transcript, validated against YouTube's own rules so they render. |
| `$yt-audit` | The whole channel, ending in ONE fix rather than twenty. |

## The six tools

Every one of these runs on a clean Python 3 with no dependencies. They are the reason the skills are
not just prompts.

```bash
python3 skills/yt-script/hookscore.py --hook "one line"        # 5-property hook panel
python3 skills/yt-package/title.py --title "..." --thumb "..." # title + thumbnail linter
python3 skills/yt-edit/deadair.py transcript.srt               # edit decision list
python3 skills/yt-chapters/chapters.py transcript.srt          # validated chapters
python3 skills/yt-retention/retention.py retention.csv         # where they left, and why
python3 skills/yt-viral/swipe.py collected.json --min 2.0      # outliers by own-channel multiple
```

## The fine print

The part most packs leave out.

**It does not publish.** YouTube's Data API would allow it with your own OAuth, which makes this
pack different from the LinkedIn and Instagram ones, where posting is not available at all. It is
still not built here: every skill ends in a block you copy and a question — ship it, or change it?
Anything that claims to run your channel unattended should be read with that distinction in mind.

**`hookscore.py` is a heuristic, not a predictor.** The panel was built and calibrated against 74
real short-form hooks (the first 15 seconds of auto-captions, top-8 and bottom-8 by views across
five channels). It separates deliberately bad hooks from real ones well. It separates a given
creator's hits from their own misses barely at all. A low score is a reason to look again; a high
score is not a promise.

**The formula classifier is about the words, not the result.** When `$yt-viral` says a title used
The Statistic, that is a judgement about the title you can see, not a claim about why the video got
its views.

**`$yt-viral` reads, it does not scrape.** Public listings only. It never logs in as you and never
touches your credentials.

**Tags barely matter** and this pack says so instead of selling you a tag generator.

**Nothing invents a number.** If a skill wants a figure it does not have, it asks you for it or
writes the line without it.

## Licence

MIT. Use it, change it, ship it.
