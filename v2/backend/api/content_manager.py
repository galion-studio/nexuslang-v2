"""
Content Manager API Routes
Multi-brand social media management system
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import uuid

from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.content import (
    Brand, SocialAccount, ContentPost, PlatformPost,
    PostAnalytics, ContentTemplate, TeamPermission,
    PostComment, ContentActivityLog, MediaAsset,
    N8nWebhook, ScheduledJob
)

router = APIRouter(prefix="/content-manager", tags=["Content Manager"])


# ============================================================
# PYDANTIC SCHEMAS
# ============================================================

class BrandCreate(BaseModel):
    name: str
    slug: str
    logo_url: Optional[str] = None
    brand_color: str = "#000000"
    voice_guidelines: Optional[str] = None
    website_url: Optional[str] = None
    description: Optional[str] = None


class BrandResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    logo_url: Optional[str]
    brand_color: str
    voice_guidelines: Optional[str]
    website_url: Optional[str]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class SocialAccountCreate(BaseModel):
    brand_id: uuid.UUID
    platform: str
    account_name: str
    account_url: Optional[str] = None
    account_id: Optional[str] = None
    credentials: Optional[dict] = {}
    platform_metadata: Optional[dict] = {}


class SocialAccountResponse(BaseModel):
    id: uuid.UUID
    brand_id: uuid.UUID
    platform: str
    account_name: str
    account_url: Optional[str]
    is_active: bool
    sync_status: str
    last_synced: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ContentPostCreate(BaseModel):
    brand_id: uuid.UUID
    title: Optional[str] = None
    content: str
    content_html: Optional[str] = None
    excerpt: Optional[str] = None
    media_urls: List[dict] = []
    platforms: List[str] = []
    hashtags: List[str] = []
    mentions: List[str] = []
    metadata: dict = {}
    status: str = "draft"
    scheduled_at: Optional[datetime] = None
    template_id: Optional[uuid.UUID] = None


class ContentPostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    content_html: Optional[str] = None
    excerpt: Optional[str] = None
    media_urls: Optional[List[dict]] = None
    platforms: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None
    metadata: Optional[dict] = None
    status: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class ContentPostResponse(BaseModel):
    id: uuid.UUID
    brand_id: uuid.UUID
    title: Optional[str]
    content: str
    excerpt: Optional[str]
    media_urls: List[dict]
    platforms: List[str]
    hashtags: List[str]
    status: str
    scheduled_at: Optional[datetime]
    published_at: Optional[datetime]
    created_by: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ContentTemplateCreate(BaseModel):
    brand_id: uuid.UUID
    name: str
    description: Optional[str] = None
    template_content: str
    template_variables: List[dict] = []
    platforms: List[str] = []
    tags: List[str] = []
    category: Optional[str] = None


class ContentTemplateResponse(BaseModel):
    id: uuid.UUID
    brand_id: uuid.UUID
    name: str
    description: Optional[str]
    template_content: str
    template_variables: List[dict]
    platforms: List[str]
    tags: List[str]
    category: Optional[str]
    use_count: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalyticsResponse(BaseModel):
    platform_post_id: uuid.UUID
    likes: int
    comments: int
    shares: int
    views: int
    engagement_rate: float
    synced_at: datetime
    
    class Config:
        from_attributes = True


class PostCommentCreate(BaseModel):
    content_post_id: uuid.UUID
    comment: str
    parent_comment_id: Optional[uuid.UUID] = None


class N8nWebhookCreate(BaseModel):
    name: str
    description: Optional[str] = None
    webhook_url: str
    webhook_method: str = "POST"
    trigger_event: Optional[str] = None


# ============================================================
# BRANDS ENDPOINTS
# ============================================================

@router.get("/brands", response_model=List[BrandResponse])
async def get_brands(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all brands"""
    result = await db.execute(select(Brand).where(Brand.is_active == True))
    brands = result.scalars().all()
    return brands


@router.get("/brands/{brand_id}", response_model=BrandResponse)
async def get_brand(
    brand_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific brand"""
    result = await db.execute(select(Brand).where(Brand.id == brand_id))
    brand = result.scalar_one_or_none()
    if not brand:
        raise HTTPException(status_code=404, detail="Brand not found")
    return brand


@router.post("/brands", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(
    brand_data: BrandCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new brand"""
    brand = Brand(**brand_data.dict())
    db.add(brand)
    await db.commit()
    await db.refresh(brand)
    return brand


# ============================================================
# SOCIAL ACCOUNTS ENDPOINTS
# ============================================================

@router.get("/social-accounts", response_model=List[SocialAccountResponse])
async def get_social_accounts(
    brand_id: Optional[uuid.UUID] = None,
    platform: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all social accounts with optional filters"""
    query = select(SocialAccount)
    
    conditions = []
    if brand_id:
        conditions.append(SocialAccount.brand_id == brand_id)
    if platform:
        conditions.append(SocialAccount.platform == platform)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    result = await db.execute(query)
    accounts = result.scalars().all()
    return accounts


@router.post("/social-accounts", response_model=SocialAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_social_account(
    account_data: SocialAccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Connect a new social account"""
    account = SocialAccount(**account_data.dict())
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


@router.put("/social-accounts/{account_id}")
async def update_social_account(
    account_id: uuid.UUID,
    credentials: Optional[dict] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update social account credentials or status"""
    result = await db.execute(select(SocialAccount).where(SocialAccount.id == account_id))
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(status_code=404, detail="Social account not found")
    
    if credentials is not None:
        account.credentials = credentials
    if is_active is not None:
        account.is_active = is_active
    
    await db.commit()
    return {"message": "Account updated successfully"}


# ============================================================
# CONTENT POSTS ENDPOINTS
# ============================================================

@router.get("/posts", response_model=List[ContentPostResponse])
async def get_posts(
    brand_id: Optional[uuid.UUID] = None,
    status: Optional[str] = None,
    platform: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get content posts with optional filters"""
    query = select(ContentPost).order_by(desc(ContentPost.created_at))
    
    conditions = []
    if brand_id:
        conditions.append(ContentPost.brand_id == brand_id)
    if status:
        conditions.append(ContentPost.status == status)
    if platform:
        # Check if platform is in the platforms JSONB array
        conditions.append(ContentPost.platforms.contains([platform]))
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    posts = result.scalars().all()
    return posts


@router.get("/posts/{post_id}", response_model=ContentPostResponse)
async def get_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific content post"""
    result = await db.execute(select(ContentPost).where(ContentPost.id == post_id))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.post("/posts", response_model=ContentPostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post_data: ContentPostCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new content post"""
    post = ContentPost(
        **post_data.dict(),
        created_by=current_user.id,
        updated_by=current_user.id
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    
    # Log activity
    activity = ContentActivityLog(
        user_id=current_user.id,
        action="created",
        entity_type="content_post",
        entity_id=post.id,
        metadata={"title": post.title, "brand_id": str(post.brand_id)}
    )
    db.add(activity)
    await db.commit()
    
    # If scheduled, create scheduled job
    if post.status == "scheduled" and post.scheduled_at:
        background_tasks.add_task(schedule_post_job, post.id, post.scheduled_at, db)
    
    return post


@router.put("/posts/{post_id}", response_model=ContentPostResponse)
async def update_post(
    post_id: uuid.UUID,
    post_data: ContentPostUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a content post"""
    result = await db.execute(select(ContentPost).where(ContentPost.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Update fields
    update_data = post_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)
    
    post.updated_by = current_user.id
    
    await db.commit()
    await db.refresh(post)
    
    # Log activity
    activity = ContentActivityLog(
        user_id=current_user.id,
        action="updated",
        entity_type="content_post",
        entity_id=post.id,
        changes=update_data
    )
    db.add(activity)
    await db.commit()
    
    return post


@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a content post"""
    result = await db.execute(select(ContentPost).where(ContentPost.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    await db.delete(post)
    await db.commit()
    
    # Log activity
    activity = ContentActivityLog(
        user_id=current_user.id,
        action="deleted",
        entity_type="content_post",
        entity_id=post_id,
        metadata={"title": post.title}
    )
    db.add(activity)
    await db.commit()
    
    return {"message": "Post deleted successfully"}


@router.post("/posts/{post_id}/publish")
async def publish_post(
    post_id: uuid.UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Publish a post to all selected platforms immediately"""
    result = await db.execute(select(ContentPost).where(ContentPost.id == post_id))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Update status
    post.status = "publishing"
    await db.commit()
    
    # Trigger publishing in background
    background_tasks.add_task(publish_to_platforms, post_id, db)
    
    return {"message": "Publishing started", "post_id": str(post_id)}


# ============================================================
# CONTENT TEMPLATES ENDPOINTS
# ============================================================

@router.get("/templates", response_model=List[ContentTemplateResponse])
async def get_templates(
    brand_id: Optional[uuid.UUID] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get content templates"""
    query = select(ContentTemplate).where(ContentTemplate.is_active == True)
    
    if brand_id:
        query = query.where(ContentTemplate.brand_id == brand_id)
    if category:
        query = query.where(ContentTemplate.category == category)
    
    result = await db.execute(query)
    templates = result.scalars().all()
    return templates


@router.post("/templates", response_model=ContentTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: ContentTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new content template"""
    template = ContentTemplate(
        **template_data.dict(),
        created_by=current_user.id
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


# ============================================================
# ANALYTICS ENDPOINTS
# ============================================================

@router.get("/analytics/post/{post_id}")
async def get_post_analytics(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics for all platform posts of a content post"""
    # Get all platform posts for this content post
    result = await db.execute(
        select(PlatformPost, PostAnalytics)
        .join(PostAnalytics, PlatformPost.id == PostAnalytics.platform_post_id, isouter=True)
        .where(PlatformPost.content_post_id == post_id)
    )
    
    analytics_data = []
    for platform_post, analytics in result.all():
        analytics_data.append({
            "platform": platform_post.platform,
            "platform_url": platform_post.platform_url,
            "status": platform_post.status,
            "likes": analytics.likes if analytics else 0,
            "comments": analytics.comments if analytics else 0,
            "shares": analytics.shares if analytics else 0,
            "views": analytics.views if analytics else 0,
            "engagement_rate": float(analytics.engagement_rate) if analytics else 0.0
        })
    
    return {"post_id": str(post_id), "platforms": analytics_data}


@router.get("/analytics/brand/{brand_id}")
async def get_brand_analytics(
    brand_id: uuid.UUID,
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get aggregated analytics for a brand"""
    date_from = datetime.utcnow() - timedelta(days=days)
    
    # Get all posts for this brand published in the time range
    result = await db.execute(
        select(
            func.count(ContentPost.id).label('total_posts'),
            func.sum(PostAnalytics.likes).label('total_likes'),
            func.sum(PostAnalytics.comments).label('total_comments'),
            func.sum(PostAnalytics.shares).label('total_shares'),
            func.sum(PostAnalytics.views).label('total_views'),
            func.avg(PostAnalytics.engagement_rate).label('avg_engagement_rate')
        )
        .select_from(ContentPost)
        .join(PlatformPost, ContentPost.id == PlatformPost.content_post_id)
        .join(PostAnalytics, PlatformPost.id == PostAnalytics.platform_post_id, isouter=True)
        .where(
            and_(
                ContentPost.brand_id == brand_id,
                ContentPost.published_at >= date_from
            )
        )
    )
    
    row = result.first()
    
    return {
        "brand_id": str(brand_id),
        "period_days": days,
        "total_posts": row.total_posts or 0,
        "total_likes": row.total_likes or 0,
        "total_comments": row.total_comments or 0,
        "total_shares": row.total_shares or 0,
        "total_views": row.total_views or 0,
        "avg_engagement_rate": float(row.avg_engagement_rate or 0.0)
    }


# ============================================================
# POST COMMENTS ENDPOINTS
# ============================================================

@router.post("/posts/{post_id}/comments")
async def add_comment(
    post_id: uuid.UUID,
    comment_data: PostCommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a comment to a post"""
    comment = PostComment(
        content_post_id=post_id,
        user_id=current_user.id,
        comment=comment_data.comment,
        parent_comment_id=comment_data.parent_comment_id
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)
    return comment


@router.get("/posts/{post_id}/comments")
async def get_post_comments(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all comments for a post"""
    result = await db.execute(
        select(PostComment)
        .where(PostComment.content_post_id == post_id)
        .order_by(PostComment.created_at)
    )
    comments = result.scalars().all()
    return comments


# ============================================================
# N8N WEBHOOK ENDPOINTS
# ============================================================

@router.post("/n8n/trigger")
async def trigger_n8n_webhook(
    webhook_id: uuid.UUID,
    payload: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger an N8n workflow"""
    result = await db.execute(select(N8nWebhook).where(N8nWebhook.id == webhook_id))
    webhook = result.scalar_one_or_none()
    
    if not webhook or not webhook.is_active:
        raise HTTPException(status_code=404, detail="Webhook not found or inactive")
    
    # Import here to avoid circular dependency
    from services.social.n8n_integration import trigger_webhook
    
    success = await trigger_webhook(webhook.webhook_url, payload, webhook.webhook_method)
    
    # Update webhook stats
    webhook.last_triggered_at = datetime.utcnow()
    if success:
        webhook.success_count += 1
    else:
        webhook.failure_count += 1
    
    await db.commit()
    
    return {"success": success, "webhook_id": str(webhook_id)}


@router.post("/n8n/callback")
async def n8n_callback(
    payload: dict,
    db: AsyncSession = Depends(get_db)
):
    """Receive callback from N8n workflow"""
    # Process N8n callback
    # This can update post status, analytics, etc.
    return {"received": True, "timestamp": datetime.utcnow().isoformat()}


# ============================================================
# TEAM PERMISSIONS ENDPOINTS
# ============================================================

@router.get("/permissions/user/{user_id}")
async def get_user_permissions(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get permissions for a user"""
    result = await db.execute(
        select(TeamPermission).where(
            and_(
                TeamPermission.user_id == user_id,
                TeamPermission.is_active == True
            )
        )
    )
    permissions = result.scalars().all()
    return permissions


# ============================================================
# HELPER FUNCTIONS
# ============================================================

async def schedule_post_job(post_id: uuid.UUID, scheduled_at: datetime, db: AsyncSession):
    """Create a scheduled job for publishing a post"""
    job = ScheduledJob(
        job_type="post_content",
        entity_type="content_post",
        entity_id=post_id,
        scheduled_for=scheduled_at,
        payload={"post_id": str(post_id)}
    )
    db.add(job)
    await db.commit()


async def publish_to_platforms(post_id: uuid.UUID, db: AsyncSession):
    """Publish a post to all selected platforms"""
    # This will be implemented in the platform connectors
    # For now, just update the status
    result = await db.execute(select(ContentPost).where(ContentPost.id == post_id))
    post = result.scalar_one_or_none()
    
    if post:
        post.status = "published"
        post.published_at = datetime.utcnow()
        await db.commit()

