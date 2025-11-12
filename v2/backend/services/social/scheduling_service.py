"""
Scheduling Service
Handles scheduled post publishing using Redis queue
"""

from typing import Dict, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import uuid
import asyncio
import json

from core.redis_client import get_redis
from models.content import ContentPost, ScheduledJob
from .content_service import ContentService


class SchedulingService:
    """
    Service for scheduling content posts
    Uses Redis for job queue management
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.content_service = ContentService(db)
    
    async def schedule_post(
        self,
        post_id: uuid.UUID,
        scheduled_at: datetime
    ) -> Dict:
        """
        Schedule a post for future publishing
        
        Args:
            post_id: Content post ID
            scheduled_at: When to publish
        
        Returns:
            Dict with job info
        """
        # Create scheduled job
        job = ScheduledJob(
            job_type="post_content",
            entity_type="content_post",
            entity_id=post_id,
            scheduled_for=scheduled_at,
            status="pending",
            payload={"post_id": str(post_id)}
        )
        
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        
        # Add to Redis queue
        redis = await get_redis()
        if redis.is_connected:
            # Calculate delay in seconds
            delay = (scheduled_at - datetime.utcnow()).total_seconds()
            
            # Add job to Redis sorted set (score = unix timestamp)
            await redis.zadd(
                "scheduled_jobs",
                {str(job.id): scheduled_at.timestamp()}
            )
        
        return {
            "job_id": str(job.id),
            "scheduled_for": scheduled_at.isoformat(),
            "status": "scheduled"
        }
    
    async def cancel_scheduled_post(self, job_id: uuid.UUID) -> bool:
        """
        Cancel a scheduled post
        
        Args:
            job_id: Scheduled job ID
        
        Returns:
            True if cancelled, False otherwise
        """
        result = await self.db.execute(
            select(ScheduledJob).where(ScheduledJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job or job.status != "pending":
            return False
        
        # Update job status
        job.status = "cancelled"
        await self.db.commit()
        
        # Remove from Redis queue
        redis = await get_redis()
        if redis.is_connected:
            await redis.zrem("scheduled_jobs", str(job_id))
        
        return True
    
    async def process_due_jobs(self) -> Dict:
        """
        Process all jobs that are due for execution
        This should be called by a background worker
        
        Returns:
            Dict with processing results
        """
        current_time = datetime.utcnow()
        
        # Get all pending jobs that are due
        result = await self.db.execute(
            select(ScheduledJob).where(
                and_(
                    ScheduledJob.status == "pending",
                    ScheduledJob.scheduled_for <= current_time
                )
            )
        )
        due_jobs = result.scalars().all()
        
        processed = {
            "total": len(due_jobs),
            "successful": 0,
            "failed": 0,
            "details": []
        }
        
        for job in due_jobs:
            try:
                # Mark as running
                job.status = "running"
                job.started_at = datetime.utcnow()
                await self.db.commit()
                
                # Execute job based on type
                if job.job_type == "post_content":
                    post_id = uuid.UUID(job.payload.get("post_id"))
                    result = await self.content_service.publish_post(post_id)
                    
                    # Update job
                    job.status = "completed"
                    job.completed_at = datetime.utcnow()
                    job.result = result
                    
                    processed["successful"] += 1
                    processed["details"].append({
                        "job_id": str(job.id),
                        "status": "success",
                        "result": result
                    })
                
                await self.db.commit()
                
                # Remove from Redis
                redis = await get_redis()
                if redis.is_connected:
                    await redis.zrem("scheduled_jobs", str(job.id))
            
            except Exception as e:
                # Mark job as failed
                job.status = "failed"
                job.error_message = str(e)
                job.retry_count += 1
                
                # Retry if under max retries
                if job.retry_count < job.max_retries:
                    job.status = "pending"
                    job.scheduled_for = current_time + timedelta(minutes=5)  # Retry in 5 minutes
                    job.last_retry_at = current_time
                
                await self.db.commit()
                
                processed["failed"] += 1
                processed["details"].append({
                    "job_id": str(job.id),
                    "status": "failed",
                    "error": str(e)
                })
        
        return processed
    
    async def get_upcoming_jobs(self, limit: int = 50) -> list:
        """
        Get upcoming scheduled jobs
        
        Args:
            limit: Maximum number of jobs to return
        
        Returns:
            List of scheduled jobs
        """
        result = await self.db.execute(
            select(ScheduledJob)
            .where(ScheduledJob.status == "pending")
            .order_by(ScheduledJob.scheduled_for)
            .limit(limit)
        )
        
        return result.scalars().all()


async def start_scheduler_worker():
    """
    Background worker that continuously processes scheduled jobs
    This should be run as a separate task
    """
    from core.database import get_db
    
    while True:
        try:
            async for db in get_db():
                scheduler = SchedulingService(db)
                results = await scheduler.process_due_jobs()
                
                if results["total"] > 0:
                    print(f"Processed {results['total']} scheduled jobs: "
                          f"{results['successful']} successful, {results['failed']} failed")
        
        except Exception as e:
            print(f"Scheduler worker error: {e}")
        
        # Check every 30 seconds
        await asyncio.sleep(30)

