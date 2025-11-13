"""
Admin API endpoints for user management, roles, and system administration
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from typing import List, Optional
from datetime import datetime
import uuid

from ..core.database import get_db
from ..core.permissions import require_admin, PermissionChecker, assign_role, remove_role
from ..models.user import User
from ..models.rbac import Role, UserRole, BetaTesterProfile, UserFeedback, AuditLog

router = APIRouter()


# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================

class UserListItem(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login_at: Optional[datetime]
    roles: List[str]


class UserDetail(BaseModel):
    id: str
    email: str
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login_at: Optional[datetime]
    roles: List[str]
    permissions: List[str]


class AssignRoleRequest(BaseModel):
    user_id: str
    role_name: str


class UpdateUserRequest(BaseModel):
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class InviteBetaTesterRequest(BaseModel):
    user_id: str
    cohort: str


class SystemStats(BaseModel):
    total_users: int
    active_users: int
    beta_testers: int
    total_feedback: int
    critical_bugs: int


# ============================================================
# USER MANAGEMENT
# ============================================================

@router.get("/users", response_model=List[UserListItem])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = None,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    List all users with pagination and search.
    Requires admin role.
    """
    query = select(User).options(
        selectinload(User.user_roles).selectinload(UserRole.role)
    )
    
    # Add search filter
    if search:
        query = query.where(
            or_(
                User.email.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%")
            )
        )
    
    # Add pagination
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    # Format response
    user_list = []
    for user in users:
        roles = await PermissionChecker.get_user_roles(user, db)
        user_list.append(UserListItem(
            id=str(user.id),
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_login_at=user.last_login_at,
            roles=[role.name for role in roles]
        ))
    
    return user_list


@router.get("/users/{user_id}", response_model=UserDetail)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific user.
    Requires admin role.
    """
    result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get roles and permissions
    roles = await PermissionChecker.get_user_roles(user, db)
    permissions = await PermissionChecker.get_user_permissions(user, db)
    
    return UserDetail(
        id=str(user.id),
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        bio=user.bio,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        updated_at=user.updated_at,
        last_login_at=user.last_login_at,
        roles=[role.name for role in roles],
        permissions=permissions
    )


@router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    update_data: UpdateUserRequest,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user properties (activate/deactivate, verify, etc.)
    Requires admin role.
    """
    result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update fields
    if update_data.is_active is not None:
        user.is_active = update_data.is_active
    
    if update_data.is_verified is not None:
        user.is_verified = update_data.is_verified
    
    await db.commit()
    await db.refresh(user)
    
    return {"message": "User updated successfully", "user_id": str(user.id)}


# ============================================================
# ROLE MANAGEMENT
# ============================================================

@router.post("/users/{user_id}/roles")
async def assign_user_role(
    user_id: str,
    request: AssignRoleRequest,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Assign a role to a user.
    Requires admin role.
    """
    # Get target user
    result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        await assign_role(user, request.role_name, db, assigned_by=current_user)
        return {"message": f"Role '{request.role_name}' assigned to user"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/users/{user_id}/roles/{role_name}")
async def remove_user_role(
    user_id: str,
    role_name: str,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove a role from a user.
    Requires admin role.
    """
    # Get target user
    result = await db.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        await remove_role(user, role_name, db)
        return {"message": f"Role '{role_name}' removed from user"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================
# BETA TESTER MANAGEMENT
# ============================================================

@router.post("/beta-testers/invite")
async def invite_beta_tester(
    request: InviteBetaTesterRequest,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Invite a user to be a beta tester.
    Requires admin role.
    """
    # Get user
    result = await db.execute(
        select(User).where(User.id == uuid.UUID(request.user_id))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if already a beta tester
    result = await db.execute(
        select(BetaTesterProfile).where(BetaTesterProfile.user_id == user.id)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a beta tester"
        )
    
    # Create beta tester profile
    beta_profile = BetaTesterProfile(
        user_id=user.id,
        cohort=request.cohort,
        invited_by=current_user.id,
        invited_at=datetime.utcnow(),
        status='invited'
    )
    
    db.add(beta_profile)
    
    # Assign beta_tester role
    await assign_role(user, 'beta_tester', db, assigned_by=current_user)
    
    await db.commit()
    
    return {"message": "Beta tester invitation created", "profile_id": str(beta_profile.id)}


@router.get("/beta-testers")
async def list_beta_testers(
    cohort: Optional[str] = None,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    List all beta testers with optional cohort filter.
    Requires admin role.
    """
    query = select(BetaTesterProfile).options(
        selectinload(BetaTesterProfile.user)
    )
    
    if cohort:
        query = query.where(BetaTesterProfile.cohort == cohort)
    
    result = await db.execute(query)
    profiles = result.scalars().all()
    
    return [
        {
            "id": str(profile.id),
            "user_id": str(profile.user_id),
            "username": profile.user.username,
            "email": profile.user.email,
            "cohort": profile.cohort,
            "status": profile.status,
            "feedback_count": profile.feedback_count,
            "bugs_reported": profile.bugs_reported,
            "invited_at": profile.invited_at,
            "accepted_at": profile.accepted_at
        }
        for profile in profiles
    ]


# ============================================================
# SYSTEM STATISTICS
# ============================================================

@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Get system-wide statistics.
    Requires admin role.
    """
    # Total users
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar()
    
    # Active users (logged in last 30 days)
    from datetime import timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    result = await db.execute(
        select(func.count(User.id)).where(User.last_login_at >= thirty_days_ago)
    )
    active_users = result.scalar()
    
    # Beta testers
    result = await db.execute(
        select(func.count(BetaTesterProfile.id))
        .where(BetaTesterProfile.status == 'active')
    )
    beta_testers = result.scalar()
    
    # Total feedback
    result = await db.execute(select(func.count(UserFeedback.id)))
    total_feedback = result.scalar()
    
    # Critical bugs
    result = await db.execute(
        select(func.count(UserFeedback.id))
        .where(UserFeedback.feedback_type == 'bug')
        .where(UserFeedback.severity == 'critical')
        .where(UserFeedback.status != 'resolved')
    )
    critical_bugs = result.scalar()
    
    return SystemStats(
        total_users=total_users or 0,
        active_users=active_users or 0,
        beta_testers=beta_testers or 0,
        total_feedback=total_feedback or 0,
        critical_bugs=critical_bugs or 0
    )


# ============================================================
# FEEDBACK MANAGEMENT
# ============================================================

@router.get("/feedback")
async def list_feedback(
    feedback_type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    List all user feedback with filters.
    Requires admin role.
    """
    query = select(UserFeedback).options(
        selectinload(UserFeedback.user)
    )
    
    if feedback_type:
        query = query.where(UserFeedback.feedback_type == feedback_type)
    
    if status:
        query = query.where(UserFeedback.status == status)
    
    query = query.order_by(UserFeedback.created_at.desc())
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    feedback_items = result.scalars().all()
    
    return [
        {
            "id": str(item.id),
            "user": {
                "id": str(item.user.id),
                "username": item.user.username,
                "email": item.user.email
            },
            "feature_name": item.feature_name,
            "feedback_type": item.feedback_type,
            "title": item.title,
            "description": item.description,
            "severity": item.severity,
            "status": item.status,
            "created_at": item.created_at
        }
        for item in feedback_items
    ]


@router.patch("/feedback/{feedback_id}")
async def update_feedback(
    feedback_id: str,
    status: str,
    current_user: User = Depends(require_admin()),
    db: AsyncSession = Depends(get_db)
):
    """
    Update feedback status.
    Requires admin role.
    """
    result = await db.execute(
        select(UserFeedback).where(UserFeedback.id == uuid.UUID(feedback_id))
    )
    feedback = result.scalar_one_or_none()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )
    
    feedback.status = status
    
    if status == 'resolved':
        feedback.resolved_at = datetime.utcnow()
    
    await db.commit()
    
    return {"message": "Feedback updated", "feedback_id": str(feedback.id)}


# Security Dashboard Endpoints
@router.get("/security/dashboard")
async def get_security_dashboard(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get security dashboard data"""
    from ..core.security.anti_raid import get_anti_raid_system

    anti_raid_system = await get_anti_raid_system()
    return await anti_raid_system.get_security_dashboard_data()

@router.post("/security/unblock-ip")
async def unblock_ip(
    request: dict,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Unblock an IP address"""
    from ..core.security.anti_raid import get_anti_raid_system

    ip = request.get("ip")
    if not ip:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="IP address required"
        )

    anti_raid_system = await get_anti_raid_system()
    success = await anti_raid_system.unblock_ip(ip)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="IP not found or not blocked"
        )

    return {"message": "IP unblocked successfully"}

@router.get("/security/threats")
async def get_active_threats(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get list of active threats"""
    from ..core.security.anti_raid import get_anti_raid_system

    anti_raid_system = await get_anti_raid_system()
    dashboard_data = await anti_raid_system.get_security_dashboard_data()

    return {
        "threats": dashboard_data.get("recent_events", []),
        "total": dashboard_data.get("active_threats", 0)
    }

@router.post("/security/settings")
async def update_security_settings(
    settings: dict,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update security system settings"""
    from ..core.security.anti_raid import get_anti_raid_system

    anti_raid_system = await get_anti_raid_system()

    # Update settings
    if "auto_response_enabled" in settings:
        anti_raid_system.auto_response_enabled = settings["auto_response_enabled"]

    if "ddos_thresholds" in settings:
        anti_raid_system.ddos_thresholds.update(settings["ddos_thresholds"])

    if "rate_limits" in settings:
        anti_raid_system.rate_limits.update(settings["rate_limits"])

    return {"message": "Security settings updated successfully"}


# ============================================================
# PERFORMANCE MONITORING ENDPOINTS
# ============================================================

@router.get("/performance/report")
async def get_performance_report(
    current_user: User = Depends(require_admin)
):
    """Get comprehensive performance report"""
    from ..core.performance import get_performance_monitor

    monitor = get_performance_monitor()
    report = monitor.get_performance_report()

    return report


@router.get("/performance/endpoints")
async def get_endpoint_performance(
    current_user: User = Depends(require_admin),
    limit: int = Query(50, description="Number of endpoints to return"),
    sort_by: str = Query("avg_time", description="Sort by: avg_time, count, max_time")
):
    """Get endpoint performance statistics"""
    from ..core.performance import get_performance_monitor

    monitor = get_performance_monitor()

    # Sort endpoints by the specified metric
    endpoints = []
    for endpoint, stats in monitor.endpoint_stats.items():
        endpoints.append({
            "endpoint": endpoint,
            "requests_per_second": monitor._calculate_rps(endpoint),
            "avg_response_time": round(stats['avg_time'], 3),
            "min_response_time": round(stats['min_time'], 3),
            "max_response_time": round(stats['max_time'], 3),
            "total_requests": stats['count'],
            "status_codes": dict(stats['status_codes']),
            "slow_request_count": len(stats['slow_requests'])
        })

    # Sort the results
    reverse_sort = sort_by in ["count", "avg_time", "max_time"]
    endpoints.sort(key=lambda x: x[sort_by], reverse=reverse_sort)

    return {
        "endpoints": endpoints[:limit],
        "total_endpoints": len(endpoints)
    }


@router.get("/performance/database")
async def get_database_performance(
    current_user: User = Depends(require_admin),
    limit: int = Query(50, description="Number of queries to return")
):
    """Get database query performance statistics"""
    from ..core.performance import get_performance_monitor

    monitor = get_performance_monitor()

    queries = []
    for query, stats in monitor.db_query_stats.items():
        queries.append({
            "query": query[:200] + "..." if len(query) > 200 else query,
            "execution_count": stats['count'],
            "avg_time": round(stats['avg_time'], 4),
            "total_time": round(stats['total_time'], 2),
            "slow_query_count": len(stats['slow_queries'])
        })

    # Sort by average time (slowest first)
    queries.sort(key=lambda x: x['avg_time'], reverse=True)

    return {
        "queries": queries[:limit],
        "total_queries": len(queries)
    }


@router.get("/performance/cache")
async def get_cache_performance(
    current_user: User = Depends(require_admin)
):
    """Get cache performance statistics"""
    from ..core.performance import get_performance_monitor
    from ..core.cache import get_cache_manager

    monitor = get_performance_monitor()
    cache_manager = get_cache_manager()

    # Analyze cache performance
    from ..core.performance import CacheOptimizer
    optimizer = CacheOptimizer(cache_manager)
    analysis = await optimizer.analyze_cache_performance()

    return analysis


@router.get("/performance/optimization")
async def get_performance_optimization_suggestions(
    current_user: User = Depends(require_admin)
):
    """Get performance optimization suggestions"""
    from ..core.performance import get_performance_monitor
    from ..core.cache import get_cache_manager

    monitor = get_performance_monitor()
    cache_manager = get_cache_manager()

    # Get comprehensive analysis
    report = monitor.get_performance_report()

    # Database optimization analysis
    from ..core.performance import DatabaseOptimizer
    from ..core.database import engine
    db_optimizer = DatabaseOptimizer(engine)
    db_analysis = await db_optimizer.analyze_query_performance()

    # Cache optimization analysis
    from ..core.performance import CacheOptimizer
    cache_optimizer = CacheOptimizer(cache_manager)
    cache_analysis = await cache_optimizer.analyze_cache_performance()

    return {
        "overall_performance_score": calculate_performance_score(report),
        "critical_issues": get_critical_issues(report),
        "database_optimization": db_analysis,
        "cache_optimization": cache_analysis,
        "recommendations": report.get('recommendations', [])
    }


def calculate_performance_score(report: dict) -> float:
    """Calculate overall performance score (0-100)"""
    score = 100.0

    # Penalize for slow endpoints
    for endpoint, stats in report.get('endpoints', {}).items():
        if stats['avg_response_time'] > 2.0:
            score -= 10
        elif stats['avg_response_time'] > 1.0:
            score -= 5

    # Penalize for high error rates
    for endpoint, stats in report.get('endpoints', {}).items():
        total = stats['total_requests']
        errors = sum(count for code, count in stats['status_codes'].items() if code >= 400)
        if total > 0 and (errors / total) > 0.1:
            score -= 15

    # Penalize for low cache hit rates
    for cache_type, stats in report.get('cache', {}).items():
        if stats['hit_rate'] < 0.5:
            score -= 10

    return max(0.0, min(100.0, score))


def get_critical_issues(report: dict) -> list:
    """Identify critical performance issues"""
    issues = []

    # Check for very slow endpoints
    for endpoint, stats in report.get('endpoints', {}).items():
        if stats['avg_response_time'] > 5.0:
            issues.append(f"CRITICAL: {endpoint} is extremely slow ({stats['avg_response_time']:.2f}s avg)")

    # Check for high error rates
    for endpoint, stats in report.get('endpoints', {}).items():
        total = stats['total_requests']
        errors = sum(count for code, count in stats['status_codes'].items() if code >= 500)
        if total > 10 and (errors / total) > 0.2:
            issues.append(f"CRITICAL: {endpoint} has high 5xx error rate ({errors/total:.1%})")

    # Check for database issues
    for query, stats in report.get('database', {}).items():
        if stats['avg_time'] > 2.0:
            issues.append(f"CRITICAL: Database query is extremely slow ({stats['avg_time']:.3f}s avg)")

    return issues


@router.post("/performance/cache/clear")
async def clear_performance_cache(
    cache_type: Optional[str] = None,
    current_user: User = Depends(require_admin)
):
    """Clear performance cache (for testing or maintenance)"""
    from ..core.performance import get_performance_monitor

    monitor = get_performance_monitor()

    if cache_type == "request_times":
        monitor.request_times.clear()
    elif cache_type == "endpoint_stats":
        monitor.endpoint_stats.clear()
    elif cache_type == "db_query_stats":
        monitor.db_query_stats.clear()
    elif cache_type == "cache_stats":
        monitor.cache_stats.clear()
    else:
        # Clear all
        monitor.request_times.clear()
        monitor.endpoint_stats.clear()
        monitor.db_query_stats.clear()
        monitor.cache_stats.clear()

    return {"message": f"Performance cache cleared: {cache_type or 'all'}"}


@router.post("/performance/cache/warmup")
async def warmup_performance_cache(
    current_user: User = Depends(require_admin)
):
    """Warm up performance-related caches"""
    from ..core.cache import get_cache_warmer

    warmer = get_cache_warmer()
    await warmer.warmup_all()

    return {"message": "Performance cache warmup completed"}


# ============================================================
# MONITORING & BACKUP ENDPOINTS
# ============================================================

@router.get("/monitoring/report")
async def get_monitoring_report(
    current_user: User = Depends(require_admin)
):
    """Get comprehensive monitoring report"""
    from ..core.monitoring import get_monitoring_system

    monitoring_system = get_monitoring_system()
    report = monitoring_system.get_monitoring_report()

    return report


@router.get("/monitoring/health")
async def get_health_status(
    current_user: User = Depends(require_admin)
):
    """Get system health status"""
    from ..core.monitoring import get_monitoring_system

    monitoring_system = get_monitoring_system()
    health_results = await monitoring_system.health.run_all_checks()

    return health_results


@router.get("/monitoring/alerts")
async def get_active_alerts(
    current_user: User = Depends(require_admin)
):
    """Get active monitoring alerts"""
    from ..core.monitoring import get_monitoring_system

    monitoring_system = get_monitoring_system()
    alerts = monitoring_system.alerts.get_active_alerts()

    return {"alerts": alerts, "count": len(alerts)}


@router.post("/monitoring/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    current_user: User = Depends(require_admin)
):
    """Resolve a monitoring alert"""
    from ..core.monitoring import get_monitoring_system

    monitoring_system = get_monitoring_system()
    monitoring_system.alerts.resolve_alert(alert_id)

    return {"message": "Alert resolved", "alert_id": alert_id}


@router.get("/backups")
async def list_backups(
    current_user: User = Depends(require_admin)
):
    """List all available backups"""
    from ..core.backup import list_available_backups

    backups = list_available_backups()
    return {"backups": backups, "count": len(backups)}


@router.post("/backups/database")
async def create_database_backup(
    current_user: User = Depends(require_admin)
):
    """Create database backup"""
    from ..core.backup import get_backup_manager

    backup_manager = get_backup_manager()
    backup_path = await backup_manager.create_database_backup()

    if backup_path:
        return {"message": "Database backup created", "path": backup_path}
    else:
        raise HTTPException(status_code=500, detail="Database backup failed")


@router.post("/backups/files")
async def create_file_backup(
    current_user: User = Depends(require_admin)
):
    """Create file system backup"""
    from ..core.backup import get_backup_manager

    backup_manager = get_backup_manager()
    backup_path = await backup_manager.create_file_backup()

    if backup_path:
        return {"message": "File backup created", "path": backup_path}
    else:
        raise HTTPException(status_code=500, detail="File backup failed")


@router.post("/backups/full")
async def create_full_backup(
    current_user: User = Depends(require_admin)
):
    """Create full system backup"""
    from ..core.backup import get_backup_manager

    backup_manager = get_backup_manager()
    backup_path = await backup_manager.create_full_backup()

    if backup_path:
        return {"message": "Full backup created", "path": backup_path}
    else:
        raise HTTPException(status_code=500, detail="Full backup failed")


@router.post("/backups/{backup_name}/restore")
async def restore_backup(
    backup_name: str,
    restore_type: str = "database",
    current_user: User = Depends(require_admin)
):
    """Restore from backup"""
    from ..core.backup import get_backup_manager

    backup_manager = get_backup_manager()
    success = await backup_manager.restore_backup(backup_name, restore_type)

    if success:
        return {"message": f"Backup restored successfully", "backup": backup_name, "type": restore_type}
    else:
        raise HTTPException(status_code=500, detail="Backup restore failed")


@router.post("/backups/{backup_name}/verify")
async def verify_backup(
    backup_name: str,
    current_user: User = Depends(require_admin)
):
    """Verify backup integrity"""
    from ..core.backup import get_backup_manager

    backup_manager = get_backup_manager()
    verification = await backup_manager.verify_backup(backup_name)

    return {"backup": backup_name, "verification": verification}


@router.delete("/backups/old")
async def cleanup_old_backups(
    current_user: User = Depends(require_admin)
):
    """Clean up old backups"""
    from ..core.backup import get_backup_manager

    backup_manager = get_backup_manager()
    await backup_manager.cleanup_old_backups()

    return {"message": "Old backups cleaned up"}


@router.get("/disaster-recovery/plan")
async def get_recovery_plan(
    current_user: User = Depends(require_admin)
):
    """Get disaster recovery plan"""
    from ..core.backup import get_disaster_recovery

    dr_system = get_disaster_recovery()
    plan = await dr_system.create_recovery_plan()

    return plan


@router.post("/disaster-recovery/execute")
async def execute_disaster_recovery(
    recovery_type: str,
    backup_name: Optional[str] = None,
    current_user: User = Depends(require_admin)
):
    """Execute disaster recovery"""
    from ..core.backup import get_disaster_recovery

    dr_system = get_disaster_recovery()
    result = await dr_system.execute_recovery(recovery_type, backup_name)

    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=500, detail=f"Recovery failed: {result.get('error', 'Unknown error')}")