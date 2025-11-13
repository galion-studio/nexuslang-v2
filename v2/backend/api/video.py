"""
Video Generation API Endpoints
Handles text-to-video and image-to-video generation.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional
import base64

from ..services.video.video_service import get_video_service
from ..models.user import User
from ..api.auth import get_current_user, get_optional_user

router = APIRouter()


# Request/Response Models
class VideoGenerationRequest(BaseModel):
    """Video generation request."""
    prompt: str = Field(..., min_length=1, max_length=1000, description="Video description")
    duration: float = Field(4.0, ge=2.0, le=10.0, description="Duration in seconds")
    fps: int = Field(24, ge=16, le=30, description="Frames per second")
    width: int = Field(1280, description="Video width")
    height: int = Field(720, description="Video height")
    model: str = Field("stable-video", description="Model to use")
    style: Optional[str] = Field(None, description="Style preset")


class ImageToVideoRequest(BaseModel):
    """Image-to-video animation request."""
    prompt: Optional[str] = Field(None, description="Motion description")
    duration: float = Field(4.0, ge=2.0, le=10.0, description="Duration in seconds")
    motion_strength: float = Field(0.7, ge=0.1, le=1.0, description="Motion strength")


class VideoGenerationResponse(BaseModel):
    """Video generation response."""
    video_url: str = Field(..., description="Generated video URL")
    model: str = Field(..., description="Model used")
    provider: str = Field(..., description="Provider")
    duration: float = Field(..., description="Duration in seconds")
    resolution: str = Field(..., description="Video resolution")
    status: str = Field(..., description="Generation status")
    credits_used: float = Field(..., description="Credits deducted")
    note: Optional[str] = Field(None, description="Additional notes")


class VideoStatusResponse(BaseModel):
    """Video generation status response."""
    task_id: str
    status: str
    progress: int
    video_url: Optional[str] = None


# Credit costs
VIDEO_CREDIT_COSTS = {
    "text_to_video": 5.0,  # 5 credits per video
    "image_to_video": 3.0,  # 3 credits per animation
}


# Endpoints

@router.post("/generate", response_model=VideoGenerationResponse)
async def generate_video(
    request: VideoGenerationRequest,
    current_user: User = Depends(get_current_user),
    video_service = Depends(get_video_service)
):
    """
    Generate video from text prompt.
    
    Creates a video based on text description using AI models.
    Supports various durations, resolutions, and styles.
    
    **Costs**: 5 credits per video
    """
    # Check user has enough credits
    if current_user.credits < VIDEO_CREDIT_COSTS["text_to_video"]:
        raise HTTPException(
            status_code=402,
            detail="Insufficient credits for video generation"
        )
    
    # Generate video
    try:
        result = await video_service.generate_from_text(
            prompt=request.prompt,
            duration=request.duration,
            fps=request.fps,
            width=request.width,
            height=request.height,
            model=request.model,
            style=request.style
        )
        
        # Deduct credits (would be done in database)
        credits_used = VIDEO_CREDIT_COSTS["text_to_video"]
        
        return VideoGenerationResponse(
            **result,
            credits_used=credits_used
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Video generation failed: {str(e)}"
        )


@router.post("/animate", response_model=VideoGenerationResponse)
async def animate_image(
    image: UploadFile = File(..., description="Image to animate"),
    prompt: Optional[str] = None,
    duration: float = 4.0,
    motion_strength: float = 0.7,
    current_user: User = Depends(get_current_user),
    video_service = Depends(get_video_service)
):
    """
    Animate a static image into a video.
    
    Takes a still image and creates smooth motion/animation.
    Perfect for bringing artwork, photos, or designs to life.
    
    **Costs**: 3 credits per animation
    """
    # Validate file type
    if not image.content_type or not image.content_type.startswith('image/'):
        raise HTTPException(400, "File must be an image")
    
    # Check user has enough credits
    if current_user.credits < VIDEO_CREDIT_COSTS["image_to_video"]:
        raise HTTPException(
            status_code=402,
            detail="Insufficient credits for image animation"
        )
    
    # Read image data
    image_data = await image.read()
    
    if len(image_data) == 0:
        raise HTTPException(400, "Image file is empty")
    
    if len(image_data) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(400, "Image file too large (max 10MB)")
    
    # Animate image
    try:
        result = await video_service.animate_image(
            image_data=image_data,
            prompt=prompt,
            duration=duration,
            motion_strength=motion_strength
        )
        
        # Deduct credits
        credits_used = VIDEO_CREDIT_COSTS["image_to_video"]
        
        return VideoGenerationResponse(
            **result,
            credits_used=credits_used
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Image animation failed: {str(e)}"
        )


@router.get("/status/{task_id}", response_model=VideoStatusResponse)
async def get_video_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    video_service = Depends(get_video_service)
):
    """
    Check status of an async video generation task.
    
    Use this to poll for completion when video generation
    is processed asynchronously.
    """
    try:
        status = await video_service.check_generation_status(task_id)
        return VideoStatusResponse(**status)
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Task not found: {str(e)}"
        )


@router.get("/models")
async def list_video_models(
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    List available video generation models.
    
    Returns information about supported models, their capabilities,
    and pricing.
    """
    return {
        "models": [
            {
                "id": "stable-video",
                "name": "Stable Video Diffusion",
                "provider": "Stability AI",
                "max_duration": 10,
                "resolutions": ["512x512", "768x768", "1024x1024"],
                "features": ["text-to-video", "image-to-video"],
                "cost_credits": 5.0
            },
            {
                "id": "runway-gen2",
                "name": "RunwayML Gen-2",
                "provider": "RunwayML",
                "max_duration": 18,
                "resolutions": ["1280x720", "1920x1080"],
                "features": ["text-to-video", "image-to-video", "style-transfer"],
                "cost_credits": 5.0
            }
        ],
        "total": 2
    }

