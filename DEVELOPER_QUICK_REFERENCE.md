# 🚀 **DEVELOPER QUICK REFERENCE GUIDE**

## ⚡ **INSTANT SETUP**

### **Clone & Start (5 Minutes)**
```bash
# 1. Clone repository
git clone <repository-url>
cd wedding-invitation-app

# 2. Backend setup
cd backend/
pip install -r requirements.txt

# 3. Frontend setup  
cd ../frontend/
yarn install
yarn build

# 4. Start services
sudo supervisorctl restart all

# 5. Verify working
curl http://localhost:8001/api/test
```

### **Environment Configuration**
```bash
# Backend .env (required)
MONGO_URL="mongodb+srv://prasannagoudasp12_db_user:RVj1n8gEkHewSwIL@cluster0.euowph1.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DB_NAME="weddingcard"
CORS_ORIGINS="*"
JWT_SECRET_KEY="your-super-secret-jwt-key-change-in-production-123456789"

# Frontend .env (required)
REACT_APP_BACKEND_URL="http://localhost:8001"
WDS_SOCKET_PORT=0
```

## 🔧 **COMMON COMMANDS**

### **Service Management**
```bash
# Restart specific service
sudo supervisorctl restart backend
sudo supervisorctl restart frontend

# Check service status
sudo supervisorctl status

# View logs in real-time
tail -f /var/log/supervisor/backend.*.log
tail -f /var/log/supervisor/frontend.*.log

# Stop/start all services
sudo supervisorctl stop all
sudo supervisorctl start all
```

### **Development Commands**
```bash
# Frontend development
cd frontend/
yarn start          # Development server
yarn build          # Production build
yarn test           # Run tests

# Backend development
cd backend/
python server.py    # Run FastAPI dev server
pip freeze > requirements.txt  # Update dependencies
```

## 🗄️ **DATABASE OPERATIONS**

### **Quick MongoDB Queries**
```python
# Connect to database
from motor.motor_asyncio import AsyncIOMotorClient
client = AsyncIOMotorClient("mongodb+srv://...")
db = client["weddingcard"]

# Find all users
users = await db.users.find({}).to_list(length=10)

# Find wedding by ID
wedding = await db.weddings.find_one({"id": "wedding-uuid"})

# Find wedding by shareable ID
wedding = await db.weddings.find_one({"shareable_id": "abc123"})
```

### **Database Schema Quick Reference**
```javascript
// Users: id, username, password_hash, created_at
// Sessions: session_id, user_id, created_at, expires_at  
// Weddings: id, user_id, shareable_id, custom_url, couple_name_1, couple_name_2, wedding_date, venue_name, venue_location, their_story, [extended_fields...]
```

## 🌐 **API ENDPOINTS**

### **Authentication**
```bash
# Register user
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'

# Login
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass"}'
```

### **Wedding Data**
```bash
# Get wedding data (requires session)
curl "http://localhost:8001/api/wedding?session_id=SESSION_ID"

# Update wedding data
curl -X PUT http://localhost:8001/api/wedding \
  -H "Content-Type: application/json" \
  -d '{"session_id": "SESSION_ID", "couple_name_1": "John", "couple_name_2": "Jane"}'

# Get public wedding (shareable link)
curl "http://localhost:8001/api/wedding/share/SHAREABLE_ID"
```

## 🎨 **FRONTEND STRUCTURE**

### **Key Components**
```
src/
├── App.js                    # Main app with routing
├── contexts/
│   └── UserDataContext.js   # Global state management
├── pages/
│   ├── HomePage.js           # Landing page
│   ├── DashboardPage.js      # User dashboard
│   ├── PublicWeddingPage.js  # Shareable wedding view
│   ├── RegisterPage.js       # User registration
│   └── LoginPage.js          # User login
└── components/
    ├── navigation/           # Navigation components
    └── wedding/              # Wedding-specific components
```

### **Routing Quick Reference**
```javascript
// Public routes
"/" → HomePage (landing)
"/register" → RegisterPage
"/login" → LoginPage
"/wedding/:weddingId" → PublicWeddingPage (by wedding ID)
"/share/:shareableId" → PublicWeddingPage (by shareable ID)

// Protected routes  
"/dashboard" → DashboardPage (requires auth)
```

## 🔍 **DEBUGGING CHECKLIST**

### **Common Issues & Solutions**

#### **❌ 404 on Shareable Links**
```bash
# Check if wedding exists in database
curl "http://localhost:8001/api/wedding/share/YOUR_ID"

# If 404, check both shareable_id and custom_url fields
# Wedding might use legacy custom_url instead of shareable_id
```

#### **❌ React App Not Loading**
```bash
# Check if backend is serving static files
curl "http://localhost:8001/" | head -5

# Should return HTML, not JSON
# If JSON, restart backend: sudo supervisorctl restart backend
```

#### **❌ Database Connection Issues**
```bash
# Test MongoDB connection
python -c "
from motor.motor_asyncio import AsyncIOMotorClient
client = AsyncIOMotorClient('YOUR_MONGO_URL')
print('Connection successful')
"
```

#### **❌ Session/Auth Issues**
```bash
# Check session in MongoDB
# Sessions should exist in 'sessions' collection
# Check if session_id exists and hasn't expired
```

## 🧪 **TESTING SHORTCUTS**

### **Quick Manual Tests**
```bash
# 1. Test API health
curl http://localhost:8001/api/test

# 2. Test user registration
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "quicktest", "password": "test123"}'

# 3. Test frontend loading
curl -s http://localhost:8001/ | grep -i "react"

# 4. Test known working shareable link
curl http://localhost:8001/api/wedding/share/sridharandsneha
```

### **Working Test Examples**
```bash
# Known working shareable links (for testing)
http://localhost:8001/share/sridharandsneha        # Sridhar & Sneha
http://localhost:8001/share/abhishek-ananya-wedding # Abhishek & Ananya
http://localhost:8001/share/689f5b01               # Ankith & Shreya
```

## ⚠️ **GOTCHAS & IMPORTANT NOTES**

### **Critical Rules**
1. **Never hardcode URLs** - Always use environment variables
2. **Backend must run on 0.0.0.0:8001** - Don't change port
3. **Use `/api` prefix** for all backend routes
4. **MongoDB URLs are case-sensitive** - Double-check connection strings
5. **Frontend build must exist** - Run `yarn build` before production

### **URL Format Differences**
```javascript
// Two URL systems exist (both supported):
// Legacy: custom_url field → /share/custom-slug-name  
// New: shareable_id field → /share/abc123def

// Backend handles both automatically
```

### **Session Management**
```javascript
// Sessions stored in localStorage AND MongoDB
// localStorage: 'sessionId' 
// MongoDB: sessions collection with expiration
// Both must be valid for authentication
```

## 🔧 **QUICK FIXES**

### **Service Not Starting**
```bash
# Check supervisor logs
tail -20 /var/log/supervisor/backend.*.log

# Common issues:
# - Missing dependencies: pip install -r requirements.txt
# - MongoDB connection: Check MONGO_URL in .env
# - Port conflicts: Kill processes on 8001/3000
```

### **Frontend Build Issues**
```bash
# Clear cache and rebuild
cd frontend/
rm -rf node_modules/ package-lock.json
yarn install
yarn build

# Check build output
ls -la build/
```

### **Database Access Issues**
```bash
# Test MongoDB access
python -c "
import asyncio
from backend.server import connect_to_mongo
asyncio.run(connect_to_mongo())
"
```

## 📊 **Performance Monitoring**

### **Quick Performance Checks**
```bash
# API response time
time curl http://localhost:8001/api/test

# Frontend load time  
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8001/

# Database query time
# Check MongoDB Atlas metrics dashboard
```

### **Resource Usage**
```bash
# Check supervisor processes
sudo supervisorctl status

# Check system resources
htop
df -h
free -m
```

## 🆘 **Emergency Procedures**

### **Complete Service Reset**
```bash
# Nuclear option - restart everything
sudo supervisorctl stop all
sudo supervisorctl start all
sudo supervisorctl status

# Verify services
curl http://localhost:8001/api/test
curl http://localhost:8001/ | head -5
```

### **Database Recovery**
```bash
# If database connection lost:
# 1. Check MongoDB Atlas status
# 2. Verify MONGO_URL in backend/.env
# 3. Test connection manually
# 4. Restart backend service
```

## 📋 **CURRENT STATUS**

### **✅ Working Features**
- User registration and authentication
- Wedding data CRUD operations  
- Shareable link personalization
- Public wedding page display
- Mobile responsive design
- MongoDB data persistence

### **⚠️ Known Issues**
- Dashboard session persistence on refresh (minor UX issue)

### **🔧 Next Steps**
1. Fix dashboard session persistence
2. Enhanced mobile UX improvements
3. Email sharing integration

---

**Quick Reference Version**: 2.0  
**Last Updated**: September 18, 2024  
**Emergency Contact**: E1 Agent Development Team

---

## 💡 **PRO TIPS**

- **Always check logs first** when debugging issues
- **Use curl** for quick API testing instead of browser
- **MongoDB Atlas dashboard** provides excellent query monitoring  
- **Supervisor logs** are your best friend for service debugging
- **Test on mobile** early and often - 65% of users are mobile
- **Keep documentation updated** - future developers will thank you!