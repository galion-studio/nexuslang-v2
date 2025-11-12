"""
Database Models for CMS
Defines the structure of our database tables
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# User model for authentication
# Stores admin users who can manage content
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)  # Never store plain passwords!
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship: One user can create many content items
    content_items = relationship("Content", back_populates="author")

# Category model for organizing content
# Helps organize posts into topics like "Technology", "News", etc.
class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)  # URL-friendly version of name
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship: One category can have many content items
    content_items = relationship("Content", back_populates="category")

# Content model - the heart of our CMS
# Stores all blog posts, pages, and articles
class Content(Base):
    __tablename__ = "content"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), unique=True, nullable=False)  # Used in URLs
    content = Column(Text, nullable=False)  # The actual content body
    excerpt = Column(Text, nullable=True)  # Short description/preview
    
    # Content type: "post", "page", "article", etc.
    content_type = Column(String(50), default="post")
    
    # Publishing status: "draft", "published", "archived"
    status = Column(String(20), default="draft")
    
    # Foreign keys to link to other tables
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    
    # SEO and metadata
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(Text, nullable=True)
    featured_image = Column(String(500), nullable=True)  # URL to image
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    
    # View counter for analytics
    views = Column(Integer, default=0)
    
    # Relationships to access related data
    author = relationship("User", back_populates="content_items")
    category = relationship("Category", back_populates="content_items")

