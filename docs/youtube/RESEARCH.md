# Research → ideas

Open **Research → ideas** in the Studio sidebar, even when there are no projects. Save a question, optional categories (leave blank for broad discovery), language and time window. A pending request is durable; saving it does not start a worker. Ask your active agent session to research public listings with its available web tools and save a report against the displayed request ID. Use **Refresh research** to see newly saved reports.

Select skills from both the [eleven-skill catalog](WORKFLOW.md) and Director Studio's contracts. This stage uses `yt-viral` for public evidence and channel-relative comparison and `director-studio` for the selected production handoff. It does not require unrelated downstream skills yet. Required inputs are public video/channel identities, source URLs, capture dates, comparable formats and known or explicitly unknown metrics. Retained outputs include exact observations, actual fixed `swipe.py --min 2.0 --json` input/output, resource hashes, sampling limitations, shared structure and feasible original ideas. Each report also records selected-skill inputs, outputs and approval boundaries.

Agents use the shared operations documented in [Agent interface](../AGENT_INTERFACE.md):

1. `list_research_requests()` or `create_research_request(payload)`.
2. Read `get_research_request(research_id)` for exact request/latest report identity.
3. Research public sources in the active session, without login/credentials. Missing views are `null`. Do not invent values or describe supplied observations as independently verified measurements.
4. `save_research_report(research_id,payload)` stores evidence and runs the fixed local helper. Set `expected_report_id` to `null` for the first report, otherwise the exact latest report ID. Reports are append-only. Optional **Import report JSON** uses the same validated server path; invalid or oversized JSON produces an error without creating a report.

Report payload example (the listed identifiers and counts are **test fixtures**, not live research):

```json
{
  "expected_report_id": null,
  "sampling_note": "One public listing fixture, insufficient for comparison",
  "shared_pattern": "No supported shared pattern yet",
  "limitations": "Fixture only; missing views and too few comparable videos",
  "collected": [{
    "channel": "Garden Lab",
    "channel_url": "https://www.youtube.com/@gardenlab",
    "title": "Garden experiment",
    "url": "https://www.youtube.com/watch?v=video000000",
    "category": "gardening",
    "format": "short",
    "views": null,
    "duration": 24,
    "observed_at": "2026-11-08T12:00:00+00:00",
    "evidence_url": "https://www.youtube.com/@gardenlab/videos",
    "evidence_note": "Fixture, not an observed measurement"
  }],
  "ideas": [{
    "title": "A robot tries gardening",
    "original_angle": "A tiny robot learns to care for one stubborn seed",
    "source_urls": ["https://www.youtube.com/watch?v=video000000"],
    "feasibility": "One illustrated character and setting",
    "format": "short",
    "target_seconds": 24
  }]
}
```

At least four unique videos with known views in each channel/format group are required for a sample median. Shorts and long videos remain separate. Unknown metrics are excluded, and aliases of the same video cannot inflate support. An unranked report can mean insufficient evidence **or** enough comparable counts with no video clearing 2×. The UI shows support counts, explicit insufficient-data notes, up to five ranked outliers and the full exact report. Title formulas describe words in titles, not why a video succeeded. Shared structure and original feasible angles are authored by the researching agent. No result promises reach or revenue.

Inspect source links, capture dates, counts, limitations and proposed angles. **Choose this idea** asks the human director for audience, visual style and optional creator voice. **Create Flow project** pins the exact report, idea and resulting brief in one transaction, then opens the normal Studio at premise. It leaves all twelve diagram obligations, human review gates and separate spending approvals intact. It creates no scenes, approvals, generation jobs or allowance. Agents have no selection/approval tool.

Exact retry returns the same project; changing direction on a retry conflicts. Use **Open selected project** from the report history to resume. New reports do not rewrite earlier selections. A superseded report cannot create a new selection; changed helper/skill sources also prevent selection. Saved historical evidence remains inspectable. Research references and exact helper output remain in the project's Production handoff and exported `research.json`; ordinary artifact receipts remain separately downloadable.

The Research workspace is a completed local coordination path, not continuous monitoring, automated media production or publication. Google Flow film execution and the real-video acceptance gate remain required future work.
