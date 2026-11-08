param([string]$RequestPath, [switch]$ListVoices)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $available = @($synth.GetInstalledVoices() | Where-Object { $_.Enabled } | ForEach-Object { $_.VoiceInfo.Name })
    if ($ListVoices) {
        [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
        $voices = @($synth.GetInstalledVoices() | Where-Object { $_.Enabled } | ForEach-Object {
            @{ id = $_.VoiceInfo.Name; name = $_.VoiceInfo.Name; language = $_.VoiceInfo.Culture.Name }
        })
        ConvertTo-Json -InputObject $voices -Compress
        return
    }
    if (-not $RequestPath) { throw "RequestPath is required for synthesis" }
    $request = Get-Content -LiteralPath $RequestPath -Raw -Encoding UTF8 | ConvertFrom-Json
    $format = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(48000, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)
    foreach ($line in $request.lines) {
        if ($available -notcontains $line.voice) { throw "Voice '$($line.voice)' is unavailable. Installed voices: $($available -join ', ')" }
        $synth.SelectVoice($line.voice)
        $synth.Rate = [int]$line.rate
        $synth.Volume = 100
        $synth.SetOutputToWaveFile([string]$line.output, $format)
        $synth.Speak([string]$line.text)
        $synth.SetOutputToNull()
    }
} finally { $synth.Dispose() }
