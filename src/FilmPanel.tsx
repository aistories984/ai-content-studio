import React, { useEffect, useState } from "react";

type Json = Record<string, any>;
type Request = (path: string, method?: string, body?: unknown) => Promise<any>;

export function FilmPanel({ project, request }: { project: { id: string; revision: number }; request: Request }) {
  const projectId = project.id;
  const [state, setState] = useState<Json | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [cap, setCap] = useState("");
  const [note, setNote] = useState("");
  const [confirmed, setConfirmed] = useState(false);
  const path = `/projects/${projectId}/film`;
  useEffect(() => {
    let active = true;
    setState(null);
    setError("");
    request(path).then(s => { if (active) setState(s); }).catch(e => { if (active) setError(e.message); });
    return () => { active = false; };
  }, [project, request]);

  async function decide(route: string, body: Json, success: string) {
    setBusy(true); setError(""); setMessage("");
    try {
      await request(route, "POST", body);
      setState(await request(path));
      setMessage(success);
    } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  return <section className="panel film-panel" aria-label="Film packages and credit limits">
    <div className="panel-heading"><h3>Film packages and credit limits</h3></div>
    <div className="panel-body">
      <p>Review the exact film package and authorize spending separately. Saving a cap or allowance does not generate a video.</p>
      <p className="production-limit">Live Flow execution, original-download verification and final rendering are not connected.</p>
      {error && <p role="alert" className="alert error">{error}</p>}
      {message && <p role="status">{message}</p>}
      {!state ? <p>Loading film records…</p> : <>
        <p>Project cap: {state.budget.max_credits === null ? "not set" : `${state.budget.max_credits} credits`}</p>
        <p>Committed: {state.budget.committed_credits} credits · Remaining: {state.budget.remaining_credits ?? "not set"}</p>
        <p className="hint">Commitments include unresolved attempts and failures. A failed result does not automatically refund credits. This cap is separate from the planning budget in USD.</p>
        <form onSubmit={e => { e.preventDefault(); if (!confirmed) return; void decide(`${path}/budget`, { max_credits: Number(cap), note }, "Project credit cap saved."); setConfirmed(false); }}>
          <div className="form-row">
            <label className="field">Project credit cap<input type="number" min="0" max="100000" step="any" required value={cap} onChange={e => setCap(e.target.value)} /></label>
            <label className="field">Budget decision note<input required maxLength={10000} value={note} onChange={e => setNote(e.target.value)} /></label>
          </div>
          <label className="checkbox"><input type="checkbox" required checked={confirmed} onChange={e => setConfirmed(e.target.checked)} /><span>Confirm this project credit cap</span></label>
          <button className="button secondary" disabled={busy || !confirmed}>Save credit cap</button>
        </form>
        {state.packages.length === 0 && <p>No film package prepared. Approved story, comic, screenplay, audio, boards and Blender previs are required first.</p>}
        {state.packages.map((p: Json) => <PackageReview key={p.id} pack={p} state={state} busy={busy} decide={decide} />)}
        {state.attempts.length > 0 && <div className="film-attempts"><h4>Attempt history</h4>
          {state.attempts.map((a: Json) => <article key={a.id}>
            <p><strong>{a.status}</strong> · {a.committed_credits} credits committed · <code>{a.id}</code></p>
            <p>Reported cost: {a.observed_credits ?? "unknown"} · Original download verified: {a.local_download_verified ? "yes" : "no"}</p>
            <p className="hint">A result report is separate from verified downloaded media and your creative approval.</p>
            <details><summary>Observed result history</summary><pre>{JSON.stringify(a.history, null, 2)}</pre></details>
          </article>)}
        </div>}
        <details><summary>Current blockers and capability observations</summary>
          <ul>{state.blockers.map((b: string, i: number) => <li key={i}>{b}</li>)}</ul>
          {state.capabilities.map((c: Json) => <div key={c.id}><p><strong>{c.data.model}</strong> · Account: {c.data.account_ref}</p><p>Observed: {c.data.observed_at} · Expires: {c.data.expires_at}</p><p>{c.data.evidence}</p></div>)}
          <p>Recorded observations do not establish a connected browser session.</p>
        </details>
      </>}
    </div>
  </section>;
}

function PackageReview({ pack, state, busy, decide }: { pack: Json; state: Json; busy: boolean; decide: (path: string, body: Json, message: string) => Promise<void> }) {
  const [reviewNote, setReviewNote] = useState("");
  const [reviewed, setReviewed] = useState(false);
  const [attempts, setAttempts] = useState("");
  const [credits, setCredits] = useState("");
  const [expires, setExpires] = useState("");
  const [allowanceNote, setAllowanceNote] = useState("");
  const [upload, setUpload] = useState(false);
  const data = pack.data;
  const settings = data.settings;
  const decisions = state.decisions.filter((r: Json) => r.data.package_id === pack.id);
  const decision = decisions[decisions.length - 1]?.data.decision || "not reviewed";
  const allowances = state.allowances.filter((r: Json) => r.data.package_id === pack.id);
  const allowance = allowances[allowances.length - 1];
  const capability = state.capabilities.find((r: Json) => r.id === data.capability_id)?.data;
  const base = `/film/packages/${pack.id}`;
  return <article className="film-package" aria-label={`Film package ${pack.id}`}>
    <h4>Generation package</h4>
    <p><strong>{pack.current ? "Current inputs" : "Stale inputs"}</strong> · Package review: {decision}</p>
    <p>Account: {settings.account_ref} · Model: {settings.model} · Input mode: {settings.input_mode}</p>
    <p>{settings.duration} seconds · {settings.aspect_ratio} · {settings.outputs} output · Observed cost: {capability?.credit_cost ?? "unknown"} credits</p>
    <p className="hint">Audio and Blender previs remain approved planning sources. This record does not claim Flow ingests those files.</p>
    <label className="field">Exact approved prompt<textarea aria-label="Exact approved prompt" readOnly rows={4} value={data.prompt} /></label>
    <div className="film-references">{data.references.map((r: Json, i: number) => <figure key={`${r.version_id}-${r.file_index}-${i}`}>
      <img src={`/api/media/${r.version_id}/${r.file_index}`} alt={`Reference ${i + 1}: ${r.name}`} />
      <figcaption>{i + 1}. {r.name} · {r.role}</figcaption>
    </figure>)}</div>
    <details><summary>Exact source pins and package identity</summary><p><code>{pack.id}</code></p><p><code>{pack.hash}</code></p><pre>{JSON.stringify(data.sources, null, 2)}</pre></details>
    {pack.blockers.length > 0 && <ul>{pack.blockers.map((b: string, i: number) => <li key={i}>{b}</li>)}</ul>}
    <form onSubmit={e => { e.preventDefault(); if (!reviewed) return; void decide(`${base}/review`, { package_hash: pack.hash, expected_current: pack.current, decision: "approved", note: reviewNote }, "Exact package approved. Spending still requires a separate allowance."); setReviewed(false); }}>
      <label className="field">Package review note<input required value={reviewNote} onChange={e => setReviewNote(e.target.value)} /></label>
      <label className="checkbox"><input type="checkbox" required checked={reviewed} onChange={e => setReviewed(e.target.checked)} /><span>I reviewed this exact prompt, references and settings</span></label>
      <div className="film-actions">
        <button className="button secondary" disabled={busy || !pack.current || !reviewed}>Approve package</button>
        <button className="button secondary" type="button" disabled={busy || !reviewNote.trim()} onClick={() => void decide(`${base}/review`, { package_hash: pack.hash, expected_current: pack.current, decision: "rejected", note: reviewNote }, "Package rejected. New reservations are blocked.")}>Reject package</button>
      </div>
    </form>
    <details open={decision === "approved"}>
      <summary>Separate spending allowance</summary>
      {allowance && <p>Saved ceiling: {allowance.data.max_attempts} attempts · {allowance.data.max_credits} credits · Expires: {allowance.data.expires_at}</p>}
      <p className="hint">Ceilings include previous reservations for this scene across package revisions. A new allowance does not reset past spending.</p>
      <form onSubmit={e => { e.preventDefault(); if (!upload) return; void decide(`${base}/allowance`, { package_hash: pack.hash, upload_authorized: true, max_attempts: Number(attempts), max_credits: Number(credits), expires_at: new Date(expires).toISOString(), note: allowanceNote }, "Exact spending allowance saved. No generation was submitted."); setUpload(false); }}>
        <div className="form-row">
          <label className="field">Cumulative attempt ceiling<input type="number" required min="1" max="100" value={attempts} onChange={e => setAttempts(e.target.value)} /></label>
          <label className="field">Cumulative credit ceiling<input type="number" required min="0" max="100000" step="any" value={credits} onChange={e => setCredits(e.target.value)} /></label>
        </div>
        <label className="field">Allowance expiry<input type="datetime-local" required value={expires} onChange={e => setExpires(e.target.value)} /></label>
        <label className="field">Allowance decision note<input required value={allowanceNote} onChange={e => setAllowanceNote(e.target.value)} /></label>
        <label className="checkbox"><input type="checkbox" required checked={upload} onChange={e => setUpload(e.target.checked)} /><span>Authorize these exact references and settings within these limits</span></label>
        <button className="button secondary" disabled={busy || !pack.current || decision !== "approved" || !upload}>Approve spending allowance</button>
      </form>
    </details>
  </article>;
}
