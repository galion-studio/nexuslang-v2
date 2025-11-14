# 🎨 Nexus Frontend - Next.js Web Application

**Modern, responsive web interface for the Project Nexus platform**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Development](#development)
- [Components](#components)
- [Styling](#styling)
- [API Integration](#api-integration)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

The Nexus Frontend is a modern, responsive web application built with Next.js 13+ that provides an intuitive interface for:

- 🔬 **Scientific Research** - Interactive research tools
- 💬 **NexusLang IDE** - Code editor with AI assistance
- 🤖 **AI Chat** - Conversational interface with AI agents
- 📊 **Analytics Dashboard** - Visualize usage and insights
- 👥 **Collaboration** - Team research features

### Key Highlights

- ⚡ **Lightning Fast** - Next.js 13+ with App Router
- 🎨 **Beautiful UI** - Modern design with Tailwind CSS
- 📱 **Responsive** - Works on desktop, tablet, and mobile
- 🌙 **Dark Mode** - Easy on the eyes
- ♿ **Accessible** - WCAG 2.1 compliant
- 🔄 **Real-time** - Live updates and collaboration

---

## ✨ Features

### Core Features

1. **Research Dashboard**
   - Scientific query interface
   - Research templates
   - History tracking
   - Export capabilities

2. **NexusLang IDE**
   - Monaco editor integration
   - Syntax highlighting
   - AI code generation
   - Real-time compilation
   - Multi-language support

3. **AI Chat Interface**
   - Natural conversation with AI
   - Multi-agent selection
   - Context-aware responses
   - Voice input/output

4. **Analytics & Insights**
   - Usage statistics
   - Performance metrics
   - Research trends
   - Team analytics

5. **User Management**
   - Authentication
   - Profile management
   - Team collaboration
   - Role-based access

---

## 🛠️ Tech Stack

### Core Framework

- **Next.js 13+** - React framework with App Router
- **React 18+** - UI library
- **TypeScript** - Type safety
- **Node.js 16+** - Runtime environment

### UI & Styling

- **Tailwind CSS** - Utility-first CSS
- **Framer Motion** - Animations
- **Lucide Icons** - Icon library
- **Radix UI** - Headless components

### Code Editor

- **Monaco Editor** - VS Code's editor
- **React Monaco Editor** - React wrapper
- **Prism.js** - Syntax highlighting

### State & Data

- **React Query** - Server state management
- **Axios** - HTTP client
- **SWR** - Data fetching
- **Zustand** - Client state (optional)

### Development Tools

- **ESLint** - Linting
- **Prettier** - Code formatting
- **TypeScript ESLint** - TS linting
- **Husky** - Git hooks

---

## 🚀 Quick Start

### Prerequisites

- Node.js 16 or higher
- npm or yarn
- Backend server running (see backend README)

### Installation

```bash
# Navigate to frontend directory
cd v2/frontend

# Install dependencies
npm install
# or
yarn install

# Set up environment variables
cp .env.local.example .env.local
# Edit .env.local with your configuration

# Run development server
npm run dev
# or
yarn dev
```

### Environment Variables

Create `.env.local` file:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_TIMEOUT=30000

# Authentication
NEXT_PUBLIC_JWT_EXPIRY=3600

# Features
NEXT_PUBLIC_ENABLE_VOICE=true
NEXT_PUBLIC_ENABLE_ANALYTICS=true

# Analytics (optional)
NEXT_PUBLIC_GA_ID=G-XXXXXXXXXX
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn

# Environment
NEXT_PUBLIC_ENV=development
```

### Verify Installation

```bash
# Development server should be running on:
# http://localhost:3000

# Open in browser
open http://localhost:3000
```

---

## 📁 Project Structure

```
v2/frontend/
├── app/                        # Next.js 13 App Router
│   ├── (auth)/                # Auth routes
│   │   ├── login/
│   │   └── register/
│   ├── dashboard/             # Dashboard pages
│   ├── research/              # Research tools
│   ├── nexuslang/             # NexusLang IDE
│   ├── api/                   # API routes (optional)
│   ├── layout.tsx             # Root layout
│   ├── page.tsx               # Home page
│   └── globals.css            # Global styles
│
├── components/                 # React components
│   ├── ui/                    # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Card.tsx
│   │   └── ...
│   ├── research/              # Research components
│   │   ├── QueryInterface.tsx
│   │   ├── ResultsDisplay.tsx
│   │   └── ...
│   ├── editor/                # Code editor components
│   │   ├── MonacoEditor.tsx
│   │   ├── CodePanel.tsx
│   │   └── ...
│   ├── chat/                  # Chat components
│   │   ├── ChatInterface.tsx
│   │   ├── MessageList.tsx
│   │   └── ...
│   └── layout/                # Layout components
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Footer.tsx
│
├── lib/                        # Utilities and helpers
│   ├── api/                   # API client
│   │   ├── client.ts
│   │   ├── auth.ts
│   │   ├── research.ts
│   │   └── ...
│   ├── hooks/                 # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useAPI.ts
│   │   └── ...
│   ├── utils/                 # Utility functions
│   │   ├── formatting.ts
│   │   ├── validation.ts
│   │   └── ...
│   └── constants/             # Constants
│       ├── routes.ts
│       └── config.ts
│
├── public/                     # Static assets
│   ├── images/
│   ├── icons/
│   └── fonts/
│
├── styles/                     # Styles (if needed)
│   └── custom.css
│
├── types/                      # TypeScript types
│   ├── api.ts
│   ├── models.ts
│   └── index.ts
│
├── .env.local                 # Environment variables (not in git)
├── .eslintrc.json             # ESLint configuration
├── .prettierrc                # Prettier configuration
├── next.config.js             # Next.js configuration
├── package.json               # Dependencies
├── tailwind.config.js         # Tailwind configuration
├── tsconfig.json              # TypeScript configuration
└── README.md                  # This file
```

---

## 💻 Development

### Development Server

```bash
# Start development server
npm run dev

# Server runs on http://localhost:3000
# Auto-reloads on file changes
```

### Building for Production

```bash
# Create production build
npm run build

# Test production build locally
npm start

# Production server runs on http://localhost:3000
```

### Linting and Formatting

```bash
# Run ESLint
npm run lint

# Fix ESLint issues
npm run lint:fix

# Format with Prettier
npm run format

# Type check
npm run type-check
```

### Code Quality

```bash
# Run all checks
npm run check

# This runs:
# - TypeScript type checking
# - ESLint
# - Tests (if configured)
```

---

## 🧩 Components

### Creating a New Component

```typescript
// components/ui/MyComponent.tsx
import React from 'react';

interface MyComponentProps {
  title: string;
  children?: React.ReactNode;
}

export const MyComponent: React.FC<MyComponentProps> = ({
  title,
  children
}) => {
  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h2 className="text-xl font-bold mb-4">{title}</h2>
      {children}
    </div>
  );
};
```

### Component Best Practices

1. **Use TypeScript** - Define proper types/interfaces
2. **Keep components small** - Single responsibility
3. **Use hooks** - Prefer functional components
4. **Memoization** - Use React.memo for expensive components
5. **Accessibility** - Include ARIA labels
6. **Responsive** - Mobile-first design

### Example Component Structure

```typescript
// components/research/QueryInterface.tsx
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { useQuery } from '@/lib/hooks/useQuery';

interface QueryInterfaceProps {
  onSubmit: (query: string) => void;
}

export const QueryInterface: React.FC<QueryInterfaceProps> = ({
  onSubmit
}) => {
  const [query, setQuery] = useState('');
  const { isLoading } = useQuery();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSubmit(query);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter your scientific question..."
        disabled={isLoading}
      />
      <Button type="submit" disabled={isLoading || !query.trim()}>
        {isLoading ? 'Processing...' : 'Submit Query'}
      </Button>
    </form>
  );
};
```

---

## 🎨 Styling

### Tailwind CSS

We use Tailwind CSS for styling. Key principles:

1. **Utility-first** - Use Tailwind classes
2. **Responsive** - Mobile-first breakpoints
3. **Dark mode** - Support both themes
4. **Custom theme** - Extended in `tailwind.config.js`

### Tailwind Configuration

```javascript
// tailwind.config.js
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          500: '#3b82f6',
          900: '#1e3a8a',
        },
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};
```

### Example Styling

```typescript
// Responsive, dark mode, hover effects
<div className="
  p-4 md:p-6 lg:p-8
  bg-white dark:bg-gray-800
  hover:shadow-lg
  transition-all duration-200
  rounded-lg border border-gray-200 dark:border-gray-700
">
  <h2 className="text-xl md:text-2xl font-bold text-gray-900 dark:text-white">
    Title
  </h2>
</div>
```

---

## 🔌 API Integration

### API Client

```typescript
// lib/api/client.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default apiClient;
```

### Making API Calls

```typescript
// lib/api/research.ts
import apiClient from './client';

export interface ScientificQuery {
  query: string;
  domain?: string;
  depth?: string;
}

export const submitQuery = async (data: ScientificQuery) => {
  const response = await apiClient.post('/api/v1/grokopedia/scientific-query', data);
  return response.data;
};
```

### Using in Components

```typescript
// components/research/ResearchForm.tsx
'use client';

import { useState } from 'react';
import { submitQuery } from '@/lib/api/research';

export const ResearchForm = () => {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      const data = await submitQuery({ query });
      setResult(data);
    } catch (error) {
      console.error('Query failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form content */}
    </form>
  );
};
```

---

## 🚀 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel

# Production deployment
vercel --prod
```

### Docker

```bash
# Build image
docker build -t nexus-frontend .

# Run container
docker run -p 3000:3000 nexus-frontend
```

### Static Export

```bash
# Build static site
npm run build
npm run export

# Files in out/ directory
# Deploy to any static host
```

### Environment Variables for Production

Set these in your hosting platform:

```bash
NEXT_PUBLIC_API_URL=https://api.galion.studio
NEXT_PUBLIC_ENV=production
# ... other variables
```

---

## 🔧 Troubleshooting

### Common Issues

#### Build Errors

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
```

#### Module Not Found

```bash
# Check tsconfig.json paths
# Ensure imports use correct aliases
import { Button } from '@/components/ui/Button';
```

#### API Connection Issues

```bash
# Check .env.local
cat .env.local | grep NEXT_PUBLIC_API_URL

# Test API
curl $NEXT_PUBLIC_API_URL/health
```

#### Hydration Errors

```typescript
// Use 'use client' directive for client-only components
'use client';

// Or use dynamic import with ssr: false
import dynamic from 'next/dynamic';

const ClientComponent = dynamic(
  () => import('./ClientComponent'),
  { ssr: false }
);
```

---

## 📚 Additional Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [React Documentation](https://react.dev)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [TypeScript Documentation](https://www.typescriptlang.org/docs)

---

## 📄 License

MIT License - see LICENSE file for details.

---

## 🙏 Support

- **Documentation**: See [main README](../../README.md)
- **Issues**: [GitHub Issues](https://github.com/galion-studio/nexuslang-v2/issues)
- **Email**: support@galion.studio

---

**Built with ❤️ by the Galion Studio team**

**Version**: 2.0.0  
**Last Updated**: November 14, 2025

