"""
Generation API - ComfyUI Integration with Credit Management
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging
import asyncio
from datetime import datetime

from ..services.comfyui.generation_service import GenerationService
from ..services.billing.credit_service import CreditService
from ..core.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/v2/generation", tags=["generation"])

# Initialize services (these would be injected in production)
generation_service = None
credit_service = None

class GenerationRequest(BaseModel):
    workflow_id: str = Field(..., description="ComfyUI workflow ID")
    parameters: Dict[str, Any] = Field(..., description="Generation parameters")
    priority: str = Field("normal", description="Generation priority")
    estimated_credits: int = Field(..., description="Estimated credits for generation")

class GenerationStatus(BaseModel):
    job_id: str
    status: str
    progress: float
    result: Optional[Dict[str, Any]] = None
    credits_used: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

class WorkflowInfo(BaseModel):
    id: str
    name: str
    description: str
    category: str
    estimated_credits: int
    tags: List[str]

class PodStatus(BaseModel):
    pod_id: str
    available: bool
    queue_length: int

@router.post("/image", response_model=Dict[str, str])
async def generate_image(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Generate an image using ComfyUI with credit management"""
    try:
        # Validate user has sufficient credits
        has_credits = await credit_service.check_credit_balance(
            str(current_user.id),
            request.estimated_credits
        )

        if not has_credits:
            raise HTTPException(
                status_code=402,
                detail="Insufficient credits. Please purchase more credits to continue."
            )

        # Start generation job
        job = await generation_service.start_generation({
            user_id: str(current_user.id),
            workflow_id: request.workflow_id,
            parameters: request.parameters,
            priority: request.priority,
            estimated_credits: request.estimated_credits
        })

        # Add background task to monitor completion and deduct credits
        background_tasks.add_task(
            _monitor_generation_completion,
            job.id,
            str(current_user.id)
        )

        return {"job_id": job.id, "message": "Generation started successfully"}

    except Exception as e:
        logging.error(f"Image generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/video", response_model=Dict[str, str])
async def generate_video(
    request: GenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Generate a video using ComfyUI with credit management"""
    try:
        # Validate user has sufficient credits (videos cost more)
        video_cost = request.estimated_credits * 2  # Videos cost 2x images
        has_credits = await credit_service.check_credit_balance(
            str(current_user.id),
            video_cost
        )

        if not has_credits:
            raise HTTPException(
                status_code=402,
                detail="Insufficient credits for video generation. Videos require more credits."
            )

        # Start generation job
        job = await generation_service.start_generation({
            user_id: str(current_user.id),
            workflow_id: request.workflow_id,
            parameters: request.parameters,
            priority: request.priority,
            estimated_credits: video_cost
        })

        # Add background task to monitor completion
        background_tasks.add_task(
            _monitor_generation_completion,
            job.id,
            str(current_user.id)
        )

        return {"job_id": job.id, "message": "Video generation started successfully"}

    except Exception as e:
        logging.error(f"Video generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{job_id}", response_model=GenerationStatus)
async def get_generation_status(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get the status of a generation job"""
    try:
        job = generation_service.get_job_status(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Ensure user can only access their own jobs
        if job.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")

        return GenerationStatus(
            job_id=job.id,
            status=job.status,
            progress=job.progress,
            result=job.result.result if job.result else None,
            credits_used=job.credits_used,
            created_at=job.created_at,
            completed_at=job.completed_at,
            error=job.error
        )

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to get job status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get job status")

@router.delete("/cancel/{job_id}")
async def cancel_generation(
    job_id: str,
    current_user: User = Depends(get_current_user)
):
    """Cancel a generation job and refund credits"""
    try:
        job = generation_service.get_job_status(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # Ensure user can only cancel their own jobs
        if job.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")

        # Can only cancel pending or processing jobs
        if job.status not in ['pending', 'processing']:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot cancel job with status: {job.status}"
            )

        await generation_service.cancel_generation(job_id)

        return {"message": "Generation cancelled successfully", "refunded_credits": job.credits_reserved}

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to cancel generation: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel generation")

@router.get("/workflows", response_model=List[WorkflowInfo])
async def get_workflows(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get available ComfyUI workflows"""
    try:
        workflows = await generation_service.get_available_workflows()

        # Filter by category if specified
        if category:
            workflows = [w for w in workflows if w.category == category]

        return [
            WorkflowInfo(
                id=w.id,
                name=w.name,
                description=w.description,
                category=w.category,
                estimated_credits=w.metadata.estimated_credits,
                tags=w.metadata.tags
            )
            for w in workflows
        ]

    except Exception as e:
        logging.error(f"Failed to get workflows: {e}")
        raise HTTPException(status_code=500, detail="Failed to get workflows")

@router.get("/pods/status", response_model=List[PodStatus])
async def get_pod_status(current_user: User = Depends(get_current_user)):
    """Get GPU pod availability status"""
    try:
        pods = await generation_service.get_pod_availability()
        return pods

    except Exception as e:
        logging.error(f"Failed to get pod status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pod status")

@router.get("/history", response_model=List[GenerationStatus])
async def get_generation_history(
    limit: int = 50,
    offset: int = 0,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get user's generation history"""
    try:
        jobs = generation_service.get_user_jobs(str(current_user.id))

        # Filter by status if specified
        if status:
            jobs = [j for j in jobs if j.status == status]

        # Apply pagination
        jobs = jobs[offset:offset + limit]

        return [
            GenerationStatus(
                job_id=job.id,
                status=job.status,
                progress=job.progress,
                result=job.result.result if job.result else None,
                credits_used=job.credits_used,
                created_at=job.created_at,
                completed_at=job.completed_at,
                error=job.error
            )
            for job in jobs
        ]

    except Exception as e:
        logging.error(f"Failed to get generation history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get generation history")

@router.get("/stats")
async def get_generation_stats(current_user: User = Depends(get_current_user)):
    """Get user's generation statistics"""
    try:
        stats = generation_service.get_job_stats(str(current_user.id))

        return {
            "total_generations": stats.total,
            "successful_generations": stats.completed,
            "failed_generations": stats.failed,
            "in_progress": stats.processing,
            "total_credits_used": stats.total_credits_used,
            "average_processing_time": round(stats.average_processing_time, 2),
            "success_rate": round((stats.completed / max(stats.total, 1)) * 100, 2)
        }

    except Exception as e:
        logging.error(f"Failed to get generation stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get generation stats")

@router.post("/estimate-credits")
async def estimate_credits(
    workflow_id: str,
    parameters: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Estimate credits required for a generation"""
    try:
        estimated_credits = await generation_service.estimate_credits(workflow_id, parameters)

        return {
            "estimated_credits": estimated_credits,
            "workflow_id": workflow_id
        }

    except Exception as e:
        logging.error(f"Failed to estimate credits: {e}")
        raise HTTPException(status_code=500, detail="Failed to estimate credits")

# Background task to monitor generation completion
async def _monitor_generation_completion(job_id: str, user_id: str):
    """Background task to monitor generation completion and handle credit deductions"""
    try:
        max_attempts = 300  # 5 minutes with 1 second polling
        attempts = 0

        while attempts < max_attempts:
            job = generation_service.get_job_status(job_id)
            if not job:
                logging.error(f"Job {job_id} not found during monitoring")
                return

            if job.status in ['completed', 'failed', 'cancelled']:
                break

            await asyncio.sleep(1)
            attempts += 1

        # Final status check
        job = generation_service.get_job_status(job_id)
        if job:
            if job.status == 'completed':
                logging.info(f"Generation {job_id} completed successfully for user {user_id}")
                # Credits already deducted by GenerationService
            elif job.status == 'failed':
                logging.warning(f"Generation {job_id} failed for user {user_id}: {job.error}")
                # Credits already refunded by GenerationService
            elif job.status == 'cancelled':
                logging.info(f"Generation {job_id} cancelled for user {user_id}")
                # Credits already refunded by GenerationService

    except Exception as e:
        logging.error(f"Error monitoring generation {job_id}: {e}")

# Initialize services function (called during app startup)
def init_generation_services(comfyui_client, credit_svc):
    global generation_service, credit_service
    generation_service = GenerationService(comfyui_client, credit_svc)
    credit_service = credit_svc
