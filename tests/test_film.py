"""Offline film contracts: real temporary files/approval chains, no provider actions."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import wave
from PIL import Image
from studio.store import Store, Problem
from tests.test_production import BRIEF


def future(hours=1):
    return (datetime.now(timezone.utc) + timedelta(hours=hours)).isoformat()


class FilmTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.media = tempfile.TemporaryDirectory()
        target = Path(cls.media.name) / 'preview.mp4'
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-f', 'lavfi', '-i',
                        'color=s=32x32:r=30:d=2', '-c:v', 'libx264', str(target)], check=True)
        cls.video = target.read_bytes()
        out = io.BytesIO()
        with wave.open(out, 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000); w.writeframes(b'\0' * 32000)
        cls.audio = out.getvalue()
        out = io.BytesIO(); Image.new('RGB', (32, 32)).save(out, format='PNG'); cls.image = out.getvalue()

    @classmethod
    def tearDownClass(cls):
        cls.media.cleanup()

    def setUp(self):
        self.assertIsNotNone(importlib.util.find_spec('studio.film'), 'film ledger is missing')
        from studio.film import FilmService
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.store = Store(self.tmp.name); self.service = FilmService(self.store)
        self.p, self.scene, self.claim, self.board = self.fixture()

    def fixture(self):
        p = self.store.create_project({'title': 'Offline fixture', 'workflow_id': 'comic-to-flow', 'production_brief': BRIEF})['id']
        scene = self.store.save_scene(p, {'title': 'Test shot', 'duration': 2})
        board = None
        for stage, kind in [('premise','premise'), ('comic','comic'), ('script','script'), ('audio','audio'), ('boards','storyboard'), ('blender','previs')]:
            files = None; metadata = {}
            if stage == 'comic': files = [(f'{i}.png', self.image) for i in range(10)]
            if stage == 'audio': files = [('audio.wav', self.audio)]; metadata = {'duration':2, 'timing_passed':True}
            if stage == 'boards': files = [('clean.png', self.image)]; metadata = {'reference_map':'Hero', 'clean_reference_indices':[0]}
            if stage == 'blender': files = [('preview.mp4', self.video), ('scene.blend', b'Offline fixture editable bytes')]; metadata = {'duration':2}
            sid = scene if stage in ('audio','boards','blender') else None
            r = self.store.add_version(p, {'title':stage, 'kind':kind, 'stage':stage, 'scene_id':sid, 'inputs':self.store.next_action(p,sid)['inputs'], 'content':'Fixture story', 'prompt':'Exact reviewed prompt', 'metadata':metadata}, uploaded=files)
            self.store.review(r['version_id'], 'approved')
            if stage == 'boards': board = r['version_id']
        return p, scene, self.store.claim(p, 'film-test', scene), board

    def capability(self, **changes):
        return self.service.record_capability(self.p, {'account_ref':'test-account', 'model':'Observed model', 'input_mode':'ingredients', 'duration':2, 'aspect_ratio':'9:16', 'outputs':1, 'credit_cost':5, 'upload_supported':True, 'download_supported':True, 'evidence':'Visible UI fixture observations', 'expires_at':future(), **changes}, self.claim['task_id'], self.claim['token'])

    def payload(self, **changes):
        c = self.capability()
        return {'capability_id':c['id'], 'prompt':'Exact reviewed prompt', 'settings':{k:c['data'][k] for k in ('account_ref','model','input_mode','duration','aspect_ratio','outputs')}, 'references':[{'version_id':self.board, 'file_index':0, 'role':'ingredient'}], **changes}

    def package(self, **changes):
        return self.service.prepare_package(self.p, self.scene, self.payload(**changes), self.claim['task_id'], self.claim['token'])

    def approved(self):
        pkg = self.package(); self.service.set_budget(self.p, {'max_credits':100, 'note':'Fixture budget'})
        self.service.review_package(pkg['id'], {'package_hash':pkg['hash'], 'expected_current':True, 'decision':'approved', 'note':'Exact fixture review'})
        self.allow(pkg)
        return pkg

    def allow(self, pkg, **changes):
        return self.service.approve_allowance(pkg['id'], {'package_hash':pkg['hash'], 'upload_authorized':True, 'max_attempts':3, 'max_credits':15, 'expires_at':future(), 'note':'Fixture only', **changes})

    def reserve(self, pkg):
        return self.service.reserve_attempt(pkg['id'], self.claim['task_id'], self.claim['token'])

    def result(self, attempt, status, **changes):
        return self.service.record_result(attempt['id'], {'status':status, 'evidence':'Observed fixture result', **changes}, self.claim['task_id'], self.claim['token'])

    def test_reopen_additive_and_preserve_twelve_obligations(self):
        from studio.film import FilmService
        self.assertEqual(len(self.store.project(self.p)['workflow']['diagram_mapping']), 12)
        self.assertEqual(FilmService(Store(self.tmp.name)).get_state(self.p)['packages'], [])
        self.assertEqual(self.store.next_action(self.p,self.scene)['stage'], 'flow')

    def test_hash_stability_exact_prompt_and_no_secret_or_paths(self):
        payload = self.payload()
        a = self.service.prepare_package(self.p,self.scene,payload,self.claim['task_id'],self.claim['token'])
        b = self.service.prepare_package(self.p,self.scene,payload,self.claim['task_id'],self.claim['token'])
        self.assertEqual(a['hash'], b['hash']); self.assertNotEqual(a['id'], b['id'])
        self.assertTrue(a['current']); self.assertTrue(a['no_external_action'])
        state = json.dumps(self.service.get_state(self.p))
        self.assertNotIn(self.claim['token'], state); self.assertNotIn('assets/', state)
        for changes in ({'prompt':'Unreviewed'}, {'references':[{'version_id':self.board,'file_index':0,'role':'invalid'}]}):
            with self.assertRaises(Problem): self.package(**changes)

    def test_capability_rejects_secrets_nonfinite_extra_and_expiry(self):
        for changes in ({'cookies':'secret'}, {'token':'secret'}, {'credit_cost':float('nan')}, {'outputs':2}, {'expires_at':future(25)}, {'expires_at':future(-1)}, {'upload_supported':False}):
            with self.subTest(changes=changes), self.assertRaises(Problem): self.capability(**changes)

    def test_settings_must_match_observation_scene_and_project(self):
        payload = self.payload(); payload['settings']['duration'] = 3
        with self.assertRaises(Problem): self.service.prepare_package(self.p,self.scene,payload,self.claim['task_id'],self.claim['token'])
        self.capability(duration=3)
        with self.assertRaises(Problem): self.package(settings={'account_ref':'test-account','model':'Observed model','input_mode':'ingredients','duration':3,'aspect_ratio':'9:16','outputs':1})

    def test_mutated_audio_or_blender_blocks_currentness(self):
        pkg = self.package()
        p = self.store.project(self.p)
        for kind in ('audio','previs'):
            a = next(a for a in p['artifacts'] if a['kind'] == kind)
            path,_ = self.store.file_path(a['approved_version_id'], 0 if kind == 'audio' else 1)
            old = path.read_bytes(); path.write_bytes(b'changed')
            self.assertFalse(self.service.get_state(self.p)['packages'][0]['current'])
            with self.assertRaises(Problem): self.package()
            path.write_bytes(old)
        self.assertTrue(self.service.get_state(self.p)['packages'][0]['current'])

    def test_lease_wrong_scope_expiry_and_upstream_revocation(self):
        pkg = self.package()
        with self.assertRaises(Problem): self.service.prepare_package(self.p,self.scene,self.payload(),self.claim['task_id'],'wrong')
        self.store.review(self.board,'changes_requested','Needs changes')
        self.assertFalse(self.service.get_state(self.p)['packages'][0]['current'])
        with self.assertRaises(Problem): self.package()

    def test_unapproved_and_unmapped_refs_block(self):
        other = self.store.create_project({'title':'Early', 'workflow_id':'comic-to-flow','production_brief':BRIEF})['id']
        early = self.store.claim(other,'early')
        with self.assertRaises(Problem): self.service.record_capability(other,self.capability()['data'],early['task_id'],early['token'])
        with self.store.db(True) as db:
            row = db.execute('SELECT data FROM versions WHERE id=?',(self.board,)).fetchone(); data=json.loads(row[0]); data['metadata'].pop('clean_reference_indices'); db.execute('UPDATE versions SET data=? WHERE id=?',(json.dumps(data),self.board))
        with self.assertRaises(Problem): self.package()

    def test_human_gates_and_hash_rejection_do_not_reserve(self):
        p = self.package()
        with self.assertRaises(Problem): self.reserve(p)
        with self.assertRaises(Problem): self.allow(p)
        self.service.set_budget(self.p, {'max_credits':100,'note':'Budget'})
        with self.assertRaises(Problem): self.service.review_package(p['id'], {'package_hash':'bad','expected_current':True,'decision':'approved','note':''})
        self.service.review_package(p['id'], {'package_hash':p['hash'],'expected_current':True,'decision':'approved','note':'Review'})
        with self.assertRaises(Problem): self.allow(p,upload_authorized=False)
        self.allow(p)
        a = self.reserve(p); self.assertTrue(a['no_external_action']); self.assertEqual(a['data']['reserved_credits'],5)
        self.service.review_package(p['id'], {'package_hash':p['hash'],'expected_current':True,'decision':'rejected','note':'Revoked'})
        self.result(a,'failed')
        with self.assertRaises(Problem): self.reserve(p)

    def test_cumulative_ceilings_survive_new_allowance_and_duplicate_package(self):
        p = self.approved(); self.allow(p,max_attempts=1,max_credits=5)
        a = self.reserve(p); self.result(a,'failed')
        self.allow(p,max_attempts=1,max_credits=5)
        with self.assertRaises(Problem): self.reserve(p)
        # Re-preparing the exact same reviewed package cannot reset its ceilings.
        data = p['data']; payload = {k:data[k] for k in ('capability_id','settings','prompt')}; payload['references']=[{k:r[k] for k in ('version_id','file_index','role')} for r in data['references']]
        duplicate = self.service.prepare_package(self.p,self.scene,payload,self.claim['task_id'],self.claim['token'])
        self.service.review_package(duplicate['id'], {'package_hash':duplicate['hash'],'expected_current':True,'decision':'approved','note':'Again'})
        self.allow(duplicate,max_attempts=1,max_credits=5)
        with self.assertRaises(Problem): self.reserve(duplicate)
        self.allow(p,max_attempts=2,max_credits=10)
        self.result(self.reserve(p),'failed')
        self.assertEqual(self.service.get_state(self.p)['budget']['committed_credits'],10)

    def test_project_cap_cost_overrun_failure_no_refund_and_raise(self):
        p = self.approved(); self.service.set_budget(self.p, {'max_credits':5,'note':'One attempt'})
        a = self.reserve(p); self.result(a,'failed',observed_credits=7)
        state = self.service.get_state(self.p)
        self.assertEqual(state['budget']['committed_credits'],7)
        self.assertEqual(state['budget']['observed_credits'],7)
        self.assertEqual(state['budget']['remaining_credits'],0)
        self.assertTrue(any('budget' in b.lower() for b in state['blockers']))
        with self.assertRaises(Problem): self.service.set_budget(self.p, {'max_credits':6,'note':'Cannot erase cost'})
        with self.assertRaises(Problem): self.reserve(p)
        self.service.set_budget(self.p, {'max_credits':20,'note':'Explicit raise'})
        self.result(self.reserve(p),'failed')
        self.assertEqual(self.service.get_state(self.p)['budget']['committed_credits'],12)
        self.assertEqual(len(self.service.get_state(self.p)['budget']['history']),3)

    def test_unknown_blocks_other_packages_project_account_and_reopen(self):
        from studio.film import FilmService
        p = self.approved(); a = self.reserve(p); self.result(a,'unknown')
        p2 = self.approved()
        with self.assertRaises(Problem): self.reserve(p2)
        self.service = FilmService(Store(self.tmp.name))
        with self.assertRaises(Problem): self.reserve(p)
        old = self.p,self.scene,self.claim,self.board
        self.p,self.scene,self.claim,self.board = self.fixture()
        cross = self.approved()
        with self.assertRaises(Problem): self.reserve(cross)
        self.p,self.scene,self.claim,self.board = old
        self.result(a,'failed')
        self.assertEqual(self.reserve(p)['status'],'reserved')

    def test_competing_reservations_are_atomic(self):
        p = self.approved()
        def reserve_one(_):
            try: return self.reserve(p)['id']
            except Problem: return None
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(reserve_one,range(2)))
        self.assertEqual(sum(x is not None for x in results),1)
        self.assertEqual(self.service.get_state(self.p)['budget']['committed_credits'],5)

    def test_fresh_project_claim_reconciles_after_direction_revision(self):
        p = self.approved(); a = self.reserve(p); self.result(a,'unknown')
        self.store.finish_claim(self.claim['task_id'],self.claim['token'],release=True)
        self.store.update_project(self.p,{'expected_revision':1,'creative_locks':'Revision moves upstream'})
        self.claim = self.store.claim(self.p,'recovery')
        self.assertIsNone(self.claim['action']['scene_id'])
        r = self.result(a,'submitted',provider_id='visible-generation-1')
        self.assertEqual(r['data']['task_id'],a['data']['task_id'])
        self.result(a,'observed',observed_credits=6)
        self.result(a,'downloaded')
        with self.assertRaises(Problem): self.reserve(p)
        state = self.service.get_state(self.p); self.assertEqual(state['attempts'][0]['status'],'downloaded')
        self.assertFalse(state['automation']['download_verification_ready'])
        self.assertEqual(len(state['attempts'][0]['history']),4)

    def test_transitions_identity_evidence_and_no_refunds(self):
        p = self.approved(); a = self.reserve(p)
        for status in ('observed','downloaded','reserved'):
            with self.assertRaises(Problem): self.result(a,status)
        with self.assertRaises(Problem): self.result(a,'submitted',evidence='')
        self.result(a,'submitted',provider_id='one',observed_credits=6)
        with self.assertRaises(Problem): self.result(a,'observed',provider_id='two')
        with self.assertRaises(Problem): self.result(a,'observed',observed_credits=4)
        self.result(a,'observed'); self.result(a,'downloaded')
        with self.assertRaises(Problem): self.result(a,'failed')
        state = self.service.get_state(self.p)
        self.assertEqual(state['budget']['consumed_credits'],6)
        self.assertEqual(state['budget']['reserved_credits'],0)
        self.assertNotIn(self.claim['token'], json.dumps(state))

    def test_reservation_revalidates_currentness_and_expiry(self):
        from unittest.mock import patch
        p = self.approved()
        with patch('studio.film.expired',return_value=True):
            with self.assertRaises(Problem): self.reserve(p)
        path,_ = self.store.file_path(self.board,0); path.write_bytes(b'changed')
        with self.assertRaises(Problem): self.reserve(p)

    def test_expired_lease_and_foreign_recovery_rejected(self):
        p = self.approved(); a = self.reserve(p)
        with self.store.db(True) as db: db.execute('UPDATE tasks SET expires=0 WHERE id=?',(self.claim['task_id'],))
        with self.assertRaises(Problem): self.result(a,'unknown')
        self.claim=self.store.claim(self.p,'fresh',self.scene)
        self.result(a,'unknown')
        old=self.claim; other,scene,claim,board=self.fixture(); self.claim=claim
        with self.assertRaises(Problem): self.result(a,'failed')
        self.claim=old

    def test_schema_records_are_immutable_and_budget_not_project_metadata(self):
        import sqlite3
        p=self.approved(); a=self.reserve(p)
        with self.assertRaises(sqlite3.IntegrityError), self.store.db(True) as db:
            db.execute('DELETE FROM film_attempts WHERE id=?',(a['id'],))
        self.store.update_project(self.p,{'expected_revision':1,'budget':0})
        self.assertEqual(self.service.get_state(self.p)['budget']['max_credits'],100)

    def test_revised_package_and_observation_never_reset_scene_ceilings(self):
        p = self.approved(); self.allow(p,max_attempts=1,max_credits=5)
        self.result(self.reserve(p),'failed')
        revised = self.package()  # New capability ID, same scene/package lineage.
        self.service.review_package(revised['id'], {'package_hash':revised['hash'],'expected_current':True,'decision':'approved','note':'Reobserved'})
        self.allow(revised,max_attempts=1,max_credits=5)
        with self.assertRaises(Problem): self.reserve(revised)

    def test_invalid_payload_types_raise_problem_not_internal_errors(self):
        for changes in ({'input_mode':[]},{'model':{}},{'duration':10**1000},{'expires_at':[]},{'credit_cost':True}):
            with self.subTest(changes=changes),self.assertRaises(Problem): self.capability(**changes)
        payload=self.payload()
        for changes in ({'capability_id':[]},{'references':[{'version_id':[], 'file_index':0,'role':'ingredient'}]}, {'references':[{'version_id':self.board, 'file_index':0,'role':[]}]}):
            with self.subTest(changes=changes),self.assertRaises(Problem): self.service.prepare_package(self.p,self.scene,{**payload,**changes},self.claim['task_id'],self.claim['token'])

    def test_hash_changes_on_order_and_referenced_role(self):
        p=self.package()
        frames=self.capability(input_mode='frames')
        payload={'capability_id':frames['id'],'settings':{k:frames['data'][k] for k in ('account_ref','model','input_mode','duration','aspect_ratio','outputs')},'prompt':p['data']['prompt'],'references':[{'version_id':self.board,'file_index':0,'role':'first_frame'}]}
        revised=self.service.prepare_package(self.p,self.scene,payload,self.claim['task_id'],self.claim['token'])
        self.assertNotEqual(p['hash'],revised['hash'])
        payload['references']=[{'version_id':self.board,'file_index':0,'role':'last_frame'}]
        with self.assertRaises(Problem): self.service.prepare_package(self.p,self.scene,payload,self.claim['task_id'],self.claim['token'])

    def test_expired_allowance_separate_from_fresh_capability(self):
        from unittest.mock import patch
        from studio.film import expired
        p=self.approved()
        def allowance_only(data):
            return True if 'max_attempts' in data else expired(data)
        with patch('studio.film.expired',side_effect=allowance_only),self.assertRaises(Problem): self.reserve(p)

    def test_current_package_rejection_then_reapproval_requires_new_allowance(self):
        p=self.approved()
        for decision in ('rejected','approved'):
            self.service.review_package(p['id'],{'package_hash':p['hash'],'expected_current':True,'decision':decision,'note':'Changed mind'})
        with self.assertRaises(Problem): self.reserve(p)
        self.allow(p); self.reserve(p)

    def test_migrates_existing_database_without_changing_old_rows(self):
        import sqlite3
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'studio.sqlite'
            with sqlite3.connect(path) as db:
                db.execute('CREATE TABLE projects(id TEXT PRIMARY KEY,title TEXT NOT NULL,brief TEXT NOT NULL,settings TEXT NOT NULL,created TEXT NOT NULL,revision INTEGER NOT NULL DEFAULT 1)')
                values=('old-film','Legacy title','Original brief',json.dumps({'workflow_id':'comic-to-wan'}),'2026-01-01',4)
                db.execute('INSERT INTO projects VALUES(?,?,?,?,?,?)',values)
            Store(directory); reopened=Store(directory)
            with reopened.db() as db:
                self.assertEqual(tuple(db.execute('SELECT * FROM projects WHERE id=?',('old-film',)).fetchone()),values)
                self.assertEqual(db.execute('SELECT COUNT(*) FROM film_attempts').fetchone()[0],0)

    def test_cross_account_blocker_visible_without_foreign_details(self):
        p=self.approved(); a=self.reserve(p); self.result(a,'unknown')
        other,scene,claim,board=self.fixture()
        old=self.p,self.scene,self.claim,self.board
        self.p,self.scene,self.claim,self.board=other,scene,claim,board
        self.package()
        state=self.service.get_state(other)
        self.assertTrue(any('account' in b.lower() and 'unresolved' in b.lower() for b in state['blockers']))
        self.assertNotIn(a['id'],json.dumps(state))
        self.p,self.scene,self.claim,self.board=old

    def test_new_current_package_after_scene_revision_preserves_project_cap(self):
        p=self.approved(); a=self.reserve(p); self.result(a,'failed',observed_credits=20)
        self.store.finish_claim(self.claim['task_id'],self.claim['token'],release=True)
        self.store.update_project(self.p,{'expected_revision':1,'creative_locks':'New approved creative direction pending'})
        state=self.service.get_state(self.p)
        self.assertEqual(state['budget']['max_credits'],100)
        self.assertEqual(state['budget']['committed_credits'],20)
        self.assertFalse(state['packages'][0]['current'])
