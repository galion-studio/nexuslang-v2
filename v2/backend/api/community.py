"""
Community API routes.
Handles social features, forums, teams, and project sharing.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import Optional, List
from datetime import datetime
import uuid

from ..core.database import get_db
from ..models.user import User
from ..models.project import Project, VisibilityType
from ..models.community import Post, Comment, Team, TeamMember, Star
from ..api.auth import get_current_user, get_optional_user

router = APIRouter()


# Request/Response Models
class CreatePostRequest(BaseModel):
    title: str
    content: str
    category: Optional[str] = "general"
    tags: Optional[List[str]] = None


class UpdatePostRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None


class PostResponse(BaseModel):
    id: str
    title: str
    content: str
    category: str
    tags: List[str]
    author_id: str
    author_username: str
    upvotes_count: int
    comments_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CreateCommentRequest(BaseModel):
    content: str
    parent_id: Optional[str] = None


class CommentResponse(BaseModel):
    id: str
    post_id: str
    content: str
    author_id: str
    author_username: str
    parent_id: Optional[str]
    upvotes_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CreateTeamRequest(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = True


class TeamResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    owner_id: str
    is_public: bool
    member_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class PublicProjectResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    stars_count: int
    forks_count: int
    author_id: str
    author_username: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Forum/Discussion Endpoints
@router.get("/posts", response_model=List[PostResponse])
async def list_posts(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    sort: str = "recent",  # recent, popular, trending
    limit: int = Query(20, ge=1, le=100),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    List community posts/discussions.
    """
    query = select(Post)
    
    # Apply filters
    if category:
        query = query.where(Post.category == category)
    
    if tag:
        query = query.where(Post.tags.contains([tag]))
    
    # Apply sorting
    if sort == "popular":
        query = query.order_by(Post.upvotes_count.desc())
    elif sort == "trending":
        query = query.order_by((Post.upvotes_count + Post.comments_count * 2).desc())
    else:  # recent
        query = query.order_by(Post.created_at.desc())
    
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    posts = result.scalars().all()
    
    # Get author usernames
    post_responses = []
    for post in posts:
        author_result = await db.execute(
            select(User).where(User.id == post.author_id)
        )
        author = author_result.scalar_one_or_none()
        
        post_responses.append(PostResponse(
            id=str(post.id),
            title=post.title,
            content=post.content,
            category=post.category,
            tags=post.tags or [],
            author_id=str(post.author_id),
            author_username=author.username if author else "Unknown",
            upvotes_count=post.upvotes_count,
            comments_count=post.comments_count,
            created_at=post.created_at,
            updated_at=post.updated_at
        ))
    
    return post_responses


@router.post("/posts", response_model=PostResponse)
async def create_post(
    request: CreatePostRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new discussion post.
    """
    post = Post(
        title=request.title,
        content=request.content,
        category=request.category,
        tags=request.tags or [],
        author_id=current_user.id
    )
    
    db.add(post)
    await db.commit()
    await db.refresh(post)
    
    return PostResponse(
        id=str(post.id),
        title=post.title,
        content=post.content,
        category=post.category,
        tags=post.tags or [],
        author_id=str(post.author_id),
        author_username=current_user.username,
        upvotes_count=0,
        comments_count=0,
        created_at=post.created_at,
        updated_at=post.updated_at
    )


@router.get("/posts/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a single post by ID.
    """
    result = await db.execute(
        select(Post).where(Post.id == uuid.UUID(post_id))
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Get author
    author_result = await db.execute(
        select(User).where(User.id == post.author_id)
    )
    author = author_result.scalar_one_or_none()
    
    return PostResponse(
        id=str(post.id),
        title=post.title,
        content=post.content,
        category=post.category,
        tags=post.tags or [],
        author_id=str(post.author_id),
        author_username=author.username if author else "Unknown",
        upvotes_count=post.upvotes_count,
        comments_count=post.comments_count,
        created_at=post.created_at,
        updated_at=post.updated_at
    )


@router.post("/posts/{post_id}/upvote")
async def upvote_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upvote a post.
    """
    result = await db.execute(
        select(Post).where(Post.id == uuid.UUID(post_id))
    )
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    post.upvotes_count += 1
    await db.commit()
    
    return {"upvotes_count": post.upvotes_count}


# Comments
@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
async def get_post_comments(
    post_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get comments for a post.
    """
    result = await db.execute(
        select(Comment)
        .where(Comment.post_id == uuid.UUID(post_id))
        .order_by(Comment.created_at.asc())
    )
    comments = result.scalars().all()
    
    comment_responses = []
    for comment in comments:
        author_result = await db.execute(
            select(User).where(User.id == comment.author_id)
        )
        author = author_result.scalar_one_or_none()
        
        comment_responses.append(CommentResponse(
            id=str(comment.id),
            post_id=str(comment.post_id),
            content=comment.content,
            author_id=str(comment.author_id),
            author_username=author.username if author else "Unknown",
            parent_id=str(comment.parent_id) if comment.parent_id else None,
            upvotes_count=comment.upvotes_count,
            created_at=comment.created_at
        ))
    
    return comment_responses


@router.post("/posts/{post_id}/comments", response_model=CommentResponse)
async def create_comment(
    post_id: str,
    request: CreateCommentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a comment on a post.
    """
    # Verify post exists
    post_result = await db.execute(
        select(Post).where(Post.id == uuid.UUID(post_id))
    )
    post = post_result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    comment = Comment(
        post_id=uuid.UUID(post_id),
        content=request.content,
        author_id=current_user.id,
        parent_id=uuid.UUID(request.parent_id) if request.parent_id else None
    )
    
    db.add(comment)
    
    # Update post comment count
    post.comments_count += 1
    
    await db.commit()
    await db.refresh(comment)
    
    return CommentResponse(
        id=str(comment.id),
        post_id=str(comment.post_id),
        content=comment.content,
        author_id=str(comment.author_id),
        author_username=current_user.username,
        parent_id=str(comment.parent_id) if comment.parent_id else None,
        upvotes_count=0,
        created_at=comment.created_at
    )


# Public Projects
@router.get("/projects/public", response_model=List[PublicProjectResponse])
async def list_public_projects(
    sort: str = "recent",  # recent, popular, stars
    limit: int = Query(20, ge=1, le=100),
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """
    List publicly shared projects.
    """
    query = select(Project).where(Project.visibility == VisibilityType.PUBLIC)
    
    # Apply sorting
    if sort == "stars":
        query = query.order_by(Project.stars_count.desc())
    elif sort == "popular":
        query = query.order_by((Project.stars_count + Project.forks_count * 2).desc())
    else:  # recent
        query = query.order_by(Project.created_at.desc())
    
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    projects = result.scalars().all()
    
    project_responses = []
    for project in projects:
        author_result = await db.execute(
            select(User).where(User.id == project.user_id)
        )
        author = author_result.scalar_one_or_none()
        
        project_responses.append(PublicProjectResponse(
            id=str(project.id),
            name=project.name,
            description=project.description,
            stars_count=project.stars_count,
            forks_count=project.forks_count,
            author_id=str(project.user_id),
            author_username=author.username if author else "Unknown",
            created_at=project.created_at,
            updated_at=project.updated_at
        ))
    
    return project_responses


@router.post("/projects/{project_id}/star")
async def star_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Star a project.
    """
    # Check if already starred
    existing_result = await db.execute(
        select(Star).where(
            and_(
                Star.user_id == current_user.id,
                Star.project_id == uuid.UUID(project_id)
            )
        )
    )
    existing_star = existing_result.scalar_one_or_none()
    
    if existing_star:
        # Unstar
        await db.delete(existing_star)
        
        # Update project count
        project_result = await db.execute(
            select(Project).where(Project.id == uuid.UUID(project_id))
        )
        project = project_result.scalar_one_or_none()
        if project:
            project.stars_count = max(0, project.stars_count - 1)
        
        await db.commit()
        return {"starred": False, "stars_count": project.stars_count if project else 0}
    else:
        # Star
        star = Star(
            user_id=current_user.id,
            project_id=uuid.UUID(project_id)
        )
        db.add(star)
        
        # Update project count
        project_result = await db.execute(
            select(Project).where(Project.id == uuid.UUID(project_id))
        )
        project = project_result.scalar_one_or_none()
        if project:
            project.stars_count += 1
        
        await db.commit()
        return {"starred": True, "stars_count": project.stars_count if project else 1}


@router.post("/projects/{project_id}/fork")
async def fork_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Fork a public project.
    """
    # Get original project
    result = await db.execute(
        select(Project).where(Project.id == uuid.UUID(project_id))
    )
    original_project = result.scalar_one_or_none()
    
    if not original_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    if original_project.visibility != VisibilityType.PUBLIC:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot fork private project"
        )
    
    # Create forked project
    from ...models.project import File
    
    forked_project = Project(
        user_id=current_user.id,
        name=f"{original_project.name} (forked)",
        description=f"Forked from {original_project.name}",
        visibility=VisibilityType.PRIVATE,
        forked_from=original_project.id
    )
    
    db.add(forked_project)
    await db.commit()
    await db.refresh(forked_project)
    
    # Copy all files
    files_result = await db.execute(
        select(File).where(File.project_id == original_project.id)
    )
    original_files = files_result.scalars().all()
    
    for original_file in original_files:
        new_file = File(
            project_id=forked_project.id,
            path=original_file.path,
            content=original_file.content,
            size_bytes=original_file.size_bytes
        )
        db.add(new_file)
    
    # Update original project fork count
    original_project.forks_count += 1
    
    await db.commit()
    
    return {
        "project_id": str(forked_project.id),
        "name": forked_project.name,
        "message": "Project forked successfully!"
    }


# Teams
@router.get("/teams", response_model=List[TeamResponse])
async def list_teams(
    public_only: bool = True,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List teams (public or user's teams).
    """
    if public_only or not current_user:
        query = select(Team).where(Team.is_public == True)
    else:
        # Get teams where user is member
        query = select(Team).join(
            TeamMember, TeamMember.team_id == Team.id
        ).where(TeamMember.user_id == current_user.id)
    
    result = await db.execute(query)
    teams = result.scalars().all()
    
    team_responses = []
    for team in teams:
        # Count members
        members_result = await db.execute(
            select(func.count()).select_from(TeamMember).where(TeamMember.team_id == team.id)
        )
        member_count = members_result.scalar()
        
        team_responses.append(TeamResponse(
            id=str(team.id),
            name=team.name,
            description=team.description,
            owner_id=str(team.owner_id),
            is_public=team.is_public,
            member_count=member_count or 0,
            created_at=team.created_at
        ))
    
    return team_responses


@router.post("/teams", response_model=TeamResponse)
async def create_team(
    request: CreateTeamRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new team.
    """
    team = Team(
        name=request.name,
        description=request.description,
        owner_id=current_user.id,
        is_public=request.is_public
    )
    
    db.add(team)
    await db.commit()
    await db.refresh(team)
    
    # Add creator as admin member
    member = TeamMember(
        team_id=team.id,
        user_id=current_user.id,
        role="admin"
    )
    db.add(member)
    await db.commit()
    
    return TeamResponse(
        id=str(team.id),
        name=team.name,
        description=team.description,
        owner_id=str(team.owner_id),
        is_public=team.is_public,
        member_count=1,
        created_at=team.created_at
    )


@router.post("/teams/{team_id}/join")
async def join_team(
    team_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Join a public team.
    """
    # Verify team exists and is public
    team_result = await db.execute(
        select(Team).where(Team.id == uuid.UUID(team_id))
    )
    team = team_result.scalar_one_or_none()
    
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found"
        )
    
    if not team.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Team is private"
        )
    
    # Check if already member
    existing_result = await db.execute(
        select(TeamMember).where(
            and_(
                TeamMember.team_id == uuid.UUID(team_id),
                TeamMember.user_id == current_user.id
            )
        )
    )
    if existing_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already a team member"
        )
    
    # Add as member
    member = TeamMember(
        team_id=uuid.UUID(team_id),
        user_id=current_user.id,
        role="member"
    )
    db.add(member)
    await db.commit()
    
    return {"message": "Joined team successfully!", "team_name": team.name}

