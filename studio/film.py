"""Offline Google Flow film packages and conservative, append-only credit accounting.

This service never connects a browser, uploads, generates, verifies a download or
approves media. Human decision methods must only be exposed by director routes.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import math
from typing import TypedDict

from .store import Problem, direction_hash, encode, ident, now, text


class Settings(TypedDict):
    account_ref: str
    model: str
    input_mode: str
    duration: float
    aspect_ratio: str
    outputs: int


class Reference(TypedDict):
    version_id: str
    file_index: int
    role: str


class CapabilityPayload(Settings):
    credit_cost: float
    upload_supported: bool
    download_supported: bool
    evidence: str
    expires_at: str


class PackagePayload(TypedDict):
    capability_id: str
    settings: Settings
    references: list[Reference]
    prompt: str


@dataclass(frozen=True)
class Record:
    """Immutable canonical JSON snapshot, copied on return to callers."""
    id: str
    data: str

    def export(self):
        return {'id': self.id, 'data': json.loads(self.data)}


TABLES = ('capabilities', 'packages', 'budgets', 'decisions', 'allowances', 'attempts', 'results')
SETTINGS = {'account_ref', 'model', 'input_mode', 'duration', 'aspect_ratio', 'outputs'}
UNRESOLVED = {'reserved', 'submitted', 'unknown', 'observed'}
TRANSITIONS = {
    'reserved': {'submitted', 'unknown', 'failed'},
    'submitted': {'observed', 'unknown', 'failed'},
    'unknown': {'submitted', 'observed', 'unknown', 'failed'},
    'observed': {'downloaded', 'unknown'},
    'failed': set(), 'downloaded': set(),
}


def initialize_schema(db):
    # Separate from old Wan/sprite state; repeated Store initialization is safe.
    for name in TABLES:
        table = 'film_' + name
        db.execute(f'CREATE TABLE IF NOT EXISTS {table}(id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id), data TEXT NOT NULL, created TEXT NOT NULL)')
        db.execute(f'CREATE INDEX IF NOT EXISTS {table}_project ON {table}(project_id)')
        for operation in ('UPDATE', 'DELETE'):
            db.execute(f"CREATE TRIGGER IF NOT EXISTS {table}_immutable_{operation.lower()} BEFORE {operation} ON {table} BEGIN SELECT RAISE(ABORT, 'Film records are immutable'); END")


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def digest(data):
    return hashlib.sha256(canonical(data).encode()).hexdigest()


def fields(payload, required, optional=()):
    if not isinstance(payload, dict) or set(payload) - set(required) - set(optional) or set(required) - set(payload):
        raise Problem('Unsupported or missing film fields.')


def number(value, name, low=0, high=100000, integer=False):
    try:
        valid = not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value) and low <= value <= high
    except OverflowError:
        valid = False
    if not valid or (integer and int(value) != value):
        raise Problem(f'{name} must be a finite number between {low} and {high}' + (' (whole number).' if integer else '.'))
    return int(value) if integer else float(value)


def expiry(value):
    raw = text(value, 'Expiry', 80, True)
    try:
        parsed = datetime.fromisoformat(raw.replace('Z', '+00:00'))
        if parsed.tzinfo is None:
            raise ValueError()
        seconds = (parsed - datetime.now(timezone.utc)).total_seconds()
    except (ValueError, OverflowError):
        raise Problem('Expiry must be an explicit timezone timestamp.')
    if not 0 < seconds <= 86400:
        raise Problem('Expiry must be in the next 24 hours.')
    return parsed.astimezone(timezone.utc).isoformat()


def expired(record):
    return datetime.fromisoformat(record['expires_at']) <= datetime.now(timezone.utc)


def settings(payload) -> Settings:
    fields(payload, SETTINGS)
    result = {key: text(payload[key], key, 200, True) for key in ('account_ref', 'model', 'input_mode', 'aspect_ratio')}
    result['duration'] = number(payload['duration'], 'Duration', .001, 86400)
    result['outputs'] = number(payload['outputs'], 'Outputs', 1, 1, True)
    return result


class FilmService:
    def __init__(self, store):
        self.store = store

    def _append(self, db, kind, project, data):
        record = Record(ident('film_' + kind.rstrip('s')), canonical(data))
        db.execute(f'INSERT INTO film_{kind} VALUES(?,?,?,?)', (record.id, project, record.data, now()))
        return record.export()

    def _records(self, db, kind, project):
        return [Record(r['id'], r['data']).export() for r in db.execute(f'SELECT * FROM film_{kind} WHERE project_id=? ORDER BY rowid', (project,))]

    def _record(self, db, kind, key):
        key = text(key, 'Record ID', 100, True)
        row = self.store.required(db, 'film_' + kind, key)
        return Record(row['id'], row['data']).export(), row['project_id']

    def _project(self, db, project):
        project = text(project, 'Project ID', 100, True)
        p = self.store._project(db, project)
        if p['workflow_id'] != 'comic-to-flow':
            raise Problem('Film state requires the Google Flow film workflow.', 409)
        return p

    def _claim(self, db, project, task_id, token, scene=None, recovery=False):
        project = text(project, 'Project ID', 100, True)
        task_id = text(task_id, 'Task ID', 100, True)
        token = text(token, 'Task token', 200, True)
        if scene is not None:
            scene = text(scene, 'Scene ID', 100, True)
        claim = self.store._check_claim(db, task_id, token, project)
        if recovery:
            if claim['scene_id'] not in (None, scene):
                raise Problem('Reconciliation requires a current claim in the attempt project and scene.', 409)
        elif claim['stage'] != 'flow' or (scene is not None and claim['scene_id'] != scene):
            raise Problem('A matching Flow scene task lease is required.', 409)
        return claim

    def record_capability(self, project_id, payload: CapabilityPayload, task_id, token):
        fields(payload, SETTINGS | {'credit_cost','upload_supported','download_supported','evidence','expires_at'})
        data = settings({k:payload[k] for k in SETTINGS})
        data.update(credit_cost=number(payload['credit_cost'], 'Observed credit cost'),
                    evidence=text(payload['evidence'], 'Evidence', 10000, True), expires_at=expiry(payload['expires_at']))
        for key in ('upload_supported','download_supported'):
            if payload[key] is not True:
                raise Problem('Usable observations require upload and download support.')
            data[key] = True
        data['observed_at'] = now()
        with self.store.db(True) as db:
            self._project(db, project_id)
            claim = self._claim(db, project_id, task_id, token)
            if claim['scene_id'] is None:
                raise Problem('A Flow scene claim is required.', 409)
            data['scene_id'] = claim['scene_id']
            return self._append(db,'capabilities',project_id,data)

    def _sources(self, db, project, scene_id):
        p = self._project(db, project)
        action = self.store._next(p, scene_id)
        if action['stage'] != 'flow' or action['state'] != 'ready':
            raise Problem('All upstream diagram stages must be approved and current before Flow preparation.', 409)
        scene = next(s for s in p['scenes'] if s['id'] == scene_id)
        sources, versions = [], {}
        for key in action['inputs']:
            artifact = next(a for a in p['artifacts'] if a['approved_version_id'] == key)
            version = next(v for v in artifact['versions'] if v['id'] == key)
            if version['stale'] or version['status'] != 'approved':
                raise Problem('A pinned source is stale or no longer approved.', 409)
            # Retain only explicit reviewed content in the hash; exclude review/lease
            # metadata and stored paths from the exported package.
            content = {k:version.get(k) for k in ('content','prompt','metadata','inputs','scene_revision','direction_hash')}
            safe_files = []
            for file in version['files']:
                path = (self.store.root / file['path']).resolve()
                if not path.is_relative_to(self.store.root / 'assets') or not path.is_file():
                    raise Problem('Pinned source file is missing.', 409)
                if hashlib.sha256(path.read_bytes()).hexdigest() != file['sha256']:
                    raise Problem('Pinned source file integrity changed.', 409)
                safe_files.append({k:file[k] for k in ('name','mime','size','sha256')})
            content['files'] = safe_files
            sources.append({'version_id':key, 'kind':artifact['kind'], 'stage':artifact['stage'], 'hash':digest(content), 'files':safe_files})
            versions[key] = version
        return p, scene, sources, versions

    def _package_data(self, db, project, scene_id, payload):
        fields(payload, {'capability_id','settings','references','prompt'})
        p, scene, sources, versions = self._sources(db, project, scene_id)
        cap, cap_project = self._record(db, 'capabilities', payload['capability_id'])
        c = cap['data']
        if cap_project != project or c['scene_id'] != scene_id or expired(c):
            raise Problem('Capability observation is expired or belongs to another scope.', 409)
        selected = settings(payload['settings'])
        if selected != {k:c[k] for k in SETTINGS}:
            raise Problem('Settings must exactly match the observed account/model/configuration.', 409)
        if selected['duration'] != scene['duration'] or selected['aspect_ratio'] != p['settings']['aspect_ratio']:
            raise Problem('Observed timing/aspect does not match the approved scene/project; reviewed adaptation is required.', 409)
        prompt = text(payload['prompt'], 'Exact prompt', 100000, True)
        if prompt != payload['prompt'] or prompt not in [v['prompt'] for key,v in versions.items() if any(s['version_id']==key and s['kind'] in ('storyboard','previs') for s in sources)]:
            raise Problem('Prompt must exactly equal the approved boards or previs prompt.', 409)
        refs = payload['references']
        if not isinstance(refs,list) or not 1 <= len(refs) <= 100:
            raise Problem('Supply ordered clean still references.')
        clean_refs, seen, roles = [], set(), []
        for ref in refs:
            fields(ref, {'version_id','file_index','role'})
            text(ref['version_id'], 'Reference version ID', 100, True)
            index = number(ref['file_index'],'File index',0,1000,True)
            role = ref['role']
            if role not in ('ingredient','first_frame','last_frame'):
                raise Problem('Unsupported reference role.')
            version = versions.get(ref['version_id'])
            if not version or index >= len(version['files']) or (ref['version_id'], index, role) in seen:
                raise Problem('References must be unique current pinned approved files.', 409)
            file = version['files'][index]
            indices = version['metadata'].get('clean_reference_indices', [])
            if not isinstance(indices,list) or any(type(i) is not int for i in indices) or index not in indices or file['mime'] not in ('image/png','image/jpeg','image/webp'):
                raise Problem('Reference requires explicitly reviewed clean_reference_indices and a clean still image.', 409)
            seen.add((ref['version_id'],index,role)); roles.append(role)
            clean_refs.append({'version_id':ref['version_id'], 'file_index':index, 'role':role, 'name':file['name'], 'sha256':file['sha256']})
        if selected['input_mode'] == 'ingredients':
            valid = all(r == 'ingredient' for r in roles)
        elif selected['input_mode'] == 'frames':
            valid = roles in (['first_frame'], ['first_frame','last_frame'])
        else:
            valid = False
        if not valid:
            raise Problem('Supported input modes are ingredients or frames with matching ordered roles.')
        return {'project_id':project, 'scene_id':scene_id, 'scene_revision':scene['revision'], 'direction_hash':direction_hash(p), 'capability_id':cap['id'], 'settings':selected, 'prompt':prompt, 'references':clean_refs, 'sources':sources}

    def _current(self, db, package):
        data = package['data']
        payload = {'capability_id':data['capability_id'], 'settings':data['settings'], 'prompt':data['prompt'], 'references':[{k:r[k] for k in ('version_id','file_index','role')} for r in data['references']]}
        try:
            current = self._package_data(db,data['project_id'],data['scene_id'],payload)
            if digest(current) != digest(data):
                return ['Pinned source versions, direction, settings or reviewed files changed.']
            return []
        except Problem as error:
            return [str(error)]

    def _export_package(self, db, package):
        blockers = self._current(db, package)
        return {**package, 'hash':digest(package['data']), 'current':not blockers, 'status':'stale' if blockers else 'prepared', 'blockers':blockers, 'no_external_action':True}

    def prepare_package(self, project_id, scene_id, payload: PackagePayload, task_id, token):
        with self.store.db(True) as db:
            self._claim(db,project_id,task_id,token,scene_id)
            data = self._package_data(db,project_id,scene_id,payload)
            return self._export_package(db,self._append(db,'packages',project_id,data))

    def _attempt(self, db, record):
        data = record['data']
        history = [r for r in self._records(db,'results',data['project_id']) if r['data']['attempt_id'] == record['id']]
        status, observed, provider = 'reserved', 0, None
        for result in history:
            status = result['data']['status']
            observed = max(observed,result['data'].get('observed_credits',0))
            provider = result['data'].get('provider_id',provider)
        return {**record, 'status':status, 'observed_credits':observed, 'committed_credits':max(data['reserved_credits'],observed), 'provider_id':provider, 'history':history, 'no_external_action':True, 'local_download_verified':False, 'creative_approved':False}

    def _attempts(self, db, project):
        return [self._attempt(db,r) for r in self._records(db,'attempts',project)]

    def _budget(self, db, project):
        history = self._records(db,'budgets',project)
        attempts = self._attempts(db,project)
        committed = sum(a['committed_credits'] for a in attempts)
        reserved = sum(a['committed_credits'] for a in attempts if a['status'] in UNRESOLVED)
        cap = history[-1]['data']['max_credits'] if history else None
        return {'max_credits':cap, 'committed_credits':committed, 'consumed_credits':committed-reserved, 'reserved_credits':reserved, 'observed_credits':sum(a['observed_credits'] for a in attempts), 'remaining_credits':max(0,cap-committed) if cap is not None else 0, 'history':history}

    def set_budget(self, project_id, payload):
        """Human-only audited project cap; route authorization is caller's duty."""
        fields(payload, {'max_credits','note'})
        data = {'max_credits':number(payload['max_credits'],'Project credit cap'), 'note':text(payload['note'],'Budget note',10000,True), 'decided_at':now()}
        with self.store.db(True) as db:
            self._project(db,project_id)
            if data['max_credits'] < self._budget(db,project_id)['committed_credits']:
                raise Problem('Project cap cannot fall below historical credit commitments.',409)
            self._append(db,'budgets',project_id,data)
            return self._budget(db,project_id)

    def review_package(self, package_id, payload):
        """Human-only exact package review; rejection also revokes spending."""
        fields(payload, {'package_hash','expected_current','decision','note'})
        if payload['decision'] not in ('approved','rejected') or type(payload['expected_current']) is not bool:
            raise Problem('Choose approved/rejected and the expected currentness.')
        with self.store.db(True) as db:
            package, project = self._record(db,'packages',package_id)
            current = not self._current(db,package)
            if payload['package_hash'] != digest(package['data']) or payload['expected_current'] != current:
                raise Problem('Package hash/currentness changed. Refresh before review.',409)
            if payload['decision'] == 'approved' and not current:
                raise Problem('Stale packages cannot be approved.',409)
            data = {'package_id':package_id,'package_hash':digest(package['data']), 'decision':payload['decision'], 'expected_current':current, 'note':text(payload['note'],'Review note',10000,payload['decision']=='rejected'), 'decided_at':now()}
            return self._append(db,'decisions',project,data)

    def _review(self, db, project, package_id):
        return next((r for r in reversed(self._records(db,'decisions',project)) if r['data']['package_id']==package_id),None)

    def approve_allowance(self, package_id, payload):
        """Human-only cumulative exact-scope allowance; this never reserves."""
        fields(payload, {'package_hash','upload_authorized','max_attempts','max_credits','expires_at','note'})
        if payload['upload_authorized'] is not True:
            raise Problem('Explicit upload authorization is required.')
        data = {'max_attempts':number(payload['max_attempts'],'Attempt ceiling',1,100,True), 'max_credits':number(payload['max_credits'],'Credit ceiling'), 'expires_at':expiry(payload['expires_at']), 'note':text(payload['note'],'Allowance note',10000,True), 'upload_authorized':True, 'decided_at':now()}
        with self.store.db(True) as db:
            package, project = self._record(db,'packages',package_id)
            review = self._review(db,project,package_id)
            if self._current(db,package) or not review or review['data']['decision'] != 'approved' or payload['package_hash'] != digest(package['data']):
                raise Problem('Allowance requires the exact current human-approved package.',409)
            if self._budget(db,project)['max_credits'] is None:
                raise Problem('Set a human project credit cap first.',409)
            data.update(package_id=package_id,package_hash=digest(package['data']),review_id=review['id'],settings=package['data']['settings'],scene_id=package['data']['scene_id'])
            return self._append(db,'allowances',project,data)

    def reserve_attempt(self, package_id, task_id, token):
        with self.store.db(True) as db:
            package, project = self._record(db,'packages',package_id)
            data = package['data']
            self._claim(db,project,task_id,token,data['scene_id'])
            blockers = self._current(db,package)
            if blockers:
                raise Problem(' '.join(blockers),409)
            review = self._review(db,project,package_id)
            allowance = next((r for r in reversed(self._records(db,'allowances',project)) if r['data']['package_id']==package_id),None)
            if not review or review['data']['decision'] != 'approved' or not allowance or allowance['data']['review_id'] != review['id'] or expired(allowance['data']):
                raise Problem('Current human package approval and unexpired allowance are required.',409)
            account = data['settings']['account_ref']
            # BEGIN IMMEDIATE serializes all competing account/project reservations.
            all_attempts = [self._attempt(db,Record(r['id'],r['data']).export()) for r in db.execute('SELECT * FROM film_attempts ORDER BY rowid')]
            if any(a['status'] in UNRESOLVED and (a['data']['project_id']==project or a['data']['settings']['account_ref']==account) for a in all_attempts):
                raise Problem('Unresolved project/account attempt must be reconciled before another reservation.',409)
            capability,_ = self._record(db,'capabilities',data['capability_id'])
            cost = capability['data']['credit_cost']
            package_hash = digest(data)
            # All revisions of a scene's package share its cumulative ceiling.
            # A fresh observation or package ID cannot erase spent attempts.
            previous = [a for a in all_attempts if a['data']['project_id']==project and a['data']['scene_id']==data['scene_id']]
            if len(previous)+1 > allowance['data']['max_attempts'] or sum(a['committed_credits'] for a in previous)+cost > allowance['data']['max_credits']:
                raise Problem('Cumulative package attempt/credit allowance exhausted.',409)
            budget = self._budget(db,project)
            if budget['max_credits'] is None or budget['committed_credits']+cost > budget['max_credits']:
                raise Problem('Project credit budget exhausted.',409)
            record = {'project_id':project,'scene_id':data['scene_id'],'package_id':package_id,'package_hash':package_hash,'capability_id':data['capability_id'],'review_id':review['id'],'allowance_id':allowance['id'],'settings':data['settings'],'task_id':task_id,'estimated_credits':cost,'reserved_credits':cost,'reserved_at':now()}
            return self._attempt(db,self._append(db,'attempts',project,record))

    def record_result(self, attempt_id, payload, task_id, token):
        fields(payload, {'status','evidence'}, {'observed_credits','provider_id'})
        status = text(payload['status'],'Observed state',30,True)
        evidence = text(payload['evidence'],'Result evidence',10000,True)
        with self.store.db(True) as db:
            initial, project = self._record(db,'attempts',attempt_id)
            self._claim(db,project,task_id,token,initial['data']['scene_id'],recovery=True)
            attempt = self._attempt(db,initial)
            if status not in TRANSITIONS[attempt['status']]:
                raise Problem(f"Invalid attempt transition: {attempt['status']} to {status}.",409)
            result = {'attempt_id':attempt_id,'status':status,'evidence':evidence,'reported_by_task_id':task_id,'observed_at':now()}
            if 'observed_credits' in payload:
                observed = number(payload['observed_credits'],'Observed credits',0,1e12)
                if observed < attempt['observed_credits']:
                    raise Problem('Observed credits cannot reduce historical commitments.',409)
                result['observed_credits'] = observed
            if 'provider_id' in payload:
                provider = text(payload['provider_id'],'Provider identity',200,True)
                if attempt['provider_id'] is not None and provider != attempt['provider_id']:
                    raise Problem('Provider identity is immutable once observed.',409)
                result['provider_id'] = provider
            self._append(db,'results',project,result)
            return self._attempt(db,initial)

    def get_state(self, project_id):
        with self.store.db() as db:
            self._project(db,project_id)
            packages = [self._export_package(db,p) for p in self._records(db,'packages',project_id)]
            attempts = self._attempts(db,project_id)
            budget = self._budget(db,project_id)
            blockers = ['Live browser, execution, download verification and render adapters are not connected.']
            if budget['max_credits'] is None:
                blockers.append('A human project credit budget is required.')
            elif budget['committed_credits'] > budget['max_credits']:
                blockers.append('Observed spending exceeds the project budget; an explicit human cap increase is required.')
            if any(a['status'] in UNRESOLVED for a in attempts):
                blockers.append('Unresolved project attempts require reconciliation before generation reservations.')
            accounts = {c['data']['account_ref'] for c in self._records(db,'capabilities',project_id)}
            for row in db.execute('SELECT * FROM film_attempts WHERE project_id<>?',(project_id,)):
                foreign = Record(row['id'],row['data']).export()
                if foreign['data']['settings']['account_ref'] in accounts and self._attempt(db,foreign)['status'] in UNRESOLVED:
                    blockers.append('An unresolved attempt on the same account in another project requires reconciliation.')
                    break
            return {'project_id':project_id,'capabilities':self._records(db,'capabilities',project_id),'packages':packages,'decisions':self._records(db,'decisions',project_id),'allowances':self._records(db,'allowances',project_id),'attempts':attempts,'budget':budget,'blockers':blockers,'automation':{'browser_connected':False,'generation_ready':False,'download_verification_ready':False,'render_ready':False}}
