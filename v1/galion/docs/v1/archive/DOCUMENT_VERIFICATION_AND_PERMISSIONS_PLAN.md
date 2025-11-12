# 🚀 DOCUMENT VERIFICATION + CUSTOM PERMISSIONS - FIRST PRINCIPLES BUILD

**Status:** Building | **Approach:** Elon Musk's First Principles  
**Date:** November 9, 2025

---

## 🎯 ELON MUSK'S FIRST PRINCIPLES (Applied)

### 1. QUESTION EVERY REQUIREMENT

**Document Verification - Do we really need:**
- ✅ **YES:** File upload and storage (users need to submit docs)
- ✅ **YES:** Admin review workflow (manual verification required initially)
- ✅ **YES:** Status tracking (pending/approved/rejected)
- ❌ **NO:** AI-based OCR (premature optimization - manual review first)
- ❌ **NO:** Blockchain proof (overcomplicated - database timestamp is sufficient)
- ❌ **NO:** Facial recognition (overkill for Alpha/Beta)

**Custom Permissions - Do we really need:**
- ✅ **YES:** Role-based access control (RBAC - industry standard)
- ✅ **YES:** Permission assignment to roles (flexible access management)
- ✅ **YES:** Resource-level permissions (control what users can access)
- ❌ **NO:** Complex ACL trees (keep it flat and simple)
- ❌ **NO:** Time-based permissions (add later if needed)
- ❌ **NO:** Geographic restrictions (unnecessary complexity)

### 2. DELETE UNNECESSARY PARTS

**What We're NOT Building:**
- ❌ Complex document parsing (upload → storage → review, that's it)
- ❌ Multi-step approval workflows (one admin approves/rejects)
- ❌ Advanced permission inheritance (flat role → permissions mapping)
- ❌ Permission request system (admin assigns directly)
- ❌ Document expiration (add later if needed)

### 3. SIMPLIFY & OPTIMIZE

**Document Verification - Simplified:**
```
User uploads → File stored → Admin reviews → Status updated → User notified
```

**Custom Permissions - Simplified:**
```
Admin creates role → Admin assigns permissions → Admin assigns role to user → User has access
```

### 4. ACCELERATE CYCLE TIME

**Build Order (Ship Fast):**
1. Database schema (20 minutes)
2. Document service (60 minutes)
3. Permissions service (60 minutes)
4. API Gateway routing (15 minutes)
5. Docker setup (15 minutes)
6. Test scripts (30 minutes)

**Total Time to Ship:** ~3 hours

### 5. AUTOMATE

**What We Automate:**
- ✅ File upload and storage
- ✅ Permission checking middleware
- ✅ Automatic status updates
- ✅ Kafka event publishing
- ✅ Metrics collection

---

## 🏗️ ARCHITECTURE (Simple & Effective)

```
┌─────────────────────────────────────────────────────────────────┐
│                         NEW SERVICES                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────┐  ┌────────────────────────────┐  │
│  │  Document Service        │  │  Permissions Service       │  │
│  │  (Python/FastAPI :8002)  │  │  (Python/FastAPI :8003)    │  │
│  │                          │  │                            │  │
│  │  • File Upload           │  │  • Role Management         │  │
│  │  • Document Storage      │  │  • Permission Assignment   │  │
│  │  • Status Management     │  │  • Access Control Check    │  │
│  │  • Admin Review          │  │  • User Role Assignment    │  │
│  │  • Notifications         │  │  • Middleware Integration  │  │
│  └──────────────────────────┘  └────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Integration Points

**API Gateway:**
- Route: `/api/v1/documents/*` → Document Service (8002)
- Route: `/api/v1/permissions/*` → Permissions Service (8003)
- Middleware: Check permissions before routing

**Database:**
- New tables: `documents`, `document_types`
- New tables: `roles`, `permissions`, `role_permissions`, `user_roles`

**Events (Kafka):**
- `document.uploaded`
- `document.approved`
- `document.rejected`
- `permission.granted`
- `role.assigned`

---

## 📊 DATABASE SCHEMA

### Document Verification Tables

```sql
-- Document Types (KYC, ID, Proof of Address, etc.)
CREATE TABLE document_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    required_for_verification BOOLEAN DEFAULT false,
    max_file_size_mb INTEGER DEFAULT 10,
    allowed_formats VARCHAR(255) DEFAULT 'pdf,jpg,png',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Documents
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    document_type_id INTEGER NOT NULL REFERENCES document_types(id),
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    
    -- Status tracking
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'expired')),
    
    -- Review information
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP,
    rejection_reason TEXT,
    
    -- Metadata
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    metadata JSONB,
    
    -- Indexing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_type ON documents(document_type_id);
```

### Custom Permissions Tables

```sql
-- Roles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    is_system BOOLEAN DEFAULT false, -- Cannot be deleted (admin, user, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Permissions
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    resource VARCHAR(100) NOT NULL, -- e.g., 'users', 'documents', 'analytics'
    action VARCHAR(50) NOT NULL,    -- e.g., 'read', 'write', 'delete', 'admin'
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(resource, action)
);

-- Role-Permission Mapping
CREATE TABLE role_permissions (
    id SERIAL PRIMARY KEY,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(role_id, permission_id)
);

-- User-Role Mapping
CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    assigned_by UUID REFERENCES users(id),
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP, -- Optional: role expiration
    UNIQUE(user_id, role_id)
);

CREATE INDEX idx_user_roles_user_id ON user_roles(user_id);
CREATE INDEX idx_role_permissions_role_id ON role_permissions(role_id);
```

### Seed Data (Default Roles & Permissions)

```sql
-- Insert default roles
INSERT INTO roles (name, description, is_system) VALUES
('admin', 'Full system access', true),
('user', 'Standard user access', true),
('moderator', 'Content moderation access', true),
('verified_user', 'Verified user with additional privileges', true);

-- Insert default permissions
INSERT INTO permissions (resource, action, description) VALUES
-- User management
('users', 'read', 'View user profiles'),
('users', 'write', 'Edit user profiles'),
('users', 'delete', 'Delete users'),
('users', 'admin', 'Full user management'),

-- Document management
('documents', 'read', 'View documents'),
('documents', 'write', 'Upload documents'),
('documents', 'delete', 'Delete documents'),
('documents', 'review', 'Review and approve documents'),

-- Analytics
('analytics', 'read', 'View analytics'),
('analytics', 'admin', 'Manage analytics'),

-- System
('system', 'admin', 'System administration');

-- Assign permissions to admin role
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r CROSS JOIN permissions p WHERE r.name = 'admin';

-- Assign basic permissions to user role
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p 
WHERE r.name = 'user' AND p.action IN ('read', 'write') 
AND p.resource IN ('users', 'documents');

-- Assign moderator permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM roles r, permissions p 
WHERE r.name = 'moderator' AND 
(p.resource = 'documents' AND p.action = 'review');
```

---

## 📡 API ENDPOINTS

### Document Verification Service (Port 8002)

```
POST   /api/v1/documents/upload              - Upload document
GET    /api/v1/documents                     - List user's documents (or all if admin)
GET    /api/v1/documents/{document_id}       - Get document details
DELETE /api/v1/documents/{document_id}       - Delete document
GET    /api/v1/documents/{document_id}/file  - Download document file

# Admin endpoints
GET    /api/v1/documents/pending             - List pending documents (admin)
POST   /api/v1/documents/{document_id}/approve - Approve document (admin)
POST   /api/v1/documents/{document_id}/reject  - Reject document (admin)

# Document types
GET    /api/v1/documents/types               - List document types
POST   /api/v1/documents/types               - Create document type (admin)
```

### Permissions Service (Port 8003)

```
# Roles
GET    /api/v1/permissions/roles             - List all roles
POST   /api/v1/permissions/roles             - Create role (admin)
GET    /api/v1/permissions/roles/{role_id}   - Get role details
PUT    /api/v1/permissions/roles/{role_id}   - Update role (admin)
DELETE /api/v1/permissions/roles/{role_id}   - Delete role (admin)

# Permissions
GET    /api/v1/permissions                   - List all permissions
POST   /api/v1/permissions                   - Create permission (admin)

# Role-Permission assignment
POST   /api/v1/permissions/roles/{role_id}/permissions - Assign permission to role
DELETE /api/v1/permissions/roles/{role_id}/permissions/{permission_id} - Remove permission

# User-Role assignment
POST   /api/v1/permissions/users/{user_id}/roles - Assign role to user (admin)
DELETE /api/v1/permissions/users/{user_id}/roles/{role_id} - Remove role from user
GET    /api/v1/permissions/users/{user_id}/roles - Get user's roles

# Access check
POST   /api/v1/permissions/check             - Check if user has permission
GET    /api/v1/permissions/me                - Get current user's permissions
```

---

## 🔐 SECURITY CONSIDERATIONS

### Document Verification Security

1. **File Upload Security:**
   - Max file size: 10MB per document
   - Allowed formats: PDF, JPG, PNG only
   - Virus scanning: TODO (Phase Beta)
   - Filename sanitization: Remove special chars

2. **Access Control:**
   - Users can only view their own documents
   - Admins can view all documents
   - Document URLs are signed/time-limited

3. **Storage Security:**
   - Files stored outside web root
   - UUID-based filenames (prevent enumeration)
   - No direct file access (served via API)

### Permissions Security

1. **Role Management:**
   - Only admins can create/modify roles
   - System roles cannot be deleted
   - Permission changes are audit-logged

2. **Permission Checking:**
   - Middleware validates on every request
   - Cached in Redis (5-minute TTL)
   - Fail-closed (deny if check fails)

3. **Audit Trail:**
   - All role/permission changes logged
   - Published to Kafka for analytics
   - Includes who, what, when

---

## 🔄 EVENT FLOW

### Document Upload Flow

```
1. User → API Gateway: POST /api/v1/documents/upload
2. API Gateway → Check permissions (documents.write)
3. Document Service → Validate file
4. Document Service → Save to disk
5. Document Service → Insert record to DB
6. Document Service → Publish event: document.uploaded
7. Analytics Service ← Consume event
8. Document Service → Return document ID
```

### Document Review Flow

```
1. Admin → API Gateway: POST /api/v1/documents/{id}/approve
2. API Gateway → Check permissions (documents.review)
3. Document Service → Update status to 'approved'
4. Document Service → Publish event: document.approved
5. Document Service → Return success
6. (Future) Notification Service ← Send email to user
```

### Permission Check Flow

```
1. Client → API Gateway: Any protected endpoint
2. API Gateway → Permissions Service: Check user permission
3. Permissions Service → Check Redis cache
4. (If cache miss) → Query PostgreSQL
5. Permissions Service → Return true/false
6. API Gateway → Route or deny request
```

---

## 📦 FILE STRUCTURE

```
services/
├── document-service/
│   ├── app/
│   │   ├── main.py                  # FastAPI app
│   │   ├── models.py                # Pydantic models
│   │   ├── database.py              # DB connection
│   │   ├── routers/
│   │   │   ├── documents.py         # Document endpoints
│   │   │   └── admin.py             # Admin endpoints
│   │   ├── services/
│   │   │   ├── storage.py           # File storage logic
│   │   │   └── validation.py        # File validation
│   │   └── middleware/
│   │       └── auth.py              # JWT validation
│   ├── uploads/                     # Document storage
│   ├── requirements.txt
│   └── Dockerfile
│
└── permissions-service/
    ├── app/
    │   ├── main.py                  # FastAPI app
    │   ├── models.py                # Pydantic models
    │   ├── database.py              # DB connection
    │   ├── routers/
    │   │   ├── roles.py             # Role endpoints
    │   │   ├── permissions.py       # Permission endpoints
    │   │   └── assignments.py       # User-role assignments
    │   ├── services/
    │   │   ├── rbac.py              # RBAC logic
    │   │   └── cache.py             # Redis caching
    │   └── middleware/
    │       └── permission_check.py  # Permission middleware
    ├── requirements.txt
    └── Dockerfile

database/
└── migrations/
    ├── 005_document_verification.sql
    └── 006_custom_permissions.sql

scripts/
├── test-documents.ps1               # Test document upload
└── test-permissions.ps1             # Test permissions
```

---

## ⚡ PERFORMANCE CONSIDERATIONS

### Document Service

- **File Upload:** Stream directly to disk (no memory buffering)
- **File Retrieval:** Use sendfile() for efficient transfer
- **Listing:** Paginated queries (50 per page)
- **Storage:** Local disk initially, S3-compatible later

### Permissions Service

- **Caching:** Redis cache for permission checks (5-min TTL)
- **Query Optimization:** Denormalized permission check query
- **Connection Pooling:** Reuse DB connections
- **Response Time:** <10ms for cached checks, <50ms for DB queries

---

## 💰 COST IMPACT

### Storage (Documents)

- **Alpha (100 users):** ~1GB storage ($0.10/month)
- **Beta (1,000 users):** ~10GB storage ($1/month)
- **Production (10,000 users):** ~100GB storage ($10/month)

### Performance Impact

- **Document Service:** +1 service = +512MB RAM = ~$2-5/month
- **Permissions Service:** +1 service = +512MB RAM = ~$2-5/month
- **Total New Cost:** $5-10/month

### Optimization

- Move to S3-compatible storage at scale (cheaper)
- Enable CDN for document delivery
- Compress documents automatically

---

## 🚀 DEPLOYMENT PLAN

### Phase 1: Build (3 hours)

1. ✅ Create database migrations
2. ✅ Build Document Service
3. ✅ Build Permissions Service
4. ✅ Update API Gateway
5. ✅ Docker configuration
6. ✅ Test scripts

### Phase 2: Test (1 hour)

1. Unit tests for both services
2. Integration tests with database
3. End-to-end flow testing
4. Load testing (100 concurrent uploads)

### Phase 3: Deploy (30 minutes)

1. Run database migrations
2. Deploy new services via docker-compose
3. Update API Gateway routing
4. Verify health checks
5. Test production flow

### Phase 4: Monitor (Ongoing)

1. Check Prometheus metrics
2. Monitor error rates
3. Review uploaded documents
4. Optimize based on usage

---

## 📊 SUCCESS METRICS

### Document Verification

- ✅ Users can upload documents
- ✅ Admins can review documents
- ✅ Status updates in real-time
- ✅ Events published to Kafka
- ✅ <2 second upload time (10MB file)

### Custom Permissions

- ✅ Roles can be created/assigned
- ✅ Permissions can be granted
- ✅ Access checks work correctly
- ✅ <10ms permission check (cached)
- ✅ No unauthorized access

---

## 🔧 NEXT STEPS

1. **Build services** (this document → code)
2. **Test locally** (docker-compose up)
3. **Deploy to production** (15 minutes)
4. **Monitor and iterate** (fix what breaks)

---

## 📚 REFERENCES

- **Elon Musk's Algorithm:** [Twitter Thread](https://twitter.com/elonmusk/status/1582824623441498112)
- **First Principles Thinking:** Question assumptions, build from ground truth
- **RBAC Best Practices:** [NIST RBAC Standard](https://csrc.nist.gov/projects/role-based-access-control)

---

**Philosophy:** Build what's needed. Delete what's not. Ship fast. Iterate based on reality.

**Status:** Ready to build. Let's go! 🚀

