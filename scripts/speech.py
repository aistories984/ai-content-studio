"""Bounded, local, temporary native speech. No fallback, shell, network or approval."""
from __future__ import annotations

from array import array
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import wave

ROOT = Path(__file__).resolve().parents[1]
WINDOWS_TOOL = r'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
MAX_LINES = 100
MAX_TEXT = 50000
BATCH_TIMEOUT = 180


def _native():
    if sys.platform == 'darwin':
        return 'macOS say', ['/usr/bin/say']
    if sys.platform == 'win32':
        return 'Windows System.Speech', [WINDOWS_TOOL, '-NoProfile', '-NonInteractive', '-File', str(ROOT / 'scripts' / 'synthesize.ps1')]
    return None, []


def get_speech_capabilities():
    """Discover installed voices only; availability does not guarantee synthesis."""
    engine, command = _native()
    result = {'platform': sys.platform, 'engine': engine, 'available': False, 'voices': [],
              'issues': [], 'temporary_only': True}
    if not command:
        result['issues'].append('Native speech is unsupported on this platform; supply mono 48 kHz 16-bit PCM recordings through audio_file.')
        return result
    try:
        process = subprocess.run(command + (['-v', '?'] if sys.platform == 'darwin' else ['-ListVoices']),
                                 shell=False, check=True, capture_output=True, text=True,
                                 encoding='utf-8', errors='replace', timeout=15)
        if sys.platform == 'darwin':
            voices = []
            for line in process.stdout.splitlines():
                match = re.fullmatch(r'(.+?)\s+([a-z]{2,3}_(?:[A-Z]{2}|[0-9]{3})(?:_[A-Za-z0-9]+)?)\s+#.*', line.strip())
                if match:
                    name, language = match.groups()
                    voices.append({'id': name, 'name': name, 'language': language})
        else:
            voices = json.loads(process.stdout.lstrip('\ufeff'))
            if isinstance(voices, dict):
                voices = [voices]
            if not isinstance(voices, list) or any(not isinstance(v, dict) or any(not isinstance(v.get(k), str) or not v[k] for k in ('id', 'name', 'language')) for v in voices):
                raise ValueError('Invalid installed-voice inventory')
            voices = [{key: v[key] for key in ('id', 'name', 'language')} for v in voices]
        result['voices'] = voices
        result['available'] = bool(voices)
        if not voices:
            result['issues'].append('No installed enabled voices found; supply PCM recordings through audio_file.')
    except (OSError, subprocess.SubprocessError, ValueError) as error:
        result['issues'].append(f'Native voice discovery failed: {error}. Supply PCM recordings through audio_file.')
    return result


def _validate_requests(requests, work_dir):
    if not isinstance(requests, list) or len(requests) > MAX_LINES:
        raise ValueError('Speech requests must be a bounded list of at most 100 lines')
    checked, total, outputs = [], 0, set()
    for request in requests:
        if not isinstance(request, dict):
            raise ValueError('Each speech request must be an object')
        text, voice = request.get('text'), request.get('voice')
        if not isinstance(text, str) or not text.strip() or '\x00' in text:
            raise ValueError('Speech text must be nonempty plain text without NUL')
        total += len(text)
        if total > MAX_TEXT:
            raise ValueError('Speech requests exceed 50000 total text characters')
        if not isinstance(voice, str) or not voice.strip() or len(voice) > 256 or any(c in voice for c in ('\x00', '\r', '\n')):
            raise ValueError('An explicit installed voice is required')
        rate = request.get('rate', 0)
        if isinstance(rate, bool) or not isinstance(rate, int) or not -10 <= rate <= 10:
            raise ValueError('Windows rate must be an integer from -10 to 10')
        wpm = request.get('rate_wpm')
        if 'rate_wpm' in request and (isinstance(wpm, bool) or not isinstance(wpm, int) or not 40 <= wpm <= 600):
            raise ValueError('rate_wpm must be an integer from 40 to 600')
        if sys.platform == 'darwin' and rate != 0:
            raise ValueError('Nonzero Windows rate is unsupported on macOS; use explicit rate_wpm or rate 0 for native default')
        if sys.platform == 'win32' and 'rate_wpm' in request:
            raise ValueError('rate_wpm is unsupported on Windows; use Windows rate from -10 to 10')
        output = request.get('output')
        if not isinstance(output, (str, Path)) or not str(output) or len(str(output)) > 4096:
            raise ValueError('A bounded output WAV path is required')
        output = Path(output)
        output = (output if output.is_absolute() else work_dir / output).resolve()
        if not output.is_relative_to(work_dir) or output in outputs or output.exists():
            raise ValueError('Speech output must be a new unique path within work_dir')
        outputs.add(output)
        checked.append({**request, 'text': text, 'voice': voice, 'rate': rate, 'output': str(output)})
    return checked


def _verify_pcm(path):
    try:
        with wave.open(str(path), 'rb') as stream:
            if (stream.getnchannels(), stream.getsampwidth(), stream.getframerate(), stream.getcomptype()) != (1, 2, 48000, 'NONE'):
                raise ValueError(f'{path}: expected mono 48 kHz 16-bit PCM WAV')
            frames = stream.getnframes()
            nonzero, actual = False, 0
            while True:
                data = stream.readframes(48000)
                if not data:
                    break
                if len(data) % 2:
                    raise ValueError(f'{path}: truncated PCM samples')
                samples = array('h', data)
                actual += len(samples)
                nonzero = nonzero or any(samples)
            if not frames or actual != frames or not nonzero:
                raise ValueError(f'Empty, silent or truncated native speech output: {path}. Local speech may be restricted; supply a PCM recording through audio_file.')
    except (wave.Error, EOFError) as error:
        raise ValueError(f'Invalid native speech WAV: {path}: {error}') from error
    return frames


def synthesize_requests(requests, work_dir):
    """Synthesize bounded explicit-voice requests, verifying measured PCM before return.

    Outputs must be new unique paths within work_dir. At most 100 lines/50000
    characters; one 180 second deadline covers discovery and the entire batch.
    Each invocation retains request/text evidence in a new exclusive directory.
    Errors propagate, never retry or silently choose another voice/provider.
    """
    work_dir = Path(work_dir).resolve()
    requests = _validate_requests(requests, work_dir)
    started = time.monotonic()
    capabilities = get_speech_capabilities()
    if not capabilities['available']:
        raise RuntimeError('; '.join(capabilities['issues']))
    installed = {voice['id'] for voice in capabilities['voices']}
    for request in requests:
        if request['voice'] not in installed:
            raise ValueError(f"Voice {request['voice']!r} is unavailable; select an exact installed voice or supply a PCM recording")
    work_dir.mkdir(parents=True, exist_ok=True)
    for request in requests:
        Path(request['output']).parent.mkdir(parents=True, exist_ok=True)
    evidence_dir = Path(tempfile.mkdtemp(prefix='speech-evidence-', dir=work_dir))
    if any(Path(request['output']).is_relative_to(evidence_dir) for request in requests):
        raise ValueError('Speech output must not overlap the invocation evidence directory')
    request_path = evidence_dir / 'synthesis-request.json'
    with request_path.open('x', encoding='utf-8') as stream:
        json.dump({'lines': requests}, stream, indent=2, ensure_ascii=False)
    engine, command = _native()
    def remaining():
        seconds = BATCH_TIMEOUT - (time.monotonic() - started)
        if seconds <= 0:
            raise subprocess.TimeoutExpired(command, BATCH_TIMEOUT)
        return seconds
    if sys.platform == 'darwin':
        for index, request in enumerate(requests):
            text_path = evidence_dir / f'speech-text-{index:03}.txt'
            with text_path.open('x', encoding='utf-8') as stream:
                stream.write(request['text'])
            args = command + ['-v', request['voice'], '-o', request['output'], '--file-format=WAVE', '--data-format=LEI16@48000', '--channels=1']
            if 'rate_wpm' in request:
                args += ['-r', str(request['rate_wpm'])]
            args += ['-f', str(text_path)]
            subprocess.run(args, shell=False, check=True, capture_output=True, timeout=remaining())
            _verify_pcm(request['output'])
    else:
        subprocess.run(command + ['-RequestPath', str(request_path)], shell=False, check=True,
                       capture_output=True, timeout=remaining())
    outputs = [{'output': r['output'], 'voice': r['voice'], 'frames': _verify_pcm(r['output'])} for r in requests]
    return {'engine': engine, 'temporary_only': True, 'outputs': outputs, 'request_file': str(request_path)}
