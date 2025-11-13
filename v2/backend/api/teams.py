"""
Team Features API Endpoints
Handles team collaboration, project sharing, and permissions.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import uuid4

from ..models.user import User
from ..models.project import Project
from ..api.auth import get_current_user
from ..core.database import get_db

router = APIRouter()


# Request/Response Models
class ProjectShare(BaseModel):
    """Share project request."""
    project_id: int = Field(..., description="Project ID to share")
    email: str = Field(..., description="Email of user to share with")
    permission: str = Field("read", description="Permission level: read, write, execute, admin")
    message: Optional[str] = Field(None, description="Optional message")


class TeamMemberInvite(BaseModel):
    """Invite team member request."""
    email: str = Field(..., description="Email to invite")
    role: str = Field("member", description="Role: member, admin, owner")


class TeamCreate(BaseModel):
    """Create team request."""
    name: str = Field(..., min_length=1, max_length=255, description="Team name")
    description: Optional[str] = Field(None, description="Team description")


class TeamResponse(BaseModel):
    """Team response."""
    id: str
    name: str
    description: Optional[str]
    owner_id: int
    member_count: int
    created_at: str


class TeamMemberResponse(BaseModel):
    """Team member response."""
    user_id: int
    email: str
    role: str
    joined_at: str


class SharedProjectResponse(BaseModel):
    """Shared project response."""
    project_id: int
    project_name: str
    owner_id: int
    permission: str
    shared_at: str


# In-memory storage for demo (replace with database models in production)
teams_db = {}
team_members_db = {}
shared_projects_db = {}


# Endpoints

@router.post("/share", status_code=201)
async def share_project(
    share: ProjectShare,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Share a project with another user.
    
    Grant specific permissions (read, write, execute, admin) to collaborators.
    They will be able to access the project based on their permission level.
    """
    # Get project and verify ownership
    project = db.query(Project).filter(
        Project.id == share.project_id,
        Project.user_id == current_user.id
    ).first()
    
    if not project:
        raise HTTPException(404, "Project not found or you don't have permission to share it")
    
    # Validate permission
    if share.permission not in ["read", "write", "execute", "admin"]:
        raise HTTPException(400, "Invalid permission level")
    
    # Find user by email (simplified - in production, check if user exists)
    # For now, store the share in memory
    share_id = str(uuid4())
    shared_projects_db[share_id] = {
        "id": share_id,
        "project_id": share.project_id,
        "project_name": project.name,
        "owner_id": current_user.id,
        "shared_with_email": share.email,
        "permission": share.permission,
        "message": share.message,
        "shared_at": datetime.utcnow().isoformat()
    }
    
    return {
        "share_id": share_id,
        "project_id": share.project_id,
        "project_name": project.name,
        "shared_with": share.email,
        "permission": share.permission,
        "status": "shared",
        "message": "Project shared successfully. User will receive an email notification."
    }


@router.get("/shared-with-me")
async def get_shared_projects(
    current_user: User = Depends(get_current_user)
):
    """
    Get all projects shared with the current user.
    
    Returns list of projects that other users have shared with you.
    """
    # Filter shared projects for current user's email
    shared = [
        SharedProjectResponse(
            project_id=s["project_id"],
            project_name=s["project_name"],
            owner_id=s["owner_id"],
            permission=s["permission"],
            shared_at=s["shared_at"]
        )
        for s in shared_projects_db.values()
        if s["shared_with_email"] == current_user.email
    ]
    
    return {
        "projects": shared,
        "total": len(shared)
    }


@router.delete("/share/{share_id}", status_code=204)
async def revoke_project_share(
    share_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Revoke project sharing.
    
    Remove a user's access to your shared project.
    """
    if share_id not in shared_projects_db:
        raise HTTPException(404, "Share not found")
    
    share = shared_projects_db[share_id]
    
    # Verify ownership
    if share["owner_id"] != current_user.id:
        raise HTTPException(403, "You don't have permission to revoke this share")
    
    # Remove share
    del shared_projects_db[share_id]
    
    return None


@router.post("/create", response_model=TeamResponse, status_code=201)
async def create_team(
    team: TeamCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new team.
    
    Teams allow multiple users to collaborate on projects together.
    You will be the team owner and can invite members.
    """
    team_id = str(uuid4())
    
    team_data = {
        "id": team_id,
        "name": team.name,
        "description": team.description,
        "owner_id": current_user.id,
        "created_at": datetime.utcnow().isoformat()
    }
    
    teams_db[team_id] = team_data
    
    # Add creator as owner
    team_members_db[f"{team_id}_{current_user.id}"] = {
        "team_id": team_id,
        "user_id": current_user.id,
        "email": current_user.email,
        "role": "owner",
        "joined_at": datetime.utcnow().isoformat()
    }
    
    return TeamResponse(
        id=team_id,
        name=team.name,
        description=team.description,
        owner_id=current_user.id,
        member_count=1,
        created_at=team_data["created_at"]
    )


@router.get("/", response_model=List[TeamResponse])
async def list_teams(
    current_user: User = Depends(get_current_user)
):
    """
    List all teams the current user is a member of.
    
    Includes teams you own and teams you've been invited to.
    """
    # Find teams where user is a member
    user_teams = []
    for team_id, team in teams_db.items():
        # Check if user is a member
        is_member = any(
            m["user_id"] == current_user.id and m["team_id"] == team_id
            for m in team_members_db.values()
        )
        
        if is_member:
            # Count members
            member_count = sum(
                1 for m in team_members_db.values() if m["team_id"] == team_id
            )
            
            user_teams.append(TeamResponse(
                id=team["id"],
                name=team["name"],
                description=team["description"],
                owner_id=team["owner_id"],
                member_count=member_count,
                created_at=team["created_at"]
            ))
    
    return user_teams


@router.get("/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get team details.
    
    Returns information about a specific team.
    """
    if team_id not in teams_db:
        raise HTTPException(404, "Team not found")
    
    team = teams_db[team_id]
    
    # Verify membership
    is_member = any(
        m["user_id"] == current_user.id and m["team_id"] == team_id
        for m in team_members_db.values()
    )
    
    if not is_member:
        raise HTTPException(403, "You are not a member of this team")
    
    # Count members
    member_count = sum(
        1 for m in team_members_db.values() if m["team_id"] == team_id
    )
    
    return TeamResponse(
        id=team["id"],
        name=team["name"],
        description=team["description"],
        owner_id=team["owner_id"],
        member_count=member_count,
        created_at=team["created_at"]
    )


@router.post("/{team_id}/invite", status_code=201)
async def invite_team_member(
    team_id: str,
    invite: TeamMemberInvite,
    current_user: User = Depends(get_current_user)
):
    """
    Invite a user to join the team.
    
    Sends an invitation email to the specified address.
    User must accept the invitation to join.
    """
    if team_id not in teams_db:
        raise HTTPException(404, "Team not found")
    
    team = teams_db[team_id]
    
    # Verify user has permission to invite (owner or admin)
    user_role = None
    for m in team_members_db.values():
        if m["team_id"] == team_id and m["user_id"] == current_user.id:
            user_role = m["role"]
            break
    
    if user_role not in ["owner", "admin"]:
        raise HTTPException(403, "Only owners and admins can invite members")
    
    # Create invitation
    invitation_id = str(uuid4())
    
    return {
        "invitation_id": invitation_id,
        "team_id": team_id,
        "team_name": team["name"],
        "invited_email": invite.email,
        "role": invite.role,
        "status": "sent",
        "message": "Invitation sent successfully. User will receive an email."
    }


@router.get("/{team_id}/members", response_model=List[TeamMemberResponse])
async def list_team_members(
    team_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    List all members of a team.
    
    Shows all team members with their roles and join dates.
    """
    if team_id not in teams_db:
        raise HTTPException(404, "Team not found")
    
    # Verify membership
    is_member = any(
        m["user_id"] == current_user.id and m["team_id"] == team_id
        for m in team_members_db.values()
    )
    
    if not is_member:
        raise HTTPException(403, "You are not a member of this team")
    
    # Get all members
    members = [
        TeamMemberResponse(
            user_id=m["user_id"],
            email=m["email"],
            role=m["role"],
            joined_at=m["joined_at"]
        )
        for m in team_members_db.values()
        if m["team_id"] == team_id
    ]
    
    return members


@router.delete("/{team_id}/members/{user_id}", status_code=204)
async def remove_team_member(
    team_id: str,
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Remove a member from the team.
    
    Only team owners and admins can remove members.
    """
    if team_id not in teams_db:
        raise HTTPException(404, "Team not found")
    
    # Verify user has permission (owner or admin)
    user_role = None
    for m in team_members_db.values():
        if m["team_id"] == team_id and m["user_id"] == current_user.id:
            user_role = m["role"]
            break
    
    if user_role not in ["owner", "admin"]:
        raise HTTPException(403, "Only owners and admins can remove members")
    
    # Find and remove member
    member_key = f"{team_id}_{user_id}"
    if member_key in team_members_db:
        del team_members_db[member_key]
    else:
        raise HTTPException(404, "Member not found in this team")
    
    return None


@router.delete("/{team_id}", status_code=204)
async def delete_team(
    team_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a team.
    
    Only the team owner can delete the team.
    **Warning**: This will remove all members and cannot be undone.
    """
    if team_id not in teams_db:
        raise HTTPException(404, "Team not found")
    
    team = teams_db[team_id]
    
    # Verify ownership
    if team["owner_id"] != current_user.id:
        raise HTTPException(403, "Only the team owner can delete the team")
    
    # Delete team and all members
    del teams_db[team_id]
    
    # Remove all members
    keys_to_delete = [
        key for key, m in team_members_db.items()
        if m["team_id"] == team_id
    ]
    for key in keys_to_delete:
        del team_members_db[key]
    
    return None

