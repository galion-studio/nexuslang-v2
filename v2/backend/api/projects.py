"""
Projects API Endpoints
Handles project CRUD operations, code storage, and project management.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime

from ..models.user import User
from ..models.project import Project
from ..api.auth import get_current_user
from ..core.database import get_db

router = APIRouter()


# Request/Response Models
class ProjectCreate(BaseModel):
    """Create project request."""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=5000, description="Project description")
    language: str = Field("nexuslang", description="Programming language")
    code: Optional[str] = Field(None, description="Initial code")
    visibility: str = Field("private", description="Visibility: private, public, unlisted")


class ProjectUpdate(BaseModel):
    """Update project request."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    code: Optional[str] = None
    status: Optional[str] = Field(None, description="Status: draft, active, archived")
    visibility: Optional[str] = Field(None, description="Visibility: private, public, unlisted")


class ProjectResponse(BaseModel):
    """Project response."""
    id: int
    user_id: int
    name: str
    description: Optional[str]
    language: str
    status: str
    visibility: str
    execution_count: int
    last_executed: Optional[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    """Detailed project response with code."""
    code: Optional[str]


class ProjectListResponse(BaseModel):
    """List of projects response."""
    projects: List[ProjectResponse]
    total: int
    page: int
    page_size: int


# Endpoints

@router.post("/", response_model=ProjectDetailResponse, status_code=201)
async def create_project(
    project: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new project.
    
    Projects store your code, configurations, and execution history.
    You can organize your work across multiple projects.
    """
    # Validate visibility
    if project.visibility not in ["private", "public", "unlisted"]:
        raise HTTPException(400, "Invalid visibility option")
    
    # Create project
    db_project = Project(
        user_id=current_user.id,
        name=project.name,
        description=project.description,
        language=project.language,
        code=project.code,
        visibility=project.visibility,
        status="draft"
    )
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    return ProjectDetailResponse(
        id=db_project.id,
        user_id=db_project.user_id,
        name=db_project.name,
        description=db_project.description,
        language=db_project.language,
        code=db_project.code,
        status=db_project.status,
        visibility=db_project.visibility,
        execution_count=db_project.execution_count,
        last_executed=db_project.last_executed.isoformat() if db_project.last_executed else None,
        created_at=db_project.created_at.isoformat(),
        updated_at=db_project.updated_at.isoformat()
    )


@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    language: Optional[str] = Query(None, description="Filter by language"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all projects for the current user.
    
    Supports pagination and filtering by language or status.
    """
    # Build query
    query = db.query(Project).filter(Project.user_id == current_user.id)
    
    # Apply filters
    if language:
        query = query.filter(Project.language == language)
    if status:
        query = query.filter(Project.status == status)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    projects = query.order_by(desc(Project.updated_at)).offset(offset).limit(page_size).all()
    
    # Convert to response models
    project_responses = [
        ProjectResponse(
            id=p.id,
            user_id=p.user_id,
            name=p.name,
            description=p.description,
            language=p.language,
            status=p.status,
            visibility=p.visibility,
            execution_count=p.execution_count,
            last_executed=p.last_executed.isoformat() if p.last_executed else None,
            created_at=p.created_at.isoformat(),
            updated_at=p.updated_at.isoformat()
        )
        for p in projects
    ]
    
    return ProjectListResponse(
        projects=project_responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific project by ID.
    
    Returns full project details including code.
    """
    # Get project
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(404, "Project not found")
    
    return ProjectDetailResponse(
        id=project.id,
        user_id=project.user_id,
        name=project.name,
        description=project.description,
        language=project.language,
        code=project.code,
        status=project.status,
        visibility=project.visibility,
        execution_count=project.execution_count,
        last_executed=project.last_executed.isoformat() if project.last_executed else None,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat()
    )


@router.put("/{project_id}", response_model=ProjectDetailResponse)
async def update_project(
    project_id: int,
    updates: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a project.
    
    You can update name, description, code, status, and visibility.
    Only provided fields will be updated.
    """
    # Get project
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(404, "Project not found")
    
    # Update fields
    update_data = updates.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(project, field, value)
    
    # Update timestamp
    project.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(project)
    
    return ProjectDetailResponse(
        id=project.id,
        user_id=project.user_id,
        name=project.name,
        description=project.description,
        language=project.language,
        code=project.code,
        status=project.status,
        visibility=project.visibility,
        execution_count=project.execution_count,
        last_executed=project.last_executed.isoformat() if project.last_executed else None,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat()
    )


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a project.
    
    **Warning**: This permanently deletes the project and all its code.
    This action cannot be undone.
    """
    # Get project
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(404, "Project not found")
    
    # Delete project
    db.delete(project)
    db.commit()
    
    return None


@router.post("/{project_id}/execute")
async def execute_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Execute project code.
    
    Runs the project's code and returns the output.
    Increments execution count and updates last_executed timestamp.
    """
    # Get project
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(404, "Project not found")
    
    if not project.code:
        raise HTTPException(400, "Project has no code to execute")
    
    # TODO: Integrate with NexusLang executor
    # For now, return a mock response
    
    # Update execution stats
    project.execution_count += 1
    project.last_executed = datetime.utcnow()
    db.commit()
    
    return {
        "project_id": project_id,
        "status": "success",
        "output": "Mock execution result. Integrate with NexusLang executor.",
        "execution_time_ms": 42,
        "execution_count": project.execution_count
    }


@router.post("/{project_id}/duplicate", response_model=ProjectDetailResponse)
async def duplicate_project(
    project_id: int,
    new_name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Duplicate a project.
    
    Creates a copy of the project with a new name.
    Useful for creating variations or templates.
    """
    # Get original project
    original = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not original:
        raise HTTPException(404, "Project not found")
    
    # Create duplicate
    duplicate = Project(
        user_id=current_user.id,
        name=new_name or f"{original.name} (Copy)",
        description=original.description,
        language=original.language,
        code=original.code,
        status="draft",
        visibility="private"
    )
    
    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)
    
    return ProjectDetailResponse(
        id=duplicate.id,
        user_id=duplicate.user_id,
        name=duplicate.name,
        description=duplicate.description,
        language=duplicate.language,
        code=duplicate.code,
        status=duplicate.status,
        visibility=duplicate.visibility,
        execution_count=duplicate.execution_count,
        last_executed=duplicate.last_executed.isoformat() if duplicate.last_executed else None,
        created_at=duplicate.created_at.isoformat(),
        updated_at=duplicate.updated_at.isoformat()
    )


@router.get("/public/explore", response_model=ProjectListResponse)
async def explore_public_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    language: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Explore public projects from all users.
    
    Browse and discover projects shared by the community.
    """
    # Build query for public projects
    query = db.query(Project).filter(Project.visibility == "public")
    
    if language:
        query = query.filter(Project.language == language)
    
    # Get total
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    projects = query.order_by(desc(Project.updated_at)).offset(offset).limit(page_size).all()
    
    # Convert to responses
    project_responses = [
        ProjectResponse(
            id=p.id,
            user_id=p.user_id,
            name=p.name,
            description=p.description,
            language=p.language,
            status=p.status,
            visibility=p.visibility,
            execution_count=p.execution_count,
            last_executed=p.last_executed.isoformat() if p.last_executed else None,
            created_at=p.created_at.isoformat(),
            updated_at=p.updated_at.isoformat()
        )
        for p in projects
    ]
    
    return ProjectListResponse(
        projects=project_responses,
        total=total,
        page=page,
        page_size=page_size
    )

