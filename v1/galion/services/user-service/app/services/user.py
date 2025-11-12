"""
Business logic for user operations.
Separating business logic from API endpoints makes code more testable and maintainable.
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import Optional, List
import uuid

from app.models.user import User
from app.schemas.user import UserUpdate, UserSearch


class UserService:
    """
    Service class for user-related operations.
    Contains all business logic for user management.
    """
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[User]:
        """
        Fetch user by their ID.
        
        Args:
            db: Database session
            user_id: User's UUID
            
        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Fetch user by their email address.
        
        Args:
            db: Database session
            email: User's email address
            
        Returns:
            User object if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def update_user(
        db: Session,
        user: User,
        update_data: UserUpdate
    ) -> User:
        """
        Update user profile information.
        
        Only updates fields that are provided (not None).
        This allows partial updates.
        
        Args:
            db: Database session
            user: User object to update
            update_data: UserUpdate schema with new values
            
        Returns:
            Updated user object
        """
        # Get dictionary of provided fields (excluding None values)
        update_dict = update_data.model_dump(exclude_unset=True)
        
        # Update each provided field
        for field, value in update_dict.items():
            setattr(user, field, value)
        
        # Commit changes to database
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def search_users(
        db: Session,
        search: UserSearch
    ) -> tuple[List[User], int]:
        """
        Search for users based on criteria.
        
        Supports:
        - Text search in name and email
        - Filter by role
        - Filter by active status
        - Pagination (limit and offset)
        
        Args:
            db: Database session
            search: UserSearch schema with search criteria
            
        Returns:
            Tuple of (list of users, total count)
        """
        # Start with base query
        query = db.query(User)
        
        # Apply text search if provided
        if search.query:
            # Search in both name and email
            # ilike is case-insensitive LIKE
            search_filter = or_(
                User.name.ilike(f"%{search.query}%"),
                User.email.ilike(f"%{search.query}%")
            )
            query = query.filter(search_filter)
        
        # Apply role filter if provided
        if search.role:
            query = query.filter(User.role == search.role)
        
        # Apply active status filter if provided
        if search.is_active is not None:
            query = query.filter(User.is_active == search.is_active)
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination
        query = query.offset(search.offset).limit(search.limit)
        
        # Execute query
        users = query.all()
        
        return users, total
    
    @staticmethod
    def deactivate_user(db: Session, user: User) -> User:
        """
        Deactivate a user account.
        
        Deactivated users cannot log in or access the system.
        This is softer than deleting the account.
        
        Args:
            db: Database session
            user: User object to deactivate
            
        Returns:
            Updated user object
        """
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def activate_user(db: Session, user: User) -> User:
        """
        Reactivate a user account.
        
        Args:
            db: Database session
            user: User object to activate
            
        Returns:
            Updated user object
        """
        user.is_active = True
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_users_list(
        db: Session,
        limit: int = 10,
        offset: int = 0
    ) -> tuple[List[User], int]:
        """
        Get paginated list of all users.
        
        Args:
            db: Database session
            limit: Maximum number of users to return
            offset: Number of users to skip
            
        Returns:
            Tuple of (list of users, total count)
        """
        # Get total count
        total = db.query(User).count()
        
        # Get paginated results
        users = db.query(User)\
            .order_by(User.created_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
        
        return users, total

