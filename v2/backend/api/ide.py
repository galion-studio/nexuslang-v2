"""
IDE API routes.
Handles project management, file operations, and collaboration.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
from datetime import datetime
import uuid

from ..core.database import get_db
from ..models.user import User
from ..models.project import Project, File, VisibilityType
from ..api.auth import get_current_user

router = APIRouter()


# Request/Response Models
class CreateProjectRequest(BaseModel):
    name: str
    description: Optional[str] = None
    visibility: Optional[str] = "private"


class UpdateProjectRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    visibility: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    visibility: str
    stars_count: int
    forks_count: int
    created_at: datetime
    updated_at: datetime
    file_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


class CreateFileRequest(BaseModel):
    path: str
    content: str = ""


class UpdateFileRequest(BaseModel):
    content: str


class FileResponse(BaseModel):
    id: str
    project_id: str
    path: str
    content: Optional[str]
    size_bytes: Optional[int]
    version: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Projects Endpoints
@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all projects belonging to the current user.
    """
    result = await db.execute(
        select(Project)
        .where(Project.user_id == current_user.id)
        .order_by(Project.updated_at.desc())
    )
    projects = result.scalars().all()
    
    # Convert to response format
    response_projects = []
    for project in projects:
        # Count files in project
        file_count_result = await db.execute(
            select(File).where(File.project_id == project.id)
        )
        file_count = len(file_count_result.scalars().all())
        
        project_dict = {
            "id": str(project.id),
            "name": project.name,
            "description": project.description,
            "visibility": project.visibility.value,
            "stars_count": project.stars_count,
            "forks_count": project.forks_count,
            "created_at": project.created_at,
            "updated_at": project.updated_at,
            "file_count": file_count
        }
        response_projects.append(project_dict)
    
    return response_projects


@router.post("/projects", response_model=ProjectResponse)
async def create_project(
    request: CreateProjectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new project.
    """
    # Validate visibility
    try:
        visibility = VisibilityType(request.visibility)
    except ValueError:
        visibility = VisibilityType.PRIVATE
    
    # Create project
    project = Project(
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        visibility=visibility
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    # Create default main.nx file
    default_file = File(
        project_id=project.id,
        path="main.nx",
        content="// Welcome to NexusLang v2!\n\nfn main() {\n    print(\"Hello, NexusLang!\")\n}\n\nmain()\n",
        size_bytes=len("// Welcome to NexusLang v2!\n\nfn main() {\n    print(\"Hello, NexusLang!\")\n}\n\nmain()\n")
    )
    db.add(default_file)
    await db.commit()
    
    return ProjectResponse(
        id=str(project.id),
        name=project.name,
        description=project.description,
        visibility=project.visibility.value,
        stars_count=project.stars_count,
        forks_count=project.forks_count,
        created_at=project.created_at,
        updated_at=project.updated_at,
        file_count=1
    )


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get project details.
    """
    result = await db.execute(
        select(Project).where(
            and_(
                Project.id == uuid.UUID(project_id),
                Project.user_id == current_user.id
            )
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Count files
    file_count_result = await db.execute(
        select(File).where(File.project_id == project.id)
    )
    file_count = len(file_count_result.scalars().all())
    
    return ProjectResponse(
        id=str(project.id),
        name=project.name,
        description=project.description,
        visibility=project.visibility.value,
        stars_count=project.stars_count,
        forks_count=project.forks_count,
        created_at=project.created_at,
        updated_at=project.updated_at,
        file_count=file_count
    )


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    request: UpdateProjectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update project details.
    """
    result = await db.execute(
        select(Project).where(
            and_(
                Project.id == uuid.UUID(project_id),
                Project.user_id == current_user.id
            )
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Update fields
    if request.name:
        project.name = request.name
    if request.description is not None:
        project.description = request.description
    if request.visibility:
        try:
            project.visibility = VisibilityType(request.visibility)
        except ValueError:
            pass
    
    project.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(project)
    
    return ProjectResponse(
        id=str(project.id),
        name=project.name,
        description=project.description,
        visibility=project.visibility.value,
        stars_count=project.stars_count,
        forks_count=project.forks_count,
        created_at=project.created_at,
        updated_at=project.updated_at,
        file_count=0
    )


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a project and all its files.
    """
    result = await db.execute(
        select(Project).where(
            and_(
                Project.id == uuid.UUID(project_id),
                Project.user_id == current_user.id
            )
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Delete all files in project
    await db.execute(
        select(File).where(File.project_id == project.id)
    )
    
    # Delete project
    await db.delete(project)
    await db.commit()
    
    return {"message": "Project deleted successfully"}


# Files Endpoints
@router.get("/projects/{project_id}/files", response_model=List[FileResponse])
async def list_files(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all files in a project.
    """
    # Verify project ownership
    project_result = await db.execute(
        select(Project).where(
            and_(
                Project.id == uuid.UUID(project_id),
                Project.user_id == current_user.id
            )
        )
    )
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Get files
    result = await db.execute(
        select(File)
        .where(File.project_id == uuid.UUID(project_id))
        .order_by(File.path)
    )
    files = result.scalars().all()
    
    return [
        FileResponse(
            id=str(file.id),
            project_id=str(file.project_id),
            path=file.path,
            content=file.content,
            size_bytes=file.size_bytes,
            version=file.version,
            created_at=file.created_at,
            updated_at=file.updated_at
        )
        for file in files
    ]


@router.post("/projects/{project_id}/files", response_model=FileResponse)
async def create_file(
    project_id: str,
    request: CreateFileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new file in a project.
    """
    # Verify project ownership
    project_result = await db.execute(
        select(Project).where(
            and_(
                Project.id == uuid.UUID(project_id),
                Project.user_id == current_user.id
            )
        )
    )
    project = project_result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check if file already exists
    existing_file_result = await db.execute(
        select(File).where(
            and_(
                File.project_id == uuid.UUID(project_id),
                File.path == request.path
            )
        )
    )
    if existing_file_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File already exists at this path"
        )
    
    # Create file
    file = File(
        project_id=uuid.UUID(project_id),
        path=request.path,
        content=request.content,
        size_bytes=len(request.content.encode('utf-8'))
    )
    
    db.add(file)
    
    # Update project's updated_at
    project.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(file)
    
    return FileResponse(
        id=str(file.id),
        project_id=str(file.project_id),
        path=file.path,
        content=file.content,
        size_bytes=file.size_bytes,
        version=file.version,
        created_at=file.created_at,
        updated_at=file.updated_at
    )


@router.get("/files/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get file content and metadata.
    """
    result = await db.execute(
        select(File).where(File.id == uuid.UUID(file_id))
    )
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Verify user owns the project
    project_result = await db.execute(
        select(Project).where(
            and_(
                Project.id == file.project_id,
                Project.user_id == current_user.id
            )
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return FileResponse(
        id=str(file.id),
        project_id=str(file.project_id),
        path=file.path,
        content=file.content,
        size_bytes=file.size_bytes,
        version=file.version,
        created_at=file.created_at,
        updated_at=file.updated_at
    )


@router.put("/files/{file_id}", response_model=FileResponse)
async def update_file(
    file_id: str,
    request: UpdateFileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update file content.
    """
    result = await db.execute(
        select(File).where(File.id == uuid.UUID(file_id))
    )
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Verify user owns the project
    project_result = await db.execute(
        select(Project).where(
            and_(
                Project.id == file.project_id,
                Project.user_id == current_user.id
            )
        )
    )
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Update file
    file.content = request.content
    file.size_bytes = len(request.content.encode('utf-8'))
    file.version += 1
    file.updated_at = datetime.utcnow()
    
    # Update project's updated_at
    project.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(file)
    
    return FileResponse(
        id=str(file.id),
        project_id=str(file.project_id),
        path=file.path,
        content=file.content,
        size_bytes=file.size_bytes,
        version=file.version,
        created_at=file.created_at,
        updated_at=file.updated_at
    )


@router.delete("/files/{file_id}")
async def delete_file(
    file_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a file.
    """
    result = await db.execute(
        select(File).where(File.id == uuid.UUID(file_id))
    )
    file = result.scalar_one_or_none()
    
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    # Verify user owns the project
    project_result = await db.execute(
        select(Project).where(
            and_(
                Project.id == file.project_id,
                Project.user_id == current_user.id
            )
        )
    )
    if not project_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    await db.delete(file)
    await db.commit()
    
    return {"message": "File deleted successfully"}


# Code Execution Endpoints
class ExecuteCodeRequest(BaseModel):
    code: str
    timeout: Optional[int] = 10


class CompileCodeRequest(BaseModel):
    code: str


class ExecutionResponse(BaseModel):
    output: str
    execution_time: float
    success: bool
    error: Optional[str] = None


class CompilationResponse(BaseModel):
    output: str
    execution_time: float
    success: bool
    binary_size: Optional[int] = None


@router.post("/execute", response_model=ExecutionResponse)
async def execute_code(
    request: ExecuteCodeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Execute NexusLang code and return output.
    
    This endpoint runs the provided code in a sandboxed environment
    with timeout protection and resource limits.
    """
    from ..services.nexuslang_executor import get_executor
    
    # Get executor
    executor = get_executor()
    
    # Execute code
    result = await executor.execute(
        code=request.code,
        compile_binary=False
    )
    
    return ExecutionResponse(**result)


@router.post("/compile", response_model=CompilationResponse)
async def compile_code(
    request: CompileCodeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Compile NexusLang code to binary format.
    
    This endpoint compiles the provided code to the optimized .nxb
    binary format for faster AI processing (10x speedup).
    """
    from ..services.nexuslang_executor import get_executor
    
    # Get executor
    executor = get_executor()
    
    # Compile code
    result = await executor.execute(
        code=request.code,
        compile_binary=True
    )
    
    return CompilationResponse(**result)


@router.post("/analyze")
async def analyze_code(
    request: ExecuteCodeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze code for errors, warnings, and suggestions.
    
    This endpoint performs static analysis on the code without executing it.
    """
    from ..services.nexuslang_executor import get_executor
    
    # Get executor
    executor = get_executor()
    
    # Analyze code
    result = await executor.analyze(code=request.code)
    
    return result


# ============================================================================
# AI-POWERED CODE ASSISTANCE ENDPOINTS
# ============================================================================

class AICodeRequest(BaseModel):
    """Request for AI code operations."""
    code: str
    language: str = "nexuslang"
    cursor_position: Optional[int] = None
    context: Optional[str] = None


class NaturalLanguageRequest(BaseModel):
    """Request for natural language to code."""
    description: str
    language: str = "nexuslang"
    context: Optional[str] = None


class RefactorRequest(BaseModel):
    """Request for code refactoring."""
    code: str
    goal: str
    language: str = "nexuslang"


class ChatRequest(BaseModel):
    """Request for code conversation."""
    code: str
    question: str
    language: str = "nexuslang"
    conversation_history: Optional[List[Dict]] = None


@router.post("/ai/complete")
async def ai_code_completion(
    request: AICodeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    AI-powered code completion.
    Uses CodeLlama 70B for intelligent suggestions.
    """
    from ..services.ide import get_ide_ai_assistant
    
    assistant = get_ide_ai_assistant()
    result = await assistant.complete_code(
        code=request.code,
        cursor_position=request.cursor_position or len(request.code),
        language=request.language,
        context=request.context
    )
    
    return result


@router.post("/ai/explain")
async def ai_explain_code(
    request: AICodeRequest,
    detail_level: str = "medium",
    current_user: User = Depends(get_current_user)
):
    """
    Explain what code does using AI.
    Uses Claude Sonnet for best explanations.
    
    Detail levels: simple, medium, detailed
    """
    from ..services.ide import get_ide_ai_assistant
    
    assistant = get_ide_ai_assistant()
    result = await assistant.explain_code(
        code=request.code,
        language=request.language,
        detail_level=detail_level
    )
    
    return result


@router.post("/ai/find-bugs")
async def ai_find_bugs(
    request: AICodeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Find bugs and issues in code using AI.
    Uses Claude Sonnet for comprehensive analysis.
    """
    from ..services.ide import get_ide_ai_assistant
    
    assistant = get_ide_ai_assistant()
    result = await assistant.find_bugs(
        code=request.code,
        language=request.language
    )
    
    return result


@router.post("/ai/improve")
async def ai_suggest_improvements(
    request: AICodeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Get AI suggestions for code improvements and best practices.
    Uses Claude Sonnet for detailed code review.
    """
    from ..services.ide import get_ide_ai_assistant
    
    assistant = get_ide_ai_assistant()
    result = await assistant.suggest_improvements(
        code=request.code,
        language=request.language
    )
    
    return result


@router.post("/ai/optimize")
async def ai_optimize_code(
    request: AICodeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Get AI suggestions for performance optimizations.
    Uses Claude Sonnet for optimization analysis.
    """
    from ..services.ide import get_ide_ai_assistant
    
    assistant = get_ide_ai_assistant()
    result = await assistant.optimize_code(
        code=request.code,
        language=request.language
    )
    
    return result


@router.post("/ai/generate")
async def ai_generate_code(
    request: NaturalLanguageRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate code from natural language description.
    Uses CodeLlama 70B specialized for code generation.
    """
    from ..services.ide import get_ide_ai_assistant
    
    assistant = get_ide_ai_assistant()
    result = await assistant.natural_language_to_code(
        description=request.description,
        language=request.language,
        context=request.context
    )
    
    return result


@router.post("/ai/document")
async def ai_generate_docs(
    request: AICodeRequest,
    doc_style: str = "inline",
    current_user: User = Depends(get_current_user)
):
    """
    Generate documentation for code.
    Uses Claude Sonnet for high-quality documentation.
    
    Doc styles: inline, docstring
    """
    from ..services.ide import get_ide_ai_assistant
    
    assistant = get_ide_ai_assistant()
    result = await assistant.generate_documentation(
        code=request.code,
        language=request.language,
        doc_style=doc_style
    )
    
    return result


@router.post("/ai/refactor")
async def ai_refactor_code(
    request: RefactorRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Refactor code according to specified goal.
    Uses Claude Sonnet for intelligent refactoring.
    """
    from ..services.ide import get_ide_ai_assistant
    
    assistant = get_ide_ai_assistant()
    result = await assistant.refactor_code(
        code=request.code,
        refactoring_goal=request.goal,
        language=request.language
    )
    
    return result


@router.post("/ai/chat")
async def ai_chat_about_code(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Have a conversation about code with AI.
    Uses Claude Sonnet for intelligent code discussions.
    
    Maintains conversation history for context.
    """
    from ..services.ide import get_ide_ai_assistant
    
    assistant = get_ide_ai_assistant()
    result = await assistant.chat_about_code(
        code=request.code,
        question=request.question,
        language=request.language,
        conversation_history=request.conversation_history
    )
    
    return result