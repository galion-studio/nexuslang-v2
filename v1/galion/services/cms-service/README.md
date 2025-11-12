# Simple Content Management System (CMS)

A clean, modular, and easy-to-use Content Management System built with **FastAPI** (backend) and **React** (frontend).

## ✨ Features

- 📝 **Content Management**: Create, edit, and delete blog posts, pages, and articles
- 🏷️ **Category System**: Organize content with categories
- 🔐 **User Authentication**: Secure login and registration with JWT tokens
- 📊 **Content Status**: Draft, Published, and Archived states
- 👀 **View Counter**: Track content views automatically
- 🎨 **Clean UI**: Modern, responsive interface
- 📱 **SEO Ready**: Meta tags and featured images support
- 🚀 **Easy Setup**: Simple scripts to get started quickly

## 📋 Requirements

### Backend
- Python 3.8 or higher
- pip (Python package manager)

### Frontend
- Node.js 14 or higher
- npm (comes with Node.js)

## 🚀 Quick Start

### Option 1: Start Everything at Once (Recommended)

**Windows:**
```bash
START-CMS.bat
```

**Linux/Mac:**
```bash
chmod +x START-CMS.sh
./START-CMS.sh
```

This will automatically start both the backend and frontend.

### Option 2: Start Services Separately

**Backend (Terminal 1):**
```bash
# Windows
start-backend.bat

# Linux/Mac
chmod +x start-backend.sh
./start-backend.sh
```

**Frontend (Terminal 2):**
```bash
cd frontend

# Windows
start-frontend.bat

# Linux/Mac
chmod +x start-frontend.sh
./start-frontend.sh
```

## 🌐 Access the CMS

After starting the services:

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Interactive Swagger UI)
- **Alternative API Docs**: http://localhost:8000/redoc

## 👤 Getting Started Guide

### 1. Create Your First Account

1. Open http://localhost:3000
2. Click "Register" in the navigation bar
3. Fill in:
   - Username (min 3 characters)
   - Email address
   - Password (min 6 characters)
4. Click "Register"
5. You'll be automatically logged in

### 2. Create a Category

1. Click "Categories" in the navigation
2. Click "+ Add Category"
3. Enter:
   - Name (e.g., "Technology", "News")
   - Slug (auto-generated from name)
   - Description (optional)
4. Click "Create Category"

### 3. Create Your First Post

1. Click "Create" in the navigation
2. Fill in the form:
   - **Title**: Your post title
   - **Slug**: Auto-generated URL-friendly version
   - **Content**: Your post content
   - **Excerpt**: Short preview (optional)
   - **Content Type**: Post, Page, or Article
   - **Status**: Draft or Published
   - **Category**: Select a category
3. Click "Create Content"
4. Your content is now live!

## 📁 Project Structure

```
cms-service/
├── app/                      # Backend application
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── database.py          # Database configuration
│   ├── models.py            # SQLAlchemy models (User, Content, Category)
│   ├── schemas.py           # Pydantic schemas for validation
│   ├── auth.py              # Authentication & JWT handling
│   └── routers/             # API route handlers
│       ├── auth_router.py   # Login/register endpoints
│       ├── content_router.py # Content CRUD endpoints
│       └── category_router.py # Category CRUD endpoints
├── frontend/                 # React frontend application
│   ├── public/
│   │   └── index.html       # HTML template
│   └── src/
│       ├── index.js         # React entry point
│       ├── App.js           # Main app with routing
│       ├── api.js           # API service layer
│       ├── AuthContext.js   # Authentication context
│       └── components/      # React components
│           ├── Login.js
│           ├── Register.js
│           ├── ContentList.js
│           ├── ContentEditor.js
│           └── CategoryManager.js
├── requirements.txt          # Python dependencies
├── start-backend.bat/sh     # Backend startup scripts
├── START-CMS.bat/sh         # Full system startup scripts
└── README.md                # This file
```

## 🔧 Configuration

### Backend Configuration

The backend uses SQLite by default (no configuration needed). The database file `cms.db` is created automatically in the project root.

To use a different database, edit `app/database.py`:

```python
# PostgreSQL example
DATABASE_URL = "postgresql://user:password@localhost/cms_db"

# MySQL example
DATABASE_URL = "mysql://user:password@localhost/cms_db"
```

### Frontend Configuration

To change the API URL, edit `frontend/src/api.js`:

```javascript
const API_BASE_URL = 'http://your-api-url:8000';
```

## 📚 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get token
- `GET /api/auth/me` - Get current user info

### Content
- `GET /api/content/` - List all content (with filters)
- `GET /api/content/{id}` - Get content by ID
- `GET /api/content/slug/{slug}` - Get content by slug
- `POST /api/content/` - Create new content (auth required)
- `PUT /api/content/{id}` - Update content (auth required)
- `DELETE /api/content/{id}` - Delete content (auth required)

### Categories
- `GET /api/categories/` - List all categories
- `GET /api/categories/{id}` - Get category by ID
- `POST /api/categories/` - Create category (auth required)
- `PUT /api/categories/{id}` - Update category (auth required)
- `DELETE /api/categories/{id}` - Delete category (auth required)

## 🧪 Testing the API

Visit http://localhost:8000/docs for interactive API documentation where you can test all endpoints directly in your browser.

## 🛠️ Development

### Backend Development

The backend uses FastAPI with SQLAlchemy ORM. Key files:

- `models.py` - Database table definitions
- `schemas.py` - Request/response validation
- `routers/` - API endpoint handlers
- `auth.py` - JWT authentication logic

The API automatically reloads when you save changes to Python files.

### Frontend Development

The frontend is a React app with React Router for navigation. Key files:

- `App.js` - Main app with routing
- `api.js` - Backend API calls
- `AuthContext.js` - Global auth state
- `components/` - UI components

The frontend automatically reloads when you save changes.

## 🐛 Troubleshooting

### Backend won't start

**Issue**: Python not found
```bash
# Install Python from python.org
# Or use: py -m pip install -r requirements.txt (Windows)
```

**Issue**: Port 8000 already in use
```bash
# Change port in start script:
uvicorn app.main:app --port 8001
```

### Frontend won't start

**Issue**: Node.js not found
```bash
# Install Node.js from nodejs.org
```

**Issue**: Port 3000 already in use
```bash
# The script will offer to use a different port automatically
```

### Cannot connect to API

**Issue**: CORS errors in browser console
- Make sure backend is running on port 8000
- Check `app/main.py` CORS configuration

### Database errors

**Issue**: Database locked
```bash
# Delete cms.db and restart to create a fresh database
rm cms.db  # Linux/Mac
del cms.db # Windows
```

## 📦 Production Deployment

### Backend

1. Set a strong `SECRET_KEY` in `app/auth.py`
2. Use a production database (PostgreSQL recommended)
3. Set `allow_origins` in CORS to specific domains
4. Use a production server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Frontend

1. Update `API_BASE_URL` in `src/api.js` to your production API
2. Build for production:
   ```bash
   cd frontend
   npm run build
   ```
3. Serve the `build/` folder with any static server

## 🤝 Contributing

This is a simple, educational CMS. Feel free to:
- Add features (image uploads, comments, tags)
- Improve the UI
- Add tests
- Fix bugs

## 📝 License

MIT License - Feel free to use this for any purpose.

## 🎓 Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **React**: https://react.dev/
- **SQLAlchemy**: https://www.sqlalchemy.org/
- **JWT Authentication**: https://jwt.io/

## 💡 Next Steps

Ideas for extending this CMS:

1. **Rich Text Editor**: Add a WYSIWYG editor (TinyMCE, Quill)
2. **Image Upload**: Add file upload functionality
3. **Comments**: Allow readers to comment on content
4. **Tags**: Add tagging system alongside categories
5. **Search**: Full-text search functionality
6. **Media Library**: Manage uploaded images and files
7. **Multiple Authors**: User roles and permissions
8. **Analytics Dashboard**: View statistics and trends
9. **Email Notifications**: Notify on new content
10. **API Rate Limiting**: Prevent abuse

## 🆘 Support

If you encounter issues:

1. Check this README for troubleshooting tips
2. Review the API documentation at `/docs`
3. Check console logs for error messages
4. Verify both backend and frontend are running

## 📸 Screenshots

The CMS includes:
- ✅ Clean login and registration pages
- ✅ Content list with filtering
- ✅ Rich content editor
- ✅ Category management
- ✅ Responsive design

---

**Built with simplicity and clarity in mind.**

**Happy content managing! 🎉**

