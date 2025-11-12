"""
Grokopedia knowledge base models.
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, Float, ARRAY, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector
import uuid
from datetime import datetime
import enum

from ..core.database import Base


class RelationshipType(str, enum.Enum):
    """Knowledge graph relationship types."""
    RELATED_TO = "related_to"
    PART_OF = "part_of"
    PREREQUISITE = "prerequisite"
    SIMILAR_TO = "similar_to"
    OPPOSITE_OF = "opposite_of"


class ContributionType(str, enum.Enum):
    """Contribution types."""
    CREATE = "create"
    EDIT = "edit"
    VERIFY = "verify"
    COMMENT = "comment"


class KnowledgeEntry(Base):
    """Knowledge entry model."""
    
    __tablename__ = "knowledge_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False, index=True)
    slug = Column(String(500), unique=True, nullable=False, index=True)
    summary = Column(Text)
    content = Column(Text, nullable=False)
    embeddings = Column(Vector(1536))  # OpenAI embedding dimension
    tags = Column(ARRAY(String), default=[])
    verified = Column(Boolean, default=False, index=True)
    verified_by = Column(UUID(as_uuid=True))
    verified_at = Column(DateTime)
    views_count = Column(Integer, default=0)
    upvotes_count = Column(Integer, default=0)
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class KnowledgeGraph(Base):
    """Knowledge graph relationships."""
    
    __tablename__ = "knowledge_graph"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    target_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    relationship = Column(SQLEnum(RelationshipType), nullable=False)
    weight = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class Contribution(Base):
    """Knowledge contribution tracking."""
    
    __tablename__ = "contributions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entry_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    type = Column(SQLEnum(ContributionType), nullable=False)
    changes = Column(JSONB)
    approved = Column(Boolean, default=False)
    approved_by = Column(UUID(as_uuid=True))
    approved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

