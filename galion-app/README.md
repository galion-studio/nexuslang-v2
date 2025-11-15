# 🎤 Galion App - Voice-First Development Platform

**Revolutionary voice-first interface for AI-powered development**

**URL:** https://app.galion.studio  
**Port:** 3000

---

## Overview

Galion App is the world's first truly voice-first development platform, enabling developers to code, query, and create using natural language and voice commands.

---

## Key Features

### Voice Interface
- Natural language code generation
- Voice command recognition
- Real-time transcription
- Text-to-speech responses
- Conversation flow management

### AI Assistance
- Real-time AI-powered suggestions
- Context-aware help
- Code generation and completion
- Error detection and fixes
- Learning from your patterns

### Development Tools
- Voice-activated IDE
- Natural language queries
- Code compilation
- Real-time execution
- Integrated debugging

### User Experience
- Intuitive onboarding
- Beta signup flow
- User analytics dashboard
- Subscription management
- Mobile app support

---

## Tech Stack

- **Framework:** Next.js 14.2.33 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Components:** Radix UI, Lucide React
- **Voice:** Web Speech API
- **State:** React Hooks
- **Mobile:** React Native (Expo)

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

Access at: http://localhost:3000

### Build for Production
```bash
npm run build
npm run start
```

---

## Project Structure

```
galion-app/
├── app/                        # Next.js app router
│   ├── (auth)/                # Authentication pages
│   │   ├── beta/              # Beta signup
│   │   ├── login/             # Login page
│   │   └── register/          # Registration
│   │
│   ├── (dashboard)/           # Dashboard pages
│   │   ├── agents/            # AI agents
│   │   ├── analytics/         # Analytics
│   │   ├── billing/           # Billing
│   │   ├── dashboard/         # Main dashboard
│   │   ├── developers/        # Developer tools
│   │   ├── grokopedia/        # Knowledge graph
│   │   ├── profile/           # User profile
│   │   ├── subscription/      # Subscriptions
│   │   └── voice/             # Voice interface
│   │
│   ├── admin-*/               # Admin pages
│   ├── ai-studio/             # AI studio
│   ├── onboarding/            # User onboarding
│   └── layout.tsx             # Root layout
│
├── components/                # React components
│   ├── agents/                # Agent components
│   ├── beta/                  # Beta signup components
│   ├── chat/                  # Chat interface
│   ├── voice/                 # Voice components
│   ├── dashboard/             # Dashboard components
│   ├── settings/              # Settings components
│   ├── onboarding/            # Onboarding flow
│   └── ui/                    # Reusable UI
│
├── lib/                       # Utilities
│   ├── utils.ts               # Helper functions
│   └── api-client.ts          # API client
│
├── middleware/                # Next.js middleware
│   └── rateLimit.ts           # Rate limiting
│
├── mobile/                    # React Native app
│   ├── app/                   # Mobile screens
│   ├── assets/                # Images, icons
│   └── package.json           # Mobile dependencies
│
├── types/                     # TypeScript types
│   └── speech.d.ts            # Voice API types
│
└── styles/                    # Styles
    └── globals.css            # Global CSS
```

---

## Environment Variables

Create `.env.local`:
```env
# Backend API
NEXT_PUBLIC_API_URL=https://api.galion.studio

# App Configuration
NEXT_PUBLIC_APP_URL=https://app.galion.studio
NEXT_PUBLIC_ENV=production

# Voice API (optional)
NEXT_PUBLIC_SPEECH_API_KEY=your_key_here

# Analytics (optional)
NEXT_PUBLIC_ANALYTICS_ID=your_id_here
```

---

## Voice Commands

### Supported Commands:
- "Create a new project"
- "Show my dashboard"
- "Generate code for [description]"
- "Search for [topic]"
- "Open settings"
- "Compile my code"
- "Run tests"

### Adding New Commands:
Edit `components/voice/VoiceCommandHandler.tsx`

---

## Mobile App

### Setup React Native:
```bash
cd mobile
npm install

# iOS
npx expo start --ios

# Android
npx expo start --android
```

### Build for Production:
```bash
cd mobile
eas build --platform all
```

---

## API Integration

The app communicates with the backend API:

```typescript
// Example API call
import { apiClient } from '@/lib/api-client'

const data = await apiClient.post('/api/v1/query', {
  query: 'Your query here'
})
```

---

## Testing

```bash
# Run tests (when implemented)
npm run test

# E2E tests
npm run test:e2e
```

---

## Troubleshooting

### Voice Not Working
- Check browser permissions for microphone
- Ensure HTTPS connection (required for Web Speech API)
- Test in Chrome/Edge (best support)

### API Connection Failed
- Verify backend is running: `pm2 status`
- Check CORS settings in backend
- Verify API URL in environment variables

### Build Errors
- Clear cache: `rm -rf .next`
- Reinstall: `rm -rf node_modules && npm install`
- Check Node version: `node --version` (should be 20+)

---

## Performance

### Optimizations:
- Code splitting
- Lazy loading
- Image optimization
- Font optimization
- CSS purging

### Monitoring:
- Check build size: `npm run build`
- Analyze bundle: `npm run analyze` (if configured)

---

## Contributing

1. Create feature branch
2. Make changes
3. Test locally
4. Submit pull request

---

**Galion App - Voice-first development made simple** 🎤✨

