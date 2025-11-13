"""
Project Model
User projects for code storage and management.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, BINARY
from sqlalchemy.orm import relationship
from datetime import datetime
from .user import Base


class Project(Base):
    """
    Project model for storing user code projects.
    
    Supports NexusLang and other languages.
    """
    
    __tablename__ = "projects"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Project info
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    language = Column(String(50), default="nexuslang", nullable=False)
    
    # Code
    code = Column(Text, nullable=True)
    compiled_binary = Column(BINARY, nullable=True)
    
    # Status
    status = Column(String(50), default="draft", nullable=False)  # draft, active, archived
    visibility = Column(String(50), default="private", nullable=False)  # private, public, unlisted
    
    # Stats
    execution_count = Column(Integer, default=0)
    last_executed = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    # user = relationship("User", back_populates="projects")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.name}', user_id={self.user_id})>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "language": self.language,
            "status": self.status,
            "visibility": self.visibility,
            "execution_count": self.execution_count,
            "last_executed": self.last_executed.isoformat() if self.last_executed else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
