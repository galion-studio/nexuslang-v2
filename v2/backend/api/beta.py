"""
Beta Testing API Endpoints
Comprehensive beta program management for 10,000 users.

"Your imagination is the end."
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from enum import Enum

from ..core.database import get_db
from ..services.beta.beta_testing_service import get_beta_service, BetaTestingService
from ..core.auth import get_current_user, get_current_admin_user
from ..models.user import User

router = APIRouter(prefix="/beta", tags=["Beta Testing"])
security = HTTPBearer()


# Pydantic Models
class BetaTier(str, Enum):
    STANDARD = "standard"
    PREMIUM = "premium"
    VIP = "vip"


class BetaInvitationRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address to invite")
    beta_tier: BetaTier = Field(default=BetaTier.STANDARD, description="Beta tier")
    custom_message: Optional[str] = Field(None, description="Custom invitation message")
    invited_by: Optional[str] = Field(None, description="User ID who sent invitation")


class BetaRegistrationRequest(BaseModel):
    invitation_code: str = Field(..., description="Beta invitation code")


class FeedbackType(str, Enum):
    GENERAL = "general"
    BUG = "bug"
    FEATURE = "feature"
    SATISFACTION = "satisfaction"
    NPS = "nps"


class FeedbackSubmission(BaseModel):
    feedback_type: FeedbackType = Field(..., description="Type of feedback")
    rating: int = Field(..., ge=1, le=10, description="Rating (1-10)")
    comments: Optional[str] = Field(None, description="Optional comments")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class CampaignType(str, Enum):
    WELCOME = "welcome"
    ENGAGEMENT = "engagement"
    FEEDBACK = "feedback"
    REFERRAL = "referral"
    ANNOUNCEMENT = "announcement"


class GrowthCampaignRequest(BaseModel):
    campaign_type: CampaignType = Field(..., description="Type of campaign")
    target_audience: Optional[List[str]] = Field(None, description="Specific user IDs to target")
    custom_content: Optional[Dict[str, Any]] = Field(None, description="Custom campaign content")


class ReportType(str, Enum):
    COMPREHENSIVE = "comprehensive"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    EXECUTIVE = "executive"


class BetaUserProfile(BaseModel):
    user_id: str
    invitation_code: Optional[str]
    invited_by: Optional[str]
    invitation_date: Optional[str]
    first_login: Optional[str]
    last_activity: Optional[str]
    session_count: int
    total_voice_sessions: int
    feedback_submitted: int
    bugs_reported: int
    feature_requests: int
    satisfaction_score: Optional[int]
    nps_score: Optional[int]
    retention_days: int
    is_active: bool
    beta_tier: str
    special_access_features: List[str]


class BetaAnalyticsResponse(BaseModel):
    program_overview: Dict[str, Any]
    user_engagement: Dict[str, Any]
    retention_analysis: Dict[str, Any]
    satisfaction_metrics: Dict[str, Any]
    growth_metrics: Dict[str, Any]
    quality_metrics: Dict[str, Any]


# Dependencies
async def get_beta_service_dep() -> BetaTestingService:
    """Get the beta testing service instance"""
    return await get_beta_service()


# Beta Invitation Routes
@router.post("/invite", response_model=Dict[str, Any])
async def invite_beta_user(
    invitation_data: BetaInvitationRequest,
    background_tasks: BackgroundTasks,
    beta_service: BetaTestingService = Depends(get_beta_service_dep),
    current_user: User = Depends(get_current_user),
):
    """
    Invite a user to the beta program

    Requires authentication. Users can invite others to the beta program.
    """
    try:
        result = await beta_service.invite_beta_user(
            email=invitation_data.email,
            invited_by=current_user.id,
            beta_tier=invitation_data.beta_tier,
            custom_message=invitation_data.custom_message,
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Invitation failed")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Invitation failed: {str(e)}"
        )


@router.post("/register", response_model=Dict[str, Any])
async def register_beta_user(
    registration_data: BetaRegistrationRequest,
    beta_service: BetaTestingService = Depends(get_beta_service_dep),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Register as a beta tester using an invitation code

    Users must have a valid invitation code to join the beta program.
    """
    try:
        result = await beta_service.register_beta_user(
            user_id=current_user.id,
            invitation_code=registration_data.invitation_code,
            db=db
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Registration failed")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.get("/invitations/{code}/validate")
async def validate_invitation_code(
    code: str,
    beta_service: BetaTestingService = Depends(get_beta_service_dep),
):
    """
    Validate an invitation code

    Public endpoint to check if an invitation code is valid and available.
    """
    try:
        if code not in beta_service.invitations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid invitation code"
            )

        invitation = beta_service.invitations[code]

        if not invitation.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation code is inactive"
            )

        if invitation.used_count >= invitation.max_uses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation code has reached maximum uses"
            )

        if datetime.utcnow() > invitation.expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation code has expired"
            )

        return {
            "valid": True,
            "expires_at": invitation.expires_at.isoformat(),
            "uses_remaining": invitation.max_uses - invitation.used_count,
            "beta_tier": "premium" if invitation.invited_by else "standard"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


# Beta User Management Routes
@router.get("/profile", response_model=BetaUserProfile)
async def get_beta_profile(
    beta_service: BetaTestingService = Depends(get_beta_service_dep),
    current_user: User = Depends(get_current_user),
):
    """Get current user's beta profile"""
    try:
        if current_user.id not in beta_service.beta_users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not in beta program"
            )

        profile = beta_service.beta_users[current_user.id]

        return BetaUserProfile(
            user_id=profile.user_id,
            invitation_code=profile.invitation_code,
            invited_by=profile.invited_by,
            invitation_date=profile.invitation_date.isoformat() if profile.invitation_date else None,
            first_login=profile.first_login.isoformat() if profile.first_login else None,
            last_activity=profile.last_activity.isoformat() if profile.last_activity else None,
            session_count=profile.session_count,
            total_voice_sessions=profile.total_voice_sessions,
            feedback_submitted=profile.feedback_submitted,
            bugs_reported=profile.bugs_reported,
            feature_requests=profile.feature_requests,
            satisfaction_score=profile.satisfaction_score,
            nps_score=profile.nps_score,
            retention_days=profile.retention_days,
            is_active=profile.is_active,
            beta_tier=profile.beta_tier,
            special_access_features=list(profile.special_access_features)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Profile retrieval failed: {str(e)}"
        )


@router.post("/activity/track")
async def track_user_activity(
    activity_type: str,
    metadata: Optional[Dict[str, Any]] = None,
    beta_service: BetaTestingService = Depends(get_beta_service_dep),
    current_user: User = Depends(get_current_user),
):
    """
    Track user activity for beta analytics

    Automatically called by the platform to track user engagement.
    """
    try:
        await beta_service.track_user_activity(
            user_id=current_user.id,
            activity_type=activity_type,
            metadata=metadata
        )

        return {"message": "Activity tracked successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Activity tracking failed: {str(e)}"
        )


# Feedback Collection Routes
@router.post("/feedback", response_model=Dict[str, Any])
async def submit_feedback(
    feedback_data: FeedbackSubmission,
    beta_service: BetaTestingService = Depends(get_beta_service_dep),
    current_user: User = Depends(get_current_user),
):
    """
    Submit feedback from beta users

    Collects various types of feedback including bugs, features, and satisfaction scores.
    """
    try:
        result = await beta_service.collect_feedback(
            user_id=current_user.id,
            feedback_type=feedback_data.feedback_type,
            rating=feedback_data.rating,
            comments=feedback_data.comments,
            metadata=feedback_data.metadata
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Feedback submission failed")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feedback submission failed: {str(e)}"
        )


# Analytics and Reporting Routes
@router.get("/analytics", response_model=BetaAnalyticsResponse)
async def get_beta_analytics(
    beta_service: BetaTestingService = Depends(get_beta_service_dep),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),  # Requires admin permissions
):
    """
    Get comprehensive beta program analytics

    Requires admin permissions. Provides detailed insights into beta program performance.
    """
    try:
        return await beta_service.get_beta_analytics(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics retrieval failed: {str(e)}"
        )


@router.post("/campaigns/send", response_model=Dict[str, Any])
async def send_growth_campaign(
    campaign_data: GrowthCampaignRequest,
    background_tasks: BackgroundTasks,
    beta_service: BetaTestingService = Depends(get_beta_service_dep),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Send a growth campaign to beta users

    Requires admin permissions. Sends targeted campaigns to increase engagement and growth.
    """
    try:
        result = await beta_service.send_growth_campaign(
            campaign_type=campaign_data.campaign_type,
            target_audience=campaign_data.target_audience,
            custom_content=campaign_data.custom_content
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Campaign failed")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Campaign failed: {str(e)}"
        )


@router.get("/reports/{report_type}", response_model=Dict[str, Any])
async def generate_beta_report(
    report_type: ReportType,
    beta_service: BetaTestingService = Depends(get_beta_service_dep),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Generate beta program reports

    Requires admin permissions. Generates various types of reports for beta program analysis.
    """
    try:
        report = await beta_service.generate_beta_report(report_type.value)

        if "error" in report:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=report["error"]
            )

        return report

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Report generation failed: {str(e)}"
        )


# Public Beta Information Routes
@router.get("/status")
async def get_beta_status(
    beta_service: BetaTestingService = Depends(get_beta_service_dep),
):
    """
    Get public beta program status

    Public endpoint showing general beta program information.
    """
    try:
        return {
            "program_active": True,
            "current_users": beta_service.beta_config["current_users"],
            "max_users": beta_service.beta_config["max_users"],
            "utilization_rate": (beta_service.beta_config["current_users"] / beta_service.beta_config["max_users"]) * 100,
            "target_completion_date": beta_service.beta_config["target_completion_date"].isoformat(),
            "available_tiers": ["standard", "premium", "vip"],
            "special_features": [
                "early_access_to_new_features",
                "priority_support",
                "beta_exclusive_content",
                "direct_communication_with_team",
                "influence_on_product_decisions"
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Status retrieval failed: {str(e)}"
        )


@router.get("/waitlist/position/{email}")
async def check_waitlist_position(
    email: EmailStr,
    beta_service: BetaTestingService = Depends(get_beta_service_dep),
):
    """
    Check waitlist position for an email

    Public endpoint for users to check their position on the beta waitlist.
    """
    try:
        # Mock waitlist check - in real implementation would check actual waitlist
        if beta_service.beta_config["current_users"] < beta_service.beta_config["max_users"]:
            return {
                "on_waitlist": False,
                "can_join": True,
                "invitation_required": True
            }
        else:
            # Mock waitlist position
            position = 1  # Would be calculated based on actual waitlist
            estimated_wait_days = max(0, (beta_service.beta_config["max_users"] - beta_service.beta_config["current_users"]) // beta_service.beta_config["daily_growth_target"])

            return {
                "on_waitlist": True,
                "position": position,
                "estimated_wait_days": estimated_wait_days,
                "can_join": False
            }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Waitlist check failed: {str(e)}"
        )


# Beta Program Management Routes (Admin Only)
@router.post("/admin/generate-codes")
async def generate_invitation_codes(
    count: int = 100,
    beta_service: BetaTestingService = Depends(get_beta_service_dep),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Generate additional invitation codes

    Requires admin permissions. Generates more invitation codes for beta program growth.
    """
    try:
        if count < 1 or count > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Count must be between 1 and 1000"
            )

        beta_service._generate_invitation_codes(count)

        return {
            "message": f"Generated {count} new invitation codes",
            "total_codes_now": len(beta_service.invitations)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Code generation failed: {str(e)}"
        )


@router.get("/admin/users", response_model=List[BetaUserProfile])
async def list_beta_users(
    limit: int = 100,
    offset: int = 0,
    beta_service: BetaTestingService = Depends(get_beta_service_dep),
    current_user: User = Depends(get_current_admin_user),
):
    """
    List all beta users

    Requires admin permissions. Provides paginated list of all beta program participants.
    """
    try:
        users = list(beta_service.beta_users.values())[offset:offset + limit]

        return [
            BetaUserProfile(
                user_id=user.user_id,
                invitation_code=user.invitation_code,
                invited_by=user.invited_by,
                invitation_date=user.invitation_date.isoformat() if user.invitation_date else None,
                first_login=user.first_login.isoformat() if user.first_login else None,
                last_activity=user.last_activity.isoformat() if user.last_activity else None,
                session_count=user.session_count,
                total_voice_sessions=user.total_voice_sessions,
                feedback_submitted=user.feedback_submitted,
                bugs_reported=user.bugs_reported,
                feature_requests=user.feature_requests,
                satisfaction_score=user.satisfaction_score,
                nps_score=user.nps_score,
                retention_days=user.retention_days,
                is_active=user.is_active,
                beta_tier=user.beta_tier,
                special_access_features=list(user.special_access_features)
            )
            for user in users
        ]

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User listing failed: {str(e)}"
        )


@router.post("/admin/users/{user_id}/tier")
async def update_beta_tier(
    user_id: str,
    new_tier: BetaTier,
    beta_service: BetaTestingService = Depends(get_beta_service_dep),
    current_user: User = Depends(get_current_admin_user),
):
    """
    Update a beta user's tier

    Requires admin permissions. Allows upgrading/downgrading beta user access levels.
    """
    try:
        if user_id not in beta_service.beta_users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Beta user not found"
            )

        profile = beta_service.beta_users[user_id]
        old_tier = profile.beta_tier
        profile.beta_tier = new_tier.value

        # Update special features based on new tier
        if new_tier.value == "premium":
            profile.special_access_features.update([
                "early_access_to_new_features",
                "priority_support"
            ])
        elif new_tier.value == "vip":
            profile.special_access_features.update([
                "early_access_to_new_features",
                "priority_support",
                "beta_exclusive_content",
                "direct_communication_with_team",
                "influence_on_product_decisions"
            ])

        return {
            "message": f"Updated user {user_id} from {old_tier} to {new_tier.value}",
            "new_tier": new_tier.value,
            "special_features": list(profile.special_access_features)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tier update failed: {str(e)}"
        )


@router.get("/setup/guide")
async def get_beta_setup_guide():
    """
    Get beta program setup guide

    Provides comprehensive information for users interested in joining the beta program.
    """
    return {
        "program_overview": {
            "name": "Galion Beta Program",
            "goal": "Reach 10,000 engaged beta users for comprehensive testing",
            "duration": "6-12 months",
            "platforms": ["galion.app", "developer.galion.app", "galion.studio"]
        },
        "how_to_join": [
            "Receive invitation from existing beta user or team",
            "Visit beta signup page with invitation code",
            "Complete registration and onboarding",
            "Start using voice-first AI platform immediately"
        ],
        "beta_tiers": {
            "standard": {
                "features": ["Core platform access", "Basic support"],
                "requirements": ["Valid invitation code"]
            },
            "premium": {
                "features": ["Early feature access", "Priority support", "Advanced customization"],
                "requirements": ["Invited by existing user"]
            },
            "vip": {
                "features": ["All premium features", "Direct team communication", "Product influence", "Exclusive beta content"],
                "requirements": ["Selected by team for special contributions"]
            }
        },
        "expectations": [
            "Active weekly usage for engagement tracking",
            "Regular feedback submission (surveys, bug reports, feature requests)",
            "Participation in user interviews and testing sessions",
            "Helpful bug reports and constructive feedback"
        ],
        "benefits": [
            "Early access to revolutionary voice-first AI platform",
            "Direct influence on product development",
            "Priority support and communication with team",
            "Exclusive beta-only features and content",
            "Recognition in launch announcements"
        ],
        "contact": {
            "support_email": "beta@galion.app",
            "feedback_form": "https://galion.app/beta/feedback",
            "community_discord": "https://discord.gg/galion-beta"
        }
    }