# Google Flow film packages and credit decisions

The `comic-to-flow` workflow preserves the full Director Studio diagram. Local preparation/accounting works; the application still has no connected Flow film browser/execution or original-download verification adapter. A recorded capability is an operator observation, not a live connection. Real media production and final rendering remain separate unfinished work.

## Prepare and review

1. Complete the premise, ten-page comic, screenplay, measured audio, boards/clean references and Blender previs with current human-approved artifact versions. Read the Director Studio and applicable YouTube skills; retain their actual outputs and downstream links.
2. Claim the scene's `flow` task. Use `record_film_capability` to save the actual visible account label/model/input mode/duration/aspect/output count/cost, upload/download observations, evidence and expiry (at most 24 hours). Do not include credentials. This release supports one output per attempt and exact scene duration/aspect only; unsupported adaptations block.
3. `prepare_film_package` freezes the exact approved boards/previs prompt, settings and ordered approved still references. Mark clean images explicitly with reviewed `metadata.clean_reference_indices`. Ingredients cannot be mixed with first/last-frame inputs. Audio and Blender remain pinned planning assets, not claims Flow ingests them.
4. In **Film packages and credit limits**, the director sets the project credit cap, reviews the package prompt/references/settings, and approves the package separately from its spending allowance. The allowance binds the immutable package hash and authorizes exact reference uploads, cumulative scene attempt/credit ceilings and expiry. The USD planning budget does not authorize Flow credits.

The five new agent-safe HTTP/CLI/MCP operations are `record_film_capability(project_id,payload,task_id,token)`, `prepare_film_package(project_id,scene_id,payload,task_id,token)`, `get_film_state(project_id)`, `reserve_film_attempt(package_id,task_id,token)` and `record_film_result(attempt_id,payload,task_id,token)`. No budget, package-approval or allowance-approval tool is exposed to agents. See `studio/film.py` and `tests/test_film.py` for exact validated payload contracts.

## HTTP surface

Writes require the existing director-session token. The session boundary protects all local writes; human approval operations belong to the dashboard, never to a fabricated agent decision.

| Route | Body / operation |
| --- | --- |
| GET `/api/projects/{id}/film` | Read safe film records and blockers |
| POST `/api/projects/{id}/film/capabilities` | `{payload,task_id,token}` |
| POST `/api/projects/{id}/film/packages` | `{scene_id,payload,task_id,token}` |
| POST `/api/projects/{id}/film/budget` | Human `{max_credits,note}` |
| POST `/api/film/packages/{id}/review` | Human `{package_hash,expected_current,decision,note}` |
| POST `/api/film/packages/{id}/allowance` | Human `{package_hash,upload_authorized,max_attempts,max_credits,expires_at,note}` |
| POST `/api/film/packages/{id}/reserve` | `{task_id,token}`; records intent only |
| POST `/api/film/attempts/{id}/result` | `{payload,task_id,token}`; records observation only |

## Accounting and recovery

Reserve only immediately before an authorized action. The reservation atomically rechecks current pins/file hashes, capability and allowance expiry, live matching task, current package review and cumulative caps. An unresolved attempt blocks other reservations in its project and on the same account, including across projects. New package/capability/allowance versions do not reset scene spending history or the project cap.

Results append evidence to the same attempt: reserved → submitted/unknown/failed; submitted/unknown → observed/unknown/failed; observed → downloaded/unknown. Recovery may reconcile unknown to submitted. A new valid current project task may reconcile after revision/lease expiry, but does not gain permission to generate again. Original task identity is retained.

Commitment is the greater of reserved and observed credits. Failed attempts retain commitment; there is no automatic refund. Higher observed costs can exceed the approved cap and then block new reservations until an explicit human budget decision. Reported `downloaded` is not local file verification or creative approval. Terminal observations cannot be rewritten; exceptional corrections/refunds are not implemented.

Project ZIP exports include `film-production.json` with package/capability/decision/allowance/result history and budget totals alongside existing artifacts. Private task leases are not exported. This is an audit export, not an implemented database restore/import feature.

## Verified boundary

Offline tests use temporary WAV/MP4/image fixtures and placeholder Blender bytes, not a real production scene or provider acceptance. `scripts/check_film.cjs` verifies the exact package/references, separate review and allowance, unknown-result persistence and desktop/mobile layout without opening Google Flow. No live model, price or account availability is established by these fixtures.
