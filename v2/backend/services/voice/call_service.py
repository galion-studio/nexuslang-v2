"""
Voice-to-Voice Call Service
Real-time AI voice conversations using WebSocket
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Optional
import asyncio
import json
import base64
from datetime import datetime

# Import voice services
from .stt_service import get_stt_service
from .tts_service import get_tts_service


class VoiceCallSession:
    """Manages a single voice call session"""
    
    def __init__(self, session_id: str, user_id: str):
        self.session_id = session_id
        self.user_id = user_id
        self.created_at = datetime.utcnow()
        self.is_active = True
        self.conversation_history = []
    
    async def process_audio(self, audio_data: bytes) -> Dict:
        """
        Process incoming audio: STT → AI → TTS
        
        Args:
            audio_data: Raw audio bytes from user
            
        Returns:
            Dict with response audio and text
        """
        try:
            # Step 1: Speech-to-Text
            stt_service = get_stt_service()
            transcribed = await stt_service.transcribe(audio_data)
            user_text = transcribed.get("text", "")
            
            if not user_text:
                return {"error": "Could not transcribe audio"}
            
            # Step 2: AI Processing (via OpenRouter)
            # Use existing AI router to generate response
            from ..ai.ai_router import get_ai_router
            
            ai = get_ai_router()
            ai_response = await ai.chat_completion(
                messages=self.conversation_history + [
                    {"role": "user", "content": user_text}
                ],
                model="anthropic/claude-3.5-sonnet",
                temperature=0.7,
                max_tokens=500
            )
            
            response_text = ai_response.get("content", "")
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_text})
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            # Keep only last 10 messages
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]
            
            # Step 3: Text-to-Speech
            tts_service = get_tts_service()
            audio_response = await tts_service.synthesize(
                text=response_text,
                voice_id="default",
                emotion="friendly"
            )
            
            # Encode audio as base64 for transmission
            audio_base64 = base64.b64encode(audio_response).decode('utf-8')
            
            return {
                "user_text": user_text,
                "ai_text": response_text,
                "audio_base64": audio_base64,
                "session_id": self.session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Voice call processing error: {e}")
            return {"error": str(e)}


class VoiceCallService:
    """Service for managing voice call sessions"""
    
    def __init__(self):
        self.active_sessions: Dict[str, VoiceCallSession] = {}
    
    def create_session(self, user_id: str) -> str:
        """Create new voice call session"""
        import uuid
        session_id = str(uuid.uuid4())
        
        session = VoiceCallSession(session_id, user_id)
        self.active_sessions[session_id] = session
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[VoiceCallSession]:
        """Get existing session"""
        return self.active_sessions.get(session_id)
    
    def end_session(self, session_id: str):
        """End and clean up session"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session.is_active = False
            del self.active_sessions[session_id]
    
    async def handle_websocket(self, websocket: WebSocket, user_id: str):
        """
        Handle WebSocket connection for voice call.
        
        Protocol:
        - Client sends: {"type": "audio", "data": base64_audio}
        - Server responds: {"type": "response", "audio": base64_audio, "text": transcription}
        """
        # Create session
        session_id = self.create_session(user_id)
        session = self.get_session(session_id)
        
        try:
            await websocket.accept()
            
            # Send session info
            await websocket.send_json({
                "type": "session_start",
                "session_id": session_id,
                "message": "Voice call connected. Start speaking!"
            })
            
            while session.is_active:
                # Receive audio data
                data = await websocket.receive_json()
                
                if data.get("type") == "audio":
                    # Decode base64 audio
                    audio_base64 = data.get("data", "")
                    audio_bytes = base64.b64decode(audio_base64)
                    
                    # Process audio
                    result = await session.process_audio(audio_bytes)
                    
                    # Send response
                    await websocket.send_json({
                        "type": "response",
                        "user_text": result.get("user_text"),
                        "ai_text": result.get("ai_text"),
                        "audio": result.get("audio_base64"),
                        "timestamp": result.get("timestamp")
                    })
                
                elif data.get("type") == "end":
                    break
        
        except WebSocketDisconnect:
            print(f"Voice call disconnected: {session_id}")
        
        finally:
            self.end_session(session_id)


# Global service instance
_voice_call_service = None

def get_voice_call_service() -> VoiceCallService:
    """Get voice call service instance"""
    global _voice_call_service
    if _voice_call_service is None:
        _voice_call_service = VoiceCallService()
    return _voice_call_service

