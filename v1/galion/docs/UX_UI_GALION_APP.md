# UX/UI PLAN – GALION.APP

**Dark Minimal Design + Voice-First Interaction**

**Version:** 1.0  
**Date:** November 9, 2025  
**Status:** Alpha Phase

---

## DESIGN PHILOSOPHY

**Core Principles:**
1. **Voice-First:** Voice is the primary interaction method, not an afterthought
2. **Dark by Default:** Reduce eye strain, modern aesthetic
3. **Minimal:** Remove clutter, focus on content
4. **Transparent:** Show sources, reasoning, confidence
5. **Fast:** Instant feedback, no loading spinners
6. **Accessible:** WCAG 2.1 AA compliance

**Inspiration:**
- ChatGPT (clean chat interface)
- Perplexity (sources panel)
- Linear (minimal, fast)
- Arc Browser (modern, dark)
- JARVIS from Iron Man (voice-first)

---

## COLOR PALETTE

### Dark Theme (Primary)

**Background:**
- `bg-primary`: `#0A0A0A` (near black)
- `bg-secondary`: `#1A1A1A` (slightly lighter)
- `bg-tertiary`: `#2A2A2A` (cards, panels)
- `bg-hover`: `#3A3A3A` (hover states)

**Text:**
- `text-primary`: `#FFFFFF` (white, high contrast)
- `text-secondary`: `#A0A0A0` (gray, less important)
- `text-tertiary`: `#707070` (gray, metadata)
- `text-muted`: `#505050` (gray, disabled)

**Accent:**
- `accent-primary`: `#00D9FF` (cyan, primary actions)
- `accent-secondary`: `#FF006E` (magenta, secondary actions)
- `accent-success`: `#00FF88` (green, success states)
- `accent-warning`: `#FFB800` (yellow, warnings)
- `accent-error`: `#FF3B3B` (red, errors)

**Voice Indicator:**
- `voice-listening`: `#00D9FF` (cyan, pulsing)
- `voice-thinking`: `#FF006E` (magenta, animated)
- `voice-speaking`: `#00FF88` (green, waveform)

### Light Theme (Optional)

**Background:**
- `bg-primary`: `#FFFFFF`
- `bg-secondary`: `#F5F5F5`
- `bg-tertiary`: `#E5E5E5`

**Text:**
- `text-primary`: `#0A0A0A`
- `text-secondary`: `#505050`

(Same accent colors)

---

## TYPOGRAPHY

**Font Family:**
- Primary: `Inter` (clean, modern, open source)
- Monospace: `JetBrains Mono` (code blocks)

**Font Sizes:**
- `text-xs`: 12px (metadata, labels)
- `text-sm`: 14px (body text)
- `text-base`: 16px (default)
- `text-lg`: 18px (headings)
- `text-xl`: 24px (page titles)
- `text-2xl`: 32px (hero text)

**Font Weights:**
- `font-normal`: 400 (body text)
- `font-medium`: 500 (emphasis)
- `font-semibold`: 600 (headings)
- `font-bold`: 700 (strong emphasis)

**Line Height:**
- `leading-tight`: 1.25 (headings)
- `leading-normal`: 1.5 (body text)
- `leading-relaxed`: 1.75 (long-form content)

---

## LAYOUT

### Main Interface

```
┌──────────────────────────────────────────────────────────────┐
│  Galion.app                          [Profile] [Settings]    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                                                        │ │
│  │                  CHAT PANEL                            │ │
│  │                                                        │ │
│  │  User: What is the speed of light?                    │ │
│  │                                                        │ │
│  │  Nexus: The speed of light in vacuum is               │ │
│  │  299,792,458 m/s (approximately 3×10⁸ m/s).          │ │
│  │                                                        │ │
│  │  Sources: [1] [2] [3]                                 │ │
│  │                                                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  [🎤 Hold to Speak]  or  [Type your question...]      │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────────────────────┐ │
│  │  SOURCES PANEL   │  │  VOICE PANEL                     │ │
│  │                  │  │                                  │ │
│  │  [1] Physics     │  │  🎤 Listening...                │ │
│  │      Textbook    │  │                                  │ │
│  │                  │  │  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │ │
│  │  [2] Wikipedia   │  │                                  │ │
│  │      Light       │  │  "What is the speed of light?"  │ │
│  │                  │  │                                  │ │
│  │  [3] arXiv       │  │  Confidence: 95%                │ │
│  │      Paper       │  │  Latency: 1.8s                  │ │
│  │                  │  │                                  │ │
│  └──────────────────┘  └──────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Responsive Breakpoints

- **Mobile:** < 640px (single column, voice-only)
- **Tablet:** 640px - 1024px (stacked panels)
- **Desktop:** > 1024px (side-by-side panels)

---

## COMPONENTS

### 1. Voice Button

**States:**

**Idle:**
```
┌─────────────────────────┐
│   🎤  Hold to Speak     │
└─────────────────────────┘
```

**Listening:**
```
┌─────────────────────────┐
│   🎤  Listening...      │
│   ━━━━━━━━━━━━━━━━━━━  │  ← Animated waveform
└─────────────────────────┘
```

**Thinking:**
```
┌─────────────────────────┐
│   🧠  Thinking...       │
│   ⟳ ⟳ ⟳                 │  ← Spinning dots
└─────────────────────────┘
```

**Speaking:**
```
┌─────────────────────────┐
│   🔊  Speaking...       │
│   ━━━━━━━━━━━━━━━━━━━  │  ← Animated waveform
└─────────────────────────┘
```

**Implementation:**
```tsx
const VoiceButton = () => {
  const [state, setState] = useState<'idle' | 'listening' | 'thinking' | 'speaking'>('idle');
  
  const handleMouseDown = () => {
    setState('listening');
    startRecording();
  };
  
  const handleMouseUp = () => {
    setState('thinking');
    stopRecording();
    sendToServer();
  };
  
  return (
    <button
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      className={`voice-button voice-button--${state}`}
    >
      {state === 'idle' && '🎤 Hold to Speak'}
      {state === 'listening' && (
        <>
          🎤 Listening...
          <Waveform active />
        </>
      )}
      {state === 'thinking' && (
        <>
          🧠 Thinking...
          <Spinner />
        </>
      )}
      {state === 'speaking' && (
        <>
          🔊 Speaking...
          <Waveform active />
        </>
      )}
    </button>
  );
};
```

### 2. Chat Message

**User Message:**
```
┌─────────────────────────────────────┐
│  You                         10:30  │
│  What is the speed of light?        │
└─────────────────────────────────────┘
```

**Nexus Response:**
```
┌─────────────────────────────────────┐
│  Nexus                       10:30  │
│                                     │
│  The speed of light in vacuum is    │
│  299,792,458 m/s (≈ 3×10⁸ m/s).   │
│                                     │
│  This is a fundamental constant in  │
│  physics, denoted by 'c'.           │
│                                     │
│  Sources: [1] [2] [3]              │
│  Confidence: 95%                    │
│                                     │
│  [👍] [👎] [🔊 Listen]             │
└─────────────────────────────────────┘
```

**Implementation:**
```tsx
const ChatMessage = ({ message, role, sources, confidence }) => {
  return (
    <div className={`chat-message chat-message--${role}`}>
      <div className="chat-message__header">
        <span className="chat-message__author">{role === 'user' ? 'You' : 'Nexus'}</span>
        <span className="chat-message__time">{formatTime(message.timestamp)}</span>
      </div>
      
      <div className="chat-message__content">
        <Markdown>{message.content}</Markdown>
      </div>
      
      {role === 'assistant' && (
        <>
          <div className="chat-message__sources">
            Sources: {sources.map((s, i) => (
              <a key={i} href={s.url} className="source-link">[{i + 1}]</a>
            ))}
          </div>
          
          <div className="chat-message__metadata">
            Confidence: {confidence}%
          </div>
          
          <div className="chat-message__actions">
            <button onClick={() => feedback('up')}>👍</button>
            <button onClick={() => feedback('down')}>👎</button>
            <button onClick={() => speakResponse(message.content)}>🔊 Listen</button>
          </div>
        </>
      )}
    </div>
  );
};
```

### 3. Sources Panel

**Collapsed:**
```
┌─────────────────────────┐
│  Sources (3)      [▼]   │
└─────────────────────────┘
```

**Expanded:**
```
┌─────────────────────────────────────┐
│  Sources (3)                  [▲]   │
├─────────────────────────────────────┤
│  [1] Physics Textbook               │
│      OpenStax Physics, Chapter 1    │
│      Relevance: 95%                 │
│      [View] [Cite]                  │
│                                     │
│  [2] Wikipedia: Speed of Light      │
│      en.wikipedia.org/wiki/...      │
│      Relevance: 88%                 │
│      [View] [Cite]                  │
│                                     │
│  [3] arXiv:2301.12345               │
│      "Measurement of c in vacuum"   │
│      Relevance: 82%                 │
│      [View] [Cite]                  │
└─────────────────────────────────────┘
```

**Implementation:**
```tsx
const SourcesPanel = ({ sources }) => {
  const [expanded, setExpanded] = useState(true);
  
  return (
    <div className="sources-panel">
      <div className="sources-panel__header" onClick={() => setExpanded(!expanded)}>
        <h3>Sources ({sources.length})</h3>
        <button>{expanded ? '▲' : '▼'}</button>
      </div>
      
      {expanded && (
        <div className="sources-panel__list">
          {sources.map((source, i) => (
            <div key={i} className="source-item">
              <div className="source-item__number">[{i + 1}]</div>
              <div className="source-item__content">
                <h4>{source.title}</h4>
                <p>{source.snippet}</p>
                <div className="source-item__metadata">
                  Relevance: {source.relevance}%
                </div>
                <div className="source-item__actions">
                  <a href={source.url} target="_blank">View</a>
                  <button onClick={() => copyCitation(source)}>Cite</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
```

### 4. Voice Waveform

**Animated Waveform:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ▁▃▅▇█▇▅▃▁  ▁▃▅▇█▇▅▃▁  ▁▃▅▇█▇▅▃▁
```

**Implementation:**
```tsx
const Waveform = ({ active, audioData }) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  
  useEffect(() => {
    if (!active) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    const draw = () => {
      // Clear canvas
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      // Draw waveform
      ctx.strokeStyle = '#00D9FF';
      ctx.lineWidth = 2;
      ctx.beginPath();
      
      const sliceWidth = canvas.width / audioData.length;
      let x = 0;
      
      for (let i = 0; i < audioData.length; i++) {
        const v = audioData[i] / 128.0;
        const y = v * canvas.height / 2;
        
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
        
        x += sliceWidth;
      }
      
      ctx.stroke();
      
      requestAnimationFrame(draw);
    };
    
    draw();
  }, [active, audioData]);
  
  return <canvas ref={canvasRef} className="waveform" />;
};
```

---

## USER FLOWS

### Flow 1: Voice Query

```
User opens app
  ↓
Sees chat interface + voice button
  ↓
Holds voice button (spacebar or mouse)
  ↓
Microphone activates, waveform animates
  ↓
User speaks: "What is the speed of light?"
  ↓
User releases button
  ↓
Transcript appears in chat
  ↓
"Thinking..." indicator shows
  ↓
Response streams in (word by word)
  ↓
Sources panel updates with citations
  ↓
TTS speaks response (optional)
  ↓
User can give feedback (👍/👎)
```

### Flow 2: Text Query

```
User opens app
  ↓
Types in text input: "What is quantum entanglement?"
  ↓
Presses Enter
  ↓
Message appears in chat
  ↓
"Thinking..." indicator shows
  ↓
Response streams in
  ↓
Sources panel updates
  ↓
User can click "🔊 Listen" to hear response
```

### Flow 3: Source Exploration

```
User receives response with sources
  ↓
Clicks "[1]" in sources list
  ↓
Source details expand (title, snippet, relevance)
  ↓
User clicks "View"
  ↓
Opens source in new tab (PDF, webpage, etc.)
  ↓
User returns to chat
  ↓
Asks follow-up: "Tell me more about this"
```

### Flow 4: 3D Model Query

```
User asks: "Show me a model of a benzene molecule"
  ↓
Response includes 3D model viewer
  ↓
User can rotate, zoom, pan model
  ↓
Metadata shown: Formula, molecular weight, etc.
  ↓
User asks: "What's the bond angle?"
  ↓
Response highlights relevant bonds in 3D
```

---

## ACCESSIBILITY

### WCAG 2.1 AA Compliance

**Color Contrast:**
- Text on background: 7:1 (AAA level)
- Interactive elements: 4.5:1 (AA level)
- Focus indicators: 3:1 (AA level)

**Keyboard Navigation:**
- Tab order: Logical (top to bottom, left to right)
- Focus visible: 2px cyan outline
- Shortcuts:
  - `Space`: Hold to speak (voice button)
  - `Enter`: Send message (text input)
  - `Esc`: Cancel voice recording
  - `Ctrl+K`: Focus search
  - `Ctrl+/`: Show shortcuts

**Screen Reader Support:**
- ARIA labels on all interactive elements
- Live regions for dynamic content (chat messages)
- Alt text on images (3D model thumbnails)
- Semantic HTML (headings, lists, buttons)

**Voice-Only Mode:**
- Entire interface controllable by voice
- Commands: "Send message", "Show sources", "Read response"
- Confirmation: "Message sent", "Sources shown"

---

## ANIMATIONS

### Micro-Interactions

**Button Hover:**
- Scale: 1.05
- Duration: 150ms
- Easing: ease-out

**Button Click:**
- Scale: 0.95
- Duration: 100ms
- Easing: ease-in

**Message Appear:**
- Fade in + slide up
- Duration: 300ms
- Easing: ease-out

**Waveform:**
- Continuous animation
- FPS: 60
- Smooth interpolation

### Loading States

**Skeleton Screens:**
- Show placeholder content while loading
- Pulse animation (opacity 0.5 → 1.0)
- Duration: 1.5s loop

**Progress Indicators:**
- Circular spinner for indeterminate tasks
- Linear progress bar for determinate tasks (file upload)

---

## DESIGN SYSTEM

### Spacing Scale

- `space-1`: 4px
- `space-2`: 8px
- `space-3`: 12px
- `space-4`: 16px
- `space-6`: 24px
- `space-8`: 32px
- `space-12`: 48px
- `space-16`: 64px

### Border Radius

- `rounded-sm`: 4px (buttons, inputs)
- `rounded-md`: 8px (cards, panels)
- `rounded-lg`: 12px (modals)
- `rounded-full`: 9999px (avatars, pills)

### Shadows

- `shadow-sm`: 0 1px 2px rgba(0,0,0,0.05)
- `shadow-md`: 0 4px 6px rgba(0,0,0,0.1)
- `shadow-lg`: 0 10px 15px rgba(0,0,0,0.2)
- `shadow-xl`: 0 20px 25px rgba(0,0,0,0.3)

---

## IMPLEMENTATION

### Tech Stack

- **Framework:** React 18 + TypeScript
- **Styling:** Tailwind CSS 3
- **State:** Zustand (lightweight)
- **WebSocket:** Socket.IO client
- **Audio:** Web Audio API
- **3D:** Three.js + React Three Fiber
- **Markdown:** react-markdown
- **Code Highlighting:** Prism.js

### File Structure

```
src/
├── components/
│   ├── Chat/
│   │   ├── ChatMessage.tsx
│   │   ├── ChatInput.tsx
│   │   └── ChatPanel.tsx
│   ├── Voice/
│   │   ├── VoiceButton.tsx
│   │   ├── Waveform.tsx
│   │   └── VoicePanel.tsx
│   ├── Sources/
│   │   ├── SourcesPanel.tsx
│   │   ├── SourceItem.tsx
│   │   └── SourceViewer.tsx
│   └── 3D/
│       ├── ModelViewer.tsx
│       └── ModelControls.tsx
├── hooks/
│   ├── useVoice.ts
│   ├── useChat.ts
│   └── useSources.ts
├── stores/
│   ├── chatStore.ts
│   ├── voiceStore.ts
│   └── userStore.ts
├── utils/
│   ├── audio.ts
│   ├── websocket.ts
│   └── formatting.ts
└── styles/
    ├── globals.css
    └── themes.css
```

---

## NEXT STEPS

1. **This Week:**
   - Design mockups in Figma
   - Build component library (Storybook)
   - Implement voice button + waveform

2. **Next Week:**
   - Implement chat interface
   - Integrate WebSocket for real-time
   - Add sources panel

3. **Next Month:**
   - 3D model viewer
   - Accessibility audit
   - User testing (10 beta testers)

---

**Built with First Principles**  
**Status:** Ready to Design  
**Let's build a beautiful UI.** 🎨

