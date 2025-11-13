"""
Workplace Service API Router
Cross-platform workplace management endpoints.

Endpoints organized by category:
- Synchronization APIs
- User Management APIs
- Project Management APIs
- Time Tracking APIs
- Task Management APIs
- Billing APIs
- Analytics APIs
- AI Integration APIs
- Real-time Collaboration APIs
"""

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import uuid

# Database and auth dependencies
from ..core.database import get_db
from ..core.auth import get_current_user
from ..models.user import User
from ..models.project import Project

# Workplace models and schemas
from ..models.workplace import (
    Workspace, WorkspaceMember, SyncEvent, Task, TimeLog,
    LiveSession, CodeReview, Payment, _user_has_workspace_access
)
from ..schemas.workplace import (
    PlatformUpdate, SyncHistoryResponse, SyncEventResponse,
    WorkspaceInvitation, InviteUserResponse,
    SmartTimeLogRequest, SmartTimeLogResponse,
    SmartAssignmentRequest, SmartAssignmentResponse,
    AutoBillingRequest, AutoBillingResponse, BillingInvoice,
    PredictiveAnalyticsResponse,
    WorkflowOptimizationRequest, WorkflowOptimizationResponse,
    VoiceContextRequest, VoiceContextResponse,
    LiveSessionRequest, LiveSessionResponse,
    CodeReviewRequest, CodeReviewResponse,
    WorkspaceResponse, WorkspaceMemberResponse, TaskResponse,
    Platform, EventType, TaskStatus, TaskPriority, TaskComplexity, MemberRole
)

# Workplace services
from ..services.workplace import (
    WebSocketManager, AIService, NotificationService, SyncService,
    websocket_manager, ai_service, notification_service, sync_service
)

# Create router
router = APIRouter(prefix="/workplace", tags=["Workplace Service"])


# ============================================================================
# SYNCHRONIZATION APIs
# ============================================================================

@router.post("/sync/broadcast")
async def broadcast_platform_update(
    update: PlatformUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Broadcast updates across platforms in real-time
    """
    # Validate user has workspace access
    workspace = db.query(Workspace).filter(Workspace.id == update.workspace_id).first()
    if not workspace or not _user_has_workspace_access(db, current_user.id, workspace.id):
        raise HTTPException(status_code=403, detail="Access denied")

    # Create sync event
    sync_event = SyncEvent(
        event_type=update.event_type,
        payload=update.payload,
        source_platform=update.source_platform,
        target_platforms=update.target_platforms,
        workspace_id=update.workspace_id,
        user_id=current_user.id
    )

    db.add(sync_event)
    db.commit()

    # Broadcast to connected platforms via WebSocket
    await websocket_manager.broadcast_to_workspace(
        workspace.id,
        {
            "type": "sync_event",
            "event": sync_event.event_type,
            "payload": sync_event.payload,
            "source": sync_event.source_platform,
            "timestamp": sync_event.created_at.isoformat()
        }
    )

    # Send push notifications if configured
    if update.notify_users:
        await notification_service.send_workspace_notification(
            workspace.id,
            update.event_type,
            update.payload
        )

    return {"status": "broadcasted", "event_id": sync_event.id}


@router.get("/sync/history", response_model=SyncHistoryResponse)
async def get_sync_history(
    workspace_id: int,
    event_type: Optional[str] = None,
    source_platform: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get synchronization history for auditing and debugging
    """
    # Validate access
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace or not _user_has_workspace_access(db, current_user.id, workspace.id):
        raise HTTPException(status_code=403, detail="Access denied")

    query = db.query(SyncEvent).filter(SyncEvent.workspace_id == workspace_id)

    if event_type:
        query = query.filter(SyncEvent.event_type == event_type)
    if source_platform:
        query = query.filter(SyncEvent.source_platform == source_platform)
    if start_date:
        query = query.filter(SyncEvent.created_at >= start_date)
    if end_date:
        query = query.filter(SyncEvent.created_at <= end_date)

    events = query.order_by(SyncEvent.created_at.desc()).offset(skip).limit(limit).all()

    return {
        "workspace_id": workspace_id,
        "events": [
            {
                "id": event.id,
                "event_type": event.event_type,
                "source_platform": event.source_platform,
                "target_platforms": event.target_platforms,
                "payload": event.payload,
                "user_id": event.user_id,
                "timestamp": event.created_at.isoformat()
            }
            for event in events
        ],
        "total": query.count()
    }


# ============================================================================
# USER MANAGEMENT APIs
# ============================================================================

@router.post("/users/{user_id}/workspaces/{workspace_id}/invite", response_model=InviteUserResponse)
async def invite_user_to_workspace(
    user_id: int,
    workspace_id: int,
    invitation: WorkspaceInvitation,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Invite user to workspace with platform-specific permissions
    """
    # Validate inviter has permission
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    if workspace.owner_id != current_user.id:
        member = db.query(WorkspaceMember).filter(
            db.and_(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == current_user.id,
                WorkspaceMember.role.in_(["admin", "owner"])
            )
        ).first()
        if not member:
            raise HTTPException(status_code=403, detail="Not authorized to invite users")

    # Check if user already exists
    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if already a member
    existing_member = db.query(WorkspaceMember).filter(
        db.and_(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id
        )
    ).first()
    if existing_member:
        raise HTTPException(status_code=400, detail="User is already a workspace member")

    # Create workspace membership
    member = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=user_id,
        role=invitation.role,
        can_create_projects=invitation.can_create_projects,
        can_review_applications=invitation.can_review_applications,
        can_post_jobs=invitation.can_post_jobs,
        platform_permissions=invitation.platform_permissions
    )

    db.add(member)
    db.commit()

    # Send invitation notification
    await notification_service.send_invitation_notification(
        user_id, workspace_id, invitation.invitation_message
    )

    return {
        "message": "User invited to workspace",
        "workspace": workspace.name,
        "role": invitation.role,
        "platform_permissions": invitation.platform_permissions
    }


# ============================================================================
# PROJECT MANAGEMENT APIs
# ============================================================================

@router.post("/projects/{project_id}/ai-insights")
async def get_project_ai_insights(
    project_id: int,
    insight_type: str = Query("general", enum=["general", "risk", "resource", "timeline"]),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered insights for project optimization
    """
    # Validate access
    project = db.query(Project).join(Workspace).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    workspace = project.workspace
    if not _user_has_workspace_access(db, current_user.id, workspace.id):
        raise HTTPException(status_code=403, detail="Access denied")

    # Gather project data for AI analysis
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    time_logs = db.query(TimeLog).join(Task).filter(Task.project_id == project_id).all()
    team_members = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace.id
    ).all()

    project_data = {
        "project": {
            "id": project.id,
            "name": project.name,
            "budget": getattr(project, 'budget', None),
            "deadline": getattr(project, 'end_date', None).isoformat() if getattr(project, 'end_date', None) else None,
            "status": project.status
        },
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "priority": task.priority,
                "assignee_id": task.assignee_id,
                "hours_estimate": task.hours_estimate,
                "hours_logged": task.hours_logged
            }
            for task in tasks
        ],
        "time_logs": [
            {
                "task_id": log.task_id,
                "user_id": log.user_id,
                "hours": log.hours,
                "date": log.work_date.isoformat()
            }
            for log in time_logs
        ],
        "team": [
            {
                "user_id": member.user_id,
                "role": member.role,
                "skills": member.skills or []
            }
            for member in team_members
        ]
    }

    # Get AI insights based on type
    if insight_type == "risk":
        insights = await ai_service.analyze_project_risks(project_data)
    elif insight_type == "resource":
        insights = await ai_service.optimize_resource_allocation(project_data)
    elif insight_type == "timeline":
        insights = await ai_service.predict_project_timeline(project_data)
    else:
        insights = await ai_service.generate_project_insights(project_data)

    return {
        "project_id": project_id,
        "insight_type": insight_type,
        "insights": insights,
        "generated_at": datetime.utcnow().isoformat(),
        "confidence_score": insights.get("confidence", 0.8)
    }


# ============================================================================
# TIME TRACKING APIs
# ============================================================================

@router.post("/time/smart-log", response_model=SmartTimeLogResponse)
async def smart_time_logging(
    log_request: SmartTimeLogRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Intelligent time logging with automatic categorization
    """
    # Analyze the time log description with AI
    analysis = await ai_service.analyze_time_log_description(log_request.description)

    # Auto-determine task if not specified
    task_id = log_request.task_id
    if not task_id and analysis.get("suggested_task"):
        # Find matching task in user's projects
        suggested_task = db.query(Task).filter(
            db.and_(
                Task.title.ilike(f"%{analysis['suggested_task']}%"),
                Task.project_id.in_([p.id for p in db.query(Project).filter(
                    db.or_(
                        Project.user_id == current_user.id,
                        Project.id.in_([
                            wm.workspace_id for wm in db.query(WorkspaceMember).filter(
                                WorkspaceMember.user_id == current_user.id
                            ).all()
                        ])
                    )
                ).all()])
            )
        ).first()
        if suggested_task:
            task_id = suggested_task.id

    # Auto-determine project if not specified
    project_id = log_request.project_id
    if not project_id and task_id:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            project_id = task.project_id

    # Auto-categorize activity
    category = analysis.get("category", "development")
    billable = analysis.get("billable", True)

    # Create time log
    time_log = TimeLog(
        task_id=task_id,
        user_id=current_user.id,
        hours=log_request.hours,
        work_date=log_request.work_date or datetime.utcnow().date(),
        description=log_request.description,
        category=category,
        billable=billable,
        auto_categorized=True,
        ai_analysis=analysis
    )

    # Calculate amount (mock calculation)
    hourly_rate = 50.0  # Would get from user settings
    time_log.total_amount = time_log.hours * hourly_rate

    db.add(time_log)
    db.commit()

    # Update task hours if task exists
    if task_id:
        task = db.query(Task).filter(Task.id == task_id).first()
        if task:
            # Recalculate hours logged
            total_hours = db.query(db.func.sum(TimeLog.hours)).filter(
                TimeLog.task_id == task_id
            ).scalar() or 0
            task.hours_logged = total_hours
            db.commit()

    # Sync across platforms
    await sync_service.broadcast_time_log_update(time_log, current_user.id)

    return {
        "time_log_id": time_log.id,
        "task_id": task_id,
        "project_id": project_id,
        "hours": time_log.hours,
        "category": category,
        "billable": billable,
        "amount": time_log.total_amount,
        "auto_categorized": True,
        "ai_insights": analysis
    }


# ============================================================================
# TASK MANAGEMENT APIs
# ============================================================================

@router.post("/tasks/smart-assign", response_model=SmartAssignmentResponse)
async def smart_task_assignment(
    assignment_request: SmartAssignmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI-powered task assignment with skill matching and workload balancing
    """
    # Validate task exists and user has access
    task = db.query(Task).join(Project).join(Workspace).filter(Task.id == assignment_request.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    workspace = task.project.workspace
    if not _user_has_workspace_access(db, current_user.id, workspace.id):
        raise HTTPException(status_code=403, detail="Access denied")

    # Get available team members
    team_members = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace.id
    ).all()

    # Gather team member data for AI analysis
    team_data = []
    for member in team_members:
        user = db.query(User).filter(User.id == member.user_id).first()
        if user:
            # Get current workload
            current_tasks = db.query(Task).filter(
                db.and_(
                    Task.assignee_id == user.id,
                    Task.status.in_(["backlog", "in_progress"])
                )
            ).all()

            workload_hours = sum(t.hours_estimate or 0 for t in current_tasks)

            team_data.append({
                "user_id": user.id,
                "name": user.full_name or user.username,
                "role": member.role,
                "skills": member.skills or [],
                "current_workload": workload_hours,
                "availability": member.availability_status or "available",
                "performance_score": member.performance_score or 5.0
            })

    # AI-powered assignment analysis
    assignment_analysis = await ai_service.analyze_task_assignment({
        "task": {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "hours_estimate": task.hours_estimate,
            "required_skills": task.required_skills or [],
            "complexity": task.complexity or "medium"
        },
        "team": team_data,
        "assignment_criteria": assignment_request.criteria or {}
    })

    # Apply assignment if confidence is high enough
    recommended_assignee = assignment_analysis.get("recommended_assignee")
    confidence = assignment_analysis.get("confidence", 0)

    if confidence >= 0.7 and recommended_assignee:
        # Update task assignment
        task.assignee_id = recommended_assignee["user_id"]
        task.assigned_at = datetime.utcnow()
        task.assignment_method = "ai_recommended"

        db.commit()

        # Send notification
        await notification_service.send_task_assignment_notification(
            task.id, recommended_assignee["user_id"]
        )

        # Sync across platforms
        await sync_service.broadcast_task_update(task.id, "assigned")

    return {
        "task_id": task.id,
        "analysis": assignment_analysis,
        "assignment_made": confidence >= 0.7,
        "assignee": recommended_assignee if confidence >= 0.7 else None,
        "alternatives": assignment_analysis.get("alternatives", []),
        "reasoning": assignment_analysis.get("reasoning", "")
    }


# ============================================================================
# BILLING APIs
# ============================================================================

@router.post("/billing/auto-generate", response_model=AutoBillingResponse)
async def auto_generate_billing(
    billing_request: AutoBillingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI-powered automatic billing generation and optimization
    """
    # Validate workspace access
    workspace = db.query(Workspace).filter(Workspace.id == billing_request.workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    if workspace.owner_id != current_user.id:
        member = db.query(WorkspaceMember).filter(
            db.and_(
                WorkspaceMember.workspace_id == billing_request.workspace_id,
                WorkspaceMember.user_id == current_user.id,
                WorkspaceMember.role.in_(["admin", "owner"])
            )
        ).first()
        if not member:
            raise HTTPException(status_code=403, detail="Not authorized to generate billing")

    # Gather billing data
    start_date = billing_request.start_date or datetime.utcnow().replace(day=1)
    end_date = billing_request.end_date or datetime.utcnow()

    # Get time logs for billing period
    time_logs = db.query(TimeLog).join(Task).join(Project).filter(
        db.and_(
            Project.workspace_id == billing_request.workspace_id,
            TimeLog.work_date >= start_date,
            TimeLog.work_date <= end_date,
            TimeLog.billable == True
        )
    ).all()

    # Group by project and user
    billing_data = {}
    for log in time_logs:
        project_id = log.task.project_id
        user_id = log.user_id

        key = f"{project_id}_{user_id}"
        if key not in billing_data:
            billing_data[key] = {
                "project_id": project_id,
                "project_name": log.task.project.name,
                "user_id": user_id,
                "user_name": log.user.full_name or "Unknown",
                "hours": 0,
                "amount": 0,
                "tasks": set()
            }

        billing_data[key]["hours"] += log.hours
        billing_data[key]["amount"] += log.total_amount
        billing_data[key]["tasks"].add(log.task.title)

    # AI-powered billing optimization
    optimization = await ai_service.optimize_billing_structure({
        "billing_period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "billing_items": list(billing_data.values()),
        "workspace_settings": {
            "billing_cycle": workspace.billing_cycle or "monthly",
            "tax_rate": workspace.tax_rate or 0,
            "currency": workspace.currency or "USD"
        }
    })

    # Generate invoices
    invoices = []
    for item in optimization["optimized_items"]:
        invoice = Payment(
            user_id=item["user_id"],
            workspace_id=billing_request.workspace_id,
            amount=item["optimized_amount"],
            currency=workspace.currency or "USD",
            period_start=start_date,
            period_end=end_date,
            description=f"Billing for {item['project_name']} - {item['hours']} hours",
            auto_generated=True,
            billing_data=item
        )

        db.add(invoice)
        invoices.append(invoice)

    db.commit()

    return {
        "workspace_id": billing_request.workspace_id,
        "billing_period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "invoices_generated": len(invoices),
        "total_amount": sum(inv.amount for inv in invoices),
        "optimization_insights": optimization["insights"],
        "invoices": [
            {
                "id": inv.id,
                "user_id": inv.user_id,
                "amount": inv.amount,
                "description": inv.description
            }
            for inv in invoices
        ]
    }


# ============================================================================
# ANALYTICS APIs
# ============================================================================

@router.get("/analytics/predictive", response_model=PredictiveAnalyticsResponse)
async def get_predictive_analytics(
    workspace_id: int,
    prediction_type: str = Query("project_completion", enum=["project_completion", "team_performance", "resource_needs"]),
    timeframe_days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get predictive analytics for workspace optimization
    """
    # Validate access
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    if not _user_has_workspace_access(db, current_user.id, workspace.id):
        raise HTTPException(status_code=403, detail="Access denied")

    # Gather historical data for prediction
    end_date = datetime.utcnow()
    start_date = end_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)  # Start of month

    # Get projects data
    projects = db.query(Project).filter(
        db.and_(
            Project.user_id.in_([wm.user_id for wm in db.query(WorkspaceMember).filter(
                WorkspaceMember.workspace_id == workspace_id
            ).all()]),
            Project.created_at >= start_date
        )
    ).all()

    # Get tasks data
    tasks = db.query(Task).join(Project).filter(
        db.and_(
            Project.user_id.in_([wm.user_id for wm in db.query(WorkspaceMember).filter(
                WorkspaceMember.workspace_id == workspace_id
            ).all()]),
            Task.created_at >= start_date
        )
    ).all()

    # Get time logs data
    time_logs = db.query(TimeLog).join(Task).join(Project).filter(
        db.and_(
            Project.user_id.in_([wm.user_id for wm in db.query(WorkspaceMember).filter(
                WorkspaceMember.workspace_id == workspace_id
            ).all()]),
            TimeLog.work_date >= start_date
        )
    ).all()

    # Get team member data
    team_members = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id
    ).all()

    # Prepare data for AI analysis
    analytics_data = {
        "workspace": {
            "id": workspace.id,
            "name": workspace.name,
            "created_at": workspace.created_at.isoformat(),
            "member_count": len(team_members)
        },
        "projects": [
            {
                "id": p.id,
                "name": p.name,
                "status": p.status,
                "budget": getattr(p, 'budget', None),
                "created_at": p.created_at.isoformat(),
                "deadline": getattr(p, 'end_date', None).isoformat() if getattr(p, 'end_date', None) else None,
                "completion_percentage": 0.5  # Mock completion
            }
            for p in projects
        ],
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "priority": t.priority,
                "project_id": t.project_id,
                "assignee_id": t.assignee_id,
                "hours_estimate": t.hours_estimate,
                "hours_logged": t.hours_logged,
                "created_at": t.created_at.isoformat()
            }
            for t in tasks
        ],
        "time_logs": [
            {
                "task_id": tl.task_id,
                "user_id": tl.user_id,
                "hours": tl.hours,
                "date": tl.work_date.isoformat(),
                "billable": tl.billable
            }
            for tl in time_logs
        ],
        "team": [
            {
                "user_id": m.user_id,
                "role": m.role,
                "join_date": m.joined_at.isoformat(),
                "performance_score": m.performance_score or 5.0
            }
            for m in team_members
        ],
        "prediction_request": {
            "type": prediction_type,
            "timeframe_days": timeframe_days,
            "end_date": end_date.isoformat()
        }
    }

    # Get AI-powered predictions
    if prediction_type == "project_completion":
        predictions = await ai_service.predict_project_completion(analytics_data)
    elif prediction_type == "team_performance":
        predictions = await ai_service.predict_team_performance(analytics_data)
    elif prediction_type == "resource_needs":
        predictions = await ai_service.predict_resource_needs(analytics_data)
    else:
        predictions = await ai_service.generate_general_predictions(analytics_data)

    return {
        "workspace_id": workspace_id,
        "prediction_type": prediction_type,
        "timeframe_days": timeframe_days,
        "generated_at": datetime.utcnow().isoformat(),
        "predictions": predictions,
        "confidence_levels": predictions.get("confidence_levels", {}),
        "recommendations": predictions.get("recommendations", []),
        "risk_factors": predictions.get("risk_factors", [])
    }


# ============================================================================
# AI INTEGRATION APIs
# ============================================================================

@router.post("/ai/optimize-workflow", response_model=WorkflowOptimizationResponse)
async def optimize_workflow(
    optimization_request: WorkflowOptimizationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI-powered workflow optimization for projects and teams
    """
    # Validate workspace access
    workspace = db.query(Workspace).filter(Workspace.id == optimization_request.workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    if not _user_has_workspace_access(db, current_user.id, workspace.id):
        raise HTTPException(status_code=403, detail="Access denied")

    # Gather workflow data
    projects = db.query(Project).filter(Project.user_id.in_([
        wm.user_id for wm in db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == optimization_request.workspace_id
        ).all()
    ])).all()

    tasks = db.query(Task).join(Project).filter(Project.user_id.in_([
        wm.user_id for wm in db.query(WorkspaceMember).filter(
            WorkspaceMember.workspace_id == optimization_request.workspace_id
        ).all()
    ])).all()

    team_members = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == optimization_request.workspace_id
    ).all()

    workflow_data = {
        "workspace": {
            "id": workspace.id,
            "name": workspace.name,
            "workflow_type": workspace.workflow_type or "kanban"
        },
        "projects": [
            {
                "id": p.id,
                "name": p.name,
                "status": p.status,
                "tasks_count": len([t for t in tasks if t.project_id == p.id]),
                "completion_rate": 0.5  # Mock completion rate
            }
            for p in projects
        ],
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "priority": t.priority,
                "assignee_id": t.assignee_id,
                "hours_estimate": t.hours_estimate,
                "hours_logged": t.hours_logged,
                "blockers": t.blockers or []
            }
            for t in tasks
        ],
        "team": [
            {
                "user_id": m.user_id,
                "role": m.role,
                "current_tasks": len([t for t in tasks if t.assignee_id == m.user_id and t.status == "in_progress"]),
                "workload_capacity": m.workload_capacity or 40
            }
            for m in team_members
        ],
        "optimization_focus": optimization_request.focus_areas or ["bottlenecks", "resource_allocation", "timeline"],
        "constraints": optimization_request.constraints or {}
    }

    # Get AI optimization recommendations
    optimization = await ai_service.optimize_workflow(workflow_data)

    # Apply automatic optimizations if requested
    applied_changes = []
    if optimization_request.apply_changes:
        # Mock applying changes - would implement actual workflow updates
        applied_changes = [
            {"type": "task_reassignment", "description": "Reassigned 2 tasks for better load balancing"},
            {"type": "priority_update", "description": "Updated priority for 3 high-impact tasks"}
        ]

    return {
        "workspace_id": optimization_request.workspace_id,
        "optimization_focus": optimization_request.focus_areas,
        "recommendations": optimization["recommendations"],
        "expected_improvements": optimization["expected_improvements"],
        "implementation_plan": optimization["implementation_plan"],
        "applied_changes": applied_changes,
        "generated_at": datetime.utcnow().isoformat()
    }


# ============================================================================
# REAL-TIME COLLABORATION APIs
# ============================================================================

@router.websocket("/ws/{workspace_id}/{user_id}")
async def workspace_collaboration_websocket(
    websocket: WebSocket,
    workspace_id: int,
    user_id: int,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time workspace collaboration
    """
    # Validate token and workspace access (mock validation)
    try:
        # In production, validate JWT token
        if not token:  # Mock check
            await websocket.close(code=4001)
            return
    except:
        await websocket.close(code=4001)
        return

    # Validate workspace access
    if not _user_has_workspace_access(db, user_id, workspace_id):
        await websocket.close(code=4003)
        return

    await websocket_manager.connect(websocket, workspace_id, user_id)

    try:
        while True:
            # Receive message
            data = await websocket.receive_json()

            # Process message based on type
            message_type = data.get("type")

            if message_type == "task_update":
                # Handle task update
                await websocket_manager.broadcast_to_workspace(
                    workspace_id,
                    {
                        "type": "task_updated",
                        "task_id": data.get("task_id"),
                        "updates": data.get("updates"),
                        "user_id": user_id,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    exclude_user=user_id
                )
            elif message_type == "cursor_position":
                # Handle cursor position updates
                await websocket_manager.broadcast_to_workspace(
                    workspace_id,
                    {
                        "type": "cursor_update",
                        "user_id": user_id,
                        "position": data.get("position"),
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    exclude_user=user_id
                )
            elif message_type == "presence_ping":
                # Handle presence ping
                await websocket_manager.broadcast_to_workspace(
                    workspace_id,
                    {
                        "type": "user_presence",
                        "user_id": user_id,
                        "status": "active",
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    exclude_user=user_id
                )
            elif message_type == "voice_command":
                # Handle voice commands
                await websocket_manager.broadcast_to_workspace(
                    workspace_id,
                    {
                        "type": "voice_command_broadcast",
                        "user_id": user_id,
                        "command": data.get("command"),
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    exclude_user=user_id
                )
            else:
                # Echo message to all workspace members
                await websocket_manager.broadcast_to_workspace(
                    workspace_id,
                    {
                        "type": "message",
                        "from_user": user_id,
                        "content": data,
                        "timestamp": datetime.utcnow().isoformat()
                    },
                    exclude_user=user_id
                )

    except WebSocketDisconnect:
        websocket_manager.disconnect(workspace_id, user_id)
        # Broadcast user left
        await websocket_manager.broadcast_to_workspace(
            workspace_id,
            {
                "type": "user_left",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )


# ============================================================================
# PLATFORM-SPECIFIC APIs
# ============================================================================

@router.post("/voice/context", response_model=VoiceContextResponse)
async def get_voice_context(
    context_request: VoiceContextRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get contextual information for voice interactions
    """
    # Mock implementation - would gather actual user context
    workspaces = db.query(WorkspaceMember).filter(
        WorkspaceMember.user_id == current_user.id
    ).all()

    active_projects = db.query(Project).filter(
        Project.user_id == current_user.id
    ).limit(5).all()

    current_tasks = db.query(Task).filter(
        db.and_(
            Task.assignee_id == current_user.id,
            Task.status.in_(["in_progress", "review"])
        )
    ).limit(5).all()

    team_members = db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id.in_([wm.workspace_id for wm in workspaces])
    ).limit(10).all()

    # Mock recent activity
    recent_activity = [
        {"type": "task_completed", "description": "Completed task review", "timestamp": datetime.utcnow().isoformat()},
        {"type": "time_logged", "description": "Logged 2 hours on project", "timestamp": datetime.utcnow().isoformat()}
    ]

    ai_preferences = {
        "voice_enabled": True,
        "response_style": "concise",
        "auto_complete_tasks": False
    }

    return {
        "user_context": {
            "current_workspace": workspaces[0].workspace if workspaces else None,
            "active_projects": [{"id": p.id, "name": p.name} for p in active_projects],
            "current_tasks": [{"id": t.id, "title": t.title, "status": t.status} for t in current_tasks],
            "team_members": [{"id": tm.user_id, "role": tm.role} for tm in team_members],
            "recent_activity": recent_activity
        },
        "ai_preferences": ai_preferences,
        "workspace_settings": {
            "default_project": active_projects[0].id if active_projects else None,
            "working_hours": "9-17",
            "timezone": "UTC",
            "voice_commands_enabled": True
        },
        "generated_at": datetime.utcnow().isoformat()
    }


@router.post("/collaboration/live-session", response_model=LiveSessionResponse)
async def start_live_session(
    session_request: LiveSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start live collaboration session for visual editing
    """
    # Validate project access
    project = db.query(Project).filter(Project.id == session_request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Mock workspace check
    workspace_id = 1  # Would determine from project
    if not _user_has_workspace_access(db, current_user.id, workspace_id):
        raise HTTPException(status_code=403, detail="Access denied")

    # Create live session
    session_id = str(uuid.uuid4())
    live_session = LiveSession(
        id=session_id,
        project_id=session_request.project_id,
        created_by=current_user.id,
        session_type=session_request.session_type,
        max_participants=session_request.max_participants or 10,
        is_active=True,
        participants=[current_user.id]
    )

    db.add(live_session)
    db.commit()

    # Broadcast session start
    await websocket_manager.broadcast_to_workspace(
        workspace_id,
        {
            "type": "live_session_started",
            "session_id": session_id,
            "project_id": session_request.project_id,
            "session_type": session_request.session_type,
            "started_by": current_user.id,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

    # Register with websocket manager
    websocket_manager.create_live_session(
        session_id, session_request.project_id, workspace_id, session_request.session_type.value
    )
    websocket_manager.add_to_live_session(session_id, current_user.id)

    return {
        "session_id": session_id,
        "project_id": session_request.project_id,
        "session_type": session_request.session_type,
        "max_participants": live_session.max_participants,
        "participants": live_session.participants,
        "websocket_url": f"/ws/workplace/live-session/{session_id}",
        "started_at": live_session.created_at.isoformat()
    }


@router.post("/code/review/request", response_model=CodeReviewResponse)
async def request_code_review(
    review_request: CodeReviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request AI-assisted code review for development work
    """
    # Validate project access
    project = db.query(Project).filter(Project.id == review_request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Mock workspace check
    workspace_id = 1  # Would determine from project
    if not _user_has_workspace_access(db, current_user.id, workspace_id):
        raise HTTPException(status_code=403, detail="Access denied")

    # Analyze code with AI
    code_analysis = await ai_service.analyze_code(
        review_request.code_content,
        review_request.language,
        review_request.context
    )

    # Generate review feedback
    review_feedback = await ai_service.generate_code_review(
        code_analysis,
        review_request.review_type,
        review_request.severity_level
    )

    # Create review record
    code_review = CodeReview(
        project_id=review_request.project_id,
        requested_by=current_user.id,
        code_content=review_request.code_content,
        language=review_request.language,
        review_type=review_request.review_type,
        ai_analysis=code_analysis,
        ai_feedback=review_feedback,
        status="completed",
        severity_level=review_request.severity_level
    )

    db.add(code_review)
    db.commit()

    # Send notifications to reviewers (mock)
    reviewers = [current_user.id]  # Would find actual reviewers
    await notification_service.send_code_review_notification(
        code_review.id, reviewers, current_user.id
    )

    return {
        "review_id": code_review.id,
        "analysis": code_analysis,
        "feedback": review_feedback,
        "recommendations": review_feedback.get("recommendations", []),
        "severity_breakdown": review_feedback.get("severity_breakdown", {}),
        "estimated_effort": review_feedback.get("estimated_fix_effort", "unknown"),
        "generated_at": datetime.utcnow().isoformat()
    }
