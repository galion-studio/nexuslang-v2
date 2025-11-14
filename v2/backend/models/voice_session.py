"""
Voice Session Model - Database model for voice interaction tracking
Tracks voice sessions, commands, and usage analytics
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from ..core.database import Base


class VoiceSession(Base):
    """
    Voice Session model for tracking voice interaction sessions

    Records session metadata, duration, and usage statistics
    for analytics and billing purposes.
    """
    __tablename__ = "voice_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(50), nullable=False)  # galion-app, developer-platform, galion-studio
    session_type = Column(String(20), default="conversation")  # conversation, command, tutorial
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    ended_at = Column(DateTime)
    duration_seconds = Column(Integer)
    commands_count = Column(Integer, default=0)
    transcription_accuracy = Column(Float)  # Average accuracy across session
    credits_used = Column(Integer, default=0)
    total_audio_bytes = Column(Integer, default=0)
    language = Column(String(10), default="en")
    client_info = Column(JSONB)  # Browser, OS, device info
    metadata = Column(JSONB)  # Additional session metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User")
    commands = relationship("VoiceCommand", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<VoiceSession(id={self.id}, user_id={self.user_id}, platform={self.platform}, duration={self.duration_seconds}s)>"

    @property
    def is_active(self) -> bool:
        """Check if session is currently active"""
        return self.ended_at is None

    @property
    def duration_display(self) -> str:
        """Get human-readable duration"""
        if not self.duration_seconds:
            return "0s"

        minutes = self.duration_seconds // 60
        seconds = self.duration_seconds % 60

        if minutes > 0:
            return f"{minutes}m {seconds}s"
        return f"{seconds}s"

    @property
    def cost_estimate(self) -> float:
        """Estimate cost based on credits used"""
        # Assuming 1 credit = $0.01
        return self.credits_used * 0.01

    def end_session(self):
        """End the voice session and calculate duration"""
        if self.ended_at is None:
            self.ended_at = datetime.utcnow()
            if self.started_at:
                self.duration_seconds = int((self.ended_at - self.started_at).total_seconds())

    def add_command(self, transcription: str, response_text: str = None, credits: int = 1):
        """Add a voice command to this session"""
        self.commands_count += 1
        self.credits_used += credits

        # Create voice command record
        command = VoiceCommand(
            session_id=self.id,
            user_id=self.user_id,
            transcription=transcription,
            response_text=response_text,
            credits_used=credits
        )

        self.commands.append(command)

    def update_accuracy(self, accuracy: float):
        """Update transcription accuracy (moving average)"""
        if self.transcription_accuracy is None:
            self.transcription_accuracy = accuracy
        else:
            # Weighted average favoring recent accuracy
            self.transcription_accuracy = (self.transcription_accuracy * 0.7) + (accuracy * 0.3)


class VoiceCommand(Base):
    """
    Voice Command model for individual voice interactions

    Tracks each transcription, response, and processing metrics
    """
    __tablename__ = "voice_commands"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("voice_sessions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    transcription = Column(Text, nullable=False)
    transcription_confidence = Column(Float)
    intent = Column(String(100))  # Detected intent (if available)
    response_text = Column(Text)
    response_audio_url = Column(String(500))  # URL to generated audio
    credits_used = Column(Integer, default=1)
    processing_time_ms = Column(Integer)  # How long it took to process
    error_message = Column(Text)  # Any errors that occurred
    metadata = Column(JSONB)  # Additional command metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    session = relationship("VoiceSession", back_populates="commands")
    user = relationship("User")

    def __repr__(self):
        return f"<VoiceCommand(id={self.id}, session_id={self.session_id}, transcription='{self.transcription[:50]}...')>"

    @property
    def has_error(self) -> bool:
        """Check if command had an error"""
        return self.error_message is not None

    @property
    def cost(self) -> float:
        """Calculate cost for this command"""
        return self.credits_used * 0.01

    def mark_error(self, error_message: str):
        """Mark command as having an error"""
        self.error_message = error_message

    def set_response(self, text: str, audio_url: str = None):
        """Set the response for this command"""
        self.response_text = text
        if audio_url:
            self.response_audio_url = audio_url
