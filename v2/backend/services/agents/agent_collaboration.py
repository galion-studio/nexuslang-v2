"""
Advanced Agent Collaboration System for Galion Platform v2.2
Enables sophisticated multi-agent coordination and resource sharing.

Features:
- Agent communication protocols and messaging
- Resource allocation and sharing
- Task delegation and handoff mechanisms
- Collaborative decision making
- Conflict resolution strategies
- Knowledge sharing and learning
- Performance optimization through teamwork

"Your imagination is the end."
"""

import asyncio
from typing import Dict, List, Optional, Any, Set, Tuple, Callable, Union
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
import uuid

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Types of messages between agents"""
    TASK_REQUEST = "task_request"
    TASK_DELEGATION = "task_delegation"
    RESOURCE_REQUEST = "resource_request"
    KNOWLEDGE_SHARE = "knowledge_share"
    STATUS_UPDATE = "status_update"
    COORDINATION_SIGNAL = "coordination_signal"
    CONFLICT_RESOLUTION = "conflict_resolution"
    PERFORMANCE_REPORT = "performance_report"

class MessagePriority(Enum):
    """Message priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"

class AgentMessage(BaseModel):
    """Message between agents"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    receiver_id: str
    message_type: MessageType
    priority: MessagePriority = MessagePriority.NORMAL

    # Message content
    subject: str
    content: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Timing
    timestamp: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    # Delivery tracking
    delivered: bool = False
    delivered_at: Optional[datetime] = None
    read: bool = False
    read_at: Optional[datetime] = None

    # Response tracking
    requires_response: bool = False
    response_deadline: Optional[datetime] = None
    responded: bool = False
    response_message_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "message_type": self.message_type.value,
            "priority": self.priority.value,
            "subject": self.subject,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "delivered": self.delivered,
            "read": self.read,
            "responded": self.responded
        }

class ResourceType(Enum):
    """Types of resources that can be shared"""
    COMPUTE = "compute"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    API_QUOTA = "api_quota"
    TOOL_ACCESS = "tool_access"
    KNOWLEDGE = "knowledge"
    CONTEXT = "context"

class ResourceAllocation(BaseModel):
    """Resource allocation record"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    resource_type: ResourceType
    resource_id: str  # Specific resource identifier
    allocated_to: str  # Agent ID
    allocated_by: str  # Agent or system that allocated

    amount: float  # Amount allocated
    unit: str  # Unit of measurement

    allocated_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    # Usage tracking
    used_amount: float = 0.0
    last_used: Optional[datetime] = None

    # Status
    active: bool = True
    returned_at: Optional[datetime] = None

class CollaborationSession(BaseModel):
    """A collaborative session between agents"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str

    # Participants
    initiator: str  # Agent that started the session
    participants: Set[str] = Field(default_factory=set)
    coordinator: Optional[str] = None  # Agent responsible for coordination

    # Context
    goal: str
    context: Dict[str, Any] = Field(default_factory=dict)

    # Status
    active: bool = True
    status: str = "forming"  # forming, active, completing, completed

    # Timing
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Performance tracking
    messages_exchanged: int = 0
    tasks_completed: int = 0
    conflicts_resolved: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "initiator": self.initiator,
            "participants": list(self.participants),
            "coordinator": self.coordinator,
            "goal": self.goal,
            "status": self.status,
            "active": self.active,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "messages_exchanged": self.messages_exchanged,
            "tasks_completed": self.tasks_completed
        }

class TaskDelegation(BaseModel):
    """Task delegation record"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    original_agent: str
    delegated_to: str
    delegated_by: str

    reason: str
    context: Dict[str, Any] = Field(default_factory=dict)

    # Delegation details
    delegation_level: int = 1  # How many times this task has been delegated
    max_delegation_level: int = 3

    # Timing
    delegated_at: datetime = Field(default_factory=datetime.now)
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Status
    status: str = "pending"  # pending, accepted, in_progress, completed, failed, rejected
    result: Optional[Dict[str, Any]] = None

class AgentProfile(BaseModel):
    """Profile information about an agent for collaboration"""

    agent_id: str
    name: str
    capabilities: List[str] = Field(default_factory=list)
    expertise_domains: List[str] = Field(default_factory=list)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)

    # Collaboration preferences
    collaboration_style: str = "cooperative"  # cooperative, competitive, independent
    delegation_preference: str = "moderate"  # low, moderate, high
    resource_sharing: str = "generous"  # stingy, moderate, generous

    # Current status
    available: bool = True
    current_load: float = 0.0  # 0-1 scale
    active_sessions: Set[str] = Field(default_factory=set)

    # Reputation and trust
    trust_score: float = 0.5  # 0-1 scale
    successful_collaborations: int = 0
    total_collaborations: int = 0

class AgentCollaborationHub:
    """
    Central hub for agent collaboration and coordination.

    Manages communication, resource sharing, and collaborative workflows.
    """

    def __init__(self):
        # Communication infrastructure
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.message_handlers: Dict[MessageType, List[Callable]] = {}

        # Resource management
        self.resource_allocations: Dict[str, ResourceAllocation] = {}
        self.resource_pools: Dict[ResourceType, Dict[str, Any]] = {}

        # Collaboration sessions
        self.active_sessions: Dict[str, CollaborationSession] = {}
        self.agent_sessions: Dict[str, Set[str]] = {}  # agent_id -> session_ids

        # Agent profiles and relationships
        self.agent_profiles: Dict[str, AgentProfile] = {}
        self.agent_relationships: Dict[str, Dict[str, float]] = {}  # trust scores between agents

        # Task delegation tracking
        self.active_delegations: Dict[str, TaskDelegation] = {}

        # Configuration
        self.max_session_duration = timedelta(hours=8)
        self.resource_cleanup_interval = timedelta(minutes=5)
        self.message_expiration = timedelta(hours=1)

        self.logger = logging.getLogger(f"{__name__}.hub")

    async def initialize(self):
        """Initialize the collaboration hub"""
        # Start background tasks
        asyncio.create_task(self._message_processor())
        asyncio.create_task(self._resource_cleanup_task())
        asyncio.create_task(self._session_monitor())

        # Initialize resource pools
        self._initialize_resource_pools()

        self.logger.info("Agent Collaboration Hub initialized")

    def _initialize_resource_pools(self):
        """Initialize default resource pools"""
        for resource_type in ResourceType:
            self.resource_pools[resource_type] = {
                "total": 100.0,  # Default capacity
                "available": 100.0,
                "allocations": {},
                "limits": {}
            }

    # Message Communication Methods

    async def send_message(
        self,
        sender_id: str,
        receiver_id: str,
        message_type: MessageType,
        subject: str,
        content: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        requires_response: bool = False,
        response_deadline: Optional[datetime] = None
    ) -> str:
        """Send a message between agents"""
        message = AgentMessage(
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=message_type,
            priority=priority,
            subject=subject,
            content=content,
            requires_response=requires_response,
            response_deadline=response_deadline
        )

        await self.message_queue.put(message)

        # Track message in sessions
        await self._track_message_in_sessions(message)

        self.logger.debug(f"Message sent: {sender_id} -> {receiver_id} ({message_type.value})")
        return message.id

    async def broadcast_message(
        self,
        sender_id: str,
        message_type: MessageType,
        subject: str,
        content: Dict[str, Any],
        target_agents: Optional[List[str]] = None,
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> List[str]:
        """Broadcast message to multiple agents"""
        if target_agents is None:
            target_agents = list(self.agent_profiles.keys())

        message_ids = []
        for agent_id in target_agents:
            if agent_id != sender_id:
                msg_id = await self.send_message(
                    sender_id, agent_id, message_type, subject, content, priority
                )
                message_ids.append(msg_id)

        return message_ids

    def register_message_handler(self, message_type: MessageType, handler: Callable):
        """Register a handler for specific message types"""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []
        self.message_handlers[message_type].append(handler)

    async def _message_processor(self):
        """Process messages from the queue"""
        while True:
            try:
                message: AgentMessage = await self.message_queue.get()

                # Mark as delivered
                message.delivered = True
                message.delivered_at = datetime.now()

                # Route to appropriate handlers
                await self._route_message(message)

                # Handle response requirements
                if message.requires_response and message.response_deadline:
                    asyncio.create_task(self._monitor_response_deadline(message))

            except Exception as e:
                self.logger.error(f"Error processing message: {e}")

    async def _route_message(self, message: AgentMessage):
        """Route message to appropriate handlers"""
        # Call type-specific handlers
        if message.message_type in self.message_handlers:
            for handler in self.message_handlers[message.message_type]:
                try:
                    await handler(message)
                except Exception as e:
                    self.logger.error(f"Message handler error: {e}")

        # Call agent-specific handlers if agent is registered
        if message.receiver_id in self.agent_profiles:
            await self._deliver_to_agent(message)

    async def _deliver_to_agent(self, message: AgentMessage):
        """Deliver message to specific agent"""
        # In a real implementation, this would interface with the agent
        # For now, just log and mark as read
        message.read = True
        message.read_at = datetime.now()

        self.logger.info(f"Message delivered to agent {message.receiver_id}: {message.subject}")

    # Resource Management Methods

    async def request_resource(
        self,
        requester_id: str,
        resource_type: ResourceType,
        amount: float,
        reason: str = ""
    ) -> Optional[str]:
        """Request resource allocation"""
        pool = self.resource_pools.get(resource_type)
        if not pool:
            return None

        if pool["available"] >= amount:
            # Allocate resource
            allocation_id = str(uuid.uuid4())

            allocation = ResourceAllocation(
                resource_type=resource_type,
                resource_id=f"{resource_type.value}_{allocation_id}",
                allocated_to=requester_id,
                allocated_by="collaboration_hub",
                amount=amount,
                unit=self._get_resource_unit(resource_type),
                expires_at=datetime.now() + timedelta(hours=1)
            )

            self.resource_allocations[allocation_id] = allocation
            pool["available"] -= amount
            pool["allocations"][allocation_id] = allocation

            self.logger.info(f"Resource allocated: {resource_type.value} ({amount}) to {requester_id}")
            return allocation_id

        return None

    async def release_resource(self, allocation_id: str) -> bool:
        """Release a resource allocation"""
        if allocation_id not in self.resource_allocations:
            return False

        allocation = self.resource_allocations[allocation_id]
        if not allocation.active:
            return False

        # Return to pool
        pool = self.resource_pools[allocation.resource_type]
        pool["available"] += allocation.amount
        del pool["allocations"][allocation_id]

        allocation.active = False
        allocation.returned_at = datetime.now()

        self.logger.info(f"Resource released: {allocation.resource_type.value} from {allocation.allocated_to}")
        return True

    def _get_resource_unit(self, resource_type: ResourceType) -> str:
        """Get unit for resource type"""
        units = {
            ResourceType.COMPUTE: "cores",
            ResourceType.MEMORY: "GB",
            ResourceType.STORAGE: "GB",
            ResourceType.NETWORK: "Mbps",
            ResourceType.API_QUOTA: "calls",
            ResourceType.TOOL_ACCESS: "hours",
            ResourceType.KNOWLEDGE: "items",
            ResourceType.CONTEXT: "KB"
        }
        return units.get(resource_type, "units")

    # Collaboration Session Methods

    async def create_session(
        self,
        initiator_id: str,
        name: str,
        description: str,
        goal: str,
        initial_participants: List[str] = None
    ) -> str:
        """Create a new collaboration session"""
        session = CollaborationSession(
            name=name,
            description=description,
            initiator=initiator_id,
            goal=goal,
            participants=set(initial_participants or [initiator_id])
        )

        self.active_sessions[session.id] = session

        # Track agent participation
        for agent_id in session.participants:
            if agent_id not in self.agent_sessions:
                self.agent_sessions[agent_id] = set()
            self.agent_sessions[agent_id].add(session.id)

        # Notify participants
        await self.broadcast_message(
            initiator_id,
            MessageType.COORDINATION_SIGNAL,
            f"New collaboration session: {name}",
            {
                "session_id": session.id,
                "action": "session_created",
                "goal": goal
            },
            list(session.participants)
        )

        self.logger.info(f"Collaboration session created: {session.id} by {initiator_id}")
        return session.id

    async def join_session(self, session_id: str, agent_id: str) -> bool:
        """Join an existing collaboration session"""
        if session_id not in self.active_sessions:
            return False

        session = self.active_sessions[session_id]
        if agent_id in session.participants:
            return True

        session.participants.add(agent_id)

        if agent_id not in self.agent_sessions:
            self.agent_sessions[agent_id] = set()
        self.agent_sessions[agent_id].add(session_id)

        # Notify session participants
        await self.broadcast_message(
            agent_id,
            MessageType.COORDINATION_SIGNAL,
            f"Agent joined session: {session.name}",
            {
                "session_id": session_id,
                "action": "agent_joined",
                "agent_id": agent_id
            },
            list(session.participants - {agent_id})
        )

        return True

    async def leave_session(self, session_id: str, agent_id: str) -> bool:
        """Leave a collaboration session"""
        if session_id not in self.active_sessions:
            return False

        session = self.active_sessions[session_id]
        if agent_id not in session.participants:
            return True

        session.participants.remove(agent_id)
        self.agent_sessions[agent_id].discard(session_id)

        # If session becomes empty, close it
        if not session.participants:
            await self._close_session(session_id)
        else:
            # Notify remaining participants
            await self.broadcast_message(
                agent_id,
                MessageType.COORDINATION_SIGNAL,
                f"Agent left session: {session.name}",
                {
                    "session_id": session_id,
                    "action": "agent_left",
                    "agent_id": agent_id
                },
                list(session.participants)
            )

        return True

    async def _close_session(self, session_id: str):
        """Close a collaboration session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.active = False
            session.completed_at = datetime.now()
            session.status = "completed"

            # Clean up agent session tracking
            for agent_id in session.participants:
                self.agent_sessions[agent_id].discard(session_id)

            self.logger.info(f"Collaboration session closed: {session_id}")

    # Task Delegation Methods

    async def delegate_task(
        self,
        task_id: str,
        from_agent: str,
        to_agent: str,
        reason: str,
        context: Dict[str, Any] = None
    ) -> Optional[str]:
        """Delegate a task from one agent to another"""
        if to_agent not in self.agent_profiles:
            return None

        # Check if target agent can accept delegation
        if not self._can_accept_delegation(to_agent):
            return None

        delegation = TaskDelegation(
            task_id=task_id,
            original_agent=from_agent,
            delegated_to=to_agent,
            delegated_by=from_agent,
            reason=reason,
            context=context or {}
        )

        self.active_delegations[task_id] = delegation

        # Send delegation message
        await self.send_message(
            from_agent,
            to_agent,
            MessageType.TASK_DELEGATION,
            f"Task delegation: {task_id}",
            {
                "task_id": task_id,
                "delegation_id": delegation.id,
                "reason": reason,
                "context": context
            },
            MessageType.TASK_DELEGATION,
            requires_response=True,
            response_deadline=datetime.now() + timedelta(minutes=30)
        )

        self.logger.info(f"Task delegated: {task_id} from {from_agent} to {to_agent}")
        return delegation.id

    async def accept_delegation(self, delegation_id: str, agent_id: str) -> bool:
        """Accept a task delegation"""
        delegation = self.active_delegations.get(delegation_id)
        if not delegation or delegation.delegated_to != agent_id:
            return False

        delegation.status = "accepted"
        delegation.accepted_at = datetime.now()

        # Notify original agent
        await self.send_message(
            agent_id,
            delegation.original_agent,
            MessageType.STATUS_UPDATE,
            f"Delegation accepted: {delegation.task_id}",
            {
                "delegation_id": delegation_id,
                "status": "accepted"
            }
        )

        return True

    async def complete_delegation(self, delegation_id: str, agent_id: str, result: Dict[str, Any]) -> bool:
        """Complete a delegated task"""
        delegation = self.active_delegations.get(delegation_id)
        if not delegation or delegation.delegated_to != agent_id:
            return False

        delegation.status = "completed"
        delegation.completed_at = datetime.now()
        delegation.result = result

        # Notify original agent
        await self.send_message(
            agent_id,
            delegation.original_agent,
            MessageType.STATUS_UPDATE,
            f"Delegation completed: {delegation.task_id}",
            {
                "delegation_id": delegation_id,
                "status": "completed",
                "result": result
            }
        )

        # Clean up
        del self.active_delegations[delegation_id]

        return True

    def _can_accept_delegation(self, agent_id: str) -> bool:
        """Check if agent can accept task delegation"""
        profile = self.agent_profiles.get(agent_id)
        if not profile:
            return False

        # Check current load
        if profile.current_load > 0.8:  # Over 80% capacity
            return False

        # Check availability
        return profile.available

    # Agent Profile Management

    def register_agent_profile(self, profile: AgentProfile):
        """Register an agent profile for collaboration"""
        self.agent_profiles[profile.agent_id] = profile
        self.logger.info(f"Agent profile registered: {profile.agent_id}")

    def update_agent_status(self, agent_id: str, available: bool = None, load: float = None):
        """Update agent status"""
        if agent_id in self.agent_profiles:
            profile = self.agent_profiles[agent_id]
            if available is not None:
                profile.available = available
            if load is not None:
                profile.current_load = load

    def get_collaboration_candidates(
        self,
        requester_id: str,
        required_capabilities: List[str] = None,
        max_candidates: int = 5
    ) -> List[AgentProfile]:
        """Find suitable agents for collaboration"""
        candidates = []

        for profile in self.agent_profiles.values():
            if profile.agent_id == requester_id:
                continue

            # Check availability
            if not profile.available or profile.current_load > 0.8:
                continue

            # Check capabilities
            if required_capabilities:
                if not all(cap in profile.capabilities for cap in required_capabilities):
                    continue

            candidates.append(profile)

        # Sort by trust score and load
        candidates.sort(key=lambda p: (self.agent_relationships.get(requester_id, {}).get(p.agent_id, 0.5), p.current_load), reverse=True)

        return candidates[:max_candidates]

    # Background Tasks

    async def _resource_cleanup_task(self):
        """Clean up expired resource allocations"""
        while True:
            try:
                await asyncio.sleep(self.resource_cleanup_interval.total_seconds())

                expired = []
                for alloc_id, allocation in self.resource_allocations.items():
                    if (allocation.expires_at and datetime.now() > allocation.expires_at and allocation.active):
                        expired.append(alloc_id)

                for alloc_id in expired:
                    await self.release_resource(alloc_id)
                    self.logger.info(f"Auto-released expired resource: {alloc_id}")

            except Exception as e:
                self.logger.error(f"Error in resource cleanup: {e}")

    async def _session_monitor(self):
        """Monitor and maintain collaboration sessions"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes

                expired_sessions = []
                for session_id, session in self.active_sessions.items():
                    if session.created_at + self.max_session_duration < datetime.now():
                        expired_sessions.append(session_id)

                for session_id in expired_sessions:
                    await self._close_session(session_id)
                    self.logger.info(f"Auto-closed expired session: {session_id}")

            except Exception as e:
                self.logger.error(f"Error in session monitor: {e}")

    async def _monitor_response_deadline(self, message: AgentMessage):
        """Monitor response deadline for messages"""
        if not message.response_deadline:
            return

        delay = (message.response_deadline - datetime.now()).total_seconds()
        if delay > 0:
            await asyncio.sleep(delay)

        # Check if response was received
        if not message.responded:
            self.logger.warning(f"Message response deadline exceeded: {message.id}")

    async def _track_message_in_sessions(self, message: AgentMessage):
        """Track message in relevant collaboration sessions"""
        # Find sessions where both sender and receiver are participants
        for session in self.active_sessions.values():
            if (message.sender_id in session.participants and
                message.receiver_id in session.participants):
                session.messages_exchanged += 1

    # Query Methods

    def get_active_sessions(self, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get active collaboration sessions"""
        sessions = []
        for session in self.active_sessions.values():
            if session.active and (not agent_id or agent_id in session.participants):
                sessions.append(session.to_dict())
        return sessions

    def get_agent_sessions(self, agent_id: str) -> List[str]:
        """Get session IDs for an agent"""
        return list(self.agent_sessions.get(agent_id, set()))

    def get_resource_usage(self) -> Dict[str, Any]:
        """Get current resource usage statistics"""
        usage = {}
        for resource_type, pool in self.resource_pools.items():
            usage[resource_type.value] = {
                "total": pool["total"],
                "available": pool["available"],
                "utilization": (pool["total"] - pool["available"]) / pool["total"] if pool["total"] > 0 else 0,
                "allocations": len(pool["allocations"])
            }
        return usage

    def get_collaboration_stats(self) -> Dict[str, Any]:
        """Get collaboration statistics"""
        return {
            "active_sessions": len(self.active_sessions),
            "registered_agents": len(self.agent_profiles),
            "active_delegations": len(self.active_delegations),
            "total_messages": sum(session.messages_exchanged for session in self.active_sessions.values())
        }

# Global collaboration hub instance
collaboration_hub = AgentCollaborationHub()

# Helper functions for easy integration

async def initialize_collaboration():
    """Initialize the collaboration system"""
    await collaboration_hub.initialize()

async def create_collaboration_session(name: str, description: str, goal: str, participants: List[str]) -> str:
    """Helper to create a collaboration session"""
    return await collaboration_hub.create_session(
        initiator_id=participants[0],
        name=name,
        description=description,
        goal=goal,
        initial_participants=participants
    )

async def send_agent_message(sender: str, receiver: str, msg_type: MessageType, subject: str, content: Dict[str, Any]) -> str:
    """Helper to send messages between agents"""
    return await collaboration_hub.send_message(sender, receiver, msg_type, subject, content)
