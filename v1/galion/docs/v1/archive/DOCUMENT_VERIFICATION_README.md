# 📄 Document Verification System

**Status:** Production Ready | **Built:** First Principles Approach  
**Version:** 1.0.0 | **Date:** November 9, 2025

---

## ⚡ WHAT IS THIS?

A **bulletproof document verification system** for KYC, identity verification, and compliance.

**What it does:**
- Users upload documents (ID, proof of address, etc.)
- Admins review and approve/reject
- Status tracking (pending → approved/rejected)
- Secure file storage
- Full audit trail via Kafka events

**What it doesn't do** (by design - First Principles):
- ❌ AI-based OCR (use manual review initially, add AI later if needed)
- ❌ Blockchain verification (database timestamps are sufficient)
- ❌ Complex approval workflows (one admin decision = done)

---

## 🚀 QUICK START

### 1. Deploy the System

```powershell
# Run database migrations
.\scripts\run-migrations.ps1

# Deploy services
.\scripts\deploy-document-verification.ps1
```

### 2. Test It

```powershell
# Run comprehensive tests
.\scripts\test-documents.ps1
```

### 3. Use It

**API Documentation:**
- Swagger UI: http://localhost:8004/docs
- Health Check: http://localhost:8004/health
- Metrics: http://localhost:8004/metrics

---

## 📡 API ENDPOINTS

### User Endpoints

```bash
# Upload document
POST /api/v1/documents/upload
- Query param: document_type_id
- Form data: file (PDF, JPG, PNG)
- Returns: Document ID, status

# List my documents
GET /api/v1/documents
- Query params: page, page_size, status
- Returns: Paginated list

# Get document details
GET /api/v1/documents/{document_id}
- Returns: Full document info

# Download document file
GET /api/v1/documents/{document_id}/file
- Returns: File download

# Delete document
DELETE /api/v1/documents/{document_id}
- Returns: 204 No Content
```

### Admin Endpoints

```bash
# List pending documents
GET /api/v1/documents/pending
- Returns: All pending reviews

# List all documents (with filters)
GET /api/v1/documents/all?status=pending&user_id=xxx

# Approve document
POST /api/v1/documents/{document_id}/approve
- Returns: Updated document

# Reject document
POST /api/v1/documents/{document_id}/reject
- Body: { "rejection_reason": "..." }
- Returns: Updated document
```

### Document Types

```bash
# List document types
GET /api/v1/documents/types
- Returns: All available types

# Create document type (Admin)
POST /api/v1/documents/types
- Body: { "name": "...", "description": "...", ... }
```

---

## 📊 DATABASE SCHEMA

### Document Types

```sql
- id: Serial Primary Key
- name: Unique name (e.g., "government_id")
- description: Human-readable description
- required_for_verification: Boolean flag
- max_file_size_mb: Size limit (default: 10MB)
- allowed_formats: Comma-separated (default: "pdf,jpg,png,jpeg")
```

### Documents

```sql
- id: UUID Primary Key
- user_id: Foreign key to users table
- document_type_id: Foreign key to document_types
- file_name: Original filename
- file_path: Storage path (relative)
- file_size_bytes: File size in bytes
- mime_type: File MIME type
- status: enum('pending', 'approved', 'rejected', 'expired')
- reviewed_by: Admin user ID (nullable)
- reviewed_at: Review timestamp (nullable)
- rejection_reason: Text (nullable)
- uploaded_at: Upload timestamp
- expires_at: Expiration timestamp (nullable)
- metadata: JSONB for additional data
```

---

## 🔐 SECURITY

### File Upload Security

1. **Size Limits:** 10MB max per file (configurable)
2. **Type Validation:** Only PDF, JPG, PNG allowed
3. **MIME Type Detection:** Uses libmagic for real MIME type
4. **Filename Sanitization:** Removes special characters
5. **UUID Filenames:** Prevents enumeration attacks

### Access Control

1. **Users:** Can only access their own documents
2. **Admins:** Can access all documents for review
3. **JWT Auth:** All endpoints require valid JWT
4. **File Serving:** Documents served via API (not direct file access)

### Storage Security

1. **Outside Web Root:** Files stored in `/app/uploads`
2. **UUID Naming:** Unpredictable filenames
3. **Path Traversal Protection:** Validates all file paths
4. **No Direct Access:** Must go through API

---

## 🔄 EVENT FLOW

### Upload Flow

```
1. User uploads file via API
2. Service validates file (size, type, content)
3. File saved to disk with UUID filename
4. Database record created (status: pending)
5. Kafka event published: "document.uploaded"
6. Response returned to user
```

### Review Flow

```
1. Admin views pending documents
2. Admin approves or rejects document
3. Database updated (status, reviewer, timestamp)
4. Kafka event published: "document.approved" or "document.rejected"
5. (Future) User notified via email/push
```

### Events Published

- `document.uploaded` - New document uploaded
- `document.approved` - Document approved by admin
- `document.rejected` - Document rejected by admin
- `document.deleted` - Document deleted by user

---

## 🎛️ CONFIGURATION

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Redis (for caching)
REDIS_URL=redis://:password@localhost:6379/0

# JWT (for authentication)
JWT_SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256

# Kafka (for events)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Upload settings
UPLOAD_DIR=/app/uploads
MAX_FILE_SIZE_MB=10

# Environment
ENVIRONMENT=production
DEBUG=false
```

---

## 📈 MONITORING

### Health Check

```bash
GET /health
Response: { "status": "healthy", "service": "document-service", "version": "1.0.0" }
```

### Prometheus Metrics

```
# Request metrics
document_service_requests_total{method, endpoint, status}
document_service_request_duration_seconds{method, endpoint}

# Upload metrics
document_service_uploads_total{document_type, status}
```

**View Metrics:** http://localhost:8004/metrics  
**Prometheus Dashboard:** http://localhost:9091  
**Grafana:** http://localhost:3000

---

## 🔧 TROUBLESHOOTING

### Common Issues

**1. "File too large" error**
- Increase MAX_FILE_SIZE_MB environment variable
- Check document_types.max_file_size_mb in database

**2. "Invalid file type" error**
- Only PDF, JPG, PNG, JPEG allowed
- Verify actual file content (not just extension)

**3. "Document not found" error**
- Check file exists on disk
- Verify file path in database matches storage
- Check user ownership

**4. Service won't start**
- Check PostgreSQL is running
- Verify database migrations ran
- Check Redis connection
- Review logs: `docker-compose logs document-service`

---

## 🚀 DEPLOYMENT

### Production Checklist

- [x] Run database migrations
- [x] Set strong JWT_SECRET_KEY
- [ ] Configure external storage (S3, R2) for scale
- [ ] Enable virus scanning
- [ ] Set up automated backups
- [ ] Configure CDN for file delivery
- [ ] Set up monitoring alerts
- [ ] Enable rate limiting
- [ ] Review security settings

### Scaling

**Current Setup:** Local disk storage, single instance

**For Scale (1000+ users):**
1. Move to S3-compatible storage (R2, MinIO)
2. Enable CDN for document delivery
3. Add virus scanning (ClamAV)
4. Implement document compression
5. Add read replicas for database
6. Scale horizontally (multiple instances)

---

## 📚 EXAMPLES

### Upload Document (cURL)

```bash
curl -X POST "http://localhost:8004/api/v1/documents/upload?document_type_id=1" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "file=@/path/to/document.pdf"
```

### List Documents (Python)

```python
import requests

headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8004/api/v1/documents",
    headers=headers,
    params={"page": 1, "page_size": 50}
)
documents = response.json()
```

### Approve Document (JavaScript)

```javascript
const response = await fetch(
    `http://localhost:8004/api/v1/documents/${documentId}/approve`,
    {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
        }
    }
);
```

---

## 💡 DESIGN DECISIONS (First Principles)

### Why Local Disk Storage?

- **Reality:** Most users won't upload 100GB of documents on day 1
- **Cost:** $0/month vs $5-50/month for cloud storage
- **Simplicity:** No external dependencies, works offline
- **Migration Path:** Easy to move to S3 later when needed

### Why Manual Review?

- **Accuracy:** Humans catch things AI misses (especially fraud)
- **Cost:** AI OCR = $0.001-0.01 per page, manual = free initially
- **Legal:** Some jurisdictions require human review for KYC
- **Iterate:** Start simple, add AI when you have training data

### Why No Blockchain?

- **Overkill:** Database timestamp is legally sufficient
- **Cost:** Blockchain transactions cost money
- **Speed:** Database writes are instant
- **Compliance:** Most regulations don't require blockchain

---

## 📄 LICENSE

MIT License - Use it, modify it, ship it.

---

## 🤝 SUPPORT

**Issues?**
1. Check logs: `docker-compose logs document-service`
2. Verify database migrations ran
3. Test with curl/Postman
4. Open GitHub issue with logs

**Questions?**
- Read API docs: http://localhost:8004/docs
- Check metrics: http://localhost:8004/metrics
- Review code: `services/document-service/`

---

**Built with First Principles: Question → Delete → Simplify → Ship** 🚀

