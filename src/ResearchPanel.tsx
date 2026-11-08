import React, { useEffect, useRef, useState } from "react";

type Json = Record<string, any>;
type Api = <T = any>(
  path: string,
  method?: string,
  body?: unknown,
) => Promise<T>;

export function ResearchReport({ report }: { report: Json }) {
  const evidence = report.evidence;
  return (
    <div className="research-report">
      <p>
        <strong>
          {evidence.status === "ranked"
            ? "Ranked channel-sample outliers"
            : "Unranked — no collected video cleared 2× its channel-sample median"}
        </strong>
      </p>
      <p>{report.sampling_note}</p>
      <p>
        <strong>Shared structure:</strong> {report.shared_pattern}
      </p>
      <p>
        <strong>Limitations:</strong> {report.limitations}
      </p>
      <p className="hint">{evidence.formula_note}</p>
      {evidence.insufficient_data.map((note: string, i: number) => (
        <p key={i} className="research-note">
          {note}
        </p>
      ))}
      <ul aria-label="Sample support">
        {evidence.groups.map((g: Json) => (
          <li key={g.group}>
            {g.channel} · {g.format} · {g.known_views} known counts /{" "}
            {g.collected} collected
          </li>
        ))}
      </ul>
      {evidence.outliers.length > 0 && (
        <ol aria-label="Channel-relative outliers">
          {evidence.outliers.slice(0, 5).map((row: Json) => (
            <li key={row.url}>
              <a href={row.url} target="_blank" rel="noreferrer">
                {row.title}
              </a>{" "}
              · <strong>{row.multiple}×</strong> · {row.views.toLocaleString()}{" "}
              views / {row.median.toLocaleString()} sample median · Title
              formula: {row.formula}
            </li>
          ))}
        </ol>
      )}
      <details open>
        <summary>
          Sources and captured metrics ({report.collected.length})
        </summary>
        <div className="research-sources">
          {report.collected.map((row: Json) => (
            <article key={row.url}>
              <a href={row.url} target="_blank" rel="noreferrer">
                {row.title}
              </a>
              <p>
                <a href={row.channel_url} target="_blank" rel="noreferrer">
                  {row.channel}
                </a>{" "}
                · {row.category} · {row.format}
              </p>
              <p>
                Views:{" "}
                {row.views === null ? (
                  <span>Unknown</span>
                ) : (
                  row.views.toLocaleString()
                )}{" "}
                · Duration:{" "}
                {row.duration === null ? "Unknown" : `${row.duration}s`}
              </p>
              <p>
                Captured:{" "}
                <time dateTime={row.observed_at}>{row.observed_at}</time>
                {row.published_at && <> · Published: {row.published_at}</>}
              </p>
              <a href={row.evidence_url} target="_blank" rel="noreferrer">
                Measurement source
              </a>
              <p>{row.evidence_note}</p>
            </article>
          ))}
        </div>
      </details>
      <details>
        <summary>Exact saved report and helper output</summary>
        <p>
          Report {report.id} · SHA-256 {report.sha256}
        </p>
        <pre>{JSON.stringify(report, null, 2)}</pre>
      </details>
      <p className="hint">{evidence.gate_line}</p>
    </div>
  );
}

function Idea({
  idea,
  report,
  request,
  busy,
  select,
  open,
}: {
  idea: Json;
  report: Json;
  request: Json;
  busy: boolean;
  select: (idea: Json, payload: Json) => Promise<void>;
  open: (id: string) => Promise<void>;
}) {
  const [choosing, setChoosing] = useState(false);
  const selection = request.selections.find(
    (s: Json) => s.report_id === report.id && s.idea_id === idea.id,
  );
  return (
    <article className="research-idea">
      <h3>{idea.title}</h3>
      <p>{idea.original_angle}</p>
      <p>
        <strong>Feasibility this week:</strong> {idea.feasibility}
      </p>
      <p>
        {idea.format} · {idea.target_seconds}s
        {idea.audience ? ` · Suggested audience: ${idea.audience}` : ""}
      </p>
      <ul aria-label="Idea sources">
        {idea.source_urls.map((url: string) => (
          <li key={url}>
            <a href={url} target="_blank" rel="noreferrer">
              {url}
            </a>
          </li>
        ))}
      </ul>
      {selection ? (
        <button
          className="button primary"
          disabled={busy}
          onClick={() => open(selection.project_id)}
        >
          Open selected project
        </button>
      ) : (
        <>
          <button
            className="button"
            disabled={
              busy || !report.is_current || request.reports[0].id !== report.id
            }
            onClick={() => setChoosing(!choosing)}
          >
            Choose this idea
          </button>
          {choosing && (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const data = new FormData(e.currentTarget);
                const voice = String(data.get("creator_voice")).trim();
                void select(idea, {
                  audience: String(data.get("audience")).trim(),
                  style: String(data.get("style")).trim(),
                  ...(voice ? { creator_voice: voice } : {}),
                });
              }}
            >
              <p>
                Set this project's direction. All twelve production obligations
                and human review gates remain; generation requires a separate
                reviewed package and allowance.
              </p>
              <label>
                Audience
                <input
                  name="audience"
                  required
                  maxLength={2000}
                  defaultValue={idea.audience || ""}
                />
              </label>
              <label>
                Visual style
                <input name="style" required maxLength={2000} />
              </label>
              <label>
                Creator voice
                <input name="creator_voice" maxLength={2000} />
              </label>
              <button className="button primary" disabled={busy}>
                Create Flow project
              </button>
            </form>
          )}
        </>
      )}
    </article>
  );
}

export function ResearchPanel({
  api,
  onOpen,
}: {
  api: Api;
  onOpen: (id: string) => Promise<void>;
}) {
  const [requests, setRequests] = useState<Json[]>([]);
  const [selected, setSelected] = useState("");
  const [reportId, setReportId] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [json, setJson] = useState("");
  const epoch = useRef(0);
  const mounted = useRef(true);
  const request = requests.find((r) => r.id === selected);
  const report =
    request?.reports.find((r: Json) => r.id === reportId) ||
    request?.reports[0];
  async function refresh() {
    const current = ++epoch.current;
    setLoading(true);
    setError("");
    try {
      const list = await api<Json[]>("/research");
      if (mounted.current && current === epoch.current) {
        setRequests(list);
        setSelected((old) =>
          list.some((r) => r.id === old) ? old : list[0]?.id || "",
        );
      }
    } catch (e) {
      if (mounted.current && current === epoch.current) setError(String(e));
    } finally {
      if (mounted.current && current === epoch.current) setLoading(false);
    }
  }
  useEffect(() => {
    mounted.current = true;
    void refresh();
    return () => {
      mounted.current = false;
      epoch.current++;
    };
  }, []);
  async function run(fn: () => Promise<void>) {
    // A mutation supersedes any list snapshot captured before it started.
    epoch.current++;
    setLoading(false);
    setBusy(true);
    setError("");
    try {
      await fn();
    } catch (e) {
      if (mounted.current) setError(e instanceof Error ? e.message : String(e));
    } finally {
      if (mounted.current) setBusy(false);
    }
  }
  function update(saved: Json) {
    if (mounted.current) {
      setRequests((old) => [saved, ...old.filter((r) => r.id !== saved.id)]);
      setSelected(saved.id);
      setReportId("");
    }
  }
  return (
    <section className="research-panel" aria-label="Research workspace">
      <div className="panel research-intro">
        <h2>From public research to an original idea</h2>
        <p>
          Save a question, then ask an active agent session to research public
          sources and save a report. This dashboard stores requests and reports;
          it does not run background research or monitor trends.
        </p>
        <p className="hint">
          Broad categories are welcome. Supplied observations need sources and
          capture dates. Reach and revenue are objectives, never promises.
        </p>
        <button
          className="button"
          disabled={busy || loading}
          onClick={() => {
            setReportId("");
            void refresh();
          }}
        >
          Refresh research
        </button>
      </div>
      {error && (
        <p className="alert error" role="alert">
          {error}
        </p>
      )}
      <div className="research-layout">
        <div className="research-sidebar">
          <form
            className="panel"
            onSubmit={(e) => {
              e.preventDefault();
              const form = e.currentTarget;
              const values = new FormData(form);
              void run(async () => {
                const saved = await api("/research", "POST", {
                  query: String(values.get("query")).trim(),
                  categories: String(values.get("categories"))
                    .split(",")
                    .map((v) => v.trim())
                    .filter(Boolean),
                  language: String(values.get("language")).trim(),
                  time_window: String(values.get("time_window")).trim(),
                });
                update(saved);
                form.reset();
              });
            }}
          >
            <h3>New research request</h3>
            <label>
              Research question
              <textarea
                name="query"
                required
                maxLength={2000}
                placeholder="Explore original story opportunities across niches"
              />
            </label>
            <label>
              Categories (optional, comma separated)
              <input name="categories" maxLength={2000} />
            </label>
            <label>
              Language
              <input
                name="language"
                required
                maxLength={80}
                defaultValue="English"
              />
            </label>
            <label>
              Time window
              <input
                name="time_window"
                required
                maxLength={2000}
                defaultValue="past month"
              />
            </label>
            <button className="button primary" disabled={busy || loading}>
              Save research request
            </button>
          </form>
          <div className="panel">
            <h3>Request history</h3>
            {loading && <p role="status">Loading saved research…</p>}
            {!loading && requests.length === 0 && <p>No saved requests yet.</p>}
            <ul className="research-history">
              {requests.map((r) => (
                <li key={r.id}>
                  <button
                    className={selected === r.id ? "active" : ""}
                    aria-pressed={selected === r.id}
                    disabled={busy}
                    onClick={() => {
                      setSelected(r.id);
                      setReportId("");
                      setJson("");
                      setError("");
                    }}
                  >
                    {r.query}
                  </button>
                  <small>
                    {r.reports.length
                      ? `${r.reports.length} saved report(s)`
                      : "Pending report"}{" "}
                    · {r.created}
                  </small>
                </li>
              ))}
            </ul>
          </div>
        </div>
        {request && (
          <div className="panel research-detail" key={request.id}>
            <h2>{request.query}</h2>
            <p>
              {request.categories.join(", ") || "Broad discovery"} ·{" "}
              {request.language} · {request.time_window}
            </p>
            <p className="hint">
              Request ID: <code>{request.id}</code> — give this to the active
              agent session using the shared Studio data directory.
            </p>
            {!report && <p>Pending report</p>}
            <details>
              <summary>Import report JSON</summary>
              <p>
                Optional operator import of an agent-authored report. Include
                expected_report_id ({request.reports[0]?.id || "null"} for the
                first report), source observations and original ideas. The
                server validates data and runs the fixed yt-viral helper; it
                does not fetch or verify measurements.
              </p>
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  void run(async () => {
                    if (new Blob([json]).size > 1_000_000)
                      throw new Error("Report JSON exceeds 1 MB.");
                    let payload;
                    try {
                      payload = JSON.parse(json);
                    } catch {
                      throw new Error("Report JSON is not valid JSON.");
                    }
                    if (
                      !payload ||
                      typeof payload !== "object" ||
                      Array.isArray(payload)
                    )
                      throw new Error("Report JSON must be an object.");
                    update(
                      await api(
                        `/research/${request.id}/reports`,
                        "POST",
                        payload,
                      ),
                    );
                    setJson("");
                  });
                }}
              >
                <label>
                  Report JSON
                  <textarea
                    value={json}
                    onChange={(e) => setJson(e.target.value)}
                    maxLength={1_000_001}
                    required
                    rows={7}
                  />
                </label>
                <button className="button" disabled={busy}>
                  Save report
                </button>
              </form>
            </details>
            {report && (
              <>
                <label>
                  Saved report
                  <select
                aria-label="Saved report"
                    value={report.id}
                    disabled={busy}
                    onChange={(e) => {
                      setReportId(e.target.value);
                      setError("");
                    }}
                  >
                    {request.reports.map((r: Json, i: number) => (
                      <option key={r.id} value={r.id}>
                        {r.created} · {i === 0 ? "Latest" : "Historical"} ·{" "}
                        {r.id}
                      </option>
                    ))}
                  </select>
                </label>
                <p>
                  {report.is_current
                    ? "Helper and skill sources current"
                    : "Historical helper or skill sources — new selection unavailable"}
                  {report.id !== request.reports[0].id
                    ? " · Superseded report — earlier project selections remain pinned"
                    : ""}
                </p>
                <ResearchReport report={report} />
                <h2>Original ideas</h2>
                {report.ideas.length === 0 && (
                  <p>No original ideas supplied in this report.</p>
                )}
                {report.ideas.map((idea: Json) => (
                  <Idea
                    key={`${report.id}/${idea.id}`}
                    idea={idea}
                    report={report}
                    request={request}
                    busy={busy}
                    open={(id) => run(() => onOpen(id))}
                    select={(chosen, payload) =>
                      run(async () => {
                        const project = await api(
                          `/research/${request.id}/select`,
                          "POST",
                          { report_id: report.id, idea_id: chosen.id, payload },
                        );
                        await onOpen(project.id);
                      })
                    }
                  />
                ))}
              </>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
