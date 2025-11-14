"""
Beta Testing Service for Galion Platform v2.2
Comprehensive beta program management for 10,000 users.

"Your imagination is the end."
"""

import asyncio
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
import logging
import json
import uuid
import random
import string

from ...core.config import settings
from ...models.user import User
from ...models.rbac import Role
from ..analytics.analytics_engine import AnalyticsEngine
from ..mail.mail_service import MailService
from ..voice.voice_session import VoiceSessionService

logger = logging.getLogger(__name__)


class BetaUserProfile:
    """Beta user profile and tracking"""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.invitation_code: Optional[str] = None
        self.invited_by: Optional[str] = None
        self.invitation_date: Optional[datetime] = None
        self.first_login: Optional[datetime] = None
        self.last_activity: Optional[datetime] = None
        self.session_count = 0
        self.total_voice_sessions = 0
        self.feedback_submitted = 0
        self.bugs_reported = 0
        self.feature_requests = 0
        self.satisfaction_score: Optional[int] = None
        self.nps_score: Optional[int] = None
        self.retention_days = 0
        self.is_active = True
        self.beta_tier = "standard"  # standard, premium, vip
        self.special_access_features: Set[str] = set()
        self.metadata: Dict[str, Any] = {}


class BetaInvitation:
    """Beta invitation tracking"""

    def __init__(self, code: str, invited_by: Optional[str] = None):
        self.code = code
        self.invited_by = invited_by
        self.created_at = datetime.utcnow()
        self.expires_at = self.created_at + timedelta(days=30)
        self.max_uses = 5  # Allow multiple uses per code
        self.used_count = 0
        self.is_active = True
        self.metadata: Dict[str, Any] = {}


class BetaTestingService:
    """
    Comprehensive Beta Testing Service

    Features:
    - Beta user invitation and management
    - User onboarding and engagement tracking
    - Feedback collection and analysis
    - Beta program metrics and reporting
    - Automated user acquisition workflows
    - Retention and growth analytics
    - Beta program lifecycle management
    """

    def __init__(self):
        self.beta_users: Dict[str, BetaUserProfile] = {}
        self.invitations: Dict[str, BetaInvitation] = {}
        self.analytics = AnalyticsEngine()
        self.mail_service = MailService()
        self.voice_service = VoiceSessionService()

        # Beta program configuration
        self.beta_config = {
            "max_users": 10000,
            "current_users": 0,
            "target_completion_date": datetime(2025, 12, 31),
            "invitation_batch_size": 100,
            "daily_growth_target": 50,
            "retention_check_days": [1, 7, 14, 30, 60, 90],
            "feedback_collection_intervals": [7, 14, 30, 60],  # days
            "special_access_features": [
                "early_access_to_new_features",
                "priority_support",
                "beta_exclusive_content",
                "direct_communication_with_team",
                "influence_on_product_decisions"
            ]
        }

        # Initialize beta program
        self._initialize_beta_program()

    def _initialize_beta_program(self):
        """Initialize the beta testing program"""
        # Generate initial invitation codes
        self._generate_invitation_codes(500)  # Start with 500 codes

        # Set up automated tasks
        self._setup_automated_tasks()

        logger.info("Beta testing program initialized")

    def _generate_invitation_codes(self, count: int):
        """Generate unique invitation codes"""
        for _ in range(count):
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            while code in self.invitations:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

            invitation = BetaInvitation(code)
            self.invitations[code] = invitation

    def _setup_automated_tasks(self):
        """Set up automated beta program tasks"""
        # These would be scheduled tasks in a real implementation
        # For now, we'll track them in the config
        self.beta_config["automated_tasks"] = [
            "daily_user_engagement_check",
            "weekly_feedback_collection_reminders",
            "monthly_retention_analysis",
            "quarterly_beta_program_report",
            "continuous_growth_monitoring"
        ]

    async def invite_beta_user(
        self,
        email: str,
        invited_by: Optional[str] = None,
        beta_tier: str = "standard",
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Invite a user to the beta program

        Args:
            email: User email to invite
            invited_by: ID of user who sent the invitation
            beta_tier: Beta tier (standard, premium, vip)
            custom_message: Custom invitation message

        Returns:
            Invitation result
        """
        try:
            # Check if we're at capacity
            if self.beta_config["current_users"] >= self.beta_config["max_users"]:
                return {
                    "success": False,
                    "error": "Beta program at capacity",
                    "waitlist_position": self._add_to_waitlist(email)
                }

            # Get an available invitation code
            available_code = self._get_available_invitation_code(invited_by)
            if not available_code:
                return {
                    "success": False,
                    "error": "No available invitation codes"
                }

            # Create invitation
            invitation = BetaInvitation(available_code, invited_by)
            self.invitations[available_code] = invitation

            # Send invitation email
            await self._send_invitation_email(
                email, available_code, beta_tier, custom_message
            )

            return {
                "success": True,
                "invitation_code": available_code,
                "beta_tier": beta_tier,
                "expires_at": invitation.expires_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Beta invitation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _get_available_invitation_code(self, invited_by: Optional[str] = None) -> Optional[str]:
        """Get an available invitation code"""
        # Find unused codes
        for code, invitation in self.invitations.items():
            if invitation.is_active and invitation.used_count < invitation.max_uses:
                return code

        # Generate more codes if needed
        self._generate_invitation_codes(50)
        return self._get_available_invitation_code(invited_by)

    def _add_to_waitlist(self, email: str) -> int:
        """Add user to waitlist and return position"""
        # Mock waitlist implementation
        return random.randint(1, 1000)

    async def register_beta_user(
        self,
        user_id: str,
        invitation_code: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Register a user as a beta tester

        Args:
            user_id: New user ID
            invitation_code: Invitation code used
            db: Database session

        Returns:
            Registration result
        """
        try:
            # Validate invitation code
            if invitation_code not in self.invitations:
                return {
                    "success": False,
                    "error": "Invalid invitation code"
                }

            invitation = self.invitations[invitation_code]
            if not invitation.is_active or invitation.used_count >= invitation.max_uses:
                return {
                    "success": False,
                    "error": "Invitation code expired or fully used"
                }

            # Create beta user profile
            profile = BetaUserProfile(user_id)
            profile.invitation_code = invitation_code
            profile.invited_by = invitation.invited_by
            profile.invitation_date = invitation.created_at
            profile.first_login = datetime.utcnow()
            profile.beta_tier = "premium" if invitation.invited_by else "standard"

            # Add special access features based on tier
            if profile.beta_tier == "premium":
                profile.special_access_features.update([
                    "early_access_to_new_features",
                    "priority_support"
                ])

            self.beta_users[user_id] = profile
            invitation.used_count += 1

            # Update program stats
            self.beta_config["current_users"] += 1

            # Send welcome email
            await self._send_welcome_email(user_id, db)

            return {
                "success": True,
                "beta_tier": profile.beta_tier,
                "special_features": list(profile.special_access_features),
                "welcome_package_sent": True
            }

        except Exception as e:
            logger.error(f"Beta user registration failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def track_user_activity(
        self,
        user_id: str,
        activity_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Track beta user activity"""
        if user_id not in self.beta_users:
            return

        profile = self.beta_users[user_id]
        profile.last_activity = datetime.utcnow()

        # Update activity-specific counters
        if activity_type == "voice_session":
            profile.total_voice_sessions += 1
        elif activity_type == "feedback_submitted":
            profile.feedback_submitted += 1
        elif activity_type == "bug_reported":
            profile.bugs_reported += 1
        elif activity_type == "feature_requested":
            profile.feature_requests += 1

        profile.session_count += 1

        # Store metadata
        if metadata:
            profile.metadata[f"activity_{datetime.utcnow().isoformat()}"] = {
                "type": activity_type,
                "metadata": metadata
            }

    async def collect_feedback(
        self,
        user_id: str,
        feedback_type: str,
        rating: int,
        comments: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Collect feedback from beta users

        Args:
            user_id: User providing feedback
            feedback_type: Type of feedback (general, bug, feature, satisfaction)
            rating: Rating (1-5 for satisfaction, 1-10 for others)
            comments: Optional comments
            metadata: Additional metadata

        Returns:
            Feedback collection result
        """
        if user_id not in self.beta_users:
            return {"success": False, "error": "User not in beta program"}

        profile = self.beta_users[user_id]

        feedback_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": feedback_type,
            "rating": rating,
            "comments": comments,
            "metadata": metadata or {}
        }

        # Update profile based on feedback type
        if feedback_type == "satisfaction":
            profile.satisfaction_score = rating
        elif feedback_type == "nps":
            profile.nps_score = rating

        profile.feedback_submitted += 1

        # Store feedback
        feedback_key = f"feedback_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        profile.metadata[feedback_key] = feedback_data

        return {
            "success": True,
            "feedback_id": feedback_key,
            "follow_up_scheduled": self._schedule_follow_up(user_id, feedback_type, rating)
        }

    def _schedule_follow_up(self, user_id: str, feedback_type: str, rating: int) -> bool:
        """Schedule follow-up based on feedback"""
        # Schedule follow-up for low ratings
        if rating <= 3:
            return True
        return False

    async def get_beta_analytics(self, db: AsyncSession) -> Dict[str, Any]:
        """Get comprehensive beta program analytics"""
        try:
            # Calculate key metrics
            total_users = len(self.beta_users)
            active_users_7d = len([
                profile for profile in self.beta_users.values()
                if profile.last_activity and
                (datetime.utcnow() - profile.last_activity).days <= 7
            ])

            total_sessions = sum(profile.total_voice_sessions for profile in self.beta_users.values())
            total_feedback = sum(profile.feedback_submitted for profile in self.beta_users.values())

            # Calculate retention rates
            retention_rates = {}
            for days in self.beta_config["retention_check_days"]:
                retained = len([
                    profile for profile in self.beta_users.values()
                    if profile.first_login and
                    (datetime.utcnow() - profile.first_login).days >= days and
                    profile.last_activity and
                    (datetime.utcnow() - profile.last_activity).days <= days
                ])
                retention_rates[f"{days}d"] = (retained / total_users * 100) if total_users > 0 else 0

            # Calculate NPS
            nps_scores = [profile.nps_score for profile in self.beta_users.values() if profile.nps_score is not None]
            nps = sum(nps_scores) / len(nps_scores) if nps_scores else 0

            return {
                "program_overview": {
                    "total_beta_users": total_users,
                    "current_capacity": self.beta_config["current_users"],
                    "max_capacity": self.beta_config["max_users"],
                    "utilization_rate": (total_users / self.beta_config["max_users"]) * 100,
                    "program_progress": (total_users / 10000) * 100
                },
                "user_engagement": {
                    "active_users_7d": active_users_7d,
                    "active_user_rate": (active_users_7d / total_users * 100) if total_users > 0 else 0,
                    "total_voice_sessions": total_sessions,
                    "avg_sessions_per_user": total_sessions / total_users if total_users > 0 else 0,
                    "total_feedback_submitted": total_feedback,
                    "feedback_rate": (total_feedback / total_users * 100) if total_users > 0 else 0
                },
                "retention_analysis": retention_rates,
                "satisfaction_metrics": {
                    "average_nps": nps,
                    "satisfaction_distribution": self._calculate_satisfaction_distribution(),
                    "top_pain_points": await self._analyze_feedback_themes()
                },
                "growth_metrics": {
                    "daily_target": self.beta_config["daily_growth_target"],
                    "current_daily_average": total_users / max(1, (datetime.utcnow() - self.beta_config.get("start_date", datetime.utcnow())).days),
                    "invitation_codes_used": sum(inv.used_count for inv in self.invitations.values()),
                    "conversion_rate": (total_users / max(1, sum(inv.used_count for inv in self.invitations.values()))) * 100
                },
                "quality_metrics": {
                    "bugs_reported": sum(profile.bugs_reported for profile in self.beta_users.values()),
                    "feature_requests": sum(profile.feature_requests for profile in self.beta_users.values()),
                    "avg_bugs_per_user": sum(profile.bugs_reported for profile in self.beta_users.values()) / total_users if total_users > 0 else 0,
                    "avg_features_requested_per_user": sum(profile.feature_requests for profile in self.beta_users.values()) / total_users if total_users > 0 else 0
                }
            }

        except Exception as e:
            logger.error(f"Beta analytics generation failed: {e}")
            return {}

    def _calculate_satisfaction_distribution(self) -> Dict[str, int]:
        """Calculate satisfaction score distribution"""
        distribution = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}

        for profile in self.beta_users.values():
            if profile.satisfaction_score:
                score_str = str(profile.satisfaction_score)
                if score_str in distribution:
                    distribution[score_str] += 1

        return distribution

    async def _analyze_feedback_themes(self) -> List[str]:
        """Analyze common themes in feedback"""
        # Mock analysis - in real implementation would use NLP
        themes = [
            "Voice interaction quality",
            "User interface responsiveness",
            "Feature request: Advanced customization",
            "Bug: Occasional audio delays",
            "Positive: Intuitive voice commands"
        ]
        return themes

    async def send_growth_campaign(
        self,
        campaign_type: str,
        target_audience: Optional[List[str]] = None,
        custom_content: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Send targeted growth campaign to beta users

        Args:
            campaign_type: Type of campaign (welcome, engagement, feedback, referral)
            target_audience: Specific user IDs to target
            custom_content: Custom campaign content

        Returns:
            Campaign result
        """
        try:
            # Determine target users
            if target_audience:
                targets = [uid for uid in target_audience if uid in self.beta_users]
            else:
                targets = list(self.beta_users.keys())

            # Campaign content based on type
            campaign_content = self._get_campaign_content(campaign_type, custom_content)

            # Send campaign (mock implementation)
            sent_count = len(targets)
            open_rate = 0.65  # Mock open rate
            click_rate = 0.25  # Mock click rate

            return {
                "success": True,
                "campaign_type": campaign_type,
                "targets_reached": sent_count,
                "estimated_opens": int(sent_count * open_rate),
                "estimated_clicks": int(sent_count * click_rate),
                "content": campaign_content
            }

        except Exception as e:
            logger.error(f"Growth campaign failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _get_campaign_content(self, campaign_type: str, custom_content: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Get campaign content based on type"""
        base_content = {
            "subject": "Join the Galion Beta Revolution",
            "preview_text": "Your voice, our AI - experience the future",
            "cta_text": "Join Beta Now",
            "cta_url": "https://galion.app/beta"
        }

        if custom_content:
            base_content.update(custom_content)

        return base_content

    async def generate_beta_report(self, report_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Generate detailed beta program report

        Args:
            report_type: Type of report (comprehensive, weekly, monthly, executive)

        Returns:
            Report data
        """
        try:
            analytics = await self.get_beta_analytics(None)  # type: ignore

            if report_type == "comprehensive":
                return {
                    "report_type": "comprehensive",
                    "generated_at": datetime.utcnow().isoformat(),
                    "period": "program_lifetime",
                    "executive_summary": self._generate_executive_summary(analytics),
                    "detailed_analytics": analytics,
                    "recommendations": self._generate_recommendations(analytics),
                    "next_steps": self._generate_next_steps(analytics)
                }
            elif report_type == "weekly":
                return {
                    "report_type": "weekly",
                    "generated_at": datetime.utcnow().isoformat(),
                    "period": "last_7_days",
                    "key_metrics": self._extract_key_metrics(analytics, "weekly"),
                    "trends": self._calculate_weekly_trends(analytics),
                    "alerts": self._identify_weekly_alerts(analytics)
                }

            return analytics

        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return {"error": str(e)}

    def _generate_executive_summary(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary for reports"""
        return {
            "program_status": "on_track" if analytics["program_overview"]["program_progress"] >= 75 else "accelerating",
            "key_achievements": [
                f"{analytics['program_overview']['total_beta_users']} beta users onboarded",
                f"{analytics['user_engagement']['active_user_rate']:.1f}% weekly active users",
                f"{analytics['satisfaction_metrics']['average_nps']:.1f} average NPS score"
            ],
            "critical_insights": [
                "Strong user engagement with voice-first interactions",
                "High retention rates indicate product-market fit",
                "Feature requests suggest clear product roadmap"
            ],
            "risks_and_opportunities": [
                "Scale infrastructure to support 10K+ users",
                "Expand beta program to additional user segments",
                "Leverage user feedback for product improvements"
            ]
        }

    def _generate_recommendations(self, analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on analytics"""
        recommendations = []

        # Growth recommendations
        if analytics["growth_metrics"]["conversion_rate"] < 50:
            recommendations.append({
                "category": "growth",
                "priority": "high",
                "recommendation": "Optimize invitation conversion funnel",
                "expected_impact": "Increase user acquisition by 25%"
            })

        # Engagement recommendations
        if analytics["user_engagement"]["active_user_rate"] < 70:
            recommendations.append({
                "category": "engagement",
                "priority": "high",
                "recommendation": "Implement personalized onboarding flow",
                "expected_impact": "Improve 7-day retention by 15%"
            })

        return recommendations

    def _generate_next_steps(self, analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate next steps based on current progress"""
        current_progress = analytics["program_overview"]["program_progress"]

        if current_progress < 50:
            return [
                {"phase": "acceleration", "action": "Scale user acquisition campaigns", "timeline": "immediate"},
                {"phase": "optimization", "action": "Implement automated feedback collection", "timeline": "1 week"},
                {"phase": "expansion", "action": "Add premium beta features", "timeline": "2 weeks"}
            ]
        elif current_progress < 80:
            return [
                {"phase": "scaling", "action": "Prepare infrastructure for 10K users", "timeline": "immediate"},
                {"phase": "refinement", "action": "Address top user pain points", "timeline": "1-2 weeks"},
                {"phase": "transition", "action": "Plan general availability launch", "timeline": "1 month"}
            ]
        else:
            return [
                {"phase": "completion", "action": "Finalize beta program report", "timeline": "immediate"},
                {"phase": "launch", "action": "Execute GA launch plan", "timeline": "2 weeks"},
                {"phase": "post_launch", "action": "Monitor and optimize post-launch metrics", "timeline": "ongoing"}
            ]

    def _extract_key_metrics(self, analytics: Dict[str, Any], period: str) -> Dict[str, Any]:
        """Extract key metrics for specific reporting periods"""
        return {
            "total_users": analytics["program_overview"]["total_beta_users"],
            "active_users": analytics["user_engagement"]["active_users_7d"],
            "retention_rate": analytics["retention_analysis"]["7d"],
            "satisfaction_score": analytics["satisfaction_metrics"]["average_nps"]
        }

    def _calculate_weekly_trends(self, analytics: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate weekly trends"""
        # Mock trend calculation
        return {
            "user_growth_trend": "+12%",
            "engagement_trend": "+8%",
            "retention_trend": "+5%",
            "satisfaction_trend": "+3%"
        }

    def _identify_weekly_alerts(self, analytics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify alerts that need immediate attention"""
        alerts = []

        if analytics["user_engagement"]["active_user_rate"] < 60:
            alerts.append({
                "severity": "high",
                "alert": "Low user engagement detected",
                "action_required": "Review user onboarding and engagement strategies"
            })

        if analytics["satisfaction_metrics"]["average_nps"] < 6:
            alerts.append({
                "severity": "medium",
                "alert": "NPS score below target",
                "action_required": "Analyze feedback and implement improvements"
            })

        return alerts

    async def _send_invitation_email(
        self,
        email: str,
        invitation_code: str,
        beta_tier: str,
        custom_message: Optional[str] = None
    ):
        """Send beta invitation email"""
        # Mock email sending - would integrate with actual mail service
        logger.info(f"Sent beta invitation to {email} with code {invitation_code}")

    async def _send_welcome_email(self, user_id: str, db: AsyncSession):
        """Send welcome email to new beta user"""
        # Mock email sending
        logger.info(f"Sent welcome email to beta user {user_id}")


# Global beta testing service instance
_beta_service: Optional[BetaTestingService] = None

async def get_beta_service() -> BetaTestingService:
    """Get the global beta testing service instance"""
    global _beta_service

    if _beta_service is None:
        _beta_service = BetaTestingService()

    return _beta_service
