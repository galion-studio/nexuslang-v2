# GALION.STUDIO Alpha 🚀

**Transparent Workplace Platform - Built with Musk's First Principles**

## Quick Start (3 Steps)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
python app.py

# 3. Seed test data
curl -X POST http://localhost:5000/api/seed
```

**That's it! Your API is running.**

## What You Get

- ✅ Task management with transparent costs
- ✅ Time tracking
- ✅ Compensation transparency
- ✅ SQLite database (zero setup)
- ✅ REST API (full CRUD)

## API Endpoints

### Users
- `POST /api/users` - Create user
- `GET /api/users` - List users
- `GET /api/users/<id>` - Get user

### Workspaces
- `POST /api/workspaces` - Create workspace
- `GET /api/workspaces` - List workspaces

### Tasks
- `POST /api/tasks` - Create task
- `GET /api/tasks?workspace_id=X` - List tasks
- `PATCH /api/tasks/<id>` - Update task
- `DELETE /api/tasks/<id>` - Delete task

### Time Logs
- `POST /api/time-logs` - Log time
- `GET /api/time-logs?user_id=X` - List logs

### Analytics
- `GET /api/analytics/compensation?workspace_id=X` - Compensation summary

## Test It

```bash
# List all tasks
curl http://localhost:5000/api/tasks

# Create a new task
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "workspace_id": "YOUR_WORKSPACE_ID",
    "title": "Ship MVP",
    "hours_estimate": 40,
    "hourly_rate": 100
  }'

# Update task status
curl -X PATCH http://localhost:5000/api/tasks/TASK_ID \
  -H "Content-Type: application/json" \
  -d '{"status": "done"}'
```

## Next Steps

1. ✅ Backend running (you are here)
2. ⏳ Build React frontend
3. ⏳ Deploy locally
4. ⏳ Get 5 users
5. ⏳ Iterate based on feedback

## Architecture

**Super simple:**
- Flask (Python web framework)
- SQLite (embedded database)
- No auth yet (add after users love it)
- No caching (not needed for <100 users)
- No Docker (runs directly)

**This is ALPHA. Keep it simple.**

---

Built with ⚡ Elon Musk's First Principles ⚡

