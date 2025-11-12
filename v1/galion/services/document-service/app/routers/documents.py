"""
Document management endpoints
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
import math

from app.database import get_db, Document, DocumentType
from app.models import DocumentUploadResponse, DocumentResponse, DocumentListResponse
from app.middleware.auth import get_current_user
from app.services.storage import storage_service
from app.services.kafka_producer import kafka_producer

router = APIRouter()

@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    document_type_id: int,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a new document
    
    - **document_type_id**: ID of the document type
    - **file**: File to upload (PDF, JPG, PNG)
    """
    # Validate document type exists
    doc_type = db.query(DocumentType).filter(DocumentType.id == document_type_id).first()
    if not doc_type:
        raise HTTPException(status_code=404, detail="Document type not found")
    
    # Save file to storage
    try:
        file_path, mime_type, file_size = await storage_service.save_file(
            file,
            str(current_user["user_id"]),
            doc_type.name
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    # Create database record
    document = Document(
        user_id=current_user["user_id"],
        document_type_id=document_type_id,
        file_name=storage_service.sanitize_filename(file.filename or "document"),
        file_path=file_path,
        file_size_bytes=file_size,
        mime_type=mime_type,
        status="pending"
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    # Publish event to Kafka
    kafka_producer.publish_event(
        "document.uploaded",
        str(current_user["user_id"]),
        {
            "document_id": str(document.id),
            "document_type": doc_type.name,
            "file_size": file_size,
            "mime_type": mime_type
        }
    )
    
    return DocumentUploadResponse(
        id=document.id,
        user_id=document.user_id,
        document_type_id=document.document_type_id,
        file_name=document.file_name,
        file_size_bytes=document.file_size_bytes,
        mime_type=document.mime_type,
        status=document.status,
        uploaded_at=document.uploaded_at
    )

@router.get("", response_model=DocumentListResponse)
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: str = Query(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List user's documents (paginated)
    
    - **page**: Page number (default: 1)
    - **page_size**: Items per page (default: 50, max: 100)
    - **status**: Filter by status (optional)
    """
    # Query user's documents
    query = db.query(Document).filter(Document.user_id == current_user["user_id"])
    
    # Filter by status if provided
    if status:
        query = query.filter(Document.status == status)
    
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

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get document details"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Verify ownership
    if document.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get document type
    doc_type = db.query(DocumentType).filter(DocumentType.id == document.document_type_id).first()
    
    return DocumentResponse(
        id=document.id,
        user_id=document.user_id,
        document_type_id=document.document_type_id,
        document_type_name=doc_type.name if doc_type else None,
        file_name=document.file_name,
        file_size_bytes=document.file_size_bytes,
        mime_type=document.mime_type,
        status=document.status,
        reviewed_by=document.reviewed_by,
        reviewed_at=document.reviewed_at,
        rejection_reason=document.rejection_reason,
        uploaded_at=document.uploaded_at,
        expires_at=document.expires_at,
        metadata=document.metadata or {}
    )

@router.get("/{document_id}/file")
async def download_document(
    document_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download document file"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Verify ownership
    if document.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get file path
    try:
        file_path = storage_service.get_file_path(document.file_path)
    except HTTPException as e:
        raise e
    
    return FileResponse(
        path=file_path,
        media_type=document.mime_type,
        filename=document.file_name
    )

@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete document"""
    document = db.query(Document).filter(Document.id == document_id).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Verify ownership
    if document.user_id != current_user["user_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Delete file from storage
    storage_service.delete_file(document.file_path)
    
    # Delete from database
    db.delete(document)
    db.commit()
    
    # Publish event
    kafka_producer.publish_event(
        "document.deleted",
        str(current_user["user_id"]),
        {"document_id": str(document_id)}
    )
    
    return None

