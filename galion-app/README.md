# 🎨 Galion Frontend

Voice-first React application with no traditional UI - just a pulsing orb and voice interaction.

## Features

- 🎤 **Voice-Only Interface** - No keyboard, no mouse, pure voice
- 🎯 **Pulsing Orb** - Visual feedback that reacts to audio levels
- 🔄 **Real-Time Streaming** - WebSocket-based voice communication
- 📱 **Responsive Design** - Works on desktop and mobile
- 🌙 **Dark Theme** - True black background for immersion
- ⚡ **Next.js 14** - Modern React framework with App Router
- 🎨 **Framer Motion** - Smooth animations and transitions
- 🔒 **TypeScript** - Type-safe development

## Quick Start

### Using Docker (Recommended)

```bash
cd galion-app
docker build -t galion-frontend .
docker run -p 3003:3000 galion-frontend
```

### Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Open http://localhost:3003
```

## Project Structure

```
galion-app/
├── app/                    # Next.js App Router
│   ├── globals.css         # Global styles (true black theme)
│   ├── layout.tsx          # Root layout
│   └── page.tsx            # Home page (voice interface)
├── components/             # React components
│   └── voice/              # Voice-related components
│       └── VoiceOnlyInterface.tsx
├── lib/                    # Utility libraries
│   └── voice/              # Voice API client
│       └── voice-api-client.ts
├── public/                 # Static assets
├── styles/                 # Additional styles
└── docs/                   # Documentation
```

## Voice Interface

### The Orb

The central pulsing orb provides visual feedback:

- **Idle**: Subtle pulse, waiting for user input
- **Listening**: Bright pulse synchronized with audio levels
- **Processing**: Rapid pulse while AI processes
- **Speaking**: Smooth animation while AI responds

### Interaction Flow

1. **Page Load**: Orb appears with gentle pulse
2. **Microphone Request**: Browser asks for microphone permission
3. **Voice Detection**: Orb reacts to audio input levels
4. **AI Processing**: Visual feedback during processing
5. **Voice Response**: AI speaks back through speakers

## Configuration

### Environment Variables

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# Development
NODE_ENV=development
```

### API Integration

The frontend connects to the backend via:

- **REST API**: `NEXT_PUBLIC_API_URL`
- **WebSocket**: `NEXT_PUBLIC_WS_URL`

## Development

### Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run format       # Format code with Prettier

# Testing
npm test            # Run Jest tests
npm run test:watch  # Watch mode tests
npm run test:coverage # Test coverage report
```

### Code Quality

```bash
# Lint code
npm run lint

# Format code
npm run format

# Type checking
npm run type-check
```

## Voice API Client

### WebSocket Integration

```typescript
import { VoiceApiClient } from '@/lib/voice/voice-api-client';

const client = new VoiceApiClient();

// Connect to voice API
await client.connect();

// Send audio data
client.sendAudioChunk(audioData);

// Handle responses
client.onTranscription((text) => {
  console.log('Transcribed:', text);
});

client.onAiResponse((text, audio) => {
  console.log('AI Response:', text);
  // Play audio response
});
```

### Message Types

#### Outgoing Messages

```typescript
interface AudioChunkMessage {
  type: 'audio_chunk';
  audio: string;        // Base64 encoded audio
  format: string;       // 'webm', 'wav', etc.
  sampleRate: number;   // Audio sample rate
}
```

#### Incoming Messages

```typescript
interface TranscriptionMessage {
  type: 'transcription';
  text: string;
}

interface AiResponseMessage {
  type: 'ai_response';
  text: string;
  audio?: string;       // Base64 encoded audio response
}

interface ErrorMessage {
  type: 'error';
  message: string;
}
```

## Styling

### Global Theme

The application uses a true black theme:

```css
/* globals.css */
:root {
  --background: #000000;
  --foreground: #ffffff;
  --accent: #00ff88;
}

body {
  background: var(--background);
  color: var(--foreground);
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, sans-serif;
}
```

### Orb Animation

The pulsing orb uses CSS animations and Framer Motion:

```typescript
// Smooth pulse animation
<motion.div
  animate={{
    scale: [1, 1.1, 1],
    opacity: [0.5, 1, 0.5],
  }}
  transition={{
    duration: 2,
    repeat: Infinity,
    ease: "easeInOut",
  }}
  className="orb"
/>
```

## Browser Support

### Audio APIs

- **Web Audio API**: Real-time audio processing
- **MediaRecorder API**: Audio recording
- **WebRTC**: High-quality audio capture

### Browser Compatibility

- ✅ Chrome 88+
- ✅ Firefox 85+
- ✅ Safari 14+
- ✅ Edge 88+

## Deployment

### Docker Production

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM node:20-alpine AS runner

WORKDIR /app
COPY --from=builder /app/next.config.js ./
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

EXPOSE 3000
CMD ["npm", "start"]
```

### Static Export

For static hosting:

```bash
npm run build
npm run export
```

## Performance

### Optimizations

- **Code Splitting**: Automatic route-based splitting
- **Image Optimization**: Next.js built-in optimization
- **Bundle Analysis**: Webpack bundle analyzer
- **Service Worker**: Offline functionality (future)

### Monitoring

```bash
# Bundle size analysis
npm run analyze

# Performance metrics
npm run lighthouse
```

## Accessibility

- **Keyboard Navigation**: Full keyboard support
- **Screen Reader**: Voice feedback for visually impaired users
- **High Contrast**: True black background with high contrast elements
- **Reduced Motion**: Respects user's motion preferences

## Testing

### Unit Tests

```typescript
// components/__tests__/VoiceOnlyInterface.test.tsx
import { render, screen } from '@testing-library/react';
import VoiceOnlyInterface from '../VoiceOnlyInterface';

test('renders pulsing orb', () => {
  render(<VoiceOnlyInterface />);
  const orb = screen.getByRole('button', { name: /voice interface/i });
  expect(orb).toBeInTheDocument();
});
```

### Integration Tests

```typescript
// Test voice API integration
test('connects to voice API', async () => {
  const client = new VoiceApiClient();
  await expect(client.connect()).resolves.toBeDefined();
});
```

## Contributing

1. Follow TypeScript and React best practices
2. Add tests for new components
3. Update documentation
4. Create a pull request

## Troubleshooting

### Common Issues

1. **Microphone permission denied**
   - Check browser permissions
   - Ensure HTTPS in production
   - Verify WebRTC support

2. **WebSocket connection fails**
   - Check backend is running
   - Verify WebSocket URL configuration
   - Check firewall settings

3. **Audio playback issues**
   - Check browser audio permissions
   - Verify audio format support
   - Check volume settings

4. **Orb not animating**
   - Check Framer Motion installation
   - Verify CSS animations support
   - Check for JavaScript errors

### Debug Mode

Enable debug logging:

```bash
# In browser console
localStorage.setItem('debug', 'galion:*');
```

## License

MIT License - see LICENSE file for details.
