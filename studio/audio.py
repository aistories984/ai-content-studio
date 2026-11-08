"""Shared local temporary-audio execution; never approves or spends credits."""
from __future__ import annotations

from contextlib import redirect_stdout
from dataclasses import dataclass, field
import hashlib
import io
import json
from pathlib import Path
import shutil
import threading

from scripts import scratch_audio as scratch, speech
from .media import inspect_media
from .store import EXTENSIONS, Problem, direction_hash, encode, text, workflow_for

# redirect_stdout is process-wide. Serialize the local renderer across callers.
_RENDER_LOCK = threading.Lock()


def get_speech_capabilities():
    """Read installed voices without synthesizing or selecting a voice."""
    return speech.get_speech_capabilities()


def _hash(path):
    path = Path(path)
    if not path.is_file() or path.stat().st_size > 200 * 1024 * 1024:
        raise Problem('Audio inputs must be existing files of at most 200 MB.')
    result = hashlib.sha256()
    with path.open('rb') as stream:
        while block := stream.read(1024 * 1024):
            result.update(block)
    return result.hexdigest()


@dataclass(frozen=True)
class PreparedAudio:
    """In-memory work ticket. Private lease arguments are never saved in jobs."""
    job_id: str
    project_id: str
    scene_id: str
    source_json: str
    snapshot: str
    inputs: tuple
    recordings: tuple
    recording_bindings: tuple
    target: tuple | None
    task_id: str | None = None
    token: str | None = field(default=None, repr=False)


class AudioService:
    def __init__(self, store):
        self.store = store

    def _context(self, db, project_id, scene_id, task_id=None, token=None):
        p = self.store._project(db, project_id)
        if workflow_for(p)['id'] == 'sprite-to-flow':
            raise Problem('Scratch dialogue belongs to a film project; use sprite extraction for this mode.')
        scene = next((s for s in p['scenes'] if s['id'] == scene_id), None)
        if not scene:
            raise Problem('Select a scene belonging to this film.')
        action = self.store._next(p, scene_id)
        if task_id is not None:
            claim = self.store._check_claim(db, task_id, token, project_id)
            if claim['stage'] != 'audio' or claim['scene_id'] != scene_id or action['stage'] != 'audio' or action['state'] != 'ready':
                raise Problem('A live matching ready audio-stage scene claim is required.', 409)
        elif not p['settings'].get('demo') and action['stage'] in ('premise', 'comic', 'script'):
            raise Problem('Approve the screenplay before generating temporary audio.', 409)
        sources, inputs = [], []
        for artifact in p['artifacts']:
            if artifact['stage'] not in ('premise', 'comic', 'script') or artifact['scene_id'] not in (None, scene_id):
                continue
            version = next((v for v in artifact['versions'] if v['id'] == artifact['approved_version_id']), None)
            if not version:
                continue
            if version['stale']:
                raise Problem('Approved screenplay inputs are stale; review current upstream work first.', 409)
            files = []
            for info in version['files']:
                path = (self.store.root / info['path']).resolve()
                if not path.is_relative_to(self.store.root / 'assets') or _hash(path) != info['sha256']:
                    raise Problem('Approved source file integrity changed.', 409)
                files.append((info['path'], info['sha256']))
            sources.append((artifact['stage'], artifact['id'], version['id'], version['hash'], files))
            inputs.append(version['id'])
        if not p['settings'].get('demo') and set(s[0] for s in sources) != {'premise', 'comic', 'script'}:
            raise Problem('Pin current approved premise, comic and screenplay before generating audio.', 409)
        generated = [a for a in p['artifacts'] if a['kind'] == 'audio' and a['stage'] == 'audio' and a['scene_id'] == scene_id
                     and any(v['metadata'].get('temporary_audio') for v in a['versions'])]
        if len(generated) > 1:
            raise Problem('Multiple generated temporary-audio artifacts need director reconciliation.', 409)
        target = (generated[0]['id'], generated[0]['latest']['id']) if generated else None
        snapshot = encode({'direction': direction_hash(p), 'scene': scene, 'sources': sorted(sources)})
        return snapshot, tuple(sorted(inputs)), target, scene

    def _source(self, source, scene, allow_recordings, token):
        try:
            raw = encode(source)
            if not isinstance(source, dict) or len(raw.encode('utf-8')) > 50000:
                raise ValueError('Provide a scratch audio source under 50 KB.')
            if token and token in raw:
                raise ValueError('Private task tokens must not appear in audio source.')
            # Copy through finite JSON: callers cannot mutate an already queued source.
            source = json.loads(raw)
            scratch.validate(source)
            text(source.get('title'), 'Audio title', 160, True)
            if not source['lines']:
                raise ValueError('Enter at least one actual screenplay dialogue line.')
            if source['target_duration'] != scene['duration']:
                raise ValueError('The source duration must match the selected scene package.')
            recordings, bindings, native = {}, [], []
            for line in source['lines']:
                if 'audio_file' in line:
                    if not allow_recordings:
                        raise ValueError('Use the local CLI to import existing recordings. The dashboard synthesizes plain text.')
                    if not isinstance(line['audio_file'], str) or not Path(line['audio_file']).is_absolute():
                        raise ValueError('Recording import paths must be explicit absolute files.')
                    path = Path(line['audio_file']).resolve()
                    if token and token in str(path):
                        raise ValueError('Private task tokens must not appear in recording paths.')
                    bindings.append((line['id'], line['audio_file'], str(path)))
                    digest = _hash(path)
                    speech._verify_pcm(path)
                    recordings[str(path)] = digest
                else:
                    native.append(source['characters'][line['character']])
            if native:
                capabilities = get_speech_capabilities()
                if not capabilities['available']:
                    raise ValueError('; '.join(capabilities['issues']))
                installed = {v['id'] for v in capabilities['voices']}
                for char in native:
                    if char['voice'] not in installed:
                        raise ValueError('Select an exact installed scratch voice or supply a PCM recording.')
                    if capabilities['platform'] == 'darwin' and char.get('rate', 0) != 0:
                        raise ValueError('macOS requires rate 0 (native default); use explicit rate_wpm for speed.')
                    if capabilities['platform'] == 'win32' and 'rate_wpm' in char:
                        raise ValueError('Windows uses rate from -10 to 10; rate_wpm is only supported on macOS.')
            return raw, tuple(sorted(recordings.items())), tuple(bindings)
        except (ValueError, KeyError, TypeError, OSError) as error:
            raise Problem(str(error)) from error

    def _prepare(self, project_id, scene_id, source, task_id=None, token=None):
        if task_id is not None and (not isinstance(task_id, str) or not task_id or not isinstance(token, str) or not token):
            raise Problem('A valid task ID and private lease token are required.', 409)
        with self.store.db() as db:
            snapshot, inputs, target, scene = self._context(db, project_id, scene_id, task_id, token)
        raw, recordings, bindings = self._source(source, scene, task_id is not None, token)
        # Recheck after voice discovery/import validation, before opening a job.
        with self.store.db() as db:
            current = self._context(db, project_id, scene_id, task_id, token)
            if (snapshot, inputs, target) != current[:3]:
                raise Problem('Audio sources changed during preparation. Refresh before rendering.', 409)
        job = self.store.create_job(project_id, 'scratch_audio', scene_id)
        return PreparedAudio(job, project_id, scene_id, raw, snapshot, inputs, recordings, bindings, target, task_id, token)

    def prepare_director(self, project_id, scene_id, source):
        """Validate and queue director work; execute asynchronously in the HTTP host."""
        return self._prepare(project_id, scene_id, source)

    def render_scratch_audio(self, project_id, scene_id, source, task_id, token):
        """Synchronously render under an existing audio lease; never finish the task."""
        if not isinstance(task_id, str) or not task_id or not isinstance(token, str) or not token:
            raise Problem('A valid task ID and private lease token are required.', 409)
        return self.execute(self._prepare(project_id, scene_id, source, task_id, token))

    def _guard(self, prepared, db, current_project=None, *, check_target=True, source_paths=(), file_hashes=()):
        current = self._context(db, prepared.project_id, prepared.scene_id, prepared.task_id, prepared.token)
        if prepared.snapshot != current[0] or prepared.inputs != current[1] or (check_target and prepared.target != current[2]):
            raise Problem('Scene, approved screenplay inputs or audio version changed during synthesis. Outputs are retained; refresh before rerendering.', 409)
        for path, digest in (*prepared.recordings, *file_hashes):
            if _hash(path) != digest:
                raise Problem('Supplied PCM recording changed during synthesis. Outputs are retained.', 409)
        for source_path, expected in source_paths:
            if source_path.read_text(encoding='utf-8') != expected:
                raise Problem('Audio source changed during synthesis. Outputs are retained.', 409)

    def _bind_recordings(self, prepared, folder):
        """Render verified copies, preserving the caller's paths as provenance only."""
        source = json.loads(prepared.source_json)
        copies, hashes, evidence = {}, [], []
        for index, (path, digest) in enumerate(prepared.recordings):
            captured = folder / 'recordings' / f'recording-{index:03}.wav'
            captured.parent.mkdir(exist_ok=True)
            shutil.copyfile(path, captured)
            if _hash(captured) != digest:
                raise Problem('Supplied PCM recording changed while importing. Outputs are retained.', 409)
            speech._verify_pcm(captured)
            captured.chmod(0o400)
            copies[path] = captured
            hashes.append((str(captured), digest))
        bindings = {line_id: (original, resolved) for line_id, original, resolved in prepared.recording_bindings}
        expected = dict(prepared.recordings)
        for line in source['lines']:
            if line['id'] in bindings:
                original, resolved = bindings[line['id']]
                line['audio_file'] = str(copies[resolved])
                evidence.append({'line_id': line['id'], 'original_path': original, 'resolved_path': resolved,
                                 'captured_path': copies[resolved].relative_to(folder).as_posix(), 'sha256': expected[resolved]})
        return encode(source), evidence, hashes

    def execute(self, prepared):
        """Execute the exact queued snapshot and atomically guard registration/review."""
        job = prepared.job_id
        folder = self.store.root / 'work' / job
        try:
            with _RENDER_LOCK:
                with self.store.db() as db:
                    self._guard(prepared, db)
                self.store.update_job(job, 'running', {'message': 'Synthesizing temporary dialogue locally'})
                folder.mkdir(parents=True, exist_ok=False)
                runtime_source, imports, recording_hashes = self._bind_recordings(prepared, folder)
                source_path = folder / 'source.json'
                source_path.write_text(runtime_source, encoding='utf-8')
                source_paths = [(source_path, runtime_source)]
                evidence_files = []
                if imports:
                    original_path = folder / 'original-source.json'
                    original_path.write_text(prepared.source_json, encoding='utf-8')
                    source_paths.append((original_path, prepared.source_json))
                    imports_path = folder / 'recording-imports.json'
                    imports_json = encode(imports)
                    imports_path.write_text(imports_json, encoding='utf-8')
                    source_paths.append((imports_path, imports_json))
                    evidence_files = [(p.name, p) for p in (original_path, imports_path)]
                    evidence_files += [(Path(p).relative_to(folder).as_posix(), Path(p)) for p, _ in recording_hashes]
                # Scratch CLI prints one result; agent CLI/MCP must keep clean stdout.
                with redirect_stdout(io.StringIO()):
                    output, report = scratch.render(source_path, folder)
                # The rendered line must also match the exact accepted recording,
                # even if an input copy was changed and restored around rendering.
                recording_hashes += [(str(output / 'lines' / (item['line_id'] + '.wav')), item['sha256']) for item in imports]
                source = json.loads(prepared.source_json)
                metadata = {**inspect_media(output / 'mix.wav'), 'timing_passed': report['timing_passed'], 'timing': report,
                            'temporary_audio': True, 'engine': report['engine'], 'recording_imports': imports,
                            'reference_map': '\n'.join(f"{key} → {v['color']} → {v['voice']}" for key, v in source['characters'].items())}
                # Preserve nested relationships in metadata even though Store flattens filenames.
                flow_project = workflow_for(self.store.project(prepared.project_id))['id'] == 'comic-to-flow'
                files = [('mix.wav', output / 'mix.wav')]
                files += [(p.relative_to(output).as_posix(), p) for p in sorted(output.rglob('*'))
                          if p.is_file() and p != output / 'mix.wav' and p.suffix.lower() in EXTENSIONS
                          and not (flow_project and p.name == 'wan-plan.json')]
                files += evidence_files
                metadata['bundle_file_map'] = [{'file_index': i, 'relative_path': name} for i, (name, _) in enumerate(files)]
                payload = {'title': source['title'], 'kind': 'audio', 'stage': 'audio', 'scene_id': prepared.scene_id,
                           'inputs': list(prepared.inputs), 'content': '\n\n'.join(f"{line['character']} · {line['start']:g}s\n{line['text']}" for line in source['lines']),
                           'prompt': source.get('generation_prompt', ''), 'metadata': metadata}
                if prepared.target:
                    payload.update(artifact_id=prepared.target[0], expected_version=prepared.target[1])
                if prepared.task_id:
                    payload.update(task_id=prepared.task_id, task_token=prepared.token)
                guard = lambda db, p: self._guard(prepared, db, p, source_paths=source_paths, file_hashes=recording_hashes)
                record = self.store.add_version(prepared.project_id, payload, files, actor='audio worker',
                                                enforce_gate=bool(prepared.task_id), guard=guard)
                if report['timing_passed']:
                    def submit_guard(db, p):
                        self._guard(prepared, db, p, check_target=False, source_paths=source_paths, file_hashes=recording_hashes)
                        artifact = next(a for a in p['artifacts'] if a['id'] == record['artifact_id'])
                        if artifact['latest']['id'] != record['version_id']:
                            raise Problem('A newer audio version exists. Refresh before submitting.', 409)
                    self.store.submit(record['version_id'], 'audio worker', guard=submit_guard)
                result = {**record, 'job_id': job, 'timing_passed': report['timing_passed'], 'actual_duration': report['actual_duration'],
                          'duration': report['actual_duration'], 'issues': report['issues'], 'output': str(output), 'human_review_required': True}
                self.store.update_job(job, 'completed' if report['timing_passed'] else 'needs_changes', result)
                return result
        except Exception as error:
            message = str(error)[:2000]
            if prepared.token:
                message = message.replace(prepared.token, '[private token]')
            self.store.update_job(job, 'failed', {'message': message, 'outputs_preserved': True, 'output': str(folder)})
            raise Problem(message, getattr(error, 'status', 400)) from error
