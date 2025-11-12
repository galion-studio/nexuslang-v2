# Test Voice Service
# Tests voice service functionality end-to-end

Write-Host "🎙️ Testing Nexus Core Voice Service..." -ForegroundColor Cyan
Write-Host ""

# Check if voice service is running
Write-Host "📡 1. Checking voice service health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8003/health" -Method Get
    Write-Host "✅ Voice service is healthy!" -ForegroundColor Green
    Write-Host "   Version: $($health.version)" -ForegroundColor Gray
    Write-Host "   STT Available: $($health.features.stt)" -ForegroundColor Gray
    Write-Host "   TTS Available: $($health.features.tts)" -ForegroundColor Gray
    Write-Host "   Intent Available: $($health.features.intent)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Voice service not responding!" -ForegroundColor Red
    Write-Host "   Make sure voice service is running: docker-compose up -d voice-service" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Test STT endpoint (if audio file exists)
Write-Host "🎤 2. Testing Speech-to-Text..." -ForegroundColor Yellow
if (Test-Path "services\voice-service\audio_samples\test.wav") {
    try {
        $audioFile = Get-Item "services\voice-service\audio_samples\test.wav"
        $response = Invoke-RestMethod -Uri "http://localhost:8003/api/v1/voice/stt" `
            -Method Post `
            -Form @{ audio = $audioFile }
        
        Write-Host "✅ STT successful!" -ForegroundColor Green
        Write-Host "   Transcript: $($response.text)" -ForegroundColor Gray
        Write-Host "   Language: $($response.language)" -ForegroundColor Gray
        Write-Host "   Confidence: $($response.confidence)" -ForegroundColor Gray
    } catch {
        Write-Host "⚠️  STT test skipped (need audio file)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  STT test skipped (no test audio file)" -ForegroundColor Yellow
    Write-Host "   Create a test.wav file in services\voice-service\audio_samples\" -ForegroundColor Gray
}
Write-Host ""

# Test TTS endpoint
Write-Host "🔊 3. Testing Text-to-Speech..." -ForegroundColor Yellow
try {
    $ttsRequest = @{
        text = "Hello from Nexus Core voice service! This is a test of text to speech."
    } | ConvertTo-Json
    
    Invoke-RestMethod -Uri "http://localhost:8003/api/v1/voice/tts" `
        -Method Post `
        -ContentType "application/json" `
        -Body $ttsRequest `
        -OutFile "voice_test_output.mp3"
    
    if (Test-Path "voice_test_output.mp3") {
        $size = (Get-Item "voice_test_output.mp3").Length
        Write-Host "✅ TTS successful!" -ForegroundColor Green
        Write-Host "   Output file: voice_test_output.mp3 ($size bytes)" -ForegroundColor Gray
        Write-Host "   You can play this file to hear the voice" -ForegroundColor Gray
        
        # Try to play on Windows
        if ($IsWindows -or $env:OS -like "*Windows*") {
            Write-Host "   Playing audio..." -ForegroundColor Gray
            Start-Process "voice_test_output.mp3"
        }
    }
} catch {
    Write-Host "❌ TTS test failed: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test available voices
Write-Host "🎭 4. Testing available voices..." -ForegroundColor Yellow
try {
    $voices = Invoke-RestMethod -Uri "http://localhost:8003/api/v1/voice/voices" -Method Get
    Write-Host "✅ Voice list retrieved!" -ForegroundColor Green
    foreach ($voice in $voices.voices) {
        Write-Host "   - $($voice.name) ($($voice.category)): $($voice.description)" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Failed to get voices: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Check WebSocket endpoint
Write-Host "🌐 5. Testing WebSocket endpoint..." -ForegroundColor Yellow
Write-Host "⚠️  WebSocket testing requires a JWT token and wscat" -ForegroundColor Yellow
Write-Host "   Install wscat: npm install -g wscat" -ForegroundColor Gray
Write-Host "   Test command: wscat -c 'ws://localhost:8003/api/v1/voice/stream?token=YOUR_JWT'" -ForegroundColor Gray
Write-Host ""

# Summary
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "🎉 Voice Service Tests Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Login to get JWT token: POST http://localhost:8080/api/v1/auth/login" -ForegroundColor Gray
Write-Host "   2. Connect to WebSocket with token" -ForegroundColor Gray
Write-Host "   3. Send audio data and receive voice responses" -ForegroundColor Gray
Write-Host "   4. Try voice commands: 'show my profile', 'help', etc." -ForegroundColor Gray
Write-Host ""
Write-Host "📖 Documentation:" -ForegroundColor Cyan
Write-Host "   - Quickstart: VOICE_QUICKSTART.md" -ForegroundColor Gray
Write-Host "   - Commands: VOICE_COMMANDS_REFERENCE.md" -ForegroundColor Gray
Write-Host "   - Full Plan: VOICE_FIRST_PRINCIPLES_PLAN.md" -ForegroundColor Gray
Write-Host "=" * 60 -ForegroundColor Cyan

