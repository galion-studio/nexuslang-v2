# 🚀 VOICE QUICKSTART - 5 MINUTES TO WORKING VOICE

## ⚡ FASTEST PATH TO VOICE

**Goal**: Get voice working in 5 minutes.

**What You Need**:
- OpenAI API key (for Whisper STT)
- ElevenLabs API key (for TTS)
- OpenRouter API key (for intent understanding)

---

## 📋 STEP-BY-STEP (5 MINUTES)

### **STEP 1: Add API Keys to .env** (1 minute)

```bash
# Open .env file and add:

OPENAI_API_KEY=sk-your-openai-key-here
ELEVENLABS_API_KEY=your-elevenlabs-key-here
OPENROUTER_API_KEY=your-openrouter-key-here
```

**Get API Keys**:
- OpenAI: https://platform.openai.com/api-keys
- ElevenLabs: https://elevenlabs.io/speech-synthesis (free tier available)
- OpenRouter: https://openrouter.ai/keys

---

### **STEP 2: Build Voice Service** (2 minutes)

```powershell
# Navigate to project root
cd C:\Users\Gigabyte\Documents\project-nexus

# Build voice service
docker-compose build voice-service

# Start voice service
docker-compose up -d voice-service
```

**Expected output**:
```
✅ Voice service built successfully
✅ Voice service started on port 8003
✅ Health check: healthy
```

---

### **STEP 3: Test Voice** (2 minutes)

**Option A: Web Interface**
1. Open browser: http://localhost:3000/voice
2. Click "Hold to Speak" button
3. Say: "Show my profile"
4. Release button
5. ✅ You should hear a voice response!

**Option B: WebSocket Test**
```powershell
# Test WebSocket connection
wscat -c "ws://localhost:8003/api/v1/voice/stream?token=YOUR_JWT_TOKEN"

# Or use test script
.\scripts\test-voice.ps1
```

---

## 🎤 YOUR FIRST VOICE COMMAND

1. **Login first** (if not logged in):
   - Open: http://localhost:8080/api/v1/auth/login
   - Login with your credentials
   - Copy JWT token

2. **Try voice command**:
   - Hold space bar
   - Say: "Show my profile"
   - Release space bar
   - Listen to response

3. **Try more commands**:
   - "Search for AI articles"
   - "What can you do"
   - "Help"

---

## 🔍 VERIFY IT'S WORKING

### Check Service Health
```powershell
curl http://localhost:8003/health
```

**Expected response**:
```json
{
  "status": "healthy",
  "service": "voice-service",
  "version": "1.0.0"
}
```

### Check Logs
```powershell
docker logs nexus-voice --tail 50
```

**Look for**:
```
✅ Voice service started
✅ Whisper API connected
✅ ElevenLabs API connected
✅ WebSocket server ready
```

---

## 🐛 TROUBLESHOOTING

### Issue: Service won't start
**Check**:
```powershell
# View error logs
docker logs nexus-voice

# Check if port is in use
netstat -ano | findstr :8003

# Restart service
docker-compose restart voice-service
```

### Issue: Voice not transcribing
**Check**:
- Microphone permissions in browser
- Audio format (should be WebM or WAV)
- Check Whisper API key is valid
- Check logs for STT errors

### Issue: No voice response
**Check**:
- ElevenLabs API key is valid
- Check ElevenLabs account credits
- Try OpenAI TTS as fallback
- Check browser audio permissions

### Issue: "Unauthorized" error
**Check**:
- JWT token is included in WebSocket connection
- Token is not expired
- User is properly authenticated

---

## 🎯 WHAT'S WORKING NOW

After quickstart, you should have:

✅ Voice service running on port 8003
✅ WebSocket connection for voice streaming
✅ Speech-to-text with Whisper
✅ Text-to-speech with ElevenLabs
✅ Basic intent recognition
✅ Integration with existing services

---

## 📊 ARCHITECTURE (SIMPLE VIEW)

```
You speak → Microphone → Browser
                              ↓
                    WebSocket Stream
                              ↓
                      Voice Service
                              ↓
               ┌──────────────┼──────────────┐
               ↓              ↓              ↓
            Whisper      GPT-4 Intent    ElevenLabs
            (STT)        (Understand)       (TTS)
               ↓              ↓              ↓
            Text        →  Action    →    Audio
                              ↓
                         Your ears 👂
```

---

## 🎮 TRY THESE COMMANDS

### Authentication
```
"Login as john@example.com password mypass123"
"Show my profile"
"Logout"
```

### Search
```
"Search for articles about AI"
"Find users named Sarah"
```

### Research
```
"Research quantum computing"
"What's the latest on SpaceX"
```

### Help
```
"Help"
"What can you do"
```

---

## 📚 NEXT STEPS

### Learn More
- **Full command list**: `VOICE_COMMANDS_REFERENCE.md`
- **API documentation**: `VOICE_API_REFERENCE.md`
- **Architecture details**: `VOICE_FIRST_PRINCIPLES_PLAN.md`
- **Implementation guide**: `VOICE_IMPLEMENTATION_GUIDE.md`

### Advanced Features
- **Custom voices**: Change voice personality
- **Multi-language**: Support for more languages
- **Voice biometrics**: Voice-based authentication
- **Offline mode**: Cache for offline use

### Integration
- **Mobile app**: React Native voice interface
- **Desktop app**: Electron with voice
- **API integration**: Use voice in your own apps

---

## 💡 TIPS

### For Best Accuracy
1. Use good microphone (not laptop built-in)
2. Speak clearly at normal pace
3. Minimize background noise
4. Use push-to-talk (space bar)
5. Keep commands under 30 seconds

### For Faster Response
1. Use shorter commands
2. Close unnecessary browser tabs
3. Use text fallback for complex commands
4. Check internet speed

### For Better Experience
1. Learn common commands
2. Use natural language
3. Provide context when needed
4. Give feedback (thumbs up/down)

---

## 🎉 YOU'RE READY!

Voice is now your primary way to interact with Nexus Core.

**Try it**: Just press space bar and say "Help"

**That's it!** You're now using voice to control Nexus Core.

---

## 🆘 NEED HELP?

- **Can't get it working?** Check `VOICE_TROUBLESHOOTING.md`
- **Want more commands?** See `VOICE_COMMANDS_REFERENCE.md`
- **Developer integration?** Read `VOICE_API_REFERENCE.md`
- **Report bugs**: Create issue on GitHub

---

**Status**: 🎤 VOICE READY

**Time to working voice**: ~5 minutes

**Next**: Start using voice commands!

