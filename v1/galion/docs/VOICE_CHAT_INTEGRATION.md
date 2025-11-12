# VOICE ↔ CHAT INTEGRATION

**Seamless Handoff Between Voice and Text**

**Version:** 1.0  
**Date:** November 9, 2025  
**Status:** Alpha Phase

---

## MISSION

Enable users to switch seamlessly between voice and text input without losing context or conversation flow.

**Key Requirements:**
- Single conversation thread (voice + text mixed)
- Context preservation across modalities
- Real-time synchronization
- Graceful fallback (voice → text if STT fails)

---

## ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    CLIENT (Browser)                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User Input                                                 │
│      ↓                                                      │
│  ┌─────────────┐         ┌─────────────┐                  │
│  │   Voice     │         │    Text     │                  │
│  │   Button    │         │    Input    │                  │
│  └─────────────┘         └─────────────┘                  │
│      ↓                         ↓                            │
│  ┌─────────────────────────────────────┐                  │
│  │    Unified Message Queue            │                  │
│  │    (Local State)                    │                  │
│  └─────────────────────────────────────┘                  │
│      ↓                                                      │
│  ┌─────────────────────────────────────┐                  │
│  │    WebSocket Connection             │                  │
│  │    (Socket.IO)                      │                  │
│  └─────────────────────────────────────┘                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│                    SERVER (Voice Service)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────┐                  │
│  │    WebSocket Handler                │                  │
│  │    (FastAPI + Socket.IO)            │                  │
│  └─────────────────────────────────────┘                  │
│      ↓                                                      │
│  ┌─────────────────────────────────────┐                  │
│  │    Message Router                   │                  │
│  │    (Voice or Text?)                 │                  │
│  └─────────────────────────────────────┘                  │
│      ↓              ↓                                       │
│  ┌─────────┐   ┌─────────┐                                │
│  │  Voice  │   │  Text   │                                │
│  │Pipeline │   │Pipeline │                                │
│  └─────────┘   └─────────┘                                │
│      ↓              ↓                                       │
│  ┌─────────────────────────────────────┐                  │
│  │    Unified Response Generator       │                  │
│  │    (Llama 3.1 8B + RAG)             │                  │
│  └─────────────────────────────────────┘                  │
│      ↓                                                      │
│  ┌─────────────────────────────────────┐                  │
│  │    Response Formatter               │                  │
│  │    (Text + Audio)                   │                  │
│  └─────────────────────────────────────┘                  │
│      ↓                                                      │
│  WebSocket → Client                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## WEBSOCKET PROTOCOL

### Connection

**Client → Server:**
```json
{
  "event": "connect",
  "data": {
    "token": "jwt_token_here",
    "session_id": "uuid",
    "capabilities": ["voice", "text"],
    "preferences": {
      "tts_enabled": true,
      "voice_id": "default",
      "language": "en"
    }
  }
}
```

**Server → Client:**
```json
{
  "event": "connected",
  "data": {
    "session_id": "uuid",
    "server_capabilities": ["stt", "tts", "rag"],
    "latency_estimate_ms": 1500
  }
}
```

### Voice Message

**Client → Server:**
```json
{
  "event": "voice_message",
  "data": {
    "session_id": "uuid",
    "message_id": "uuid",
    "audio": "base64_encoded_audio",
    "format": "webm",
    "sample_rate": 16000,
    "duration_ms": 3500,
    "timestamp": "2025-11-09T10:30:00Z"
  }
}
```

**Server → Client (Transcript):**
```json
{
  "event": "transcript",
  "data": {
    "message_id": "uuid",
    "text": "What is the speed of light?",
    "confidence": 0.95,
    "language": "en",
    "timestamp": "2025-11-09T10:30:01Z"
  }
}
```

**Server → Client (Response):**
```json
{
  "event": "response",
  "data": {
    "message_id": "uuid",
    "text": "The speed of light in vacuum is 299,792,458 m/s...",
    "audio": "base64_encoded_audio",  // Optional (if TTS enabled)
    "sources": [
      {
        "id": "source_1",
        "title": "Physics Textbook",
        "url": "https://...",
        "relevance": 0.95
      }
    ],
    "confidence": 0.92,
    "latency_ms": 1850,
    "timestamp": "2025-11-09T10:30:03Z"
  }
}
```

### Text Message

**Client → Server:**
```json
{
  "event": "text_message",
  "data": {
    "session_id": "uuid",
    "message_id": "uuid",
    "text": "What is quantum entanglement?",
    "timestamp": "2025-11-09T10:31:00Z"
  }
}
```

**Server → Client (Response):**
```json
{
  "event": "response",
  "data": {
    "message_id": "uuid",
    "text": "Quantum entanglement is a phenomenon where...",
    "audio": null,  // No audio for text-only
    "sources": [...],
    "confidence": 0.88,
    "latency_ms": 1200,
    "timestamp": "2025-11-09T10:31:02Z"
  }
}
```

### Streaming Response

**Server → Client (Chunks):**
```json
{
  "event": "response_chunk",
  "data": {
    "message_id": "uuid",
    "chunk": "The speed of light",
    "chunk_index": 0,
    "is_final": false
  }
}
```

```json
{
  "event": "response_chunk",
  "data": {
    "message_id": "uuid",
    "chunk": " in vacuum is 299,792,458 m/s.",
    "chunk_index": 1,
    "is_final": true
  }
}
```

### Error Handling

**Server → Client:**
```json
{
  "event": "error",
  "data": {
    "message_id": "uuid",
    "error_code": "STT_FAILED",
    "error_message": "Could not transcribe audio. Please try again or use text input.",
    "fallback": "text",
    "timestamp": "2025-11-09T10:30:01Z"
  }
}
```

---

## SESSION MANAGEMENT

### Session State

**Stored in Redis:**
```json
{
  "session_id": "uuid",
  "user_id": "user_uuid",
  "created_at": "2025-11-09T10:00:00Z",
  "last_activity": "2025-11-09T10:30:00Z",
  "messages": [
    {
      "id": "msg_1",
      "role": "user",
      "content": "What is the speed of light?",
      "modality": "voice",
      "timestamp": "2025-11-09T10:30:00Z"
    },
    {
      "id": "msg_2",
      "role": "assistant",
      "content": "The speed of light in vacuum is...",
      "modality": "text",
      "sources": [...],
      "timestamp": "2025-11-09T10:30:03Z"
    }
  ],
  "context": {
    "domain": "physics",
    "entities": ["speed_of_light", "vacuum"],
    "intent": "factual_query"
  },
  "preferences": {
    "tts_enabled": true,
    "voice_id": "default"
  }
}
```

**TTL:** 1 hour (extend on activity)

### Context Preservation

**Problem:** User switches from voice to text mid-conversation. How do we preserve context?

**Solution:** Unified conversation history

**Example:**
```
User (voice): "What is the speed of light?"
Nexus (text + audio): "The speed of light is 299,792,458 m/s."

User (text): "How was this measured?"
Nexus (text): "The speed of light was first measured by..."
```

**Context Window:**
- Last 10 messages (voice + text combined)
- Max 4k tokens for Llama 3.1 8B
- Summarize older messages if context exceeds limit

---

## CLIENT IMPLEMENTATION

### React Hook: `useVoiceChat`

```typescript
import { useEffect, useState } from 'react';
import { io, Socket } from 'socket.io-client';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  modality: 'voice' | 'text';
  sources?: Source[];
  timestamp: string;
}

export const useVoiceChat = (token: string) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  
  useEffect(() => {
    // Connect to WebSocket
    const newSocket = io('wss://galion.app/voice', {
      auth: { token },
      transports: ['websocket']
    });
    
    newSocket.on('connect', () => {
      setIsConnected(true);
      console.log('Connected to voice service');
    });
    
    newSocket.on('disconnect', () => {
      setIsConnected(false);
      console.log('Disconnected from voice service');
    });
    
    newSocket.on('transcript', (data) => {
      // Add user message (transcribed)
      setMessages(prev => [...prev, {
        id: data.message_id,
        role: 'user',
        content: data.text,
        modality: 'voice',
        timestamp: data.timestamp
      }]);
      setIsListening(false);
      setIsThinking(true);
    });
    
    newSocket.on('response', (data) => {
      // Add assistant message
      setMessages(prev => [...prev, {
        id: data.message_id,
        role: 'assistant',
        content: data.text,
        modality: 'text',
        sources: data.sources,
        timestamp: data.timestamp
      }]);
      setIsThinking(false);
      
      // Play audio if available
      if (data.audio) {
        playAudio(data.audio);
      }
    });
    
    newSocket.on('error', (data) => {
      console.error('Error:', data.error_message);
      setIsListening(false);
      setIsThinking(false);
      
      // Show error to user
      alert(data.error_message);
    });
    
    setSocket(newSocket);
    
    return () => {
      newSocket.close();
    };
  }, [token]);
  
  const sendVoiceMessage = async (audioBlob: Blob) => {
    if (!socket) return;
    
    setIsListening(false);
    setIsThinking(true);
    
    // Convert to base64
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = reader.result?.toString().split(',')[1];
      
      socket.emit('voice_message', {
        session_id: sessionStorage.getItem('session_id'),
        message_id: generateUUID(),
        audio: base64,
        format: 'webm',
        sample_rate: 16000,
        duration_ms: audioBlob.size / 32,  // Approximate
        timestamp: new Date().toISOString()
      });
    };
    reader.readAsDataURL(audioBlob);
  };
  
  const sendTextMessage = (text: string) => {
    if (!socket) return;
    
    setIsThinking(true);
    
    // Add user message immediately
    const messageId = generateUUID();
    setMessages(prev => [...prev, {
      id: messageId,
      role: 'user',
      content: text,
      modality: 'text',
      timestamp: new Date().toISOString()
    }]);
    
    socket.emit('text_message', {
      session_id: sessionStorage.getItem('session_id'),
      message_id: messageId,
      text,
      timestamp: new Date().toISOString()
    });
  };
  
  return {
    messages,
    isConnected,
    isListening,
    isThinking,
    sendVoiceMessage,
    sendTextMessage,
    setIsListening
  };
};
```

### Usage in Component

```typescript
const ChatInterface = () => {
  const { 
    messages, 
    isConnected, 
    isListening, 
    isThinking,
    sendVoiceMessage, 
    sendTextMessage,
    setIsListening
  } = useVoiceChat(token);
  
  const [textInput, setTextInput] = useState('');
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);
  
  const handleVoiceStart = async () => {
    setIsListening(true);
    
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder.current = new MediaRecorder(stream);
    
    mediaRecorder.current.ondataavailable = (event) => {
      audioChunks.current.push(event.data);
    };
    
    mediaRecorder.current.onstop = () => {
      const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' });
      sendVoiceMessage(audioBlob);
      audioChunks.current = [];
    };
    
    mediaRecorder.current.start();
  };
  
  const handleVoiceStop = () => {
    if (mediaRecorder.current) {
      mediaRecorder.current.stop();
      mediaRecorder.current.stream.getTracks().forEach(track => track.stop());
    }
  };
  
  const handleTextSubmit = () => {
    if (textInput.trim()) {
      sendTextMessage(textInput);
      setTextInput('');
    }
  };
  
  return (
    <div className="chat-interface">
      <div className="messages">
        {messages.map(msg => (
          <ChatMessage key={msg.id} message={msg} />
        ))}
        {isThinking && <ThinkingIndicator />}
      </div>
      
      <div className="input-area">
        <button
          onMouseDown={handleVoiceStart}
          onMouseUp={handleVoiceStop}
          disabled={!isConnected || isThinking}
        >
          {isListening ? '🎤 Listening...' : '🎤 Hold to Speak'}
        </button>
        
        <input
          type="text"
          value={textInput}
          onChange={(e) => setTextInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleTextSubmit()}
          placeholder="Or type your question..."
          disabled={!isConnected || isThinking}
        />
        
        <button onClick={handleTextSubmit} disabled={!isConnected || isThinking}>
          Send
        </button>
      </div>
    </div>
  );
};
```

---

## SERVER IMPLEMENTATION

### WebSocket Handler (FastAPI + Socket.IO)

```python
from fastapi import FastAPI
from fastapi_socketio import SocketManager
import base64
import uuid

app = FastAPI()
sio = SocketManager(app=app, cors_allowed_origins='*')

@sio.on('connect')
async def handle_connect(sid, environ, auth):
    # Verify JWT token
    token = auth.get('token')
    user = verify_token(token)
    
    if not user:
        return False  # Reject connection
    
    # Create session
    session_id = str(uuid.uuid4())
    await redis.setex(
        f'session:{session_id}',
        3600,  # 1 hour TTL
        json.dumps({
            'user_id': user.id,
            'created_at': datetime.now().isoformat(),
            'messages': []
        })
    )
    
    await sio.emit('connected', {
        'session_id': session_id,
        'server_capabilities': ['stt', 'tts', 'rag'],
        'latency_estimate_ms': 1500
    }, to=sid)
    
    return True

@sio.on('voice_message')
async def handle_voice_message(sid, data):
    try:
        # Decode audio
        audio_bytes = base64.b64decode(data['audio'])
        
        # Save to temp file
        temp_file = f'/tmp/{data["message_id"]}.webm'
        with open(temp_file, 'wb') as f:
            f.write(audio_bytes)
        
        # Transcribe (STT)
        transcript = await stt_service.transcribe(temp_file)
        
        # Send transcript to client
        await sio.emit('transcript', {
            'message_id': data['message_id'],
            'text': transcript['text'],
            'confidence': transcript['confidence'],
            'language': 'en',
            'timestamp': datetime.now().isoformat()
        }, to=sid)
        
        # Generate response
        response = await generate_response(
            session_id=data['session_id'],
            user_message=transcript['text'],
            modality='voice'
        )
        
        # TTS (if enabled)
        audio_base64 = None
        if response.get('tts_enabled'):
            audio_bytes = await tts_service.synthesize(response['text'])
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        # Send response to client
        await sio.emit('response', {
            'message_id': data['message_id'],
            'text': response['text'],
            'audio': audio_base64,
            'sources': response['sources'],
            'confidence': response['confidence'],
            'latency_ms': response['latency_ms'],
            'timestamp': datetime.now().isoformat()
        }, to=sid)
        
    except Exception as e:
        await sio.emit('error', {
            'message_id': data['message_id'],
            'error_code': 'STT_FAILED',
            'error_message': str(e),
            'fallback': 'text',
            'timestamp': datetime.now().isoformat()
        }, to=sid)

@sio.on('text_message')
async def handle_text_message(sid, data):
    try:
        # Generate response
        response = await generate_response(
            session_id=data['session_id'],
            user_message=data['text'],
            modality='text'
        )
        
        # Send response to client
        await sio.emit('response', {
            'message_id': data['message_id'],
            'text': response['text'],
            'audio': None,  # No audio for text-only
            'sources': response['sources'],
            'confidence': response['confidence'],
            'latency_ms': response['latency_ms'],
            'timestamp': datetime.now().isoformat()
        }, to=sid)
        
    except Exception as e:
        await sio.emit('error', {
            'message_id': data['message_id'],
            'error_code': 'GENERATION_FAILED',
            'error_message': str(e),
            'timestamp': datetime.now().isoformat()
        }, to=sid)

async def generate_response(session_id: str, user_message: str, modality: str):
    # Get session context
    session = await redis.get(f'session:{session_id}')
    session_data = json.loads(session)
    
    # Add user message to history
    session_data['messages'].append({
        'role': 'user',
        'content': user_message,
        'modality': modality,
        'timestamp': datetime.now().isoformat()
    })
    
    # Build context (last 10 messages)
    context = session_data['messages'][-10:]
    
    # RAG retrieval
    sources = await rag_service.retrieve(user_message, top_k=5)
    
    # Generate response
    start_time = time.time()
    response_text = await llm_service.generate(
        query=user_message,
        context=context,
        sources=sources
    )
    latency_ms = int((time.time() - start_time) * 1000)
    
    # Add assistant message to history
    session_data['messages'].append({
        'role': 'assistant',
        'content': response_text,
        'modality': 'text',
        'sources': sources,
        'timestamp': datetime.now().isoformat()
    })
    
    # Update session in Redis
    await redis.setex(
        f'session:{session_id}',
        3600,
        json.dumps(session_data)
    )
    
    return {
        'text': response_text,
        'sources': sources,
        'confidence': 0.9,  # Placeholder
        'latency_ms': latency_ms,
        'tts_enabled': session_data['preferences'].get('tts_enabled', False)
    }
```

---

## FALLBACK STRATEGIES

### Voice → Text Fallback

**Trigger:** STT fails (low confidence, no speech detected, network error)

**Action:**
1. Show error message: "Could not transcribe. Please try again or type your question."
2. Highlight text input field
3. Keep voice button available (user can retry)

### Text → Voice Fallback

**Trigger:** TTS fails (model error, network error)

**Action:**
1. Show response as text only
2. Add "🔊 Listen" button (user can retry TTS)
3. Log error for debugging

### Network Fallback

**Trigger:** WebSocket disconnects

**Action:**
1. Show "Reconnecting..." indicator
2. Retry connection (exponential backoff: 1s, 2s, 4s, 8s)
3. After 5 retries, show "Offline. Please check your connection."
4. Queue messages locally (send when reconnected)

---

## TESTING

### Unit Tests

```python
# Test STT → Text → TTS pipeline
def test_voice_to_text_to_voice():
    # Send voice message
    audio = load_test_audio('what_is_light.webm')
    response = client.emit('voice_message', {'audio': audio})
    
    # Assert transcript
    assert response['transcript']['text'] == 'What is the speed of light?'
    
    # Assert response has audio
    assert response['response']['audio'] is not None

# Test text-only pipeline
def test_text_only():
    response = client.emit('text_message', {'text': 'What is quantum entanglement?'})
    
    # Assert response has no audio
    assert response['response']['audio'] is None
```

### Integration Tests

```python
# Test context preservation across modalities
def test_context_preservation():
    # Voice message
    client.emit('voice_message', {'audio': load_test_audio('what_is_light.webm')})
    response1 = client.wait_for('response')
    
    # Text follow-up
    client.emit('text_message', {'text': 'How was this measured?'})
    response2 = client.wait_for('response')
    
    # Assert response2 references "speed of light" from response1
    assert 'speed of light' in response2['text'].lower()
```

---

## NEXT STEPS

1. **This Week:**
   - Implement WebSocket protocol
   - Build React hook `useVoiceChat`
   - Test voice → text → voice flow

2. **Next Week:**
   - Add streaming responses
   - Implement fallback strategies
   - Load testing (100 concurrent users)

3. **Next Month:**
   - Multi-language support
   - Voice activity detection (VAD)
   - Noise cancellation

---

**Built with First Principles**  
**Status:** Ready to Integrate  
**Let's connect voice and chat.** 🔗

