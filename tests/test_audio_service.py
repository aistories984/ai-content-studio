"""Real PCM orchestration, immutable evidence and lease/race boundaries."""
from concurrent.futures import ThreadPoolExecutor
from contextlib import redirect_stdout
from copy import deepcopy
import importlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from scripts import scratch_audio as scratch
from studio import agent_tools
from studio.store import Problem, ROOT, Store

try:
    from studio.audio import AudioService
except ImportError:
    AudioService = None


class AudioServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.store = Store(self.folder / 'data')
        self.project = self.store.create_project({'title': 'Isolated audio test', 'workflow_id': 'comic-to-flow', 'topic': 'Test narration', 'audience': 'Test adults', 'format': 'short', 'target_seconds': 4, 'style': 'Illustrated'})['id']
        self.scene = self.store.save_scene(self.project, {'title': 'Test scene', 'duration': 4})
        self.inputs = []
        self.upstream = []
        for stage in ('premise', 'comic', 'script'):
            files = [(f'page{i}.png', b'isolated fixture image') for i in range(10)] if stage == 'comic' else []
            saved = self.store.add_version(self.project, {'title': stage, 'stage': stage, 'kind': stage,
                       'content': 'A test narrator speaks.', 'inputs': list(self.inputs)}, files)
            self.store.review(saved['version_id'], 'approved')
            self.inputs.append(saved['version_id'])
            self.upstream.append(saved)
        self.claim = self.store.claim(self.project, 'Audio test', self.scene)
        self.recording = self.folder / 'take.wav'
        scratch.write_wave(self.recording, [3000, -3000] * 24000)
        self.source = {'schema_version': 1, 'sequence_id': 'TEST', 'title': 'Temporary audio', 'revision': 'test',
              'target_duration': 4, 'fps': 30, 'characters': {'A': {'name': 'Narrator', 'voice': 'Recorded take', 'color': '#64b5ff'}},
              'shots': [{'id': 'SHOT', 'start': 0, 'end': 4}], 'jobs': [{'id': 'JOB', 'start': 0, 'end': 4}],
              'lines': [{'id': 'LINE', 'character': 'A', 'start': 1, 'slot_end': 3, 'text': 'A test narrator speaks.', 'audio_file': str(self.recording)}], 'actions': []}
        self.assertIsNotNone(AudioService, 'Shared guarded AudioService is missing')
        self.service = AudioService(self.store)

    def render(self, **kw):
        return self.service.render_scratch_audio(self.project, self.scene, kw.pop('source', self.source),
                    kw.pop('task_id', self.claim['task_id']), kw.pop('token', self.claim['token']))

    def audio_versions(self):
        return [v for a in self.store.project(self.project)['artifacts'] if a['kind'] == 'audio' for v in a['versions']]

    def job(self):
        return self.store.project(self.project)['jobs'][0]

    def assert_failed_retained(self):
        self.assertEqual(self.job()['status'], 'failed')
        self.assertFalse(self.audio_versions())
        self.assertTrue(list((self.store.root / 'work').rglob('mix.wav')))

    def test_recorded_agent_render_is_measured_immutable_and_only_submitted(self):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            result = self.render()
        self.assertEqual(stdout.getvalue(), '')
        self.assertTrue(result['timing_passed'])
        self.assertEqual(result['actual_duration'], 4)
        self.assertEqual(self.job()['status'], 'completed')
        saved = self.store.get_version(result['version_id'])['version']
        self.assertEqual(saved['status'], 'in_review')
        self.assertEqual(saved['metadata']['timing']['lines'][0]['duration'], 1)
        self.assertEqual(saved['metadata']['engine'], 'supplied PCM recordings')
        self.assertEqual(set(saved['inputs']), set(self.inputs))
        names = {f['name'] for f in saved['files']}
        self.assertTrue({'mix.wav', 'A.wav', 'timing.json', 'dialogue.srt', 'cue-sheet.csv', 'source.json'} <= names)
        self.assertTrue(all(self.store.file_path(result['version_id'], i)[0].is_file() for i in range(len(saved['files']))))
        self.assertEqual(self.store.project(self.project)['tasks'][0]['status'], 'claimed')
        self.assertEqual(saved['reviews'], [])
        self.assertNotIn(self.claim['token'], json.dumps(self.store.project(self.project)))
        self.assertNotIn(self.claim['token'], ''.join(p.read_text() for p in (self.store.root / 'work').rglob('*.json')))

    def test_overrun_retains_full_output_and_revision_reuses_artifact(self):
        self.source['lines'][0].update(start=3.5, slot_end=4)
        first = self.render()
        self.assertFalse(first['timing_passed'])
        self.assertEqual(first['actual_duration'], 4.5)
        self.assertEqual(self.job()['status'], 'needs_changes')
        self.assertEqual(self.store.get_version(first['version_id'])['version']['status'], 'draft')
        self.source['lines'][0].update(start=1, slot_end=3)
        second = self.render()
        self.assertEqual(first['artifact_id'], second['artifact_id'])
        self.assertEqual(second['number'], 2)
        self.assertTrue(self.store.get_version(first['version_id'])['version']['files'])
        self.assertTrue(second['timing_passed'])

    def test_wrong_token_expired_and_wrong_scene_claim_never_start_job(self):
        for bad in ('wrong', ''):
            with self.assertRaises(Problem):
                self.render(token=bad)
        other = self.store.save_scene(self.project, {'title': 'Other', 'duration': 4})
        claim = self.store.claim(self.project, 'Other audio', other)
        with self.assertRaises(Problem):
            self.render(task_id=claim['task_id'], token=claim['token'])
        with self.store.db(True) as db:
            db.execute('UPDATE tasks SET expires=? WHERE id=?', (time.time()-1, self.claim['task_id']))
        with self.assertRaises(Problem):
            self.render()
        self.assertEqual(self.store.project(self.project)['jobs'], [])

    def test_missing_wrong_stage_and_sprite_workflows_reject(self):
        for workflow in ('comic-to-flow', 'sprite-to-flow'):
            project = self.store.create_project({'title': 'Premature', 'workflow_id': workflow, 'topic': 'Test narration', 'audience': 'Test adults', 'format': 'short', 'target_seconds': 4, 'style': 'Illustrated'})['id']
            scene = self.store.save_scene(project, {'title': 'Plan', 'duration': 4})
            claim = self.store.claim(project, 'Wrong stage')
            with self.assertRaises(Problem):
                self.service.render_scratch_audio(project, scene, self.source, claim['task_id'], claim['token'])
            self.assertEqual(self.store.project(project)['jobs'], [])

    def test_relative_recording_empty_lines_nonfinite_duration_and_secret_source_reject(self):
        variants = []
        for value in ('take.wav', '', None):
            source = deepcopy(self.source)
            source['lines'][0]['audio_file'] = value
            variants.append(source)
        source = deepcopy(self.source); source['lines'] = []; variants.append(source)
        source = deepcopy(self.source); source['target_duration'] = 5; variants.append(source)
        source = deepcopy(self.source); source['fps'] = float('nan'); variants.append(source)
        source = deepcopy(self.source); source['title'] = self.claim['token']; variants.append(source)
        for source in variants:
            with self.subTest(source=source), self.assertRaises(Problem):
                self.render(source=source)
        self.assertEqual(self.store.project(self.project)['jobs'], [])

    def native(self):
        source = deepcopy(self.source)
        source['lines'][0].pop('audio_file')
        source['characters']['A']['voice'] = 'Test Voice (US)'
        return source

    def prepare_native(self):
        with patch('scripts.speech.subprocess.run', side_effect=self.native_process()):
            return self.service.prepare_director(self.project, self.scene, self.native())

    def native_process(self, change=None, empty=False):
        def run(argv, **kwargs):
            if argv[-1] == '?':
                return subprocess.CompletedProcess(argv, 0, 'Test Voice (US) en_US # Voice inventory\n', '')
            if change:
                change()
            output = Path(argv[argv.index('-o') + 1])
            scratch.write_wave(output, [] if empty else [3000, -3000] * 24000)
            return subprocess.CompletedProcess(argv, 0, '', '')
        return run

    def test_unknown_voice_and_unsupported_platform_are_rejected_before_job(self):
        source = self.native()
        with patch('scripts.speech.sys.platform', 'linux'):
            with self.assertRaises(Problem):
                self.render(source=source)
        source['characters']['A']['voice'] = 'Unavailable'
        with patch('scripts.speech.subprocess.run', side_effect=self.native_process()):
            with self.assertRaises(Problem):
                self.render(source=source)
        self.assertEqual(self.store.project(self.project)['jobs'], [])

    def test_empty_native_exit_zero_creates_failed_job_without_artifact(self):
        with patch('scripts.speech.subprocess.run', side_effect=self.native_process(empty=True)):
            with self.assertRaises(Problem):
                self.render(source=self.native())
        self.assertEqual(self.job()['status'], 'failed')
        self.assertFalse(self.audio_versions())
        self.assertTrue(list((self.store.root / 'work').rglob('LINE.wav')))

    def test_changed_direction_during_generation_retains_output_without_registration(self):
        def change():
            p = self.store.project(self.project)
            self.store.update_project(self.project, {'expected_revision': p['revision'], 'brief': 'Changed direction'})
        with patch('scripts.speech.subprocess.run', side_effect=self.native_process(change)):
            with self.assertRaises(Problem):
                self.render(source=self.native())
        self.assert_failed_retained()

    def test_changed_scene_during_generation_retains_output_without_registration(self):
        def change():
            self.store.save_scene(self.project, {'title': 'Changed', 'duration': 4, 'expected_revision': 1}, self.scene)
        with patch('scripts.speech.subprocess.run', side_effect=self.native_process(change)):
            with self.assertRaises(Problem):
                self.render(source=self.native())
        self.assert_failed_retained()

    def test_new_approved_script_during_generation_blocks_director_too(self):
        pending = self.prepare_native()
        def change():
            saved = self.store.add_version(self.project, {'title': 'script', 'kind': 'script', 'stage': 'script',
                'artifact_id': self.upstream[-1]['artifact_id'], 'expected_version': self.upstream[-1]['version_id'],
                'content': 'Changed words.', 'inputs': self.inputs[:2]})
            self.store.review(saved['version_id'], 'approved')
        with patch('scripts.speech.subprocess.run', side_effect=self.native_process(change)):
            with self.assertRaises(Problem):
                self.service.execute(pending)
        self.assert_failed_retained()

    def test_changed_approved_file_hash_blocks_even_without_version_change(self):
        path, _ = self.store.file_path(self.inputs[1], 0)
        pending = self.prepare_native()
        with patch('scripts.speech.subprocess.run', side_effect=self.native_process(lambda: path.write_bytes(b'changed source'))):
            with self.assertRaises(Problem):
                self.service.execute(pending)
        self.assert_failed_retained()

    def test_expired_claim_during_generation_cannot_register(self):
        def expire():
            with self.store.db(True) as db:
                db.execute('UPDATE tasks SET expires=0 WHERE id=?', (self.claim['task_id'],))
        with patch('scripts.speech.subprocess.run', side_effect=self.native_process(expire)):
            with self.assertRaises(Problem):
                self.render(source=self.native())
        self.assert_failed_retained()

    def test_changed_explicit_recording_is_detected_after_render(self):
        # Real rendering runs; mutation occurs at media inspection, after mix generation.
        from studio.media import inspect_media
        def inspect(path):
            result = inspect_media(path)
            scratch.write_wave(self.recording, [5000, -5000] * 24000)
            return result
        with patch('studio.audio.inspect_media', side_effect=inspect):
            with self.assertRaises(Problem):
                self.render()
        self.assert_failed_retained()

    def test_concurrent_jobs_have_one_winner_and_queued_stale_work_fails(self):
        with patch('scripts.speech.subprocess.run', side_effect=self.native_process()):
            def prepare(_):
                try:
                    return self.service.prepare_director(self.project, self.scene, self.native())
                except Problem:
                    return None
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(prepare, range(2)))
            self.assertEqual(sum(r is not None for r in results), 1)
            pending = next(r for r in results if r)
            self.store.update_project(self.project, {'expected_revision': 1, 'brief': 'Changed while queued'})
            with self.assertRaises(Problem):
                self.service.execute(pending)
        self.assertEqual(self.job()['status'], 'failed')
        self.assertFalse(self.audio_versions())

    def test_director_target_conflict_cannot_overwrite_newer_audio(self):
        self.source['lines'][0].update(start=3.5, slot_end=4)
        first = self.render()
        pending = self.prepare_native()
        self.store.add_version(self.project, {'artifact_id': first['artifact_id'], 'expected_version': first['version_id'],
                    'title': 'Audio', 'kind': 'audio', 'stage': 'audio', 'content': 'Newer director edit', 'inputs': self.inputs})
        with self.assertRaises(Problem):
            self.service.execute(pending)
        self.assertEqual(len(self.audio_versions()), 2)
        self.assertEqual(self.job()['status'], 'failed')

    def test_symlink_retarget_before_real_render_uses_verified_recording_copy(self):
        other = self.folder / 'other.wav'
        scratch.write_wave(other, [5000, -5000] * 48000)
        alias = self.folder / 'selected.wav'
        alias.symlink_to(self.recording)
        source = deepcopy(self.source)
        source['lines'][0]['audio_file'] = str(alias)
        actual_render = scratch.render
        def retarget(source_path, output_root):
            alias.unlink()
            alias.symlink_to(other)
            return actual_render(source_path, output_root)
        with patch('studio.audio.scratch.render', side_effect=retarget):
            result = self.render(source=source)
        saved = self.store.get_version(result['version_id'])['version']
        self.assertEqual(saved['metadata']['timing']['lines'][0]['duration'], 1)
        self.assertEqual(saved['status'], 'in_review')
        files = {f['name']: self.store.file_path(result['version_id'], i)[0] for i, f in enumerate(saved['files'])}
        self.assertEqual(json.loads(files['original-source.json'].read_text())['lines'][0]['audio_file'], str(alias))
        imports = json.loads(files['recording-imports.json'].read_text())
        self.assertEqual(imports[0]['original_path'], str(alias))
        self.assertEqual(imports[0]['resolved_path'], str(self.recording.resolve()))
        self.assertEqual(imports[0]['line_id'], 'LINE')
        self.assertEqual(imports[0]['sha256'], hashlib.sha256(self.recording.read_bytes()).hexdigest())
        runtime = json.loads(files['source.json'].read_text())
        captured = Path(runtime['lines'][0]['audio_file'])
        self.assertNotEqual(captured, alias)
        self.assertEqual(captured.read_bytes(), self.recording.read_bytes())
        self.assertNotIn(self.claim['token'], json.dumps(saved))
        self.assertEqual(len(scratch.read_wave(other)), 96000)
        self.assertEqual(len(scratch.read_wave(self.recording)), 48000)

    def test_flow_registered_bundle_excludes_legacy_wan_plan_but_retains_diagnostic(self):
        result = self.render()
        saved = self.store.get_version(result['version_id'])['version']
        self.assertNotIn('wan-plan.json', {f['name'] for f in saved['files']})
        self.assertNotIn('wan-plan.json', {f['relative_path'] for f in saved['metadata']['bundle_file_map']})
        diagnostic = json.loads((Path(result['output']) / 'wan-plan.json').read_text())
        self.assertEqual(diagnostic['provider'], 'Alibaba Cloud Model Studio')
        self.assertEqual(saved['status'], 'in_review')

    def test_legacy_wan_service_still_retains_original_provider_plan(self):
        project = self.store.create_project({'title': 'Legacy Wan recording fixture'})['id']
        scene = self.store.save_scene(project, {'title': 'Legacy scene', 'duration': 4})
        inputs = []
        for stage in ('premise', 'comic', 'script'):
            files = [(f'page{i}.png', b'isolated fixture image') for i in range(10)] if stage == 'comic' else []
            saved = self.store.add_version(project, {'title': stage, 'stage': stage, 'kind': stage,
                'content': 'Legacy fixture narration', 'inputs': list(inputs)}, files)
            self.store.review(saved['version_id'], 'approved')
            inputs.append(saved['version_id'])
        claim = self.store.claim(project, 'Legacy audio test', scene)
        result = self.service.render_scratch_audio(project, scene, self.source, claim['task_id'], claim['token'])
        saved = self.store.get_version(result['version_id'])['version']
        self.assertIn('wan-plan.json', {f['name'] for f in saved['files']})
        self.assertIn('wan-plan.json', {f['relative_path'] for f in saved['metadata']['bundle_file_map']})

    def test_atomic_registration_guard_rolls_back_artifact_when_recording_changes_during_copy(self):
        import shutil
        original = shutil.copyfile
        changed = False
        def copy(source, dest, **kwargs):
            nonlocal changed
            result = original(source, dest, **kwargs)
            if '/assets/' in str(dest) and not changed:
                changed = True
                scratch.write_wave(self.recording, [4000, -4000] * 24000)
            return result
        with patch('studio.store.shutil.copyfile', side_effect=copy):
            with self.assertRaises(Problem):
                self.render()
        self.assert_failed_retained()

    def test_submit_guard_rejection_keeps_retained_draft_without_success(self):
        original = self.store.submit
        def submit(version, actor='agent', **kwargs):
            p = self.store.project(self.project)
            self.store.update_project(self.project, {'expected_revision': p['revision'], 'brief': 'Changed just before submit'})
            return original(version, actor, **kwargs)
        with patch.object(self.store, 'submit', side_effect=submit):
            with self.assertRaises(Problem):
                self.render()
        self.assertEqual(self.job()['status'], 'failed')
        self.assertEqual(len(self.audio_versions()), 1)
        self.assertEqual(self.audio_versions()[0]['status'], 'draft')
        self.assertFalse(self.audio_versions()[0]['submitted'])
        self.assertEqual(self.audio_versions()[0]['reviews'], [])

    def test_director_can_regenerate_existing_approved_audio_without_new_primary_artifact(self):
        first = self.render()
        self.store.review(first['version_id'], 'approved')
        pending = self.prepare_native()
        with patch('scripts.speech.subprocess.run', side_effect=self.native_process()):
            second = self.service.execute(pending)
        self.assertEqual(second['artifact_id'], first['artifact_id'])
        self.assertEqual(second['number'], 2)
        self.assertEqual(self.store.get_version(second['version_id'])['version']['status'], 'in_review')
        self.assertEqual(self.store.get_version(first['version_id'])['version']['status'], 'approved')

    def test_native_rate_and_invalid_pcm_reject_without_opening_job(self):
        source = self.native()
        source['characters']['A']['rate'] = 1
        with patch('scripts.speech.subprocess.run', side_effect=self.native_process()):
            with self.assertRaises(Problem):
                self.render(source=source)
        scratch.write_wave(self.recording, [])
        with self.assertRaises(Problem):
            self.render()
        self.assertEqual(self.store.project(self.project)['jobs'], [])

    def test_stale_claim_from_upstream_revision_rejects_before_job(self):
        saved = self.store.add_version(self.project, {'title': 'script', 'kind': 'script', 'stage': 'script',
            'artifact_id': self.upstream[-1]['artifact_id'], 'expected_version': self.upstream[-1]['version_id'],
            'content': 'Changed words.', 'inputs': self.inputs[:2]})
        self.store.review(saved['version_id'], 'approved')
        with self.assertRaises(Problem):
            self.render()
        self.assertEqual(self.store.project(self.project)['jobs'], [])

    def test_director_http_keeps_async_shape_and_shares_real_rendering(self):
        module = importlib.import_module('studio.app')
        with patch.object(module, 'store', self.store), patch.dict(os.environ, {'DIRECTOR_NO_SEED': '1'}), TestClient(module.app) as client:
            headers = {'x-director-token': module.DIRECTOR_TOKEN}
            route = f'/api/projects/{self.project}/audio'
            self.assertEqual(client.post(route, json={'scene_id': self.scene, 'source': self.source}, headers=headers).status_code, 400)
            with patch('scripts.speech.subprocess.run', side_effect=self.native_process()):
                response = client.post(route, json={'scene_id': self.scene, 'source': self.native()}, headers=headers)
                self.assertEqual(response.status_code, 200, response.text)
                self.assertEqual(response.json()['status'], 'queued')
                for _ in range(200):
                    if self.job()['status'] not in ('queued', 'running'):
                        break
                    time.sleep(.01)
            self.assertEqual(self.job()['status'], 'completed', self.job())
            self.assertTrue(self.job()['data']['timing_passed'])
            self.assertEqual(self.audio_versions()[0]['status'], 'in_review')
            self.assertIsNone(self.audio_versions()[0]['task_id'])
            self.assertEqual(client.post(route, json={}, headers=headers).status_code, 400)

    def test_voice_discovery_http_and_agent_preserve_stable_contract(self):
        module = importlib.import_module('studio.app')
        capabilities = {'platform': 'darwin', 'engine': 'macOS say', 'available': True, 'voices': [{'id': 'Test Voice (US)', 'name': 'Test Voice (US)', 'language': 'en_US'}], 'issues': [], 'temporary_only': True}
        with patch('scripts.speech.subprocess.run', side_effect=self.native_process()), patch.object(module, 'store', self.store), TestClient(module.app) as client:
            self.assertEqual(client.get('/api/audio-voices').json(), capabilities)
            self.assertEqual(agent_tools.get_speech_capabilities(), capabilities)

    def test_agent_wrapper_and_cli_emit_one_json_result_with_no_private_token(self):
        with patch.object(agent_tools, 'database', return_value=self.store):
            result = agent_tools.render_scratch_audio(self.project, self.scene, self.source, self.claim['task_id'], self.claim['token'])
        self.assertEqual(self.store.get_version(result['version_id'])['version']['status'], 'in_review')
        self.store.review(result['version_id'], 'changes_requested', 'New isolated fixture timing take.')
        request = self.folder / 'request.json'
        request.write_text(json.dumps({'project_id': self.project, 'scene_id': self.scene, 'source': self.source,
                          'task_id': self.claim['task_id'], 'token': self.claim['token']}))
        run = subprocess.run([sys.executable, '-m', 'studio.cli', 'render_scratch_audio', '--json-file', str(request)],
                  cwd=ROOT, env={**os.environ, 'DIRECTOR_DATA': str(self.store.root)}, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        result2 = json.loads(run.stdout)
        self.assertEqual(result2['artifact_id'], result['artifact_id'])
        self.assertTrue(result2['timing_passed'])
        self.assertNotIn(self.claim['token'], run.stdout + run.stderr)


if __name__ == '__main__':
    unittest.main()
