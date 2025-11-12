# CMS Testing Guide

This guide helps you verify that your CMS is working correctly.

## 🧪 Automated Testing

### Backend API Tests

Test the backend API directly:

```bash
# Activate virtual environment first
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Run tests (if you've installed pytest)
pytest tests/

# Or test manually with curl:
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "cms-api"
}
```

## ✅ Manual Testing Checklist

### 1. Backend Tests

#### Test 1: Health Check
- URL: http://localhost:8000/health
- Expected: `{"status": "healthy"}`
- ✅ Pass / ❌ Fail

#### Test 2: API Documentation
- URL: http://localhost:8000/docs
- Expected: Interactive API documentation page
- ✅ Pass / ❌ Fail

#### Test 3: Root Endpoint
- URL: http://localhost:8000/
- Expected: Welcome message with version
- ✅ Pass / ❌ Fail

### 2. Authentication Tests

#### Test 4: User Registration
1. Go to http://localhost:3000/register
2. Register with:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `test123`
3. Expected: Redirected to home page, logged in
- ✅ Pass / ❌ Fail

#### Test 5: User Login
1. Logout (if logged in)
2. Go to http://localhost:3000/login
3. Login with credentials from Test 4
4. Expected: Successfully logged in, redirected to home
- ✅ Pass / ❌ Fail

#### Test 6: Protected Routes
1. Logout
2. Try to access http://localhost:3000/create
3. Expected: Redirected to login page
- ✅ Pass / ❌ Fail

### 3. Category Tests

#### Test 7: Create Category
1. Login and go to http://localhost:3000/categories
2. Click "+ Add Category"
3. Create category:
   - Name: `Technology`
   - Slug: `technology` (auto-filled)
   - Description: `Tech articles`
4. Click "Create Category"
5. Expected: Category appears in list
- ✅ Pass / ❌ Fail

#### Test 8: Edit Category
1. On categories page, click "Edit" on your category
2. Change name to `Tech`
3. Click "Update Category"
4. Expected: Category name updated
- ✅ Pass / ❌ Fail

#### Test 9: Delete Category
1. Create a new test category
2. Click "Delete" and confirm
3. Expected: Category removed from list
- ✅ Pass / ❌ Fail

### 4. Content Tests

#### Test 10: Create Draft Post
1. Go to http://localhost:3000/create
2. Fill in:
   - Title: `Test Draft Post`
   - Content: `This is a test draft`
   - Status: `Draft`
3. Click "Create Content"
4. Expected: Success message, redirected to content list
- ✅ Pass / ❌ Fail

#### Test 11: Create Published Post
1. Go to http://localhost:3000/create
2. Fill in:
   - Title: `My First Published Post`
   - Content: `This is published content`
   - Excerpt: `A short preview`
   - Category: Select `Technology`
   - Status: `Published`
3. Click "Create Content"
4. Expected: Post appears in content list
- ✅ Pass / ❌ Fail

#### Test 12: View Content
1. On content list page
2. Find your published post
3. Expected: Shows title, excerpt, category badge, author, date, views
- ✅ Pass / ❌ Fail

#### Test 13: Edit Content
1. Click "Edit" on a post
2. Change title to `Updated Title`
3. Change status to `Published`
4. Click "Update Content"
5. Expected: Content updated successfully
- ✅ Pass / ❌ Fail

#### Test 14: View Counter
1. Click on a content item multiple times
2. Refresh the page
3. Expected: View count increases
- ✅ Pass / ❌ Fail

#### Test 15: Filter by Category
1. On content list page
2. Select a category from dropdown
3. Expected: Only content from that category shown
- ✅ Pass / ❌ Fail

#### Test 16: Filter by Status
1. On content list page (logged in)
2. Change status filter to "Draft"
3. Expected: Only draft content shown
- ✅ Pass / ❌ Fail

#### Test 17: Delete Content
1. Create a test post
2. Click "Delete" and confirm
3. Expected: Content removed from list
- ✅ Pass / ❌ Fail

### 5. SEO and Meta Tests

#### Test 18: SEO Fields
1. Create new content
2. Scroll to SEO section
3. Fill in:
   - Meta Title
   - Meta Description
   - Featured Image URL
4. Save content
5. Edit the same content
6. Expected: SEO fields preserved
- ✅ Pass / ❌ Fail

### 6. Edge Cases

#### Test 19: Duplicate Slug
1. Create content with slug `test-post`
2. Try to create another with same slug
3. Expected: Error message about duplicate slug
- ✅ Pass / ❌ Fail

#### Test 20: Invalid Login
1. Try to login with wrong password
2. Expected: Error message "Incorrect username or password"
- ✅ Pass / ❌ Fail

#### Test 21: Password Validation
1. Try to register with password less than 6 characters
2. Expected: Error about password length
- ✅ Pass / ❌ Fail

## 📊 Test Results Summary

After running all tests, count your results:

- Total Passed: _____ / 21
- Total Failed: _____ / 21

### Success Criteria
- ✅ **Excellent**: 20-21 passed (95%+)
- ✅ **Good**: 18-19 passed (85%+)
- ⚠️ **Acceptable**: 15-17 passed (70%+)
- ❌ **Needs Work**: < 15 passed

## 🐛 Common Issues and Fixes

### Backend Issues

**Issue**: Cannot connect to database
```bash
# Solution: Delete and recreate database
rm cms.db  # Linux/Mac
del cms.db # Windows
# Restart backend
```

**Issue**: Import errors
```bash
# Solution: Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Issues

**Issue**: API connection failed
```bash
# Solution: Verify backend is running on port 8000
curl http://localhost:8000/health
```

**Issue**: White screen
```bash
# Solution: Check browser console for errors
# Often fixed by reinstalling dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 🚀 Performance Tests

### Load Testing (Optional)

Test API performance:

```bash
# Install Apache Bench
# Windows: Download from Apache website
# Linux: sudo apt install apache2-utils
# Mac: brew install httpd

# Test health endpoint
ab -n 1000 -c 10 http://localhost:8000/health

# Test content list
ab -n 100 -c 5 http://localhost:8000/api/content/
```

Expected results:
- Health endpoint: 500+ requests/second
- Content list: 50+ requests/second

## ✅ All Tests Passed?

Congratulations! Your CMS is working correctly. You can now:

1. Customize the UI (edit CSS in `frontend/src/index.css`)
2. Add new features (see README.md for ideas)
3. Deploy to production (see README.md deployment guide)

## 📝 Notes

Use this space to record any issues found during testing:

```
Issue 1: ___________________________
Solution: ___________________________

Issue 2: ___________________________
Solution: ___________________________
```

---

**Testing completed on**: _______________

**Tested by**: _______________

**Overall status**: ✅ Pass / ❌ Fail

