"""
IDE Service - Project and File Management
Provides business logic for IDE operations.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import uuid
from datetime import datetime

from ...models.project import Project, File, VisibilityType
from ...models.user import User


class IDEService:
    """
    IDE service for managing projects and files.
    
    Provides:
    - Project CRUD operations
    - File management
    - Project search and filtering
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_projects(self, user_id: uuid.UUID) -> List[Project]:
        """Get all projects for a user."""
        result = await self.db.execute(
            select(Project)
            .where(Project.user_id == user_id)
            .order_by(Project.updated_at.desc())
        )
        return result.scalars().all()
    
    async def create_project(
        self,
        user_id: uuid.UUID,
        name: str,
        description: Optional[str] = None,
        visibility: VisibilityType = VisibilityType.PRIVATE
    ) -> Project:
        """Create a new project with default main.nx file."""
        # Create project
        project = Project(
            user_id=user_id,
            name=name,
            description=description,
            visibility=visibility
        )
        
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        
        # Create default file
        default_content = (
            "// Welcome to NexusLang v2!\n"
            "// Write your AI-powered code here\n\n"
            "fn main() {\n"
            "    print(\"Hello, NexusLang!\")\n"
            "}\n\n"
            "main()\n"
        )
        
        default_file = File(
            project_id=project.id,
            path="main.nx",
            content=default_content,
            size_bytes=len(default_content.encode('utf-8'))
        )
        
        self.db.add(default_file)
        await self.db.commit()
        
        return project
    
    async def get_project(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Optional[Project]:
        """Get a project by ID (checks ownership)."""
        result = await self.db.execute(
            select(Project).where(
                and_(
                    Project.id == project_id,
                    Project.user_id == user_id
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def update_project(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        **updates
    ) -> Optional[Project]:
        """Update project fields."""
        project = await self.get_project(project_id, user_id)
        if not project:
            return None
        
        for key, value in updates.items():
            if hasattr(project, key) and value is not None:
                setattr(project, key, value)
        
        project.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(project)
        
        return project
    
    async def delete_project(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """Delete a project and all its files."""
        project = await self.get_project(project_id, user_id)
        if not project:
            return False
        
        # Delete all files
        await self.db.execute(
            select(File).where(File.project_id == project_id)
        )
        
        # Delete project
        await self.db.delete(project)
        await self.db.commit()
        
        return True
    
    async def get_project_files(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> List[File]:
        """Get all files in a project."""
        # Verify ownership
        project = await self.get_project(project_id, user_id)
        if not project:
            return []
        
        result = await self.db.execute(
            select(File)
            .where(File.project_id == project_id)
            .order_by(File.path)
        )
        return result.scalars().all()
    
    async def create_file(
        self,
        project_id: uuid.UUID,
        user_id: uuid.UUID,
        path: str,
        content: str = ""
    ) -> Optional[File]:
        """Create a new file in a project."""
        # Verify ownership
        project = await self.get_project(project_id, user_id)
        if not project:
            return None
        
        # Check if file exists
        existing = await self.db.execute(
            select(File).where(
                and_(
                    File.project_id == project_id,
                    File.path == path
                )
            )
        )
        if existing.scalar_one_or_none():
            return None  # File already exists
        
        # Create file
        file = File(
            project_id=project_id,
            path=path,
            content=content,
            size_bytes=len(content.encode('utf-8'))
        )
        
        self.db.add(file)
        project.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(file)
        
        return file
    
    async def get_file(
        self,
        file_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Optional[File]:
        """Get a file by ID (checks project ownership)."""
        result = await self.db.execute(
            select(File).where(File.id == file_id)
        )
        file = result.scalar_one_or_none()
        
        if not file:
            return None
        
        # Verify user owns the project
        project = await self.get_project(file.project_id, user_id)
        if not project:
            return None
        
        return file
    
    async def update_file(
        self,
        file_id: uuid.UUID,
        user_id: uuid.UUID,
        content: str
    ) -> Optional[File]:
        """Update file content."""
        file = await self.get_file(file_id, user_id)
        if not file:
            return None
        
        file.content = content
        file.size_bytes = len(content.encode('utf-8'))
        file.version += 1
        file.updated_at = datetime.utcnow()
        
        # Update project timestamp
        project = await self.get_project(file.project_id, user_id)
        if project:
            project.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(file)
        
        return file
    
    async def delete_file(
        self,
        file_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> bool:
        """Delete a file."""
        file = await self.get_file(file_id, user_id)
        if not file:
            return False
        
        await self.db.delete(file)
        await self.db.commit()
        
        return True

