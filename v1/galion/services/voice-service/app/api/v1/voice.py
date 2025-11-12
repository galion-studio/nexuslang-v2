"""
Voice WebSocket API - Real-time voice interaction
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging
from typing import Optional

from app.services.stt_service import stt_service
from app.services.tts_service import tts_service
from app.services.intent_service import intent_service
from app.services.router_service import router_service
from app.middleware.auth import verify_websocket_token

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/stream")
async def voice_stream(
    websocket: WebSocket,
    token: Optional[str] = None
):
    """
    WebSocket endpoint for real-time voice interaction
    
    Flow:
    1. Client connects with JWT token
    2. Client sends binary audio chunks
    3. Server transcribes (STT)
    4. Server classifies intent
    5. Server executes action
    6. Server generates response text
    7. Server converts to speech (TTS)
    8. Server sends audio back to client
    """
    await websocket.accept()
    
    user_email = None
    
    try:
        # Verify authentication
        user_email = await verify_websocket_token(websocket, token)
        if not user_email:
            await websocket.send_json({
                "type": "error",
                "message": "Authentication required. Please provide a valid JWT token."
            })
            await websocket.close(code=1008, reason="Unauthorized")
            return
        
        logger.info(f"🎙️ Voice WebSocket connected for user: {user_email}")
        
        # Send welcome message
        await websocket.send_json({
            "type": "connected",
            "message": "Voice assistant ready! Start speaking or send audio.",
            "user": user_email
        })
        
        # Audio buffer for streaming
        audio_buffer = bytearray()
        
        while True:
            # Receive data from client
            data = await websocket.receive()
            
            if "bytes" in data:
                # Binary audio data
                audio_chunk = data["bytes"]
                audio_buffer.extend(audio_chunk)
                
                # Send acknowledgment
                await websocket.send_json({
                    "type": "receiving",
                    "buffer_size": len(audio_buffer)
                })
                
            elif "text" in data:
                # Text command (audio stream complete or text fallback)
                message = json.loads(data["text"])
                
                if message.get("type") == "audio_complete":
                    # Process complete audio
                    await process_voice_command(
                        websocket,
                        user_email,
                        bytes(audio_buffer),
                        message.get("format", "webm"),
                        token
                    )
                    audio_buffer.clear()
                
                elif message.get("type") == "text_fallback":
                    # Process text command directly
                    await process_text_command(
                        websocket,
                        user_email,
                        message.get("text", ""),
                        token
                    )
                
                elif message.get("type") == "ping":
                    # Keepalive ping
                    await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        logger.info(f"👋 Voice WebSocket disconnected for user: {user_email or 'unknown'}")
    except Exception as e:
        logger.error(f"❌ WebSocket error: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"An error occurred: {str(e)}"
            })
        except:
            pass


async def process_voice_command(
    websocket: WebSocket,
    user_email: str,
    audio_data: bytes,
    audio_format: str,
    jwt_token: Optional[str] = None
):
    """Process voice command through full pipeline"""
    try:
        # 1. Speech-to-Text
        await websocket.send_json({"type": "status", "message": "Transcribing your voice..."})
        
        stt_result = await stt_service.transcribe(audio_data, format=audio_format)
        transcript = stt_result["text"]
        
        await websocket.send_json({
            "type": "transcript",
            "text": transcript,
            "confidence": stt_result["confidence"],
            "language": stt_result["language"]
        })
        
        # 2. Intent Classification
        await websocket.send_json({"type": "status", "message": "Understanding your request..."})
        
        intent_result = await intent_service.classify_intent(transcript)
        
        await websocket.send_json({
            "type": "intent",
            "intent": intent_result["intent"],
            "entities": intent_result["entities"],
            "confidence": intent_result["confidence"]
        })
        
        # Check if clarification needed
        if intent_result.get("needs_clarification"):
            response_text = intent_result.get("clarification_question", "Could you clarify what you mean?")
        else:
            # 3. Execute Action
            await websocket.send_json({"type": "status", "message": "Processing your request..."})
            
            response_text = await router_service.execute_intent(
                user_email,
                intent_result["intent"],
                intent_result["entities"],
                jwt_token
            )
        
        await websocket.send_json({
            "type": "response",
            "text": response_text
        })
        
        # 4. Text-to-Speech
        await websocket.send_json({"type": "status", "message": "Generating voice response..."})
        
        audio_response = await tts_service.synthesize(response_text)
        
        # Send audio
        await websocket.send_json({
            "type": "audio_start",
            "format": "mp3",
            "size": len(audio_response)
        })
        await websocket.send_bytes(audio_response)
        await websocket.send_json({"type": "audio_complete"})
        
        logger.info(f"✅ Voice command processed successfully for {user_email}")
        
    except Exception as e:
        logger.error(f"❌ Voice processing error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": "Sorry, I encountered an error processing your request. Please try again."
        })


async def process_text_command(
    websocket: WebSocket,
    user_email: str,
    text: str,
    jwt_token: Optional[str] = None
):
    """Process text command (skip STT)"""
    try:
        logger.info(f"💬 Processing text command: '{text}' from {user_email}")
        
        # Show what was received
        await websocket.send_json({
            "type": "transcript",
            "text": text,
            "confidence": 1.0,
            "language": "en"
        })
        
        # Intent classification
        await websocket.send_json({"type": "status", "message": "Understanding your request..."})
        
        intent_result = await intent_service.classify_intent(text)
        
        await websocket.send_json({
            "type": "intent",
            "intent": intent_result["intent"],
            "entities": intent_result["entities"],
            "confidence": intent_result["confidence"]
        })
        
        # Execute action
        if intent_result.get("needs_clarification"):
            response_text = intent_result.get("clarification_question", "Could you clarify?")
        else:
            response_text = await router_service.execute_intent(
                user_email,
                intent_result["intent"],
                intent_result["entities"],
                jwt_token
            )
        
        await websocket.send_json({
            "type": "response",
            "text": response_text
        })
        
        # TTS
        await websocket.send_json({"type": "status", "message": "Generating voice..."})
        
        audio_response = await tts_service.synthesize(response_text)
        
        await websocket.send_json({
            "type": "audio_start",
            "format": "mp3",
            "size": len(audio_response)
        })
        await websocket.send_bytes(audio_response)
        await websocket.send_json({"type": "audio_complete"})
        
        logger.info(f"✅ Text command processed successfully for {user_email}")
        
    except Exception as e:
        logger.error(f"❌ Text processing error: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })

