# 🎨 GALION WORKPLACE - UI WIREFRAMES & SPECIFICATIONS

**Pixel-Perfect Design Guide for Developers**

**Version:** 1.0  
**Date:** November 9, 2025  
**Design System:** Dark Minimal, Voice-First

---

## 📐 DESIGN TOKENS

### Colors (CSS Variables)

```css
:root {
  /* Background Layers */
  --bg-primary:   #0A0A0A;  /* Page background */
  --bg-secondary: #1A1A1A;  /* Cards, panels */
  --bg-tertiary:  #2A2A2A;  /* Elevated elements */
  --bg-hover:     #3A3A3A;  /* Hover states */
  
  /* Text Hierarchy */
  --text-primary:   #FFFFFF;  /* Headings, important text */
  --text-secondary: #A0A0A0;  /* Body text, labels */
  --text-tertiary:  #707070;  /* Subtle text, metadata */
  --text-disabled:  #505050;  /* Disabled states */
  
  /* Accent Colors */
  --accent-primary:  #00D9FF;  /* Primary actions, links */
  --accent-success:  #00FF88;  /* Success, money, positive */
  --accent-warning:  #FFB800;  /* Warnings, attention */
  --accent-error:    #FF3B3B;  /* Errors, destructive actions */
  --accent-voice:    #00D9FF;  /* Voice interactions */
  
  /* Borders */
  --border-subtle: rgba(255, 255, 255, 0.1);
  --border-normal: rgba(255, 255, 255, 0.2);
  
  /* Shadows */
  --shadow-sm:  0 1px 2px rgba(0, 0, 0, 0.2);
  --shadow-md:  0 4px 6px rgba(0, 0, 0, 0.3);
  --shadow-lg:  0 10px 15px rgba(0, 0, 0, 0.4);
}
```

### Typography Scale

```css
/* Font Families */
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* Font Sizes (rem) */
--text-xs:   0.75rem;   /* 12px - Labels, metadata */
--text-sm:   0.875rem;  /* 14px - Body text */
--text-base: 1rem;      /* 16px - Default */
--text-lg:   1.125rem;  /* 18px - Subheadings */
--text-xl:   1.25rem;   /* 20px - Headings */
--text-2xl:  1.5rem;    /* 24px - Page titles */
--text-3xl:  2rem;      /* 32px - Hero text */

/* Font Weights */
--font-normal:    400;
--font-medium:    500;
--font-semibold:  600;
--font-bold:      700;

/* Line Heights */
--leading-tight:   1.25;  /* Headings */
--leading-normal:  1.5;   /* Body text */
--leading-relaxed: 1.75;  /* Long-form content */
```

### Spacing Scale (8px base unit)

```css
--space-0: 0;
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-5: 1.25rem;  /* 20px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
--space-10: 2.5rem;  /* 40px */
--space-12: 3rem;    /* 48px */
--space-16: 4rem;    /* 64px */
```

### Border Radius

```css
--rounded-sm:   4px;   /* Buttons, inputs */
--rounded-md:   8px;   /* Cards, panels */
--rounded-lg:   12px;  /* Modals */
--rounded-xl:   16px;  /* Large cards */
--rounded-full: 9999px; /* Avatars, pills */
```

---

## 📱 SCREEN LAYOUTS

### 1. Dashboard (Main Screen)

```
┌───────────────────────────────────────────────────────────────────┐
│  [Logo] GALION.STUDIO          [Search]    [@User] [Settings] ⚙️  │  ← Header (64px height)
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐                                                │
│  │              │  WORKSPACE SWITCHER                             │
│  │  Dashboard   │  ────────────────────                          │
│  │              │  Acme Corp  ▼                                   │
│  │  Tasks      │                                                  │
│  │              │  QUICK STATS                                    │
│  │  Time       │  ────────────                                    │
│  │              │  ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │  Team       │  │   145      │ │   $45k   │ │   23     │       │
│  │              │  │   Tasks    │ │   Earned │ │   People │       │
│  │  Hiring     │  │   Active   │ │   MTD    │ │   Team   │       │
│  │              │  └──────────┘ └──────────┘ └──────────┘       │
│  │  Settings   │                                                  │
│  │              │  RECENT ACTIVITY                                │
│  │              │  ───────────────                                │
│  └──────────────┘  • John logged 4h on "Voice Service" (12m ago) │
│   Sidebar (240px)  • Sarah created "Design System" (1h ago)       │
│                    • Mike completed "API Gateway" (2h ago)        │
│                                                                   │
│                    UPCOMING DEADLINES                             │
│                    ──────────────────                             │
│                    • "Hiring Page" - Due in 2 days               │
│                    • "Security Audit" - Due in 5 days            │
│                                                                   │
│                                          [🎤]  ← Voice Button     │
└───────────────────────────────────────────────────────────────────┘
```

**Specifications:**
- Header height: 64px
- Sidebar width: 240px
- Main content padding: 32px
- Card gap: 24px
- Voice button: 64px × 64px, bottom-right (32px margin)

---

### 2. Task Board (Kanban View)

```
┌───────────────────────────────────────────────────────────────────┐
│  Tasks                          [+ New Task]  [Filter ▼]  [👤 Me] │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ BACKLOG (12)    │  │ IN PROGRESS (5) │  │ DONE (8)        │  │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤  │
│  │                 │  │                 │  │                 │  │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │
│  │ │Build Hiring │ │  │ │Voice Service│ │  │ │API Gateway  │ │  │
│  │ │Page         │ │  │ │Integration  │ │  │ │             │ │  │
│  │ │             │ │  │ │             │ │  │ │[@Sarah]     │ │  │
│  │ │[@John]      │ │  │ │[@John]      │ │  │ │12h @ $120/h │ │  │
│  │ │8h @ $100/h  │ │  │ │16h @ $100/h │ │  │ │$1,440       │ │  │
│  │ │$800         │ │  │ │$1,600       │ │  │ │✓ PAID       │ │  │
│  │ │🟡 HIGH      │ │  │ │🔴 URGENT    │ │  │ └─────────────┘ │  │
│  │ └─────────────┘ │  │ └─────────────┘ │  │                 │  │
│  │                 │  │                 │  │ ┌─────────────┐ │  │
│  │ ┌─────────────┐ │  │ ┌─────────────┐ │  │ │Database     │ │  │
│  │ │Security     │ │  │ │Time Tracking│ │  │ │Migration    │ │  │
│  │ │Audit        │ │  │ │UI           │ │  │ │             │ │  │
│  │ │             │ │  │ │             │ │  │ │[@Mike]      │ │  │
│  │ │[@Sarah]     │ │  │ │[@Mike]      │ │  │ │4h @ $80/h   │ │  │
│  │ │12h @ $120/h │ │  │ │6h @ $80/h   │ │  │ │$320         │ │  │
│  │ │$1,440       │ │  │ │$480         │ │  │ │✓ PAID       │ │  │
│  │ └─────────────┘ │  │ └─────────────┘ │  │ └─────────────┘ │  │
│  │                 │  │                 │  │                 │  │
│  │ [+ Add Task]    │  │ [+ Add Task]    │  │                 │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
│                                                                   │
│                                          [🎤]                     │
└───────────────────────────────────────────────────────────────────┘
```

**Task Card Specifications:**
- Width: 280px (column width: 320px with 20px padding)
- Min height: 140px
- Border radius: 8px
- Background: #2A2A2A
- Padding: 16px
- Gap between cards: 12px
- Drag handle: Entire card is draggable

**Task Card Anatomy:**
```
┌─────────────────────────────────────┐
│ Build Hiring Page              [⋮]  │  ← Title (16px, bold) + Menu
│                                     │
│ Create public careers page with    │  ← Description (14px, gray)
│ application form and pipeline...    │
│                                     │
│ [👤 John Doe]                       │  ← Assignee (Avatar 24px)
│                                     │
│ 8h @ $100/h            $800         │  ← Time + Rate → Total (bold, green)
│                                     │
│ [🟡 HIGH]  [Due: Nov 15]           │  ← Priority + Due Date
└─────────────────────────────────────┘
   Padding: 16px all sides
   Gap between elements: 12px
```

---

### 3. Time Tracking Screen

```
┌───────────────────────────────────────────────────────────────────┐
│  Time Tracking               [This Week ▼]  [Log Time]  [Export]  │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  SUMMARY                                                          │
│  ────────                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐ │
│  │   32.5h    │  │   $3,250   │  │   8 Tasks  │  │   95%      │ │
│  │   Worked   │  │   Earned   │  │   Logged   │  │   Util     │ │
│  └────────────┘  └────────────┘  └────────────┘  └────────────┘ │
│                                                                   │
│  TIMESHEET - Week of Nov 9, 2025                                 │
│  ─────────────────────────────────                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Date    │ Task                │ Hours │ Rate   │ Total      │ │
│  ├─────────┼────────────────────┼───────┼────────┼────────────┤ │
│  │ Nov 9   │ Voice Service      │  4.0  │ $100/h │ $400.00    │ │
│  │  Mon    │ Code Review        │  2.5  │ $100/h │ $250.00    │ │
│  │         │ Team Meeting       │  1.0  │ $100/h │ $100.00    │ │
│  │         │ ──────────────────────────────────────────────────│ │
│  │         │ Day Total:         │  7.5h          │ $750.00    │ │
│  ├─────────┼────────────────────┼───────┼────────┼────────────┤ │
│  │ Nov 10  │ Voice Service      │  5.0  │ $100/h │ $500.00    │ │
│  │  Tue    │ Documentation      │  2.5  │ $100/h │ $250.00    │ │
│  │         │ ──────────────────────────────────────────────────│ │
│  │         │ Day Total:         │  7.5h          │ $750.00    │ │
│  ├─────────┼────────────────────┼───────┼────────┼────────────┤ │
│  │ Nov 11  │ Time Tracking UI   │  6.0  │ $100/h │ $600.00    │ │
│  │  Wed    │ Bug Fixes          │  1.5  │ $100/h │ $150.00    │ │
│  │         │ ──────────────────────────────────────────────────│ │
│  │         │ Day Total:         │  7.5h          │ $750.00    │ │
│  └─────────┴────────────────────┴───────┴────────┴────────────┘ │
│                                                                   │
│                    WEEK TOTAL: 32.5h → $3,250.00                 │
│                                                                   │
│                                          [🎤]                     │
└───────────────────────────────────────────────────────────────────┘
```

**Time Log Modal:**
```
┌─────────────────────────────────────────────┐
│  Log Time                           [X]     │
├─────────────────────────────────────────────┤
│                                             │
│  Task *                                     │
│  [Voice Service Integration     ▼]         │
│                                             │
│  Date *                                     │
│  [Nov 9, 2025                   📅]         │
│                                             │
│  Hours *                                    │
│  [4.0                              ]        │
│                                             │
│  Description                                │
│  [Integrated Whisper with WebSocket        │
│   and added real-time transcription        │
│                                    ]        │
│                                             │
│  ────────────────────────────────────────── │
│  Hourly Rate: $100/h                        │
│  Total:       $400.00                       │
│  ────────────────────────────────────────── │
│                                             │
│              [Cancel]  [Log Time]           │
└─────────────────────────────────────────────┘
  Modal width: 500px
  Modal padding: 32px
  Input height: 44px
  Button height: 44px
```

---

### 4. Team & Compensation Screen

```
┌───────────────────────────────────────────────────────────────────┐
│  Team & Compensation            [November 2025 ▼]  [Invite]       │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  COMPENSATION LEDGER - November 2025                              │
│  ───────────────────────────────────                              │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Team Member    │ Rate    │ Hours │ Total     │ Paid    │ %  │ │
│  ├────────────────┼─────────┼───────┼───────────┼─────────┼────┤ │
│  │ [👤] Sarah M.  │ $120/h  │  140  │  $16,800  │ $16,800 │ ✓  │ │
│  │     Admin      │         │       │           │         │100%│ │
│  ├────────────────┼─────────┼───────┼───────────┼─────────┼────┤ │
│  │ [👤] John D.   │ $100/h  │  160  │  $16,000  │ $16,000 │ ✓  │ │
│  │     Developer  │         │       │           │         │100%│ │
│  ├────────────────┼─────────┼───────┼───────────┼─────────┼────┤ │
│  │ [👤] Mike T.   │  $80/h  │  100  │   $8,000  │  $8,000 │ ✓  │ │
│  │     Developer  │         │       │           │         │100%│ │
│  ├────────────────┼─────────┼───────┼───────────┼─────────┼────┤ │
│  │ [👤] Lisa K.   │ $150/h  │   80  │  $12,000  │  $6,000 │ 🟡 │ │
│  │     Designer   │         │       │           │         │50% │ │
│  ├────────────────┼─────────┼───────┼───────────┼─────────┼────┤ │
│  │ TOTAL          │         │  480  │  $52,800  │ $46,800 │89% │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  TRANSPARENCY NOTES:                                              │
│  • All compensation visible to entire team                        │
│  • Rates based on experience, skill, and market data             │
│  • Payment status updated weekly                                  │
│                                                                   │
│  TEAM MEMBERS                                                     │
│  ────────────                                                      │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ [👤] Sarah Martinez         $120/h  Admin     [Edit]  [...]  │ │
│  │      sarah@example.com                                       │ │
│  │      Joined: Jan 2025 • Last active: 2 hours ago            │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ [👤] John Doe               $100/h  Developer [Edit]  [...]  │ │
│  │      john@example.com                                        │ │
│  │      Joined: Feb 2025 • Last active: 10 min ago             │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ [👤] Mike Turner            $80/h   Developer [Edit]  [...]  │ │
│  │      mike@example.com                                        │ │
│  │      Joined: Mar 2025 • Last active: 1 hour ago             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│                                          [🎤]                     │
└───────────────────────────────────────────────────────────────────┘
```

**Key Features:**
- ✅ All compensation visible (radical transparency)
- ✅ Color-coded payment status (green = paid, yellow = partial, red = pending)
- ✅ Percentage paid indicator
- ✅ Monthly/weekly toggle
- ✅ Export to CSV for payroll

---

### 5. Hiring Page (Public)

```
┌───────────────────────────────────────────────────────────────────┐
│                    GALION.STUDIO                                  │
│                    Join Our Team                                  │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  We're building the future of transparent collaboration.          │
│  Join us if you value honesty, autonomy, and impact.             │
│                                                                   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                   │
│  OPEN POSITIONS                                                   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  🎯 Senior ML Engineer                                       │ │
│  │  Remote • Full-time • $120k-180k/year                        │ │
│  │                                                              │ │
│  │  Build voice-to-voice AI systems with Whisper and XTTS.    │ │
│  │  Work with Llama 3.1, RAG, and AWS infrastructure.          │ │
│  │                                                              │ │
│  │  Requirements:                                               │ │
│  │  • 5+ years ML/AI experience                                │ │
│  │  • Python expert (PyTorch, FastAPI)                         │ │
│  │  • Deployed ML models to production                         │ │
│  │                                                              │ │
│  │                                    [Apply Now →]             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  💻 Full-Stack Engineer                                      │ │
│  │  Remote • Full-time • $100k-150k/year                        │ │
│  │                                                              │ │
│  │  Build React + TypeScript UIs with dark minimal design.    │ │
│  │  Work with WebSockets, voice integration, and real-time.    │ │
│  │                                                              │ │
│  │  Requirements:                                               │ │
│  │  • 3+ years React/TypeScript                                │ │
│  │  • Strong UI/UX skills                                      │ │
│  │  • Experience with real-time apps                           │ │
│  │                                                              │ │
│  │                                    [Apply Now →]             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                   │
│  WHY JOIN US?                                                     │
│  ────────────                                                      │
│  ✅ Radical Transparency   See everyone's compensation            │
│  ✅ Remote-First           Work from anywhere                     │
│  ✅ Fair Pay               Based on value, not negotiation        │
│  ✅ Cutting-Edge Tech      Llama 3.1, Whisper, AWS               │
│  ✅ Small Team             <10 people, high impact                │
│  ✅ Fast Growth            From 0 to production in 6 weeks        │
│                                                                   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                                   │
│  READY TO JOIN?                                                   │
│  [View All Positions →]                                           │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

**Application Form Modal:**
```
┌─────────────────────────────────────────────────┐
│  Apply: Senior ML Engineer             [X]     │
├─────────────────────────────────────────────────┤
│                                                 │
│  Full Name *                                    │
│  [____________________________________]         │
│                                                 │
│  Email *                                        │
│  [____________________________________]         │
│                                                 │
│  LinkedIn Profile                               │
│  [____________________________________]         │
│                                                 │
│  GitHub Profile                                 │
│  [____________________________________]         │
│                                                 │
│  Portfolio/Website                              │
│  [____________________________________]         │
│                                                 │
│  Why do you want to join GALION.STUDIO? *      │
│  [____________________________________________  │
│   ____________________________________________  │
│   ____________________________________________] │
│                                                 │
│  Describe your ML/AI experience *              │
│  [____________________________________________  │
│   ____________________________________________  │
│   ____________________________________________] │
│                                                 │
│  Expected Hourly Rate *                         │
│  [$_______/hour]                                │
│                                                 │
│  Available Start Date                           │
│  [_________ 📅]                                 │
│                                                 │
│  ─────────────────────────────────────────────  │
│  We value transparency. Your expected rate      │
│  helps us make fair offers faster.             │
│  ─────────────────────────────────────────────  │
│                                                 │
│          [Cancel]  [Submit Application →]       │
│                                                 │
└─────────────────────────────────────────────────┘
  Modal width: 600px
  Modal padding: 40px
```

---

## 🎤 VOICE BUTTON STATES

### Visual States

**1. IDLE (Default)**
```
   ┌──────────┐
   │          │
   │    🎤    │   ← Icon: 32px
   │          │   Background: #00D9FF
   └──────────┘   Size: 64px × 64px
                  Border-radius: 50%
                  Shadow: 0 4px 12px rgba(0,217,255,0.3)
```

**2. LISTENING (Active)**
```
   ┌──────────┐
   │    🎤    │   ← Pulsing animation
   │          │   Background: #00D9FF
   │ ▁▃▅▇▅▃▁  │   Waveform: Animated
   └──────────┘   Scale: 1.1 (slightly larger)
                  Animation: pulse 1s infinite
```

**3. PROCESSING (Thinking)**
```
   ┌──────────┐
   │          │
   │    🧠    │   ← Brain icon (thinking)
   │   ⟳⟳⟳    │   Spinning dots
   └──────────┘   Background: #FF006E (magenta)
                  Animation: spin 2s infinite
```

**4. SPEAKING (Audio Output)**
```
   ┌──────────┐
   │    🔊    │   ← Speaker icon
   │          │   Background: #00FF88 (green)
   │ ━━━━━━━  │   Waveform: Animated
   └──────────┘   Animation: wave 0.5s infinite
```

### Positioning & Behavior

```css
.voice-button {
  position: fixed;
  bottom: 32px;
  right: 32px;
  z-index: 1000;
  
  width: 64px;
  height: 64px;
  border-radius: 50%;
  
  display: flex;
  align-items: center;
  justify-content: center;
  
  cursor: pointer;
  transition: all 0.3s ease;
  
  /* Shadow */
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

.voice-button:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.6);
}

.voice-button:active {
  transform: scale(1.05);
}
```

**Transcript Display:**
```
  [🎤]  ← Voice button
   ↓
 ┌─────────────────────────────────┐
 │ You said:                       │
 │ "Create task: Build hiring page"│
 └─────────────────────────────────┘
  Appears below button when listening
  Background: #1A1A1A
  Text: white
  Padding: 12px
  Border-radius: 8px
  Max-width: 300px
```

---

## 🎨 COMPONENT LIBRARY

### Buttons

**Primary Button:**
```css
.btn-primary {
  background: #00D9FF;
  color: #0A0A0A;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #00B8DD;
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 217, 255, 0.3);
}

.btn-primary:active {
  transform: translateY(0);
}
```

**Secondary Button:**
```css
.btn-secondary {
  background: #2A2A2A;
  color: #FFFFFF;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  font-size: 14px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: #3A3A3A;
  border-color: rgba(255, 255, 255, 0.3);
}
```

**Danger Button:**
```css
.btn-danger {
  background: #FF3B3B;
  color: #FFFFFF;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
}

.btn-danger:hover {
  background: #FF1F1F;
}
```

### Form Inputs

**Text Input:**
```css
.input {
  width: 100%;
  padding: 12px 16px;
  background: #2A2A2A;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #FFFFFF;
  font-size: 14px;
  transition: all 0.2s;
}

.input:focus {
  outline: none;
  border-color: #00D9FF;
  box-shadow: 0 0 0 3px rgba(0, 217, 255, 0.1);
}

.input::placeholder {
  color: #707070;
}
```

**Select Dropdown:**
```css
.select {
  width: 100%;
  padding: 12px 16px;
  background: #2A2A2A;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #FFFFFF;
  font-size: 14px;
  cursor: pointer;
  appearance: none;
  background-image: url('data:image/svg+xml,...');  /* Dropdown arrow */
  background-repeat: no-repeat;
  background-position: right 12px center;
  padding-right: 40px;
}
```

### Cards

**Standard Card:**
```css
.card {
  background: #1A1A1A;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.2s;
}

.card:hover {
  background: #2A2A2A;
  border-color: rgba(255, 255, 255, 0.2);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
}
```

### Badges

**Priority Badges:**
```css
.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.badge-low    { background: #505050; color: #FFFFFF; }
.badge-medium { background: #3A3A3A; color: #FFFFFF; }
.badge-high   { background: #FFB800; color: #0A0A0A; }
.badge-urgent { background: #FF3B3B; color: #FFFFFF; }
```

---

## 📏 RESPONSIVE BREAKPOINTS

```css
/* Mobile First Approach */

/* Mobile: 320px - 640px */
@media (max-width: 640px) {
  /* Single column layout */
  /* Stack Kanban columns vertically */
  /* Hide sidebar, show hamburger menu */
  /* Voice button: 56px × 56px */
  /* Font sizes: -2px from desktop */
}

/* Tablet: 641px - 1024px */
@media (min-width: 641px) and (max-width: 1024px) {
  /* Two column layout */
  /* Kanban: 2 columns visible, scroll horizontally */
  /* Collapsible sidebar */
  /* Voice button: 60px × 60px */
}

/* Desktop: 1025px+ */
@media (min-width: 1025px) {
  /* Full layout */
  /* Kanban: 3+ columns visible */
  /* Fixed sidebar */
  /* Voice button: 64px × 64px */
}

/* Large Desktop: 1920px+ */
@media (min-width: 1920px) {
  /* Max content width: 1600px, centered */
  /* Larger font sizes */
  /* More whitespace */
}
```

---

## ✅ DEVELOPER CHECKLIST

When implementing a screen, verify:

```yaml
□ Colors match design tokens exactly
□ Font sizes from typography scale
□ Spacing uses 8px grid
□ Border radius consistent
□ Shadows applied correctly
□ Hover states implemented
□ Focus states for accessibility
□ Loading states (skeletons)
□ Empty states (no data)
□ Error states (validation)
□ Responsive on mobile/tablet/desktop
□ Voice button positioned correctly
□ Animations smooth (60fps)
□ Dark theme applied
□ High contrast (WCAG AA minimum)
```

---

## 🎯 FIGMA FILE STRUCTURE

If designing in Figma first:

```
GALION.STUDIO Design System
│
├── 🎨 Foundation
│   ├── Colors
│   ├── Typography
│   ├── Spacing
│   └── Shadows
│
├── 🧩 Components
│   ├── Buttons
│   ├── Inputs
│   ├── Cards
│   ├── Modals
│   └── Voice Button
│
├── 📱 Screens
│   ├── Dashboard
│   ├── Task Board
│   ├── Time Tracking
│   ├── Team
│   └── Hiring Page
│
└── 🔄 Flows
    ├── Task Creation Flow
    ├── Time Logging Flow
    └── Voice Command Flow
```

---

## 🚀 IMPLEMENTATION ORDER

**Phase 1: Foundation (Day 1)**
1. Set up CSS variables (design tokens)
2. Import Inter font
3. Apply dark theme globally

**Phase 2: Components (Days 2-3)**
4. Build button components
5. Build input components
6. Build card component
7. Test in isolation (Storybook optional)

**Phase 3: Layouts (Days 4-5)**
8. Build header
9. Build sidebar
10. Build main layout wrapper

**Phase 4: Screens (Days 6-10)**
11. Dashboard screen
12. Task board screen
13. Time tracking screen
14. Team screen
15. Hiring page

**Phase 5: Voice (Days 11-12)**
16. Voice button component
17. Voice integration
18. Test end-to-end

---

**REMEMBER:**

**Consistency > Creativity**

Use design tokens. Don't invent new colors or sizes.

**Accessibility > Aesthetics**

High contrast, keyboard navigation, screen reader support.

**Performance > Perfection**

60fps animations, lazy load images, optimize bundles.

**User Feedback > Assumptions**

Ship fast, learn, iterate.

---

**NOW GO BUILD BEAUTIFUL UIS!** 🎨🚀

---

**Document Version:** 1.0  
**Last Updated:** November 9, 2025  
**Design System:** Dark Minimal, Voice-First

