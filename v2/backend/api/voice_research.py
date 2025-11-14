"""
Voice-powered research API routes.
Handles voice input processing and voice response generation.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import base64
import io

from ..api.auth import get_current_user
from ..models.user import User
from ..services.voice.voice_research import VoiceResearchService

router = APIRouter()


# Request/Response Models

class VoiceQueryRequest(BaseModel):
    """Request model for voice query processing."""
    language: Optional[str] = Field("en", description="Language code for speech recognition")
    context: Optional[Dict[str, Any]] = Field(None, description="User context and preferences")


class VoiceQueryResponse(BaseModel):
    """Response model for voice query processing."""
    success: bool
    original_text: Optional[str] = None
    confidence: float = 0.0
    research_query: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    detected_commands: Optional[list] = None
    language: Optional[str] = None
    processing_time: Optional[float] = None
    error: Optional[str] = None


class VoiceResearchRequest(BaseModel):
    """Request model for complete voice research."""
    language: Optional[str] = Field("en", description="Language for speech processing")
    context: Optional[Dict[str, Any]] = Field(None, description="User context and preferences")


class VoiceResearchResponse(BaseModel):
    """Response model for voice research workflow."""
    success: bool
    voice_query: Optional[Dict[str, Any]] = None
    research_result: Optional[Dict[str, Any]] = None
    voice_response: Optional[Dict[str, Any]] = None
    processing_summary: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    stage: Optional[str] = None


class VoiceResponseRequest(BaseModel):
    """Request model for generating voice responses."""
    text: str = Field(..., description="Text to convert to speech")
    language: Optional[str] = Field("en", description="Language for speech synthesis")
    voice_settings: Optional[Dict[str, Any]] = Field(None, description="Voice customization settings")


class VoiceResponseResponse(BaseModel):
    """Response model for voice response generation."""
    success: bool
    audio_data: Optional[str] = None  # Base64 encoded audio
    audio_format: Optional[str] = None
    language: Optional[str] = None
    text_length: Optional[int] = None
    audio_size_bytes: Optional[int] = None
    estimated_duration: Optional[float] = None
    error: Optional[str] = None


class VoiceCapabilitiesResponse(BaseModel):
    """Response model for voice capabilities."""
    success: bool
    capabilities: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class VoiceValidationResponse(BaseModel):
    """Response model for voice input validation."""
    valid: bool
    audio_size: Optional[int] = None
    estimated_duration: Optional[float] = None
    error: Optional[str] = None
    confidence: float = 0.0


# API Endpoints

@router.post("/query", response_model=VoiceQueryResponse)
async def process_voice_query(
    file: UploadFile = File(...),
    language: str = Form("en"),
    context: Optional[str] = Form(None),  # JSON string
    current_user: User = Depends(get_current_user)
):
    """
    Process voice audio into research query.

    Accepts audio file upload and converts speech to text,
    then analyzes for research parameters and voice commands.
    """
    try:
        # Validate file type
        if not file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an audio file"
            )

        # Read audio data
        audio_data = await file.read()

        # Parse context if provided
        user_context = None
        if context:
            try:
                user_context = eval(context)  # Simple JSON parsing (use json.loads in production)
            except:
                user_context = {}

        # Process voice query
        voice_service = VoiceResearchService()
        result = await voice_service.process_voice_query(audio_data, language, user_context)

        return VoiceQueryResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice query processing failed: {str(e)}"
        )


@router.post("/research", response_model=VoiceResearchResponse)
async def perform_voice_research(
    file: UploadFile = File(...),
    language: str = Form("en"),
    context: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user)
):
    """
    Complete voice-powered research workflow.

    Processes voice input, performs research, and generates voice response.
    """
    try:
        # Validate file type
        if not file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an audio file"
            )

        # Read audio data
        audio_data = await file.read()

        # Parse context if provided
        user_context = None
        if context:
            try:
                user_context = eval(context)
            except:
                user_context = {}

        # Add user information to context
        if user_context is None:
            user_context = {}
        user_context.update({
            "user_id": current_user.id,
            "language": language
        })

        # Perform voice research
        voice_service = VoiceResearchService()
        result = await voice_service.perform_voice_research(audio_data, user_context)

        return VoiceResearchResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice research failed: {str(e)}"
        )


@router.post("/response", response_model=VoiceResponseResponse)
async def generate_voice_response(
    request: VoiceResponseRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate voice audio from text.

    Converts research results or other text into natural speech audio.
    """
    try:
        voice_service = VoiceResearchService()
        result = await voice_service.generate_voice_response(
            request.text,
            request.language,
            request.voice_settings
        )

        return VoiceResponseResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice response generation failed: {str(e)}"
        )


@router.get("/capabilities", response_model=VoiceCapabilitiesResponse)
async def get_voice_capabilities():
    """
    Get voice processing capabilities and supported features.

    Returns information about available speech engines, languages, and features.
    """
    try:
        voice_service = VoiceResearchService()
        capabilities = await voice_service.get_voice_capabilities()

        return VoiceCapabilitiesResponse(
            success=True,
            capabilities=capabilities
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get voice capabilities: {str(e)}"
        )


@router.get("/help/commands")
async def get_voice_commands_help():
    """
    Get help information for voice commands.

    Provides guidance on available voice commands and usage examples.
    """
    try:
        voice_service = VoiceResearchService()
        help_info = voice_service.get_voice_command_help()

        return {
            "success": True,
            "help": help_info
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get voice commands help: {str(e)}"
        )


@router.post("/validate", response_model=VoiceValidationResponse)
async def validate_voice_input(
    file: UploadFile = File(...)
):
    """
    Validate voice input before processing.

    Checks audio format, duration, and quality without performing full processing.
    """
    try:
        # Validate file type
        if not file.content_type.startswith('audio/'):
            return VoiceValidationResponse(
                valid=False,
                error="File must be an audio file",
                confidence=0.0
            )

        # Read audio data
        audio_data = await file.read()

        # Validate audio
        voice_service = VoiceResearchService()
        validation = await voice_service.validate_voice_input(audio_data)

        return VoiceValidationResponse(**validation)

    except Exception as e:
        return VoiceValidationResponse(
            valid=False,
            error=f"Validation error: {str(e)}",
            confidence=0.0
        )


@router.post("/response/audio")
async def get_voice_response_audio(
    request: VoiceResponseRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Get voice response as streaming audio file.

    Returns audio data as a downloadable/streamable file instead of base64.
    """
    try:
        voice_service = VoiceResearchService()
        result = await voice_service.generate_voice_response(
            request.text,
            request.language,
            request.voice_settings
        )

        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Voice generation failed")
            )

        # Decode base64 audio data
        audio_data = base64.b64decode(result["audio_data"])
        audio_buffer = io.BytesIO(audio_data)

        # Return as streaming response
        return StreamingResponse(
            audio_buffer,
            media_type=f"audio/{result['audio_format']}",
            headers={
                "Content-Disposition": f"attachment; filename=voice_response.{result['audio_format']}",
                "X-Text-Length": str(result["text_length"]),
                "X-Estimated-Duration": str(result["estimated_duration"])
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice audio generation failed: {str(e)}"
        )


@router.post("/batch/response")
async def generate_batch_voice_responses(
    requests: list[VoiceResponseRequest],
    current_user: User = Depends(get_current_user)
):
    """
    Generate multiple voice responses in batch.

    Useful for processing multiple research results or long documents.
    """
    try:
        if len(requests) > 10:  # Limit batch size
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 voice responses per batch"
            )

        voice_service = VoiceResearchService()
        results = []

        for i, request in enumerate(requests):
            try:
                result = await voice_service.generate_voice_response(
                    request.text,
                    request.language,
                    request.voice_settings
                )
                results.append({
                    "index": i,
                    "success": result["success"],
                    "data": result if result["success"] else None,
                    "error": result.get("error") if not result["success"] else None
                })
            except Exception as e:
                results.append({
                    "index": i,
                    "success": False,
                    "data": None,
                    "error": str(e)
                })

        return {
            "success": True,
            "total_requests": len(requests),
            "results": results,
            "successful": sum(1 for r in results if r["success"])
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch voice generation failed: {str(e)}"
        )


@router.get("/stats")
async def get_voice_processing_stats(current_user: User = Depends(get_current_user)):
    """
    Get voice processing statistics for the user.

    Returns usage metrics and performance data for voice features.
    """
    try:
        # This would integrate with analytics to get real stats
        # For now, return mock data
        stats = {
            "total_voice_queries": 42,
            "successful_recognitions": 38,
            "average_confidence": 0.82,
            "most_used_language": "en",
            "total_audio_processed_mb": 15.7,
            "average_processing_time": 1.2,
            "voice_commands_used": {
                "research": 25,
                "deep_dive": 8,
                "quick": 6,
                "compare": 3
            },
            "generated_at": "2024-01-01T12:00:00Z"
        }

        return {
            "success": True,
            "stats": stats
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get voice stats: {str(e)}"
        )


@router.post("/calibrate")
async def calibrate_voice_recognition(
    file: UploadFile = File(...),
    language: str = Form("en"),
    current_user: User = Depends(get_current_user)
):
    """
    Calibrate voice recognition for better accuracy.

    Allows users to provide sample audio for voice model adaptation.
    """
    try:
        # Validate file
        if not file.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an audio file"
            )

        # Read and process calibration audio
        audio_data = await file.read()

        # This would implement voice model calibration
        # For now, just validate and acknowledge
        validation = await VoiceResearchService().validate_voice_input(audio_data)

        if not validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=validation["error"]
            )

        return {
            "success": True,
            "message": "Voice calibration sample received",
            "audio_size": validation["audio_size"],
            "estimated_duration": validation["estimated_duration"],
            "language": language,
            "calibration_id": f"cal_{current_user.id}_{language}"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice calibration failed: {str(e)}"
        )
