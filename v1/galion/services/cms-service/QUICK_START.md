# CMS Quick Start Guide

Get your Content Management System running in **less than 5 minutes**!

## ⚡ Super Quick Start (One Command)

### Windows
```bash
START-CMS.bat
```

### Linux/Mac
```bash
chmod +x START-CMS.sh
./START-CMS.sh
```

That's it! The CMS will start automatically.

## 🌐 Access URLs

Once started, open these in your browser:

- **CMS Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs

## 👤 First Time Setup (2 minutes)

### Step 1: Create Your Account
1. Go to http://localhost:3000
2. Click "Register"
3. Fill in your details:
   - Username: `admin`
   - Email: `admin@example.com`
   - Password: `admin123` (change this!)
4. Click "Register"

### Step 2: Create a Category
1. Click "Categories" in the top menu
2. Click "+ Add Category"
3. Enter:
   - Name: `Blog`
   - Slug: `blog` (auto-filled)
4. Click "Create Category"

### Step 3: Create Your First Post
1. Click "Create" in the top menu
2. Fill in:
   - Title: `My First Post`
   - Content: `This is my first blog post!`
   - Category: Select "Blog"
   - Status: Select "Published"
3. Click "Create Content"

### Step 4: View Your Content
1. Click "Content" in the menu
2. You'll see your published post!

## ✅ You're Done!

You now have a working CMS with:
- ✅ User authentication
- ✅ Content creation
- ✅ Category management
- ✅ Publishing workflow

## 🎯 What's Next?

### Create More Content
- Try creating a "Page" instead of a "Post"
- Add featured images (paste an image URL)
- Add SEO meta tags

### Organize with Categories
- Create categories like "Technology", "News", "Tutorials"
- Filter content by category

### Manage Your Content
- Save posts as "Draft" to work on them later
- Archive old content
- Track views on each post

## 🔧 Troubleshooting

### If Backend Won't Start
```bash
# Make sure Python 3.8+ is installed
python --version

# Install dependencies manually
pip install -r requirements.txt
```

### If Frontend Won't Start
```bash
# Make sure Node.js is installed
node --version

# Install dependencies manually
cd frontend
npm install
```

### If You See Connection Errors
1. Make sure backend is running (http://localhost:8000)
2. Make sure frontend is running (http://localhost:3000)
3. Check both terminal windows for errors

## 📚 Learn More

- Read the full [README.md](README.md) for detailed documentation
- Explore the API at http://localhost:8000/docs
- Check the code comments - everything is well documented!

## 🎉 Enjoy Your CMS!

You now have a professional content management system ready to use!

