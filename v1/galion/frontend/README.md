# GALION.APP Frontend

Modern, production-ready frontend for GALION.APP built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

- ✅ **Authentication** - Login, Registration, 2FA with JWT
- ✅ **Dashboard** - Real-time metrics and activity feed
- ✅ **User Management** - Admin controls for user administration
- ✅ **Document Management** - Upload, view, and manage documents
- ✅ **Voice Interface** - Speech-to-text and voice commands
- ✅ **Analytics** - System metrics and performance monitoring
- ✅ **Service Status** - Real-time health checks for all services
- ✅ **AI Chat** - Conversational AI interface
- ✅ **Documentation** - Complete API reference and guides

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: Zustand
- **API Client**: Axios
- **Voice**: Web Audio API + WebSockets

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend services running (see main README)

### Installation

```bash
# Install dependencies
npm install

# Copy environment variables
cp .env.local.example .env.local

# Update .env.local with your backend URLs
```

### Development

```bash
# Start development server
npm run dev

# Open http://localhost:3000
```

### Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

## Environment Variables

Create a `.env.local` file with:

```env
NEXT_PUBLIC_API_URL=http://localhost:8080
NEXT_PUBLIC_AUTH_SERVICE_URL=http://localhost:8000
NEXT_PUBLIC_USER_SERVICE_URL=http://localhost:8001
NEXT_PUBLIC_VOICE_SERVICE_URL=http://localhost:8003
NEXT_PUBLIC_DOCUMENT_SERVICE_URL=http://localhost:8004
NEXT_PUBLIC_PERMISSIONS_SERVICE_URL=http://localhost:8005
NEXT_PUBLIC_ANALYTICS_SERVICE_URL=http://localhost:9090

# Optional AI APIs
NEXT_PUBLIC_OPENAI_API_KEY=your-key-here
NEXT_PUBLIC_ANTHROPIC_API_KEY=your-key-here
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── (auth)/            # Authentication pages
│   ├── (dashboard)/       # Protected dashboard pages
│   └── layout.tsx         # Root layout
├── components/            # React components
│   ├── ui/               # shadcn/ui components
│   ├── layout/           # Layout components
│   ├── auth/             # Auth components
│   └── voice/            # Voice components
├── lib/                  # Utilities and helpers
│   ├── api/             # API clients
│   ├── stores/          # Zustand stores
│   ├── hooks/           # Custom hooks
│   └── utils.ts         # Utility functions
├── types/               # TypeScript type definitions
└── public/              # Static assets
```

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

### Docker

```bash
# Build Docker image
docker build -t galion-frontend .

# Run container
docker run -p 3000:3000 galion-frontend
```

### Manual Deployment

```bash
# Build
npm run build

# The .next folder contains your production build
# Deploy to any static hosting service
```

## Features Guide

### Authentication
- Login/Register with email and password
- Two-factor authentication (TOTP)
- Protected routes with middleware
- Auto-refresh JWT tokens

### Voice Commands
Click the microphone button and try:
- "Show my documents"
- "Go to dashboard"
- "Open user management"

### Document Upload
- Drag and drop files
- Support for PDF, PNG, JPG
- Real-time upload progress
- Document status tracking

### Admin Features
- User management (admin only)
- System analytics
- Service health monitoring
- Permission management

## Development Tips

### Adding New Pages

```typescript
// Create a new page in app/(dashboard)/yourpage/page.tsx
export default function YourPage() {
  return <div>Your content</div>
}
```

### Adding New API Endpoints

```typescript
// Add to lib/api/yourservice.ts
export const yourServiceApi = {
  yourMethod: async () => {
    const response = await yourService.get('/endpoint')
    return response.data
  }
}
```

### Using Voice Features

```typescript
import { VoiceButton } from '@/components/voice/VoiceButton'

<VoiceButton 
  onTranscript={(text) => console.log(text)}
  onCommand={(response) => console.log(response)}
/>
```

## Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Check the [Documentation](http://localhost:3000/docs)
- View [Service Status](http://localhost:3000/status)
- Contact support team

---

**Built with Elon Musk's First Principles** 🚀

Question → Delete → Simplify → Accelerate → Ship
