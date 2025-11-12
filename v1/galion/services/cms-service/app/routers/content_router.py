"""
Content API Routes
Handles content CRUD operations (blog posts, pages, articles)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from ..database import get_db
from ..models import Content, User
from ..schemas import ContentCreate, ContentUpdate, ContentResponse
from ..auth import get_current_active_user

# Create router for content endpoints
router = APIRouter(prefix="/api/content", tags=["content"])

@router.get("/", response_model=List[ContentResponse])
def get_all_content(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[str] = Query(None, alias="status"),
    content_type: Optional[str] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get all content with optional filters
    - Public endpoint (shows only published content by default)
    - Supports filtering by status, type, and category
    - Supports pagination
    """
    query = db.query(Content)
    
    # If no status filter, only show published content to public
    if status_filter:
        query = query.filter(Content.status == status_filter)
    else:
        query = query.filter(Content.status == "published")
    
    # Apply optional filters
    if content_type:
        query = query.filter(Content.content_type == content_type)
    
    if category_id:
        query = query.filter(Content.category_id == category_id)
    
    # Order by newest first
    query = query.order_by(Content.created_at.desc())
    
    # Apply pagination
    content_list = query.offset(skip).limit(limit).all()
    
    return content_list

@router.get("/{content_id}", response_model=ContentResponse)
def get_content(content_id: int, db: Session = Depends(get_db)):
    """
    Get a single content item by ID
    - Public endpoint
    - Increments view counter
    """
    content = db.query(Content).filter(Content.id == content_id).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Increment view counter
    content.views += 1
    db.commit()
    db.refresh(content)
    
    return content

@router.get("/slug/{slug}", response_model=ContentResponse)
def get_content_by_slug(slug: str, db: Session = Depends(get_db)):
    """
    Get content by slug (URL-friendly identifier)
    - Useful for creating clean URLs
    - Increments view counter
    """
    content = db.query(Content).filter(Content.slug == slug).first()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Increment view counter
    content.views += 1
    db.commit()
    db.refresh(content)
    
    return content

@router.post("/", response_model=ContentResponse, status_code=status.HTTP_201_CREATED)
def create_content(
    content: ContentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create new content
    - Requires authentication
    - Automatically sets author to current user
    - Sets published_at if status is 'published'
    """
    # Check if slug already exists
    existing = db.query(Content).filter(Content.slug == content.slug).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Content with this slug already exists"
        )
    
    # Create content data
    content_data = content.dict()
    content_data["author_id"] = current_user.id
    
    # Set published_at if status is published
    if content.status == "published":
        content_data["published_at"] = datetime.utcnow()
    
    # Create new content
    db_content = Content(**content_data)
    db.add(db_content)
    db.commit()
    db.refresh(db_content)
    
    return db_content

@router.put("/{content_id}", response_model=ContentResponse)
def update_content(
    content_id: int,
    content: ContentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update existing content
    - Requires authentication
    - Only updates provided fields
    - Updates published_at when status changes to 'published'
    """
    db_content = db.query(Content).filter(Content.id == content_id).first()
    
    if not db_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Update only provided fields
    update_data = content.dict(exclude_unset=True)
    
    # Handle status change to published
    if "status" in update_data and update_data["status"] == "published":
        if db_content.status != "published":
            update_data["published_at"] = datetime.utcnow()
    
    for field, value in update_data.items():
        setattr(db_content, field, value)
    
    # Update the updated_at timestamp
    db_content.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_content)
    
    return db_content

@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_content(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete content
    - Requires authentication
    - Permanently removes content
    """
    db_content = db.query(Content).filter(Content.id == content_id).first()
    
    if not db_content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    db.delete(db_content)
    db.commit()
    
    return None

