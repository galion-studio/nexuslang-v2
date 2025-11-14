"""
Human-in-the-Loop System for Galion Platform v2.2
Enables agents to request human approval, clarification, and collaboration.

Features:
- Approval request system with escalation
- Clarification requests for ambiguous tasks
- Human feedback integration
- Decision audit trails
- Notification and alerting system
- Context preservation during human interaction

"Your imagination is the end."
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable, Union, Set
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
import uuid

logger = logging.getLogger(__name__)

class ApprovalStatus(Enum):
    """Status of an approval request"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class ApprovalType(Enum):
    """Types of approval requests"""
    STEP_EXECUTION = "step_execution"
    PARAMETER_CHANGE = "parameter_change"
    RESOURCE_ACCESS = "resource_access"
    COST_EXCEEDANCE = "cost_exceedance"
    SECURITY_CONCERN = "security_concern"
    BUSINESS_DECISION = "business_decision"
    CLARIFICATION_NEEDED = "clarification_needed"

class ApprovalPriority(Enum):
    """Priority levels for approval requests"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class ApprovalRequest(BaseModel):
    """A human approval request"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    execution_id: str
    step_id: Optional[str] = None
    type: ApprovalType
    priority: ApprovalPriority = ApprovalPriority.NORMAL

    title: str
    description: str
    context: Dict[str, Any] = Field(default_factory=dict)

    # Request details
    requested_by: str  # Agent or system component
    request_reason: str
    suggested_action: Optional[str] = None
    alternatives: List[str] = Field(default_factory=list)

    # Timing
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    responded_at: Optional[datetime] = None

    # Response
    status: ApprovalStatus = ApprovalStatus.PENDING
    approved_by: Optional[str] = None
    response_notes: Optional[str] = None
    modified_parameters: Dict[str, Any] = Field(default_factory=dict)

    # Escalation
    escalation_level: int = 0
    max_escalation_level: int = 2
    escalation_history: List[Dict[str, Any]] = Field(default_factory=list)

    # Metadata
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "execution_id": self.execution_id,
            "step_id": self.step_id,
            "type": self.type.value,
            "priority": self.priority.value,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority_level": self._get_priority_level(),
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
            "requested_by": self.requested_by,
            "approved_by": self.approved_by,
            "escalation_level": self.escalation_level,
            "time_remaining": self.get_time_remaining()
        }

    def _get_priority_level(self) -> int:
        """Get numeric priority level for sorting"""
        levels = {
            ApprovalPriority.LOW: 1,
            ApprovalPriority.NORMAL: 2,
            ApprovalPriority.HIGH: 3,
            ApprovalPriority.URGENT: 4,
            ApprovalPriority.CRITICAL: 5
        }
        return levels.get(self.priority, 2)

    def get_time_remaining(self) -> Optional[float]:
        """Get seconds remaining until expiration"""
        if not self.expires_at:
            return None
        remaining = (self.expires_at - datetime.now()).total_seconds()
        return max(0, remaining)

    def is_expired(self) -> bool:
        """Check if request has expired"""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at

    def can_escalate(self) -> bool:
        """Check if request can be escalated"""
        return self.escalation_level < self.max_escalation_level

class ClarificationRequest(BaseModel):
    """A request for human clarification"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    execution_id: str
    step_id: Optional[str] = None

    question: str
    context: Dict[str, Any] = Field(default_factory=dict)
    suggestions: List[str] = Field(default_factory=list)

    requested_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    responded_at: Optional[datetime] = None

    response: Optional[str] = None
    responded_by: Optional[str] = None

    status: str = "pending"  # pending, answered, cancelled
    priority: str = "normal"  # low, normal, high

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "execution_id": self.execution_id,
            "step_id": self.step_id,
            "question": self.question,
            "status": self.status,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "responded_at": self.responded_at.isoformat() if self.responded_at else None,
            "responded_by": self.responded_by
        }

class NotificationChannel(Enum):
    """Notification channels"""
    WEBSOCKET = "websocket"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    SLACK = "slack"
    DISCORD = "discord"

class NotificationPreference(BaseModel):
    """User notification preferences"""

    user_id: str
    channels: List[NotificationChannel] = Field(default_factory=lambda: [NotificationChannel.WEBSOCKET])

    # Channel-specific settings
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    slack_webhook: Optional[str] = None
    discord_webhook: Optional[str] = None

    # Priority thresholds
    min_priority: ApprovalPriority = ApprovalPriority.NORMAL

    # Types to notify about
    notify_types: List[ApprovalType] = Field(default_factory=lambda: [
        ApprovalType.SECURITY_CONCERN,
        ApprovalType.COST_EXCEEDANCE,
        ApprovalType.BUSINESS_DECISION
    ])

class HumanLoopManager:
    """
    Manages human-in-the-loop interactions for autonomous systems.

    Features:
    - Approval request management
    - Clarification handling
    - Notification routing
    - Escalation policies
    - Audit trails
    """

    def __init__(self):
        self.approval_requests: Dict[str, ApprovalRequest] = {}
        self.clarification_requests: Dict[str, ClarificationRequest] = {}
        self.notification_preferences: Dict[str, NotificationPreference] = {}

        # Callbacks for notifications
        self.notification_callbacks: Dict[NotificationChannel, List[Callable]] = {
            channel: [] for channel in NotificationChannel
        }

        # Configuration
        self.default_expiration_hours = 24
        self.max_pending_requests_per_user = 50
        self.escalation_intervals = [1, 4, 24]  # hours

        self.logger = logging.getLogger(f"{__name__}.manager")

    async def request_approval(
        self,
        execution_id: str,
        step_id: Optional[str],
        approval_type: ApprovalType,
        title: str,
        description: str,
        requested_by: str,
        priority: ApprovalPriority = ApprovalPriority.NORMAL,
        context: Dict[str, Any] = None,
        suggested_action: str = None,
        alternatives: List[str] = None,
        expires_in_hours: int = None
    ) -> str:
        """
        Create an approval request.

        Returns the approval request ID.
        """
        expires_at = None
        if expires_in_hours:
            expires_at = datetime.now() + timedelta(hours=expires_in_hours)
        elif approval_type in [ApprovalType.SECURITY_CONCERN, ApprovalType.URGENT]:
            expires_at = datetime.now() + timedelta(hours=1)
        else:
            expires_at = datetime.now() + timedelta(hours=self.default_expiration_hours)

        request = ApprovalRequest(
            execution_id=execution_id,
            step_id=step_id,
            type=approval_type,
            priority=priority,
            title=title,
            description=description,
            context=context or {},
            requested_by=requested_by,
            request_reason=description,
            suggested_action=suggested_action,
            alternatives=alternatives or [],
            expires_at=expires_at
        )

        self.approval_requests[request.id] = request

        # Send notifications
        await self._send_notifications(request)

        # Schedule escalation if needed
        if request.can_escalate():
            asyncio.create_task(self._schedule_escalation(request.id))

        # Schedule expiration check
        asyncio.create_task(self._schedule_expiration_check(request.id))

        self.logger.info(f"Created approval request: {request.id} - {title}")
        return request.id

    async def respond_to_approval(
        self,
        request_id: str,
        user_id: str,
        approved: bool,
        notes: str = None,
        modified_parameters: Dict[str, Any] = None
    ) -> bool:
        """
        Respond to an approval request.

        Returns True if response was accepted.
        """
        request = self.approval_requests.get(request_id)
        if not request:
            return False

        if request.status != ApprovalStatus.PENDING:
            return False

        if request.is_expired():
            request.status = ApprovalStatus.EXPIRED
            return False

        request.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        request.approved_by = user_id
        request.response_notes = notes
        request.responded_at = datetime.now()
        request.modified_parameters = modified_parameters or {}

        # Cancel escalation tasks
        # (In a real implementation, you'd track and cancel the asyncio tasks)

        self.logger.info(f"Approval request {request_id} responded by {user_id}: {request.status.value}")
        return True

    async def request_clarification(
        self,
        execution_id: str,
        step_id: Optional[str],
        question: str,
        requested_by: str,
        context: Dict[str, Any] = None,
        suggestions: List[str] = None
    ) -> str:
        """
        Request clarification from a human.

        Returns the clarification request ID.
        """
        request = ClarificationRequest(
            execution_id=execution_id,
            step_id=step_id,
            question=question,
            context=context or {},
            suggestions=suggestions or [],
            requested_by=requested_by
        )

        self.clarification_requests[request.id] = request

        # Send notification
        await self._send_clarification_notification(request)

        self.logger.info(f"Created clarification request: {request.id} - {question[:50]}...")
        return request.id

    async def respond_to_clarification(
        self,
        request_id: str,
        user_id: str,
        response: str
    ) -> bool:
        """
        Respond to a clarification request.

        Returns True if response was accepted.
        """
        request = self.clarification_requests.get(request_id)
        if not request:
            return False

        if request.status != "pending":
            return False

        request.response = response
        request.responded_by = user_id
        request.responded_at = datetime.now()
        request.status = "answered"

        self.logger.info(f"Clarification request {request_id} answered by {user_id}")
        return True

    async def _send_notifications(self, request: ApprovalRequest):
        """Send notifications for approval request"""
        # Find users to notify (based on execution context, user preferences, etc.)
        # For now, broadcast to all registered notification callbacks

        notification_data = {
            "type": "approval_request",
            "request": request.to_dict()
        }

        for channel in NotificationChannel:
            for callback in self.notification_callbacks[channel]:
                try:
                    await callback(notification_data)
                except Exception as e:
                    self.logger.error(f"Notification callback error: {e}")

    async def _send_clarification_notification(self, request: ClarificationRequest):
        """Send notifications for clarification request"""
        notification_data = {
            "type": "clarification_request",
            "request": request.to_dict()
        }

        # Send via websocket channel for now
        for callback in self.notification_callbacks[NotificationChannel.WEBSOCKET]:
            try:
                await callback(notification_data)
            except Exception as e:
                self.logger.error(f"Clarification notification error: {e}")

    async def _schedule_escalation(self, request_id: str):
        """Schedule escalation for an approval request"""
        request = self.approval_requests.get(request_id)
        if not request:
            return

        for i, interval in enumerate(self.escalation_intervals):
            if i >= request.max_escalation_level:
                break

            await asyncio.sleep(interval * 3600)  # Convert hours to seconds

            # Check if still pending
            current_request = self.approval_requests.get(request_id)
            if not current_request or current_request.status != ApprovalStatus.PENDING:
                break

            # Escalate
            current_request.escalation_level += 1
            current_request.escalation_history.append({
                "level": current_request.escalation_level,
                "timestamp": datetime.now().isoformat(),
                "action": "auto_escalated"
            })

            # Send escalation notifications
            await self._send_notifications(current_request)
            self.logger.info(f"Escalated approval request {request_id} to level {current_request.escalation_level}")

    async def _schedule_expiration_check(self, request_id: str):
        """Schedule expiration check for an approval request"""
        request = self.approval_requests.get(request_id)
        if not request or not request.expires_at:
            return

        # Calculate delay
        delay = (request.expires_at - datetime.now()).total_seconds()
        if delay <= 0:
            return

        await asyncio.sleep(delay)

        # Check if still pending
        current_request = self.approval_requests.get(request_id)
        if current_request and current_request.status == ApprovalStatus.PENDING:
            current_request.status = ApprovalStatus.EXPIRED
            self.logger.info(f"Approval request {request_id} expired")

    def register_notification_callback(self, channel: NotificationChannel, callback: Callable):
        """Register a notification callback"""
        self.notification_callbacks[channel].append(callback)

    def unregister_notification_callback(self, channel: NotificationChannel, callback: Callable):
        """Unregister a notification callback"""
        if callback in self.notification_callbacks[channel]:
            self.notification_callbacks[channel].remove(callback)

    def set_notification_preferences(self, preferences: NotificationPreference):
        """Set notification preferences for a user"""
        self.notification_preferences[preferences.user_id] = preferences

    def get_pending_approvals(self, user_id: Optional[str] = None, execution_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get pending approval requests"""
        requests = []

        for request in self.approval_requests.values():
            if request.status != ApprovalStatus.PENDING:
                continue

            if execution_id and request.execution_id != execution_id:
                continue

            # For now, include all pending requests
            # In a real system, you'd filter by user permissions
            requests.append(request.to_dict())

        # Sort by priority (highest first)
        requests.sort(key=lambda x: x["priority_level"], reverse=True)
        return requests

    def get_pending_clarifications(self, user_id: Optional[str] = None, execution_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get pending clarification requests"""
        requests = []

        for request in self.clarification_requests.values():
            if request.status != "pending":
                continue

            if execution_id and request.execution_id != execution_id:
                continue

            requests.append(request.to_dict())

        return requests

    def get_approval_history(self, execution_id: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get approval request history"""
        history = []

        for request in self.approval_requests.values():
            if execution_id and request.execution_id != execution_id:
                continue

            history.append(request.to_dict())

        # Sort by creation time (newest first)
        history.sort(key=lambda x: x["created_at"], reverse=True)
        return history[:limit]

    def cancel_request(self, request_id: str, reason: str = None) -> bool:
        """Cancel an approval or clarification request"""
        if request_id in self.approval_requests:
            request = self.approval_requests[request_id]
            if request.status == ApprovalStatus.PENDING:
                request.status = ApprovalStatus.CANCELLED
                request.response_notes = reason
                return True

        if request_id in self.clarification_requests:
            request = self.clarification_requests[request_id]
            if request.status == "pending":
                request.status = "cancelled"
                return True

        return False

    async def cleanup_expired_requests(self):
        """Clean up expired requests"""
        now = datetime.now()
        expired_approvals = []
        expired_clarifications = []

        for request_id, request in self.approval_requests.items():
            if (request.status == ApprovalStatus.PENDING and
                request.expires_at and request.expires_at < now):
                request.status = ApprovalStatus.EXPIRED
                expired_approvals.append(request_id)

        # Keep only recent requests (last 1000)
        all_approval_ids = list(self.approval_requests.keys())
        if len(all_approval_ids) > 1000:
            to_remove = all_approval_ids[:-1000]
            for request_id in to_remove:
                del self.approval_requests[request_id]

        # Similar for clarifications
        all_clarification_ids = list(self.clarification_requests.keys())
        if len(all_clarification_ids) > 1000:
            to_remove = all_clarification_ids[:-1000]
            for request_id in to_remove:
                del self.clarification_requests[request_id]

        if expired_approvals:
            self.logger.info(f"Cleaned up {len(expired_approvals)} expired approval requests")

# Global human loop manager instance
human_loop_manager = HumanLoopManager()

# Helper functions for easy integration

async def request_human_approval(
    execution_id: str,
    approval_type: ApprovalType,
    title: str,
    description: str,
    context: Dict[str, Any] = None,
    **kwargs
) -> str:
    """Helper function to request human approval"""
    return await human_loop_manager.request_approval(
        execution_id=execution_id,
        approval_type=approval_type,
        title=title,
        description=description,
        context=context,
        **kwargs
    )

async def request_clarification(
    execution_id: str,
    question: str,
    context: Dict[str, Any] = None,
    **kwargs
) -> str:
    """Helper function to request clarification"""
    return await human_loop_manager.request_clarification(
        execution_id=execution_id,
        question=question,
        context=context,
        **kwargs
    )
