# Fix: "Failed to fetch" Error on Form Templates and Submitted Requests

## 🐛 Problem Identified
The frontend pages for "Form Templates" (`/admin/forms`) and "Submitted Requests" (`/requests`) were showing "Error: Failed to fetch" because of **CORS (Cross-Origin Resource Sharing) issues** and **incorrect API endpoint usage**.

## 🔍 Root Causes

### 1. CORS Configuration Mismatch
- **Backend CORS** was configured to allow `http://localhost:5173`
- **Frontend** was running on `http://localhost:5174` (different port)
- Browser blocked cross-origin requests due to port mismatch

### 2. Bypassing Vite Proxy Configuration
- **Vite config** had a proxy setup: `/api` → `http://host.docker.internal:8000`
- **Frontend pages** were making direct calls to `http://localhost:8000`
- This bypassed the proxy and caused CORS issues

## ✅ Solutions Implemented

### 1. Updated Backend CORS Configuration
**File**: `backend/main.py`
```python
# Before
allow_origins=["http://localhost:5173"]

# After  
allow_origins=["http://localhost:5173", "http://localhost:5174"]
```

### 2. Updated Frontend API Calls to Use Proxy
All frontend pages updated to use `/api` prefix instead of direct `localhost:8000` calls:

**Files Updated**:
- ✅ `frontend/src/routes/admin/forms/+page.svelte`
- ✅ `frontend/src/routes/requests/+page.svelte`  
- ✅ `frontend/src/routes/users/+page.svelte`
- ✅ `frontend/src/routes/requests/new/+page.svelte`
- ✅ `frontend/src/routes/admin/dashboard/+page.svelte`
- ✅ `frontend/src/routes/admin/forms/[id]/+page.svelte`
- ✅ `frontend/src/routes/admin/forms/builder/+page.svelte`

**Example Change**:
```javascript
// Before
const response = await fetch('http://localhost:8000/form-definitions');

// After
const response = await fetch('/api/form-definitions');
```

### 3. Restarted Backend Container
```bash
docker compose restart backend
```

## 🧪 Verification Tests

### Backend API Tests (Direct)
```powershell
# ✅ Root endpoint
Invoke-WebRequest -Uri "http://localhost:8000/" -Method GET

# ✅ Form definitions
Invoke-WebRequest -Uri "http://localhost:8000/form-definitions" -Method GET

# ✅ Requests  
Invoke-WebRequest -Uri "http://localhost:8000/requests" -Method GET

# ✅ CORS headers present
Invoke-WebRequest -Uri "http://localhost:8000/form-definitions" -Method GET -Headers @{"Origin"="http://localhost:5174"}
# Returns: access-control-allow-origin: http://localhost:5174
```

### Frontend Pages Tests
- ✅ **Form Templates**: http://localhost:5174/admin/forms - Now loads properly
- ✅ **Submitted Requests**: http://localhost:5174/requests - Now loads properly
- ✅ **Other Pages**: All other admin functions remain operational

## 🎯 Key Lessons

1. **CORS Configuration**: Always ensure backend CORS allows the actual frontend port
2. **Proxy Usage**: Use configured Vite proxy (`/api`) instead of direct backend URLs
3. **Container Restarts**: Backend changes require container restart to take effect
4. **Systematic Updates**: Update all files consistently when changing API endpoint patterns

## 🚀 Current Status

- ✅ **Form Templates page**: Fully functional
- ✅ **Submitted Requests page**: Fully functional  
- ✅ **All other pages**: Continuing to work properly
- ✅ **New User Creation**: Working with correct `/api` proxy usage
- ✅ **Analytics Dashboard**: Already using proxy correctly

The "Failed to fetch" errors have been completely resolved and all pages are now loading data successfully from the backend API.
