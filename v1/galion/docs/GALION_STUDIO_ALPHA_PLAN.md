# GALION.STUDIO – ALPHA PLAN

**Collaborative Operations Hub for Entrepreneurs**

**Version:** 1.0  
**Date:** November 9, 2025  
**Status:** Planning Phase

---

## VISION

**What is GALION.STUDIO?**

A transparent, collaborative workspace for entrepreneurs and small teams to:
- Manage tasks and projects
- Track time and compensation
- Hire talent with analytics
- Collaborate with radical transparency

**Why build this?**

Current tools (Asana, Monday, Notion) lack:
- Pay transparency (who earns what, why)
- Time-to-money tracking (hours → compensation)
- Hiring analytics (pipeline, conversion, quality)
- Radical transparency (everyone sees everything)

**Philosophy:**
- Transparency is the default (hide nothing)
- Fair compensation (pay based on value, not negotiation)
- Data-driven decisions (analytics for everything)
- Remote-first (async collaboration)

---

## CORE FEATURES

### 1. Task Management

**Kanban Boards:**
- Columns: Backlog, To Do, In Progress, Review, Done
- Cards: Task title, description, assignee, time estimate, compensation
- Drag-and-drop
- Filters: By person, project, priority, status

**Task Details:**
```
┌─────────────────────────────────────────────────────────────┐
│  Task: Implement Voice Service                              │
├─────────────────────────────────────────────────────────────┤
│  Project: GALION.APP                                        │
│  Assignee: @john                                            │
│  Status: In Progress                                        │
│  Priority: High                                             │
│                                                             │
│  Time Estimate: 20 hours                                    │
│  Time Logged: 12 hours                                      │
│  Compensation: $1,200 ($100/hour)                           │
│  Paid: $600 (50%)                                           │
│                                                             │
│  Description:                                               │
│  Build voice-to-voice pipeline with Whisper and XTTS.      │
│                                                             │
│  Subtasks:                                                  │
│  ✅ Set up Faster-Whisper (4h, $400)                       │
│  ✅ Set up XTTS v2 (3h, $300)                              │
│  🔄 Integrate with WebSocket (5h, $500)                    │
│  ⏳ Testing and optimization (8h, $800)                    │
│                                                             │
│  Comments: 5                                                │
│  Attachments: 2                                             │
│                                                             │
│  [Edit] [Delete] [Mark Complete]                           │
└─────────────────────────────────────────────────────────────┘
```

**Transparency:**
- Everyone sees all tasks (no hidden work)
- Compensation visible to all team members
- Time logs public (who worked when, on what)

---

### 2. Roles & Permissions

**Role Hierarchy:**

| Role | Permissions |
|------|-------------|
| **Owner** | Full access, billing, delete workspace |
| **Admin** | Manage users, projects, compensation rates |
| **Manager** | Create tasks, assign work, approve timesheets |
| **Contributor** | Work on assigned tasks, log time, submit work |
| **Guest** | View-only access (no editing) |

**Permission Matrix:**

| Action | Owner | Admin | Manager | Contributor | Guest |
|--------|-------|-------|---------|-------------|-------|
| View tasks | ✅ | ✅ | ✅ | ✅ | ✅ |
| Create tasks | ✅ | ✅ | ✅ | ❌ | ❌ |
| Edit tasks | ✅ | ✅ | ✅ | Own only | ❌ |
| Delete tasks | ✅ | ✅ | ✅ | ❌ | ❌ |
| View compensation | ✅ | ✅ | ✅ | ✅ | ❌ |
| Edit compensation | ✅ | ✅ | ❌ | ❌ | ❌ |
| Manage users | ✅ | ✅ | ❌ | ❌ | ❌ |
| View analytics | ✅ | ✅ | ✅ | Own only | ❌ |

---

### 3. Time Tracking

**Manual Entry:**
```
┌─────────────────────────────────────────────────────────────┐
│  Log Time                                                   │
├─────────────────────────────────────────────────────────────┤
│  Task: Implement Voice Service                              │
│  Date: 2025-11-09                                           │
│  Hours: [4.5]                                               │
│  Description: Integrated Whisper with WebSocket             │
│                                                             │
│  [Save] [Cancel]                                            │
└─────────────────────────────────────────────────────────────┘
```

**Automatic Tracking (Future):**
- Browser extension (track active window)
- IDE plugin (track coding time)
- Git commits (estimate time from diffs)

**Timesheet View:**
```
┌─────────────────────────────────────────────────────────────┐
│  Timesheet – Week of Nov 9, 2025                           │
├─────────────────────────────────────────────────────────────┤
│  @john                                                      │
│                                                             │
│  Mon Nov 9:  8.0 hours  →  $800                            │
│    - Implement Voice Service (4.5h, $450)                  │
│    - Code review (2.0h, $200)                              │
│    - Team meeting (1.5h, $150)                             │
│                                                             │
│  Tue Nov 10: 7.5 hours  →  $750                            │
│    - Implement Voice Service (5.0h, $500)                  │
│    - Documentation (2.5h, $250)                            │
│                                                             │
│  ...                                                        │
│                                                             │
│  Total: 40.0 hours  →  $4,000                              │
│                                                             │
│  [Export] [Approve] [Request Payment]                      │
└─────────────────────────────────────────────────────────────┘
```

**Transparency:**
- All time logs visible to team
- Hourly rates visible (no secret salaries)
- Overtime flagged (> 40 hours/week)

---

### 4. Compensation Transparency

**Compensation Ledger:**
```
┌─────────────────────────────────────────────────────────────┐
│  Compensation Ledger – November 2025                        │
├─────────────────────────────────────────────────────────────┤
│  Team Member  │  Hours  │  Rate    │  Total   │  Paid     │
│───────────────┼─────────┼──────────┼──────────┼───────────│
│  @john        │  160    │  $100/h  │  $16,000 │  $16,000  │
│  @sarah       │  140    │  $120/h  │  $16,800 │  $16,800  │
│  @mike        │  100    │  $80/h   │  $8,000  │  $8,000   │
│  @lisa        │  80     │  $150/h  │  $12,000 │  $6,000   │
│───────────────┼─────────┼──────────┼──────────┼───────────│
│  Total        │  480    │  -       │  $52,800 │  $46,800  │
└─────────────────────────────────────────────────────────────┘
```

**Rate Justification:**
- Rates based on experience, skill, market
- Visible to all team members
- Adjustments logged (who changed, when, why)

**Payment Tracking:**
- Payment status: Pending, Approved, Paid
- Payment method: Bank transfer, PayPal, Crypto
- Payment date: Logged automatically

**Transparency:**
- Everyone sees everyone's compensation
- No secret raises or bonuses
- Fair pay based on value, not negotiation

---

### 5. Hiring Page

**Public Hiring Page:**
```
┌─────────────────────────────────────────────────────────────┐
│  GALION.STUDIO – Join Our Team                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  We're building the future of AI and collaboration.        │
│  Join us if you value transparency, autonomy, and impact.  │
│                                                             │
│  Open Positions:                                            │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Senior ML Engineer                                 │  │
│  │  Remote | Full-time | $120-180k/year               │  │
│  │                                                     │  │
│  │  Build voice-to-voice AI with Whisper and XTTS.   │  │
│  │  Work with Llama 3.1, RAG, and AWS infrastructure. │  │
│  │                                                     │  │
│  │  [Apply Now]                                        │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │  Full-Stack Engineer                                │  │
│  │  Remote | Full-time | $100-150k/year               │  │
│  │                                                     │  │
│  │  Build React + TypeScript UIs with dark minimal    │  │
│  │  design. Work with WebSockets, voice, and 3D.      │  │
│  │                                                     │  │
│  │  [Apply Now]                                        │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  Why Join Us?                                               │
│  ✅ Radical transparency (see everyone's compensation)     │
│  ✅ Remote-first (work from anywhere)                      │
│  ✅ Fair pay (based on value, not negotiation)            │
│  ✅ Cutting-edge tech (Llama 3.1, Whisper, AWS)           │
│  ✅ Small team (< 10 people, high impact)                 │
│                                                             │
│  [View All Positions]                                       │
└─────────────────────────────────────────────────────────────┘
```

**Application Form:**
```
┌─────────────────────────────────────────────────────────────┐
│  Apply for: Senior ML Engineer                             │
├─────────────────────────────────────────────────────────────┤
│  Name: [________________]                                   │
│  Email: [________________]                                  │
│  LinkedIn: [________________]                               │
│  GitHub: [________________]                                 │
│  Portfolio: [________________]                              │
│                                                             │
│  Why do you want to join GALION.STUDIO?                    │
│  [_____________________________________________________]    │
│  [_____________________________________________________]    │
│                                                             │
│  What's your experience with ML/AI?                         │
│  [_____________________________________________________]    │
│  [_____________________________________________________]    │
│                                                             │
│  Expected hourly rate: [$_____/hour]                        │
│  Available start date: [__________]                         │
│                                                             │
│  [Submit Application]                                       │
└─────────────────────────────────────────────────────────────┘
```

**Analytics:**
- Applications received: 50
- Applications reviewed: 30
- Interviews scheduled: 10
- Offers sent: 3
- Offers accepted: 2
- Time to hire: 14 days (average)
- Cost per hire: $500 (job board ads)

---

### 6. Analytics Dashboard

**Team Performance:**
```
┌─────────────────────────────────────────────────────────────┐
│  Team Analytics – November 2025                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Total Hours Worked: 480 hours                              │
│  Total Compensation: $52,800                                │
│  Average Rate: $110/hour                                    │
│                                                             │
│  Tasks Completed: 45                                        │
│  Tasks In Progress: 12                                      │
│  Tasks Blocked: 3                                           │
│                                                             │
│  Velocity: 15 tasks/week (↑ 20% from last month)          │
│  Cycle Time: 3.2 days (↓ 10% from last month)             │
│                                                             │
│  Top Contributors:                                          │
│  1. @sarah – 140 hours, 15 tasks, $16,800                  │
│  2. @john – 160 hours, 12 tasks, $16,000                   │
│  3. @mike – 100 hours, 10 tasks, $8,000                    │
│                                                             │
│  [View Details] [Export Report]                             │
└─────────────────────────────────────────────────────────────┘
```

**Project Health:**
```
┌─────────────────────────────────────────────────────────────┐
│  Project: GALION.APP                                        │
├─────────────────────────────────────────────────────────────┤
│  Status: On Track ✅                                        │
│  Progress: 65% complete                                     │
│  Budget: $45,000 / $60,000 (75% spent)                      │
│  Timeline: 2 weeks ahead of schedule                        │
│                                                             │
│  Milestones:                                                │
│  ✅ Alpha infrastructure (Week 1-2)                        │
│  ✅ Voice pipeline (Week 3-4)                              │
│  🔄 RAG baseline (Week 5-6) – In Progress                  │
│  ⏳ Security hardening (Week 7-8)                          │
│  ⏳ Beta launch (Week 9-10)                                │
│                                                             │
│  Risks:                                                     │
│  ⚠️ GPU costs higher than expected (+$500/month)          │
│  ⚠️ 1 developer on vacation (Week 7)                       │
│                                                             │
│  [View Tasks] [View Budget] [View Timeline]                │
└─────────────────────────────────────────────────────────────┘
```

---

## TECHNICAL ARCHITECTURE

### Tech Stack

**Frontend:**
- React 18 + TypeScript
- Tailwind CSS
- Zustand (state management)
- React Query (data fetching)
- Socket.IO client (real-time updates)

**Backend:**
- FastAPI (Python)
- PostgreSQL (data storage)
- Redis (caching, real-time)
- Socket.IO (WebSocket)
- Celery (background jobs)

**Infrastructure:**
- AWS ECS (compute)
- RDS Postgres (database)
- ElastiCache Redis (cache)
- S3 (file storage)
- CloudFront (CDN)

### Database Schema

**Users:**
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  name VARCHAR(255),
  role VARCHAR(50) NOT NULL,  -- owner, admin, manager, contributor, guest
  hourly_rate DECIMAL(10,2),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**Projects:**
```sql
CREATE TABLE projects (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  budget DECIMAL(10,2),
  start_date DATE,
  end_date DATE,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**Tasks:**
```sql
CREATE TABLE tasks (
  id UUID PRIMARY KEY,
  project_id UUID REFERENCES projects(id),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  assignee_id UUID REFERENCES users(id),
  status VARCHAR(50) NOT NULL,  -- backlog, todo, in_progress, review, done
  priority VARCHAR(50),  -- low, medium, high, urgent
  time_estimate_hours DECIMAL(10,2),
  compensation DECIMAL(10,2),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**Time Logs:**
```sql
CREATE TABLE time_logs (
  id UUID PRIMARY KEY,
  task_id UUID REFERENCES tasks(id),
  user_id UUID REFERENCES users(id),
  hours DECIMAL(10,2) NOT NULL,
  description TEXT,
  date DATE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**Payments:**
```sql
CREATE TABLE payments (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  amount DECIMAL(10,2) NOT NULL,
  status VARCHAR(50) NOT NULL,  -- pending, approved, paid
  payment_method VARCHAR(50),  -- bank_transfer, paypal, crypto
  payment_date DATE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## ROADMAP

### Alpha (Weeks 1-4)

**Features:**
- Task management (Kanban board)
- Time tracking (manual entry)
- Compensation ledger (view-only)
- Basic analytics (hours, tasks, compensation)

**Users:** Internal team only (5 people)

### Beta (Weeks 5-8)

**Features:**
- Hiring page (public)
- Application tracking (pipeline, analytics)
- Payment tracking (status, method, date)
- Advanced analytics (velocity, cycle time, project health)

**Users:** Internal + 2 partner companies (20 people total)

### 1.0 (Weeks 9-16)

**Features:**
- Automatic time tracking (browser extension, IDE plugin)
- Invoicing (generate invoices from timesheets)
- Integrations (Slack, GitHub, Linear)
- Mobile app (iOS, Android)

**Users:** Public launch (100+ companies)

---

## PRICING

### Free Tier
- Up to 5 users
- Unlimited tasks
- Basic analytics
- Community support

### Pro Tier ($20/user/month)
- Unlimited users
- Advanced analytics
- Priority support
- Integrations (Slack, GitHub)

### Enterprise Tier (Custom)
- Custom branding
- SSO (SAML, OIDC)
- Dedicated support
- On-premise deployment

---

## NEXT STEPS

1. **This Week:**
   - Design mockups (Figma)
   - Set up database schema
   - Build task management UI

2. **Next Week:**
   - Implement time tracking
   - Build compensation ledger
   - Add basic analytics

3. **Next Month:**
   - Launch alpha with internal team
   - Gather feedback
   - Iterate on UX

---

**Built with First Principles**  
**Status:** Ready to Build  
**Let's create transparency.** 🏢

