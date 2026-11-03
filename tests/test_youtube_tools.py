"""Real CLI fixtures for the imported YouTube tools and Studio handoff."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / '.agents' / 'skills'


def load_tool(skill, filename):
    spec = importlib.util.spec_from_file_location(skill.replace('-', '_'), SKILLS / skill / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class YouTubeToolTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def run_tool(self, skill, filename, *args, success=True):
        result = subprocess.run([sys.executable, str(SKILLS / skill / filename), *map(str, args)], capture_output=True, text=True)
        if success:
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0)
        return result

    def transcript(self):
        path = self.folder / 'captions.srt'
        path.write_text('\n\n'.join(f'{i+1}\n00:00:{i*10:02d},000 --> 00:00:{i*10+5:02d},000\n{text}' for i, text in enumerate([
            'Your opening makes a concrete promise.', 'Um', 'Your opening makes a concrete promise with proof.',
            'Camera framing shows the reference character.', 'Editing joins the approved scene takes.', 'Credits identify the production sources.'
        ])))
        return path

    def test_hook_cli_scores_five_properties(self):
        result = self.run_tool('yt-script', 'hookscore.py', '--hook', 'You waste 3 hours editing: what if one cut fixed it?', '--json')[0]
        self.assertEqual(len(result['properties']), 5)
        self.assertTrue(all(0 <= value <= 100 for value in result['properties'].values()))
        self.assertGreaterEqual(result['verdict'], 0)
        self.assertLessEqual(result['verdict'], 100)

    def test_title_cli_detects_duplicate_thumbnail(self):
        result = self.run_tool('yt-package', 'title.py', '--title', '3 editing mistakes', '--thumb', 'EDITING MISTAKES', '--json')[0]
        self.assertIn('duplicate', [issue[0] for issue in result['issues']])

    def test_thumbnail_enforces_three_word_limit(self):
        tool = load_tool('yt-package', 'title.py')
        result = tool.check('3 editing mistakes', 'STOP WASTING YOUR TIME')
        self.assertIn('thumb-length', [issue[0] for issue in result['issues']])
        self.assertNotIn('thumb-length', [issue[0] for issue in tool.check('3 editing mistakes', 'STOP WASTING TIME')['issues']])

    def test_transcript_cli_finds_filler_gaps_and_retakes(self):
        result = self.run_tool('yt-edit', 'deadair.py', self.transcript(), '--json')
        self.assertEqual({cut['kind'] for cut in result['cuts']}, {'FILLER', 'DEAD', 'REPEAT'})
        self.assertTrue(all(c['end'] > c['start'] for c in result['cuts']))

    def test_whisper_json_list_and_object_are_both_supported(self):
        tool = load_tool('yt-edit', 'deadair.py')
        segments = [{'start': 0, 'end': 2, 'text': 'A measured line.'}]
        path = self.folder / 'whisper.json'
        for data in [segments, {'segments': segments}]:
            path.write_text(json.dumps(data))
            self.assertEqual(tool.load(str(path)), [(0.0, 2.0, 'A measured line.')])

    def test_chapters_cli_returns_valid_spaced_boundaries(self):
        result = self.run_tool('yt-chapters', 'chapters.py', self.transcript(), '--target', '3', '--json')
        self.assertTrue(result['valid'])
        self.assertEqual(result['chapters'][0]['start'], 0)
        self.assertGreaterEqual(len(result['chapters']), 3)
        self.assertTrue(all(c['seconds'] >= 10 for c in result['chapters']))

    def test_retention_cli_reads_export_and_transcript(self):
        path = self.folder / 'retention.csv'
        path.write_text('position,retention\n'+'\n'.join(f'{i*10},{100-i*5}' for i in range(11)))
        result = self.run_tool('yt-retention', 'retention.py', path, '--duration', '100', '--transcript', self.transcript(), '--json')
        self.assertEqual(result['points'], 11)
        self.assertEqual(result['hook_leak'], 15)
        self.assertTrue(result['cliffs'])
        self.assertTrue(result['said'])
        short = self.folder / 'short.csv'
        short.write_text('0,100\n10,90\n')
        self.run_tool('yt-retention', 'retention.py', short, '--json', success=False)

    def test_viral_cli_uses_channel_median_and_skips_thin_channels(self):
        path = self.folder / 'videos.json'
        rows = [{'channel':'fixture', 'title':f'{v} editing experiments', 'views':v} for v in [100,100,100,1000]]
        rows.append({'channel':'insufficient', 'title':'Only one', 'views':9000})
        path.write_text(json.dumps(rows))
        result = self.run_tool('yt-viral', 'swipe.py', path, '--min', '2', '--json')
        self.assertEqual(len(result['outliers']), 1)
        self.assertEqual(result['outliers'][0]['multiple'], 10)
        self.assertEqual(result['skipped_thin_channels'], [['insufficient', 1]])

    def test_skill_output_roundtrips_through_studio_without_approval(self):
        from studio import agent_tools as tools
        from studio.store import Store
        result = self.run_tool('yt-script', 'hookscore.py', '--hook', 'You waste 3 hours editing: what if one cut fixed it?', '--json')
        output = self.folder / 'hook-panel.json'
        output.write_text(json.dumps(result))
        with patch.dict(os.environ, {'DIRECTOR_DATA':str(self.folder / 'studio')}):
            project = Store().create_project({'title':'YouTube integration fixture'})['id']
            claim = tools.claim_task(project, 'youtube-test')
            registered = tools.register_artifact(project, {'title':'Hook evidence', 'kind':'notes', 'stage':'premise', 'content':'Synthetic fixture, not channel evidence.', 'prompt':'Score fixture hook.', 'inputs':[], 'metadata':{'skills':['yt-script'], 'fixture':True}, 'task_id':claim['task_id'], 'task_token':claim['token']}, [str(output)])
            version = registered['version_id']
            self.assertTrue(tools.validate_artifact(version)['passed'])
            tools.submit_for_review(version, claim['task_id'], claim['token'])
            tools.finish_task(claim['task_id'], claim['token'])
            artifact = tools.get_artifact(version)
            self.assertEqual(artifact['version']['status'], 'in_review')
            self.assertEqual(json.loads(Path(artifact['local_files'][0]).read_text()), result)
            self.assertEqual(tools.get_next_action(project)['stage'], 'premise')
            self.assertFalse(tools.get_project(project)['stage_status'][0]['complete'])


if __name__ == '__main__':
    unittest.main()
