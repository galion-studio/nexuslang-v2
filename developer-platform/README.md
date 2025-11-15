# 💻 Developer Platform - Full-Featured IDE

**Complete IDE with voice integration and AI assistance**

**URL:** https://dev.galion.studio  
**Port:** 3003

---

## Overview

The Developer Platform is a full-featured web-based IDE that combines traditional development tools with cutting-edge voice commands and AI assistance.

---

## Key Features

### IDE Features
- **Monaco Code Editor** - VS Code-like editing experience
- **Multi-file Support** - Work with multiple files simultaneously
- **Syntax Highlighting** - Support for 100+ languages
- **IntelliSense** - Auto-completion and suggestions
- **Git Integration** - Version control built-in

### Voice Integration
- **Voice Command Bar** - Control IDE with voice
- **Code Dictation** - Write code by speaking
- **Voice Search** - Find files and symbols
- **Audio Feedback** - Hear compilation results

### AI Assistance
- **Agent Integration** - AI agents assist development
- **Code Generation** - Generate code from description
- **Bug Detection** - Auto-detect and suggest fixes
- **Refactoring** - AI-powered code improvements
- **Documentation** - Auto-generate docs

### Terminal
- **Integrated Terminal** - Run commands without leaving IDE
- **Multiple Sessions** - Multiple terminal tabs
- **Command History** - Easy command recall

### File Management
- **File Explorer** - Browse project files
- **Search & Replace** - Find and replace across files
- **File Upload/Download** - Transfer files easily

---

## Tech Stack

- **Framework:** Next.js 14.2.33
- **Editor:** Monaco Editor
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI:** Radix UI, Lucide React
- **Terminal:** xterm.js (planned)

---

## Development

### Install Dependencies
```bash
npm install
```

### Run Development Server
```bash
npm run dev
```

Access at: http://localhost:3003

### Build for Production
```bash
npm run build
npm run start
```

---

## Project Structure

```
developer-platform/
├── app/                       # Next.js app router
│   ├── (dashboard)/          # Dashboard pages
│   │   ├── ide/              # Main IDE interface
│   │   ├── chat/             # AI chat
│   │   └── developers/       # Developer tools
│   │
│   ├── (admin)/              # Admin interface
│   │   └── dev-interface/   # Development interface
│   │
│   ├── layout.tsx            # Root layout
│   └── page.tsx              # Home page
│
├── components/               # React components
│   ├── ide/                  # IDE components
│   │   ├── CodeEditor.tsx    # Main editor
│   │   ├── MonacoEditor.tsx  # Monaco wrapper
│   │   ├── FileExplorer.tsx  # File browser
│   │   ├── Terminal.tsx      # Terminal emulator
│   │   ├── VoiceCommandBar.tsx # Voice controls
│   │   ├── PersonalityEditor.tsx # AI personality
│   │   └── BinaryCompiler.tsx # Code compilation
│   │
│   ├── admin/                # Admin components
│   │   ├── AdminDashboard.tsx
│   │   ├── AgentMonitor.tsx
│   │   ├── AgentPrompt.tsx
│   │   ├── CodeExecutor.tsx
│   │   ├── FileManager.tsx
│   │   ├── TaskManager.tsx
│   │   └── TerminalEmulator.tsx
│   │
│   ├── browser/              # Browser compatibility
│   └── ui/                   # UI components
│
├── lib/                      # Utilities
│   └── utils.ts              # Helper functions
│
└── styles/                   # Styles
    ├── globals.css           # Global styles
    └── browser-compatibility.css # Browser fixes
```

---

## Components

### CodeEditor
Main code editing interface with Monaco integration.

**Usage:**
```typescript
import { CodeEditor } from '@/components/ide/CodeEditor'

<CodeEditor
  language="typescript"
  value={code}
  onChange={setCode}
/>
```

### VoiceCommandBar
Voice command interface for hands-free coding.

**Commands:**
- "Create new file"
- "Open file [name]"
- "Save file"
- "Run code"
- "Format code"

### AgentMonitor
Monitor and manage AI agents helping with development.

### Terminal
Integrated terminal for running commands.

---

## Configuration

### Monaco Editor Settings

Edit `components/ide/MonacoEditor.tsx`:
```typescript
const editorOptions = {
  fontSize: 14,
  theme: 'vs-dark',
  minimap: { enabled: true },
  // Add your settings
}
```

### Voice Commands

Configure in `components/ide/VoiceCommandBar.tsx`:
```typescript
const commands = {
  'new file': createNewFile,
  'save': saveFile,
  // Add your commands
}
```

---

## API Integration

Connect to backend API:

```typescript
const response = await fetch('https://api.galion.studio/api/v1/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'your query' })
})
```

---

## Environment Variables

Required:
```env
NEXT_PUBLIC_API_URL=https://api.galion.studio
```

Optional:
```env
NEXT_PUBLIC_WS_URL=wss://api.galion.studio/ws
NEXT_PUBLIC_ANALYTICS_ID=your_analytics_id
NEXT_PUBLIC_ENABLE_VOICE=true
```

---

## Deployment

### On RunPod:
```bash
cd /nexuslang-v2/developer-platform
pm2 start npm --name developer-platform -- run dev -- -p 3003
```

### Access:
- Local: http://localhost:3003
- Production: https://dev.galion.studio

---

## Troubleshooting

### Monaco Editor Not Loading
- Check if bundle is too large
- Ensure proper imports
- Check browser console for errors

### Voice Commands Not Working
- Verify HTTPS connection
- Check microphone permissions
- Test in Chrome/Edge browser

### Terminal Not Working
- Check WebSocket connection
- Verify backend is running
- Check CORS settings

---

## Browser Support

- ✅ Chrome 90+
- ✅ Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+

**Note:** Voice features require HTTPS and Chrome/Edge for best experience.

---

## Performance

- **Bundle Size:** ~1.5MB (gzipped)
- **First Load:** <2s
- **Time to Interactive:** <3s

---

**Developer Platform - Code with your voice** 💻🎤

