"""
Admin endpoints for document review and management
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime
import math

from app.database import get_db, Document, DocumentType
from app.models import DocumentResponse, DocumentListResponse, DocumentReviewRequest, DocumentReviewResponse
from app.middleware.auth import get_current_admin_user
from app.services.kafka_producer import kafka_producer

router = APIRouter()

@router.get("/pending", response_model=DocumentListResponse)
async def list_pending_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    List all pending documents (Admin only)
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 50, max: 100)
    """
    # Query pending documents
    query = db.query(Document).filter(Document.status == "pending")
    
    # Get total count
    total = query.count()
    
    # Paginate
    offset = (page - 1) * page_size
    documents = query.order_by(Document.uploaded_at.asc()).offset(offset).limit(page_size).all()
    
    # Build response
    doc_responses = []
    for doc in documents:
        doc_type = db.query(DocumentType).filter(DocumentType.id == doc.document_type_id).first()
        doc_responses.append(DocumentResponse(
            id=doc.id,
            user_id=doc.user_id,
            document_type_id=doc.document_type_id,
            document_type_name=doc_type.name if doc_type else None,
            file_name=doc.file_name,
            file_size_bytes=doc.file_size_bytes,
            mime_type=doc.mime_type,
            status=doc.status,
            reviewed_by=doc.reviewed_by,
            reviewed_at=doc.reviewed_at,
            rejection_reason=doc.rejection_reason,
            uploaded_at=doc.uploaded_at,
            expires_at=doc.expires_at,
            metadata=doc.metadata or {}
        ))
    
    return DocumentListResponse(
        documents=doc_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0
    )

@router.get("/all", response_model=DocumentListResponse)
async def list_all_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: str = Query(None),
    user_id: UUID = Query(None),
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    List all documents (Admin only)
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 50, max: 100)
    - **status**: Filter by status (optional)
    - **user_id**: Filter by user ID (optional)
    """
    # Query all documents
    query = db.query(Document)
    
    # Apply filters
    if status:
        query = query.filter(Document.status == status)
    if user_id:
        query = query.filter(Document.user_id == user_id)
    
    # Get total count
    total = query.count()
    
    # Paginate
    offset = (page - 1) * page_size
    documents = query.order_by(Document.uploaded_at.desc()).offset(offset).limit(page_size).all()
    
    # Build response
    doc_responses = []
    for doc in documents:
        doc_type = db.query(DocumentType).filter(DocumentType.id == doc.document_type_id).first()
        doc_responses.append(DocumentResponse(
            id=doc.id,
            user_id=doc.user_id,
            document_type_id=doc.document_type_id,
            document_type_name=doc_type.name if doc_type else None,
            file_name=doc.file_name,
            file_size_bytes=doc.file_size_bytes,
            mime_type=doc.mime_type,
            status=doc.status,
            reviewed_by=doc.reviewed_by,
            reviewed_at=doc.reviewed_at,
            rejection_reason=doc.rejection_reason,
            uploaded_at=doc.uploaded_at,
            expires_at=doc.expires_at,
            metadata=doc.metadata or {}
        ))
    
    return DocumentListResponse(
        documents=doc_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0
    )

@router.post("/{document_id}/approve", response_model=DocumentReviewResponse)
async def approve_document(
    document_id: UUID,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Approve a document (Admin only)"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status != "pending":
        raise HTTPException(status_code=400, detail=f"Cannot approve document with status: {document.status}")
    
    # Update document status
    document.status = "approved"
    document.reviewed_by = current_user["user_id"]
    document.reviewed_at = datetime.utcnow()
    document.rejection_reason = None
    
    db.commit()
    db.refresh(document)
    
    # Publish event
    kafka_producer.publish_event(
        "document.approved",
        str(document.user_id),
        {
            "document_id": str(document_id),
            "reviewed_by": str(current_user["user_id"]),
            "reviewed_at": document.reviewed_at.isoformat()
        }
    )
    
    return DocumentReviewResponse(
        id=document.id,
        status=document.status,
        reviewed_by=document.reviewed_by,
        reviewed_at=document.reviewed_at,
        rejection_reason=None,
        message="Document approved successfully"
    )

@router.post("/{document_id}/reject", response_model=DocumentReviewResponse)
async def reject_document(
    document_id: UUID,
    review_request: DocumentReviewRequest,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Reject a document (Admin only)"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if document.status != "pending":
        raise HTTPException(status_code=400, detail=f"Cannot reject document with status: {document.status}")
    
    if not review_request.rejection_reason:
        raise HTTPException(status_code=400, detail="Rejection reason is required")
    
    # Update document status
    document.status = "rejected"
    document.reviewed_by = current_user["user_id"]
    document.reviewed_at = datetime.utcnow()
    document.rejection_reason = review_request.rejection_reason
    
    db.commit()
    db.refresh(document)
    
    # Publish event
    kafka_producer.publish_event(
        "document.rejected",
        str(document.user_id),
        {
            "document_id": str(document_id),
            "reviewed_by": str(current_user["user_id"]),
            "reviewed_at": document.reviewed_at.isoformat(),
            "rejection_reason": document.rejection_reason
        }
    )
    
    return DocumentReviewResponse(
        id=document.id,
        status=document.status,
        reviewed_by=document.reviewed_by,
        reviewed_at=document.reviewed_at,
        rejection_reason=document.rejection_reason,
        message="Document rejected"
    )

