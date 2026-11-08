"""Native process boundaries are mocked; WAV parsing and timeline rendering are real."""
from array import array
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import wave

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import scratch_audio as scratch
try:
    from scripts import speech
except ImportError:
    speech = None

INVENTORY = 'Albert              en_US    # I have a name.\nGrandma (English (US)) en_US # Hello\nBad inventory\nThomas fr_FR # Bonjour\nMajed ar_001 # مرحبًا\n'


def wav(path, samples=(0, 1000, -1000), rate=48000, width=2, channels=1):
    with wave.open(str(path), 'wb') as stream:
        stream.setparams((channels, width, rate, 0, 'NONE', 'not compressed'))
        stream.writeframes(array('h', samples).tobytes())


class SpeechTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(speech, 'native speech adapter is not implemented')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name).resolve()
        self.request = {'text': 'Café --hello $(plain text)\nNext line', 'voice': 'Grandma (English (US))', 'rate': 0, 'output': str(self.folder / 'line.wav')}
        self.platform = patch.object(speech.sys, 'platform', 'darwin')
        self.platform.start()
        self.addCleanup(self.platform.stop)

    def native(self, args, **kwargs):
        self.assertFalse(kwargs.get('shell', False))
        self.assertGreater(kwargs['timeout'], 0)
        self.assertLessEqual(kwargs['timeout'], 180)
        if args == ['/usr/bin/say', '-v', '?']:
            return subprocess.CompletedProcess(args, 0, INVENTORY, '')
        expected = ['/usr/bin/say', '-v', self.request['voice'], '-o', self.request['output'], '--file-format=WAVE', '--data-format=LEI16@48000', '--channels=1']
        self.assertEqual(args[:8], expected)
        offset = 8
        if 'rate_wpm' in self.request:
            self.assertEqual(args[8:10], ['-r', str(self.request['rate_wpm'])])
            offset = 10
        self.assertEqual(args[offset], '-f')
        self.assertEqual(Path(args[offset + 1]).read_text(encoding='utf-8'), self.request['text'])
        wav(self.request['output'])
        return subprocess.CompletedProcess(args, 0, '', '')

    def test_inventory_preserves_exact_multiword_parenthesized_voice(self):
        with patch.object(speech.subprocess, 'run', side_effect=self.native):
            result = speech.get_speech_capabilities()
        self.assertTrue(result['available'])
        self.assertTrue(result['temporary_only'])
        self.assertEqual(result['engine'], 'macOS say')
        self.assertEqual(result['voices'][1], {'id': 'Grandma (English (US))', 'name': 'Grandma (English (US))', 'language': 'en_US'})

    def test_numeric_region_voice_is_discovered_and_selectable(self):
        self.request['voice'] = 'Majed'
        with patch.object(speech.subprocess, 'run', side_effect=self.native):
            capabilities = speech.get_speech_capabilities()
            self.assertIn({'id': 'Majed', 'name': 'Majed', 'language': 'ar_001'}, capabilities['voices'])
            result = speech.synthesize_requests([self.request], self.folder)
        self.assertEqual(result['outputs'][0]['voice'], 'Majed')

    def test_output_cannot_replace_returned_request_or_text_evidence(self):
        for filename in ('synthesis-request.json', 'speech-text-000.txt'):
            work_dir = self.folder / filename.replace('.', '-')
            work_dir.mkdir()
            self.request['output'] = str(work_dir / filename)
            with self.subTest(filename=filename), patch.object(speech.subprocess, 'run', side_effect=self.native):
                result = speech.synthesize_requests([self.request], work_dir)
                request_file = Path(result['request_file'])
                self.assertNotEqual(request_file, Path(self.request['output']))
                self.assertEqual(json.loads(request_file.read_text(encoding='utf-8'))['lines'][0]['text'], self.request['text'])
                text_files = list(request_file.parent.glob('speech-text-*.txt'))
                self.assertEqual(len(text_files), 1)
                self.assertNotEqual(text_files[0], Path(self.request['output']))
                self.assertEqual(text_files[0].read_text(encoding='utf-8'), self.request['text'])

    def test_reused_work_directory_preserves_previous_invocation_evidence(self):
        with patch.object(speech.subprocess, 'run', side_effect=self.native):
            first = speech.synthesize_requests([self.request], self.folder)
            first_request = Path(first['request_file'])
            evidence = {path: path.read_bytes() for path in first_request.parent.iterdir() if path.is_file()}
            self.request.update(text='Different second request', output=str(self.folder / 'second.wav'))
            second = speech.synthesize_requests([self.request], self.folder)
        self.assertNotEqual(first_request, Path(second['request_file']))
        for path, original in evidence.items():
            self.assertEqual(path.read_bytes(), original, str(path))
        self.assertEqual(json.loads(first_request.read_text(encoding='utf-8'))['lines'][0]['text'], 'Café --hello $(plain text)\nNext line')
        self.assertEqual(json.loads(Path(second['request_file']).read_text(encoding='utf-8'))['lines'][0]['text'], 'Different second request')

    def test_exact_native_command_and_utf8_text_file(self):
        with patch.object(speech.subprocess, 'run', side_effect=self.native):
            result = speech.synthesize_requests([self.request], self.folder)
        self.assertEqual(result['engine'], 'macOS say')
        self.assertTrue((self.folder / 'line.wav').is_file())

    def test_explicit_wpm_is_passed_without_windows_rate_conversion(self):
        self.request['rate_wpm'] = 150
        with patch.object(speech.subprocess, 'run', side_effect=self.native):
            speech.synthesize_requests([self.request], self.folder)

    def test_unknown_voice_never_invokes_synthesis(self):
        self.request['voice'] = '--invalid'
        with patch.object(speech.subprocess, 'run', side_effect=self.native):
            with self.assertRaisesRegex(ValueError, 'voice|Voice'):
                speech.synthesize_requests([self.request], self.folder)
        self.assertFalse((self.folder / 'line.wav').exists())

    def test_nonzero_windows_rate_rejects_on_mac(self):
        self.request['rate'] = 2
        with self.assertRaisesRegex(ValueError, 'rate_wpm|Windows'):
            speech.synthesize_requests([self.request], self.folder)

    def test_bounded_requests_and_malformed_values_reject_before_process(self):
        values = [iter([self.request]), {}, [self.request] * 101, [{**self.request, 'text': 'x' * 50001}], [{**self.request, 'text': []}], [{**self.request, 'rate': True}], [{**self.request, 'rate_wpm': 39}], [{**self.request, 'rate_wpm': 601}], [{**self.request, 'output': str(self.folder.parent / 'outside.wav')}]]
        with patch.object(speech.subprocess, 'run', side_effect=AssertionError('must validate before process')):
            for requests in values:
                with self.subTest(requests=type(requests)):
                    with self.assertRaises(ValueError):
                        speech.synthesize_requests(requests, self.folder)

    def test_unsupported_platform_has_recording_alternative(self):
        with patch.object(speech.sys, 'platform', 'linux'):
            result = speech.get_speech_capabilities()
            self.assertFalse(result['available'])
            self.assertIn('record', ' '.join(result['issues']).lower())
            with self.assertRaisesRegex(RuntimeError, 'record|PCM'):
                speech.synthesize_requests([self.request], self.folder)

    def test_discovery_failure_is_unavailable(self):
        for error in (FileNotFoundError('missing say'), subprocess.TimeoutExpired('say', 15), subprocess.CalledProcessError(1, 'say')):
            with self.subTest(error=error), patch.object(speech.subprocess, 'run', side_effect=error):
                result = speech.get_speech_capabilities()
                self.assertFalse(result['available'])
                self.assertTrue(result['issues'])

    def test_empty_silent_wrong_pcm_and_missing_output_fail(self):
        for kind in ('empty', 'silent', 'wrong-rate', 'wrong-width', 'missing'):
            def run(args, **kwargs):
                if args[-1] == '?':
                    return subprocess.CompletedProcess(args, 0, INVENTORY, '')
                if kind != 'missing':
                    wav(self.request['output'], samples=() if kind == 'empty' else (0, 0) if kind == 'silent' else (10, -10), rate=44100 if kind == 'wrong-rate' else 48000, width=1 if kind == 'wrong-width' else 2)
                return subprocess.CompletedProcess(args, 0, '', '')
            with self.subTest(kind=kind), patch.object(speech.subprocess, 'run', side_effect=run):
                Path(self.request['output']).unlink(missing_ok=True)
                with self.assertRaises((ValueError, OSError)):
                    speech.synthesize_requests([self.request], self.folder)

    def test_process_error_and_timeout_propagate_without_retry(self):
        for error in (subprocess.CalledProcessError(1, 'say'), subprocess.TimeoutExpired('say', 180)):
            def run(args, **kwargs):
                if args[-1] == '?':
                    return subprocess.CompletedProcess(args, 0, INVENTORY, '')
                raise error
            with self.subTest(error=error), patch.object(speech.subprocess, 'run', side_effect=run):
                with self.assertRaises(subprocess.SubprocessError):
                    speech.synthesize_requests([self.request], self.folder)

    def test_batch_deadline_includes_discovery_and_previous_lines(self):
        other = {**self.request, 'output': str(self.folder / 'second.wav')}
        with patch.object(speech.time, 'monotonic', side_effect=[0, 10, 181]), patch.object(speech.subprocess, 'run', side_effect=self.native):
            with self.assertRaises(subprocess.TimeoutExpired):
                speech.synthesize_requests([self.request, other], self.folder)
        self.assertFalse((self.folder / 'second.wav').exists())

    def test_windows_inventory_and_unconverted_rate_use_fixed_script(self):
        observed = []
        self.request.update(voice='Microsoft David Desktop', rate=-3)
        def run(args, **kwargs):
            observed.append(args)
            self.assertFalse(kwargs.get('shell', False))
            self.assertEqual(args[1:5], ['-NoProfile', '-NonInteractive', '-File', str(ROOT / 'scripts' / 'synthesize.ps1')])
            if args[-1] == '-ListVoices':
                return subprocess.CompletedProcess(args, 0, json.dumps([{'id': 'Microsoft David Desktop', 'name': 'Microsoft David Desktop', 'language': 'en-US'}]), '')
            payload = json.loads(Path(args[-1]).read_text(encoding='utf-8'))
            self.assertEqual(payload['lines'][0]['rate'], -3)
            wav(self.request['output'])
            return subprocess.CompletedProcess(args, 0, '', '')
        with patch.object(speech.sys, 'platform', 'win32'), patch.object(speech.subprocess, 'run', side_effect=run):
            result = speech.synthesize_requests([self.request], self.folder)
        self.assertEqual(result['engine'], 'Windows System.Speech')
        self.assertTrue(Path(observed[0][0]).is_absolute() or ':\\Windows\\' in observed[0][0])

    def test_windows_rejects_foreign_rate_wpm(self):
        self.request['rate_wpm'] = 150
        with patch.object(speech.sys, 'platform', 'win32'):
            with self.assertRaisesRegex(ValueError, 'rate_wpm'):
                speech.synthesize_requests([self.request], self.folder)

    def source(self):
        return {'schema_version': 1, 'sequence_id': 'QA', 'target_duration': 4, 'fps': 30, 'characters': {'A': {'voice': self.request['voice'], 'color': '#123456', 'rate_wpm': 150}}, 'shots': [{'id': 'SHOT', 'start': 0, 'end': 4}], 'jobs': [{'id': 'JOB', 'start': 0, 'end': 4}], 'lines': [{'id': 'LINE', 'character': 'A', 'text': 'QA', 'start': 0, 'slot_end': 2}]}

    def test_recorded_only_skips_native_and_reports_real_provenance(self):
        source = self.source()
        wav(self.folder / 'recording.wav')
        source['lines'][0]['audio_file'] = 'recording.wav'
        path = self.folder / 'source.json'
        path.write_text(json.dumps(source))
        with patch.object(speech.subprocess, 'run', side_effect=AssertionError('no native speech for recording')), redirect_stdout(io.StringIO()):
            _, report = scratch.render(path, self.folder / 'out')
        self.assertEqual(report['engine'], 'supplied PCM recordings')
        self.assertEqual(report['lines'][0]['audio_engine'], 'supplied PCM recordings')

    def test_mixed_render_propagates_wpm_and_reports_each_engine(self):
        source = self.source()
        wav(self.folder / 'recording.wav')
        source['lines'].append({**source['lines'][0], 'id': 'REC', 'start': 2, 'slot_end': 4, 'audio_file': 'recording.wav'})
        path = self.folder / 'source.json'
        path.write_text(json.dumps(source))
        def run(args, **kwargs):
            if args[-1] == '?':
                return subprocess.CompletedProcess(args, 0, INVENTORY, '')
            self.assertIn('-r', args)
            self.assertEqual(args[args.index('-r') + 1], '150')
            wav(args[args.index('-o') + 1])
            return subprocess.CompletedProcess(args, 0, '', '')
        with patch.object(speech.subprocess, 'run', side_effect=run), redirect_stdout(io.StringIO()):
            output, report = scratch.render(path, self.folder / 'out')
        self.assertEqual(report['engine'], 'macOS say / supplied PCM recordings')
        self.assertEqual([line['audio_engine'] for line in report['lines']], ['macOS say', 'supplied PCM recordings'])
        self.assertIsNone(report['approval'])
        self.assertTrue((output / 'dialogue.srt').is_file())

    def test_source_bounds_and_rate_wpm_validate_before_render(self):
        for change in ('count', 'text', 'not-list', 'wpm'):
            source = self.source()
            if change == 'count': source['lines'] *= 101
            if change == 'text': source['lines'][0]['text'] = 'x' * 50001
            if change == 'not-list': source['lines'] = iter(source['lines'])
            if change == 'wpm': source['characters']['A']['rate_wpm'] = True
            with self.subTest(change=change), self.assertRaises(ValueError):
                scratch.validate(source)

    def test_standalone_script_import_and_help_work(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'scratch_audio.py'), '--help'], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
