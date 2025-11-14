"""
Voice Training API
REST API endpoints for voice-to-voice AI training integration
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from pydantic import BaseModel, Field
from enum import Enum

from ...ai.training.voice_platform_integration import (
    voice_platform_integration,
    GalionPlatform,
    PlatformIntegrationConfig
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice-training", tags=["voice-training"])

# Request/Response Models

class PlatformEnum(str, Enum):
    GALION_APP = "galion_app"
    DEVELOPER_PLATFORM = "developer_platform"
    GALION_STUDIO = "galion_studio"
    ADMIN_DASHBOARD = "admin_dashboard"

class VoiceSessionRequest(BaseModel):
    platform: PlatformEnum
    user_id: str
    config: Optional[Dict[str, Any]] = None

class VoiceSessionResponse(BaseModel):
    conversation_id: str
    platform: str
    agent_type: str
    session_started: bool

class VoiceInputRequest(BaseModel):
    conversation_id: str
    platform: PlatformEnum

class VoiceProfileCreateRequest(BaseModel):
    platform: PlatformEnum
    name: str
    description: Optional[str] = ""
    engine: str = "speecht5"
    model_path: Optional[str] = None
    language: str = "en"
    gender: Optional[str] = "neutral"
    accent: Optional[str] = "neutral"

class VoiceTrainingRequest(BaseModel):
    platform: PlatformEnum
    training_type: str = "speech_recognition"  # speech_recognition, text_to_speech
    dataset_config: Dict[str, Any]
    training_config: Dict[str, Any]

class VideoProcessingRequest(BaseModel):
    platform: PlatformEnum
    video_url: str
    source: str = "youtube"  # youtube, local_file, url
    target_speaker: Optional[str] = None
    language: str = "en"
    min_segment_length: float = 2.0
    max_segment_length: float = 10.0
    quality_threshold: float = 0.6

class DataCollectionRequest(BaseModel):
    platform: PlatformEnum
    session_name: str
    description: Optional[str] = ""
    target_speaker: Optional[str] = None
    target_language: str = "en"
    target_accent: Optional[str] = "neutral"
    source: str = "microphone"  # microphone, upload, youtube, video_file

class PlatformConfigUpdateRequest(BaseModel):
    voice_features_enabled: Optional[bool] = None
    custom_voice_training_enabled: Optional[bool] = None
    real_time_voice_enabled: Optional[bool] = None
    video_training_enabled: Optional[bool] = None
    agent_orchestration_enabled: Optional[bool] = None

# API Endpoints

@router.get("/platforms/{platform}/config")
async def get_platform_config(platform: PlatformEnum):
    """Get voice configuration for a specific platform"""
    try:
        config = await voice_platform_integration.get_platform_voice_config(
            GalionPlatform(platform.value)
        )
        return config
    except Exception as e:
        logger.error(f"Failed to get platform config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/platforms/{platform}/config")
async def update_platform_config(platform: PlatformEnum, config: PlatformConfigUpdateRequest):
    """Update voice configuration for a specific platform"""
    try:
        result = await voice_platform_integration.configure_platform_voice_features(
            GalionPlatform(platform.value),
            config.dict(exclude_unset=True)
        )
        return result
    except Exception as e:
        logger.error(f"Failed to update platform config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/start")
async def start_voice_session(request: VoiceSessionRequest):
    """Start a voice session for a platform"""
    try:
        result = await voice_platform_integration.start_platform_voice_session(
            GalionPlatform(request.platform.value),
            request.user_id,
            request.config
        )
        return VoiceSessionResponse(**result)
    except Exception as e:
        logger.error(f"Failed to start voice session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{conversation_id}/process")
async def process_voice_input(
    conversation_id: str,
    request: VoiceInputRequest,
    audio_file: UploadFile = File(...)
):
    """Process voice input for a conversation"""
    try:
        # Read audio data
        audio_data = await audio_file.read()

        result = await voice_platform_integration.process_platform_voice_input(
            GalionPlatform(request.platform.value),
            conversation_id,
            audio_data
        )
        return result
    except Exception as e:
        logger.error(f"Failed to process voice input: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{conversation_id}")
async def end_voice_session(conversation_id: str, platform: PlatformEnum):
    """End a voice session"""
    try:
        # Note: This would need to be implemented in the integration class
        # For now, return success
        return {"conversation_id": conversation_id, "session_ended": True}
    except Exception as e:
        logger.error(f"Failed to end voice session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{conversation_id}/status")
async def get_session_status(conversation_id: str, platform: PlatformEnum):
    """Get status of a voice session"""
    try:
        # Note: This would need to be implemented in the integration class
        # For now, return mock status
        return {
            "conversation_id": conversation_id,
            "platform": platform.value,
            "status": "active",
            "last_activity": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get session status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice-profiles/create")
async def create_voice_profile(request: VoiceProfileCreateRequest):
    """Create a custom voice profile"""
    try:
        profile_config = {
            'name': request.name,
            'description': request.description,
            'engine': request.engine,
            'model_path': request.model_path,
            'language': request.language,
            'gender': request.gender,
            'accent': request.accent
        }

        result = await voice_platform_integration.create_platform_voice_profile(
            GalionPlatform(request.platform.value),
            profile_config
        )
        return result
    except Exception as e:
        logger.error(f"Failed to create voice profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voice-profiles/list")
async def list_voice_profiles(platform: PlatformEnum):
    """List voice profiles for a platform"""
    try:
        # Note: This would need to be implemented in the integration class
        # For now, return empty list
        return {"platform": platform.value, "voice_profiles": []}
    except Exception as e:
        logger.error(f"Failed to list voice profiles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/training/start")
async def start_voice_training(request: VoiceTrainingRequest):
    """Start voice model training"""
    try:
        result = await voice_platform_integration.start_platform_voice_training(
            GalionPlatform(request.platform.value),
            {
                'type': request.training_type,
                'dataset': request.dataset_config,
                'training': request.training_config
            }
        )
        return result
    except Exception as e:
        logger.error(f"Failed to start voice training: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/training/jobs/{job_id}")
async def get_training_job_status(job_id: str, platform: PlatformEnum):
    """Get status of a training job"""
    try:
        # Note: This would need to be implemented in the respective training classes
        # For now, return mock status
        return {
            "job_id": job_id,
            "platform": platform.value,
            "status": "running",
            "progress": 50.0,
            "created_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get training job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/video-processing/start")
async def start_video_processing(request: VideoProcessingRequest):
    """Start video processing for voice training"""
    try:
        result = await voice_platform_integration.process_platform_video_for_training(
            GalionPlatform(request.platform.value),
            {
                'video_url': request.video_url,
                'source': request.source,
                'target_speaker': request.target_speaker,
                'language': request.language,
                'min_segment_length': request.min_segment_length,
                'max_segment_length': request.max_segment_length,
                'quality_threshold': request.quality_threshold
            }
        )
        return result
    except Exception as e:
        logger.error(f"Failed to start video processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/video-processing/jobs/{job_id}")
async def get_video_processing_status(job_id: str, platform: PlatformEnum):
    """Get status of video processing job"""
    try:
        # Note: This would need to be implemented in the video pipeline class
        # For now, return mock status
        return {
            "job_id": job_id,
            "platform": platform.value,
            "status": "processing",
            "progress": 75.0,
            "created_at": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get video processing status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/data-collection/start")
async def start_data_collection(request: DataCollectionRequest):
    """Start voice data collection"""
    try:
        result = await voice_platform_integration.collect_platform_voice_data(
            GalionPlatform(request.platform.value),
            {
                'name': request.session_name,
                'description': request.description,
                'target_speaker': request.target_speaker,
                'target_language': request.target_language,
                'target_accent': request.target_accent,
                'source': request.source
            }
        )
        return result
    except Exception as e:
        logger.error(f"Failed to start data collection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/data-collection/upload")
async def upload_voice_data(
    platform: PlatformEnum,
    session_id: str,
    transcript: Optional[str] = Form(None),
    audio_file: UploadFile = File(...)
):
    """Upload voice data for training"""
    try:
        # Read audio data
        audio_data = await audio_file.read()

        # This would integrate with the data collector
        # For now, return success
        return {
            "platform": platform.value,
            "session_id": session_id,
            "upload_success": True,
            "file_size": len(audio_data),
            "filename": audio_file.filename
        }
    except Exception as e:
        logger.error(f"Failed to upload voice data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/unified")
async def get_unified_status():
    """Get unified voice status across all platforms"""
    try:
        status = await voice_platform_integration.get_unified_voice_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get unified status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/platforms/{platform}/status")
async def get_platform_status(platform: PlatformEnum):
    """Get voice status for a specific platform"""
    try:
        unified_status = await voice_platform_integration.get_unified_voice_status()
        platform_status = unified_status['platforms'].get(platform.value)

        if not platform_status:
            raise HTTPException(status_code=404, detail=f"Platform {platform.value} not found")

        return platform_status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get platform status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/data/share")
async def share_voice_data(
    source_platform: PlatformEnum,
    target_platforms: List[PlatformEnum],
    data_ids: List[str]
):
    """Share voice data across platforms"""
    try:
        result = await voice_platform_integration.share_voice_data_across_platforms(
            GalionPlatform(source_platform.value),
            [GalionPlatform(p.value) for p in target_platforms],
            data_ids
        )
        return result
    except Exception as e:
        logger.error(f"Failed to share voice data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def voice_training_health():
    """Health check for voice training API"""
    return {
        "status": "healthy",
        "service": "voice_training_api",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
