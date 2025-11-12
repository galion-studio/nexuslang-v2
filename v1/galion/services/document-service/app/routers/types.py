"""
Document type management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db, DocumentType
from app.models import DocumentTypeResponse, DocumentTypeCreate
from app.middleware.auth import get_current_user, get_current_admin_user

router = APIRouter()

@router.get("", response_model=List[DocumentTypeResponse])
async def list_document_types(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all document types"""
    document_types = db.query(DocumentType).order_by(DocumentType.name).all()
    return document_types

@router.get("/{type_id}", response_model=DocumentTypeResponse)
async def get_document_type(
    type_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get document type by ID"""
    doc_type = db.query(DocumentType).filter(DocumentType.id == type_id).first()
    
    if not doc_type:
        raise HTTPException(status_code=404, detail="Document type not found")
    
    return doc_type

@router.post("", response_model=DocumentTypeResponse, status_code=201)
async def create_document_type(
    doc_type_create: DocumentTypeCreate,
    current_user: dict = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create new document type (Admin only)"""
    # Check if type already exists
    existing = db.query(DocumentType).filter(DocumentType.name == doc_type_create.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Document type already exists")
    
    # Create new type
    doc_type = DocumentType(
        name=doc_type_create.name,
        description=doc_type_create.description,
        required_for_verification=doc_type_create.required_for_verification,
        max_file_size_mb=doc_type_create.max_file_size_mb,
        allowed_formats=doc_type_create.allowed_formats
    )
    
    db.add(doc_type)
    db.commit()
    db.refresh(doc_type)
    
    return doc_type

