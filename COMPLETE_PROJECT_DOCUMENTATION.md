# 📖 **COMPLETE WEDDING INVITATION PROJECT DOCUMENTATION**

## 🎯 **PROJECT OVERVIEW**
A full-stack wedding invitation application that allows couples to create personalized digital wedding invitations with shareable links.

## 🏗️ **TECHNICAL ARCHITECTURE**

### **Backend (FastAPI + MongoDB)**
- **Framework**: FastAPI 0.104.1
- **Database**: MongoDB Atlas (Cloud)  
- **Authentication**: Session-based with persistent storage
- **Port**: Internal 8001 (mapped via Kubernetes ingress)

### **Frontend (React + Tailwind)**
- **Framework**: React 18.x
- **Styling**: TailwindCSS with custom theme system
- **Build Tool**: Create React App (CRA) with Craco
- **Port**: Internal 3000 (production build served by backend)

### **Database Schema**
```javascript
// Users Collection
{
  id: "uuid4",
  username: "string",
  password_hash: "string",
  created_at: "datetime"
}

// Weddings Collection  
{
  id: "uuid4",              // Primary wedding ID
  user_id: "uuid4",         // Reference to users.id
  shareable_id: "string",   // Short shareable ID (new system)
  custom_url: "string",     // Custom URL slug (legacy system)
  couple_name_1: "string",
  couple_name_2: "string", 
  wedding_date: "date",
  venue_name: "string",
  venue_location: "string",
  their_story: "text",
  // ... additional wedding data fields
}

// Sessions Collection
{
  session_id: "uuid4",
  user_id: "uuid4", 
  created_at: "datetime",
  expires_at: "datetime"
}
```

## 🔗 **URL ROUTING SYSTEM**

### **Backend API Endpoints**
```
GET  /api/test                              # Health check
POST /api/auth/register                     # User registration  
POST /api/auth/login                        # User login
GET  /api/wedding?session_id={id}           # Get user's wedding data
PUT  /api/wedding                           # Update user's wedding data
GET  /api/wedding/public/{wedding_id}       # Get wedding by wedding ID
GET  /api/wedding/share/{shareable_id}      # Get wedding by shareable ID or custom URL
```

### **Frontend Routes**
```
/                           # Landing page
/register                   # User registration
/login                      # User login  
/dashboard                  # User dashboard (authenticated)
/wedding/{wedding_id}       # Public wedding view by wedding ID
/share/{shareable_id}       # Public wedding view by shareable ID
```

## ✅ **IMPLEMENTED FEATURES**

### **Authentication System**
- ✅ User registration with username/password
- ✅ Session-based authentication with MongoDB storage
- ✅ Protected routes requiring authentication
- ✅ Automatic login after registration

### **Wedding Data Management**
- ✅ Complete CRUD operations for wedding data
- ✅ Auto-save functionality in dashboard
- ✅ Real-time data persistence to MongoDB
- ✅ Fallback to localStorage for offline access

### **Shareable Link System** 
- ✅ **DUAL URL SUPPORT**: Both legacy custom URLs and new shareable IDs
- ✅ **Backend endpoint enhanced** to handle both formats seamlessly
- ✅ **Personalization working**: Shows correct couple names, dates, venues
- ✅ **Tested examples**:
  - `/share/sridharandsneha` → "Sridhar & Sneha" with Garden Paradise Resort
  - `/share/abhishek-ananya-wedding` → "Abhishek & Ananya" with Grand Banquet Hall Mumbai  
  - `/share/689f5b01` → "Ankith & Shreya" with Royal Gardens Bangalore
  - `/wedding/246c96f6-7118-40c7-8093-9d628f93a0a9` → "Ankith & Shreya" wedding page

### **Public Wedding Pages**
- ✅ Full responsive design matching landing page
- ✅ Complete navigation: Home, Our Story, RSVP, Schedule, Gallery, etc.
- ✅ Floating "Use This Template" button visible to visitors
- ✅ Personalized data rendering (names, dates, venues, stories)
- ✅ Mobile-responsive layout
- ✅ QR code and social sharing integration

### **Dashboard Interface**
- ✅ Modern left sidebar navigation
- ✅ Real-time preview of wedding page
- ✅ Comprehensive editing sections:
  - Home (couple names, date, venue)
  - Our Story (timeline and narrative)
  - RSVP management  
  - Schedule/Timeline
  - Photo Gallery
  - Wedding Party
  - Registry
  - FAQ section
  - Guest Book
  - Theme customization

## 🔧 **RECENT FIXES (September 2024)**

### **Critical Issue Resolution**
**Problem**: 404 errors on shareable links showing default "Sarah & Michael" instead of personalized data

**Root Cause**: Database schema mismatch between `custom_url` (legacy) and `shareable_id` (new) fields

**Solution Applied**:
```python
# Enhanced /api/wedding/share/{shareable_id} endpoint
async def get_wedding_by_shareable_id(shareable_id: str):
    # Search for wedding by shareable_id first (new system)
    wedding = await weddings_coll.find_one({"shareable_id": shareable_id})
    
    if not wedding:
        # If not found by shareable_id, try custom_url (legacy system)
        wedding = await weddings_coll.find_one({"custom_url": shareable_id})
    
    # Return personalized data or enhanced default fallback
```

### **React Static File Serving Fix**
**Problem**: React app returning JSON API responses instead of HTML

**Solution**: Fixed FastAPI static file serving with proper catch-all routing:
```python
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    if full_path.startswith("api"):
        raise HTTPException(status_code=404, detail="API endpoint not found") 
    return FileResponse(FRONTEND_BUILD_PATH / "index.html")
```

## ⚠️ **KNOWN ISSUES**

### **Dashboard Session Persistence** 
- **Status**: ❌ Not Working  
- **Issue**: Users get logged out when refreshing dashboard page
- **Root Cause**: Frontend session validation failing on page refresh
- **Priority**: Medium (functionality works, UX impact only)

## 🧪 **TESTING STATUS**

### **Backend API Testing**
- ✅ MongoDB connection and CRUD operations
- ✅ Authentication endpoints (register/login)
- ✅ Wedding data endpoints (GET/PUT)
- ✅ Public shareable link endpoints
- ✅ Session management and validation

### **Frontend Testing**
- ✅ User registration and login flow
- ✅ Public wedding page rendering with personalized data
- ✅ Shareable link generation and access
- ✅ Responsive design on desktop and mobile
- ❌ Dashboard session persistence (needs fix)

### **Integration Testing**
- ✅ End-to-end user journey: Register → Edit → Share → View
- ✅ Cross-browser compatibility 
- ✅ URL routing and navigation
- ✅ Data persistence across sessions

## 🚀 **DEPLOYMENT CONFIGURATION**

### **Environment Variables**
```bash
# Backend (.env)
MONGO_URL="mongodb+srv://prasannagoudasp12_db_user:RVj1n8gEkHewSwIL@cluster0.euowph1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME="weddingcard"
CORS_ORIGINS="*"
JWT_SECRET_KEY="your-super-secret-jwt-key-change-in-production-123456789"

# Frontend (.env)  
REACT_APP_BACKEND_URL="http://localhost:8001"
WDS_SOCKET_PORT=0
```

### **Service Management**
```bash
# Restart services
sudo supervisorctl restart backend
sudo supervisorctl restart frontend  
sudo supervisorctl restart all

# Check status
sudo supervisorctl status

# View logs
tail -f /var/log/supervisor/backend.*.log
tail -f /var/log/supervisor/frontend.*.log
```

## 📝 **DEVELOPER QUICK START**

### **Setup Instructions**
1. Clone repository and install dependencies
2. Configure environment variables (MongoDB, backend URL)
3. Install backend dependencies: `pip install -r requirements.txt`
4. Install frontend dependencies: `yarn install` 
5. Build frontend: `yarn build`
6. Start services: `sudo supervisorctl restart all`

### **Key Files to Know**
- `/backend/server.py` - Main FastAPI application
- `/frontend/src/App.js` - React routing and theme management
- `/frontend/src/contexts/UserDataContext.js` - Global state management
- `/frontend/src/pages/PublicWeddingPage.js` - Shareable link rendering
- `/frontend/src/pages/DashboardPage.js` - User dashboard interface

## 🔮 **NEXT DEVELOPMENT PRIORITIES**

1. **Fix dashboard session persistence** - Highest priority UX issue
2. **Enhanced mobile navigation** - Improve mobile user experience  
3. **Advanced theme customization** - More color and layout options
4. **Wedding party management** - Enhanced guest list features
5. **Analytics dashboard** - Track invitation views and RSVPs

---

**Last Updated**: September 18, 2024  
**Project Status**: ✅ Core features working, ⚠️ Minor UX improvements needed  
**Maintainer**: E1 Agent Development Team