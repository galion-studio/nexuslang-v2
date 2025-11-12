"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum

class DocumentStatus(str, Enum):
    """Document status enum"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class DocumentTypeResponse(BaseModel):
    """Document type response model"""
    id: int
    name: str
    description: Optional[str] = None
    required_for_verification: bool = False
    max_file_size_mb: int = 10
    allowed_formats: str = "pdf,jpg,png,jpeg"
    created_at: datetime
    
    class Config:
        from_attributes = True

class DocumentUploadResponse(BaseModel):
    """Response after successful document upload"""
    id: UUID
    user_id: UUID
    document_type_id: int
    file_name: str
    file_size_bytes: int
    mime_type: str
    status: DocumentStatus
    uploaded_at: datetime
    message: str = "Document uploaded successfully"

class DocumentResponse(BaseModel):
    """Complete document information"""
    id: UUID
    user_id: UUID
    document_type_id: int
    document_type_name: Optional[str] = None
    file_name: str
    file_size_bytes: int
    mime_type: str
    status: DocumentStatus
    reviewed_by: Optional[UUID] = None
    reviewed_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    uploaded_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True

class DocumentListResponse(BaseModel):
    """Paginated document list"""
    documents: list[DocumentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class DocumentReviewRequest(BaseModel):
    """Request to approve/reject document"""
    rejection_reason: Optional[str] = Field(None, max_length=500)

class DocumentReviewResponse(BaseModel):
    """Response after document review"""
    id: UUID
    status: DocumentStatus
    reviewed_by: UUID
    reviewed_at: datetime
    rejection_reason: Optional[str] = None
    message: str

class DocumentTypeCreate(BaseModel):
    """Create new document type"""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    required_for_verification: bool = False
    max_file_size_mb: int = Field(10, gt=0, le=100)
    allowed_formats: str = Field("pdf,jpg,png,jpeg", max_length=255)
    
    @field_validator('name')
    @classmethod
    def name_must_be_valid(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip().lower().replace(' ', '_')

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    request_id: Optional[str] = None

