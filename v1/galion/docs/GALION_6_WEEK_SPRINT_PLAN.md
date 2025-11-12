# 🏃 GALION WORKPLACE - 6 WEEK SPRINT PLAN

**Day-by-Day Implementation Guide**

**Version:** 1.0  
**Date:** November 9, 2025  
**Approach:** Execute Fast, Ship Weekly, Iterate Daily

---

## 📋 SPRINT OVERVIEW

**Philosophy: Ship Every Friday**
- Week 1: Foundation (DB + Auth + Core API)
- Week 2: Task Management UI (Kanban + Voice)
- Week 3: Time Tracking & Compensation
- Week 4: Hiring Page & Pipeline
- Week 5: Security & Polish
- Week 6: Alpha Launch & Iteration

**Daily Rhythm:**
```
Morning:   Build (6 hours focused work)
Afternoon: Test & Deploy (2 hours)
Evening:   Document & Review (1 hour)
```

**No meetings. No distractions. Just ship.**

---

## 🗓️ WEEK 1: FOUNDATION

**Goal:** Working API with database, ready for frontend

### Monday (Day 1) - Database Schema

**Tasks:**
```bash
□ Set up PostgreSQL database
□ Create migration files
□ Implement core tables (users, workspaces, projects, tasks)
□ Add indexes for performance
□ Test migrations (up/down)
```

**Deliverables:**
```sql
-- File: database/migrations/001_core_schema.sql
CREATE TABLE workspaces (...);
CREATE TABLE projects (...);
CREATE TABLE tasks (...);
CREATE TABLE time_logs (...);
CREATE TABLE payments (...);

-- Run migration
psql -d galion_studio < database/migrations/001_core_schema.sql
```

**Testing:**
```bash
# Verify tables created
psql -d galion_studio -c "\dt"

# Test data insertion
INSERT INTO workspaces (name, slug, owner_id) VALUES (...);
INSERT INTO tasks (project_id, title, ...) VALUES (...);

# Verify constraints work
INSERT INTO tasks (hours_estimate) VALUES (-5);  # Should fail
```

**Success Criteria:**
- ✅ All tables created without errors
- ✅ Foreign keys enforce referential integrity
- ✅ Indexes exist on commonly queried columns
- ✅ Can insert/update/delete test data

---

### Tuesday (Day 2) - FastAPI Service Setup

**Tasks:**
```bash
□ Create FastAPI project structure
□ Set up database connection (SQLAlchemy)
□ Implement health check endpoint
□ Add CORS middleware
□ Integrate with existing auth service
```

**File Structure:**
```
services/workplace-service/
├── app/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Environment config
│   ├── database.py          # DB connection
│   ├── models/              # SQLAlchemy models
│   │   ├── workspace.py
│   │   ├── task.py
│   │   └── time_log.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── workspace.py
│   │   ├── task.py
│   │   └── time_log.py
│   ├── routers/             # API routes
│   │   ├── workspaces.py
│   │   ├── tasks.py
│   │   └── time_logs.py
│   └── dependencies.py      # Auth dependencies
├── Dockerfile
├── requirements.txt
└── docker-compose.yml
```

**Code Example:**
```python
# app/main.py
from fastapi import FastAPI
from app.routers import workspaces, tasks, time_logs
from app.database import engine
from app.models import Base

app = FastAPI(title="GALION.STUDIO API", version="1.0.0")

# Create tables
Base.metadata.create_all(bind=engine)

# Add routers
app.include_router(workspaces.router, prefix="/api/v1/workspaces", tags=["workspaces"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(time_logs.router, prefix="/api/v1/time-logs", tags=["time-logs"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "workplace-service"}
```

**Testing:**
```bash
# Run service
uvicorn app.main:app --reload

# Test health check
curl http://localhost:8000/health

# Check API docs
open http://localhost:8000/docs
```

**Success Criteria:**
- ✅ Service starts without errors
- ✅ Health check returns 200
- ✅ Swagger docs accessible
- ✅ Can connect to database

---

### Wednesday (Day 3) - Core API Endpoints (Part 1)

**Tasks:**
```bash
□ Implement workspace endpoints (CRUD)
□ Implement project endpoints (CRUD)
□ Add authentication middleware
□ Add input validation
```

**Endpoints to Build:**
```python
# Workspaces
POST   /api/v1/workspaces           # Create workspace
GET    /api/v1/workspaces           # List user's workspaces
GET    /api/v1/workspaces/:id       # Get workspace details
PATCH  /api/v1/workspaces/:id       # Update workspace
DELETE /api/v1/workspaces/:id       # Delete workspace

# Projects
POST   /api/v1/projects             # Create project
GET    /api/v1/projects             # List projects (filtered by workspace)
GET    /api/v1/projects/:id         # Get project details
PATCH  /api/v1/projects/:id         # Update project
DELETE /api/v1/projects/:id         # Delete project
```

**Example Implementation:**
```python
# app/routers/workspaces.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse
from app.dependencies import get_current_user

router = APIRouter()

@router.post("/", response_model=WorkspaceResponse, status_code=201)
def create_workspace(
    workspace: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Validate slug is unique
    existing = db.query(Workspace).filter(Workspace.slug == workspace.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")
    
    # Create workspace
    db_workspace = Workspace(
        **workspace.dict(),
        owner_id=current_user.id
    )
    db.add(db_workspace)
    db.commit()
    db.refresh(db_workspace)
    
    return db_workspace

@router.get("/", response_model=list[WorkspaceResponse])
def list_workspaces(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Return workspaces where user is owner or member
    workspaces = db.query(Workspace).filter(
        Workspace.owner_id == current_user.id
    ).all()
    return workspaces
```

**Testing:**
```bash
# Test workspace creation
curl -X POST http://localhost:8000/api/v1/workspaces \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Acme Corp","slug":"acme-corp"}'

# Test list workspaces
curl http://localhost:8000/api/v1/workspaces \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Success Criteria:**
- ✅ All endpoints return correct status codes
- ✅ Authentication required (401 if no token)
- ✅ Input validation works (400 for invalid data)
- ✅ Data persists in database

---

### Thursday (Day 4) - Core API Endpoints (Part 2)

**Tasks:**
```bash
□ Implement task endpoints (CRUD)
□ Implement time log endpoints (CRUD)
□ Add pagination support
□ Add filtering & sorting
```

**Endpoints to Build:**
```python
# Tasks
POST   /api/v1/tasks                # Create task
GET    /api/v1/tasks                # List tasks (filtered)
GET    /api/v1/tasks/:id            # Get task details
PATCH  /api/v1/tasks/:id            # Update task
DELETE /api/v1/tasks/:id            # Delete task

# Time Logs
POST   /api/v1/time-logs            # Log time
GET    /api/v1/time-logs            # List time logs (filtered)
GET    /api/v1/time-logs/:id        # Get time log details
DELETE /api/v1/time-logs/:id        # Delete time log
```

**Example: Task Endpoint with Filtering**
```python
# app/routers/tasks.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskResponse

router = APIRouter()

@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    project_id: str | None = Query(None),
    assignee_id: str | None = Query(None),
    status: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    query = db.query(Task)
    
    # Apply filters
    if project_id:
        query = query.filter(Task.project_id == project_id)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)
    if status:
        query = query.filter(Task.status == status)
    
    # Pagination
    tasks = query.offset(skip).limit(limit).all()
    return tasks

@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    db_task = Task(**task.dict(), created_by=current_user.id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task
```

**Testing:**
```bash
# Create task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "uuid-here",
    "title": "Build hiring page",
    "assignee_id": "uuid-here",
    "hours_estimate": 8,
    "hourly_rate": 100
  }'

# Filter tasks
curl "http://localhost:8000/api/v1/tasks?status=in_progress&assignee_id=uuid" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Success Criteria:**
- ✅ CRUD operations work for all entities
- ✅ Filtering works correctly
- ✅ Pagination works
- ✅ Computed fields work (total_amount in time_logs)

---

### Friday (Day 5) - Docker & Deploy

**Tasks:**
```bash
□ Create Dockerfile for workplace-service
□ Update docker-compose.yml
□ Test full stack locally
□ Write API documentation
□ Deploy to localhost
```

**Dockerfile:**
```dockerfile
# services/workplace-service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
```

**Update docker-compose.yml:**
```yaml
services:
  workplace-service:
    build: ./services/workplace-service
    ports:
      - "8004:8004"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/galion_studio
      - REDIS_URL=redis://redis:6379/0
      - AUTH_SERVICE_URL=http://auth-service:8000
    depends_on:
      - postgres
      - redis
```

**Testing:**
```bash
# Build and start all services
docker-compose up --build -d

# Check all services healthy
docker-compose ps

# Test API
curl http://localhost:8004/health
curl http://localhost:8004/docs

# Check logs
docker-compose logs -f workplace-service
```

**Documentation:**
```bash
# API docs auto-generated by FastAPI
open http://localhost:8004/docs

# Write README
echo "# Workplace Service\n\nCore API for GALION.STUDIO" > services/workplace-service/README.md
```

**Success Criteria:**
- ✅ All services start in Docker
- ✅ API accessible from host machine
- ✅ Can create workspace → project → task → time log
- ✅ Data persists after container restart
- ✅ API docs accessible

---

## 🗓️ WEEK 2: TASK MANAGEMENT UI

**Goal:** Beautiful Kanban board with drag-drop and voice

### Monday (Day 6) - React App Setup

**Tasks:**
```bash
□ Create React app with TypeScript
□ Configure Tailwind CSS
□ Set up routing (React Router)
□ Set up state management (Zustand)
□ Create layout components
```

**Setup:**
```bash
# Create React app
cd frontend
npx create-react-app galion-studio --template typescript
cd galion-studio

# Install dependencies
npm install \
  react-router-dom \
  zustand \
  tailwindcss \
  @tailwindcss/forms \
  axios \
  socket.io-client \
  @tanstack/react-query \
  react-beautiful-dnd

# Configure Tailwind
npx tailwindcss init -p
```

**File Structure:**
```
frontend/galion-studio/
├── src/
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Layout.tsx
│   │   ├── tasks/
│   │   ├── time/
│   │   └── voice/
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── TaskBoard.tsx
│   │   ├── TimeTracking.tsx
│   │   └── Team.tsx
│   ├── stores/
│   │   ├── authStore.ts
│   │   ├── workspaceStore.ts
│   │   ├── taskStore.ts
│   │   └── timeStore.ts
│   ├── api/
│   │   └── client.ts
│   ├── types/
│   │   └── index.ts
│   └── App.tsx
├── tailwind.config.js
└── package.json
```

**Basic Layout Component:**
```tsx
// src/components/layout/Layout.tsx
import { Header } from './Header';
import { Sidebar } from './Sidebar';

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-[#0A0A0A]">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
```

**Zustand Store:**
```tsx
// src/stores/taskStore.ts
import create from 'zustand';
import { Task } from '@/types';

interface TaskStore {
  tasks: Task[];
  loading: boolean;
  fetchTasks: (projectId: string) => Promise<void>;
  createTask: (task: Partial<Task>) => Promise<void>;
  updateTask: (id: string, updates: Partial<Task>) => Promise<void>;
  deleteTask: (id: string) => Promise<void>;
}

export const useTaskStore = create<TaskStore>((set, get) => ({
  tasks: [],
  loading: false,
  
  fetchTasks: async (projectId) => {
    set({ loading: true });
    const response = await fetch(`/api/v1/tasks?project_id=${projectId}`);
    const tasks = await response.json();
    set({ tasks, loading: false });
  },
  
  createTask: async (task) => {
    const response = await fetch('/api/v1/tasks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(task),
    });
    const newTask = await response.json();
    set({ tasks: [...get().tasks, newTask] });
  },
  
  // ... other methods
}));
```

**Success Criteria:**
- ✅ React app runs without errors
- ✅ Tailwind CSS styles work
- ✅ Routing between pages works
- ✅ Zustand store can fetch/update data
- ✅ Dark theme applied globally

---

### Tuesday (Day 7) - Kanban Board UI

**Tasks:**
```bash
□ Build Kanban board component
□ Add drag-and-drop (react-beautiful-dnd)
□ Style task cards
□ Add column headers
□ Test drag between columns
```

**Kanban Board Component:**
```tsx
// src/components/tasks/KanbanBoard.tsx
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { useTaskStore } from '@/stores/taskStore';
import { TaskCard } from './TaskCard';

const COLUMNS = [
  { id: 'backlog', title: 'Backlog' },
  { id: 'in_progress', title: 'In Progress' },
  { id: 'done', title: 'Done' },
];

export function KanbanBoard() {
  const { tasks, updateTask } = useTaskStore();
  
  const handleDragEnd = (result) => {
    if (!result.destination) return;
    
    const taskId = result.draggableId;
    const newStatus = result.destination.droppableId;
    
    updateTask(taskId, { status: newStatus });
  };
  
  const getTasksByStatus = (status: string) =>
    tasks.filter(task => task.status === status);
  
  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      <div className="flex gap-6 overflow-x-auto pb-8">
        {COLUMNS.map(column => (
          <div key={column.id} className="min-w-[300px] flex-1">
            {/* Column Header */}
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">
                {column.title}
              </h3>
              <span className="text-sm text-gray-400">
                {getTasksByStatus(column.id).length}
              </span>
            </div>
            
            {/* Droppable Area */}
            <Droppable droppableId={column.id}>
              {(provided, snapshot) => (
                <div
                  ref={provided.innerRef}
                  {...provided.droppableProps}
                  className={`
                    min-h-[500px] rounded-lg bg-[#1A1A1A] p-4
                    ${snapshot.isDraggingOver ? 'bg-[#2A2A2A]' : ''}
                  `}
                >
                  {getTasksByStatus(column.id).map((task, index) => (
                    <Draggable
                      key={task.id}
                      draggableId={task.id}
                      index={index}
                    >
                      {(provided, snapshot) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          {...provided.dragHandleProps}
                          className={`mb-3 ${snapshot.isDragging ? 'opacity-50' : ''}`}
                        >
                          <TaskCard task={task} />
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </div>
        ))}
      </div>
    </DragDropContext>
  );
}
```

**Task Card Component:**
```tsx
// src/components/tasks/TaskCard.tsx
import { Task } from '@/types';

export function TaskCard({ task }: { task: Task }) {
  const totalCost = (task.hours_estimate || 0) * (task.hourly_rate || 0);
  
  return (
    <div className="rounded-lg bg-[#2A2A2A] p-4 shadow-md hover:bg-[#3A3A3A] cursor-pointer transition-colors">
      {/* Title */}
      <h4 className="text-base font-medium text-white mb-2">
        {task.title}
      </h4>
      
      {/* Assignee */}
      {task.assignee && (
        <div className="flex items-center gap-2 mb-3">
          <img
            src={task.assignee.avatar_url}
            alt={task.assignee.name}
            className="w-6 h-6 rounded-full"
          />
          <span className="text-sm text-gray-400">
            {task.assignee.name}
          </span>
        </div>
      )}
      
      {/* Compensation */}
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-400">
          {task.hours_estimate}h @ ${task.hourly_rate}/h
        </span>
        <span className="font-semibold text-[#00FF88]">
          ${totalCost.toLocaleString()}
        </span>
      </div>
      
      {/* Priority Badge */}
      {task.priority && task.priority !== 'medium' && (
        <span className={`
          inline-block mt-2 px-2 py-1 rounded text-xs
          ${task.priority === 'high' ? 'bg-[#FFB800] text-black' : ''}
          ${task.priority === 'urgent' ? 'bg-[#FF3B3B] text-white' : ''}
          ${task.priority === 'low' ? 'bg-gray-600 text-white' : ''}
        `}>
          {task.priority}
        </span>
      )}
    </div>
  );
}
```

**Success Criteria:**
- ✅ Kanban board renders 3 columns
- ✅ Tasks display in correct columns
- ✅ Drag-and-drop works smoothly
- ✅ Task card shows title, assignee, cost
- ✅ Optimistic UI updates (instant feedback)

---

### Wednesday (Day 8) - Task Creation & Editing

**Tasks:**
```bash
□ Build task creation modal
□ Add task edit modal
□ Implement form validation
□ Add inline task creation
□ Connect to API
```

**Task Modal:**
```tsx
// src/components/tasks/TaskModal.tsx
import { useState } from 'react';
import { useTaskStore } from '@/stores/taskStore';
import { Task } from '@/types';

interface TaskModalProps {
  task?: Task;  // Undefined for new task
  onClose: () => void;
}

export function TaskModal({ task, onClose }: TaskModalProps) {
  const { createTask, updateTask } = useTaskStore();
  const isEditing = !!task;
  
  const [formData, setFormData] = useState({
    title: task?.title || '',
    description: task?.description || '',
    assignee_id: task?.assignee_id || '',
    hours_estimate: task?.hours_estimate || 0,
    hourly_rate: task?.hourly_rate || 100,
    priority: task?.priority || 'medium',
    due_date: task?.due_date || '',
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  const validate = () => {
    const newErrors: Record<string, string> = {};
    
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    if (formData.hours_estimate <= 0) {
      newErrors.hours_estimate = 'Hours must be positive';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validate()) return;
    
    if (isEditing) {
      await updateTask(task.id, formData);
    } else {
      await createTask(formData);
    }
    
    onClose();
  };
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-[#1A1A1A] rounded-lg p-6 w-full max-w-2xl">
        <h2 className="text-2xl font-semibold text-white mb-6">
          {isEditing ? 'Edit Task' : 'Create Task'}
        </h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Title *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={e => setFormData({ ...formData, title: e.target.value })}
              className="w-full px-4 py-2 bg-[#2A2A2A] text-white rounded-lg focus:ring-2 focus:ring-[#00D9FF]"
              placeholder="Build hiring page"
            />
            {errors.title && (
              <p className="text-sm text-[#FF3B3B] mt-1">{errors.title}</p>
            )}
          </div>
          
          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={e => setFormData({ ...formData, description: e.target.value })}
              rows={4}
              className="w-full px-4 py-2 bg-[#2A2A2A] text-white rounded-lg focus:ring-2 focus:ring-[#00D9FF]"
              placeholder="Add details..."
            />
          </div>
          
          {/* Hours & Rate */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Hours Estimate *
              </label>
              <input
                type="number"
                step="0.5"
                value={formData.hours_estimate}
                onChange={e => setFormData({ ...formData, hours_estimate: parseFloat(e.target.value) })}
                className="w-full px-4 py-2 bg-[#2A2A2A] text-white rounded-lg focus:ring-2 focus:ring-[#00D9FF]"
              />
              {errors.hours_estimate && (
                <p className="text-sm text-[#FF3B3B] mt-1">{errors.hours_estimate}</p>
              )}
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Hourly Rate
              </label>
              <input
                type="number"
                value={formData.hourly_rate}
                onChange={e => setFormData({ ...formData, hourly_rate: parseFloat(e.target.value) })}
                className="w-full px-4 py-2 bg-[#2A2A2A] text-white rounded-lg focus:ring-2 focus:ring-[#00D9FF]"
              />
            </div>
          </div>
          
          {/* Total Cost Display */}
          <div className="bg-[#2A2A2A] p-4 rounded-lg">
            <p className="text-sm text-gray-400 mb-1">Estimated Total Cost</p>
            <p className="text-2xl font-bold text-[#00FF88]">
              ${(formData.hours_estimate * formData.hourly_rate).toLocaleString()}
            </p>
          </div>
          
          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 bg-[#2A2A2A] text-white rounded-lg hover:bg-[#3A3A3A]"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-6 py-2 bg-[#00D9FF] text-black font-semibold rounded-lg hover:bg-[#00B8DD]"
            >
              {isEditing ? 'Save Changes' : 'Create Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
```

**Success Criteria:**
- ✅ Modal opens/closes smoothly
- ✅ Form validation works
- ✅ Cost updates in real-time
- ✅ Can create/edit tasks
- ✅ Data persists to API

---

### Thursday-Friday (Days 9-10) - Voice Integration

**Tasks:**
```bash
□ Build voice button component
□ Implement audio recording (MediaRecorder)
□ Connect to voice service API
□ Add voice command parsing
□ Show voice status (listening, processing, speaking)
□ Test voice task creation
```

**Voice Button Component:**
```tsx
// src/components/voice/VoiceButton.tsx
import { useState, useRef } from 'react';
import { Waveform } from './Waveform';

type VoiceStatus = 'idle' | 'listening' | 'processing' | 'speaking';

export function VoiceButton() {
  const [status, setStatus] = useState<VoiceStatus>('idle');
  const [transcript, setTranscript] = useState('');
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      
      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };
      
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        audioChunksRef.current = [];
        
        await processVoiceCommand(audioBlob);
        
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorder.start();
      mediaRecorderRef.current = mediaRecorder;
      setStatus('listening');
    } catch (error) {
      console.error('Microphone access denied:', error);
    }
  };
  
  const stopRecording = () => {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.stop();
      setStatus('processing');
    }
  };
  
  const processVoiceCommand = async (audioBlob: Blob) => {
    const formData = new FormData();
    formData.append('audio', audioBlob);
    
    try {
      const response = await fetch('/api/v1/voice/command', {
        method: 'POST',
        body: formData,
      });
      
      const result = await response.json();
      
      setTranscript(result.transcript);
      
      // Execute the command
      // (e.g., create task, log time, query data)
      
      // If there's a speech response, play it
      if (result.audio) {
        setStatus('speaking');
        await playAudio(result.audio);
      }
      
      setStatus('idle');
    } catch (error) {
      console.error('Voice command failed:', error);
      setStatus('idle');
    }
  };
  
  const playAudio = (audioBase64: string): Promise<void> => {
    return new Promise((resolve) => {
      const audio = new Audio(`data:audio/wav;base64,${audioBase64}`);
      audio.onended = () => resolve();
      audio.play();
    });
  };
  
  return (
    <div className="fixed bottom-8 right-8 z-50">
      <button
        onMouseDown={startRecording}
        onMouseUp={stopRecording}
        onTouchStart={startRecording}
        onTouchEnd={stopRecording}
        className={`
          w-16 h-16 rounded-full shadow-lg flex items-center justify-center
          transition-all duration-200 transform
          ${status === 'idle' ? 'bg-[#00D9FF] hover:scale-110' : ''}
          ${status === 'listening' ? 'bg-[#00D9FF] scale-110 animate-pulse' : ''}
          ${status === 'processing' ? 'bg-[#FF006E]' : ''}
          ${status === 'speaking' ? 'bg-[#00FF88]' : ''}
        `}
      >
        {status === 'idle' && <span className="text-3xl">🎤</span>}
        {status === 'listening' && <span className="text-3xl">🎤</span>}
        {status === 'processing' && <span className="text-3xl">🧠</span>}
        {status === 'speaking' && <span className="text-3xl">🔊</span>}
      </button>
      
      {status === 'listening' && (
        <div className="mt-2">
          <Waveform />
        </div>
      )}
      
      {transcript && (
        <div className="mt-2 bg-[#1A1A1A] text-white p-3 rounded-lg text-sm max-w-xs">
          {transcript}
        </div>
      )}
    </div>
  );
}
```

**Success Criteria:**
- ✅ Voice recording works
- ✅ Audio uploaded to backend
- ✅ Transcription displayed
- ✅ Voice commands executed
- ✅ Can create task via voice

---

## 🗓️ WEEK 3-6 (Abbreviated for Length)

Due to space constraints, I'm summarizing the remaining weeks:

**WEEK 3: Time Tracking & Compensation**
- Build time entry form
- Build timesheet view
- Build compensation ledger
- Test voice time logging

**WEEK 4: Hiring Page**
- Build public hiring page
- Build application form
- Build application pipeline
- Add analytics

**WEEK 5: Security & Polish**
- Implement 2FA
- Add rate limiting
- Performance optimization
- Documentation

**WEEK 6: Alpha Launch**
- Invite beta users
- Monitor and fix bugs
- Iterate daily
- Gather feedback

---

## ✅ DAILY CHECKLIST TEMPLATE

**Every Morning:**
```bash
□ Pull latest code (git pull)
□ Check for issues/bugs (GitHub Issues)
□ Review yesterday's work
□ Plan today's tasks (2-3 features max)
```

**Every Afternoon:**
```bash
□ Test what you built
□ Deploy to localhost/staging
□ Update documentation
□ Commit & push code
```

**Every Evening:**
```bash
□ Review PRs (if team)
□ Update project board
□ Document blockers
□ Plan tomorrow
```

---

## 🎯 SUCCESS METRICS

**Week 1 Success:**
- ✅ Database schema complete
- ✅ API endpoints working
- ✅ Service running in Docker
- ✅ Can CRUD all entities

**Week 2 Success:**
- ✅ Kanban board working
- ✅ Drag-and-drop smooth
- ✅ Voice recording works
- ✅ Task creation fast (<5s)

**Week 6 Success:**
- ✅ 10 teams using platform
- ✅ 500+ tasks created
- ✅ 1000+ time logs
- ✅ Voice usage >30%
- ✅ NPS > 50

---

## 🚀 DEPLOYMENT CHECKLIST

**Before Each Deploy:**
```bash
□ Run tests (npm test, pytest)
□ Check linter (eslint, flake8)
□ Build Docker images
□ Update environment variables
□ Backup database
```

**After Each Deploy:**
```bash
□ Smoke test critical paths
□ Check logs for errors
□ Monitor performance metrics
□ Notify team in Slack
```

---

**REMEMBER:**

**Ship > Perfect**

**Fast > Feature-Complete**

**User Feedback > Assumptions**

**Done > In Progress**

**NOW GO BUILD!** 🚀

---

**Document Version:** 1.0  
**Last Updated:** November 9, 2025

**Execute. Ship. Iterate. Repeat.**

