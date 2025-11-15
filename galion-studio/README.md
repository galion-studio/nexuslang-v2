# 🏢 Galion Studio - Corporate Website

**Professional corporate website for Galion Platform**

**URL:** https://studio.galion.studio  
**Port:** 3030

---

## Overview

Galion Studio is the corporate face of the Galion Platform, showcasing our company, portfolio, team, and brand.

---

## Features

- **Portfolio Gallery** - Showcase of projects and achievements
- **Team Profiles** - Meet our team members
- **Press Releases** - Latest news and announcements
- **Brand Assets** - Logos, colors, typography
- **Career Opportunities** - Join our team
- **About Us** - Company mission and vision

---

## Tech Stack

- **Framework:** Next.js 14.2.33
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Components:** Radix UI
- **Icons:** Lucide React

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

Access at: http://localhost:3030

### Build for Production
```bash
npm run build
npm run start
```

---

## Project Structure

```
galion-studio/
├── app/                    # Next.js app router
│   ├── about/             # About page
│   ├── chat/              # Chat interface
│   ├── generate/          # AI generation
│   ├── nexuslang-agent/   # Agent integration
│   ├── subscription/      # Subscription management
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
│
├── components/            # React components
│   ├── portfolio/         # Portfolio components
│   ├── press/             # Press release components
│   ├── branding/          # Brand asset components
│   └── ui/                # Reusable UI components
│
├── lib/                   # Utilities
│   └── utils.ts           # Helper functions
│
├── styles/                # Global styles
│   └── globals.css        # Global CSS
│
└── public/                # Static assets
```

---

## Available Scripts

- `npm run dev` - Start development server (port 3030)
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

---

## Environment Variables

Create `.env.local`:
```env
NEXT_PUBLIC_API_URL=https://api.galion.studio
NEXT_PUBLIC_APP_URL=https://studio.galion.studio
```

---

## Deployment

Deployed automatically via PM2 on RunPod:
```bash
pm2 start npm --name galion-studio -- run dev -- -p 3030
```

---

## Customization

### Update Brand Colors

Edit `tailwind.config.ts`:
```typescript
theme: {
  extend: {
    colors: {
      primary: '#YOUR_COLOR',
      secondary: '#YOUR_COLOR',
    }
  }
}
```

### Add New Pages

Create new file in `app/` directory:
```typescript
// app/your-page/page.tsx
export default function YourPage() {
  return <div>Your content</div>
}
```

---

## Maintenance

- Keep dependencies updated: `npm update`
- Monitor build size: `npm run build`
- Check for security issues: `npm audit`

---

**Galion Studio - Professional corporate presence** 🏢

