"""
Media Service
Handles media uploads, processing, and storage
"""

from typing import Dict, Optional, BinaryIO
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import aiofiles
import os
from pathlib import Path
from datetime import datetime
import mimetypes

from models.content import MediaAsset


class MediaService:
    """
    Service for managing media assets (images, videos, files)
    Supports local storage and cloud storage (S3, Cloudflare R2)
    """
    
    def __init__(self, db: AsyncSession, storage_config: Optional[Dict] = None):
        self.db = db
        self.storage_config = storage_config or {}
        self.storage_type = self.storage_config.get("type", "local")  # 'local', 's3', 'r2'
        self.local_storage_path = self.storage_config.get("local_path", "./media_storage")
        self.base_url = self.storage_config.get("base_url", "http://localhost:8100/media")
        
        # Ensure local storage directory exists
        if self.storage_type == "local":
            Path(self.local_storage_path).mkdir(parents=True, exist_ok=True)
    
    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        brand_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Upload a file to storage
        
        Args:
            file_content: File bytes
            filename: Original filename
            brand_id: Optional brand association
            user_id: User who uploaded
            metadata: Optional metadata (alt_text, description, etc.)
        
        Returns:
            Dict with file info
        """
        # Generate unique filename
        file_ext = Path(filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        
        # Determine file type
        mime_type, _ = mimetypes.guess_type(filename)
        file_type = self._get_file_type(mime_type)
        
        # Upload based on storage type
        if self.storage_type == "local":
            file_url = await self._upload_local(file_content, unique_filename)
        elif self.storage_type == "s3":
            file_url = await self._upload_s3(file_content, unique_filename, mime_type)
        elif self.storage_type == "r2":
            file_url = await self._upload_r2(file_content, unique_filename, mime_type)
        else:
            raise ValueError(f"Unsupported storage type: {self.storage_type}")
        
        # Create media asset record
        media_asset = MediaAsset(
            brand_id=brand_id,
            filename=unique_filename,
            original_filename=filename,
            file_url=file_url,
            file_type=file_type,
            mime_type=mime_type,
            file_size_bytes=len(file_content),
            alt_text=metadata.get("alt_text") if metadata else None,
            description=metadata.get("description") if metadata else None,
            tags=metadata.get("tags", []) if metadata else [],
            uploaded_by=user_id
        )
        
        self.db.add(media_asset)
        await self.db.commit()
        await self.db.refresh(media_asset)
        
        return {
            "id": str(media_asset.id),
            "filename": unique_filename,
            "original_filename": filename,
            "url": file_url,
            "file_type": file_type,
            "mime_type": mime_type,
            "size_bytes": len(file_content)
        }
    
    async def _upload_local(self, file_content: bytes, filename: str) -> str:
        """Upload file to local storage"""
        file_path = os.path.join(self.local_storage_path, filename)
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        return f"{self.base_url}/{filename}"
    
    async def _upload_s3(self, file_content: bytes, filename: str, mime_type: str) -> str:
        """Upload file to AWS S3"""
        # This would require boto3 and proper configuration
        # Simplified implementation
        try:
            import aioboto3
            
            session = aioboto3.Session()
            async with session.client(
                's3',
                aws_access_key_id=self.storage_config.get("aws_access_key"),
                aws_secret_access_key=self.storage_config.get("aws_secret_key"),
                region_name=self.storage_config.get("aws_region", "us-east-1")
            ) as s3:
                bucket = self.storage_config.get("s3_bucket")
                
                await s3.put_object(
                    Bucket=bucket,
                    Key=filename,
                    Body=file_content,
                    ContentType=mime_type
                )
                
                return f"https://{bucket}.s3.amazonaws.com/{filename}"
        
        except ImportError:
            raise ValueError("aioboto3 not installed for S3 support")
    
    async def _upload_r2(self, file_content: bytes, filename: str, mime_type: str) -> str:
        """Upload file to Cloudflare R2"""
        # R2 is S3-compatible
        try:
            import aioboto3
            
            session = aioboto3.Session()
            async with session.client(
                's3',
                endpoint_url=self.storage_config.get("r2_endpoint"),
                aws_access_key_id=self.storage_config.get("r2_access_key"),
                aws_secret_access_key=self.storage_config.get("r2_secret_key")
            ) as s3:
                bucket = self.storage_config.get("r2_bucket")
                
                await s3.put_object(
                    Bucket=bucket,
                    Key=filename,
                    Body=file_content,
                    ContentType=mime_type
                )
                
                # R2 public URL
                return f"{self.storage_config.get('r2_public_url')}/{filename}"
        
        except ImportError:
            raise ValueError("aioboto3 not installed for R2 support")
    
    async def delete_file(self, media_id: uuid.UUID) -> bool:
        """
        Delete a media file
        
        Args:
            media_id: Media asset ID
        
        Returns:
            True if deleted, False otherwise
        """
        result = await self.db.execute(
            select(MediaAsset).where(MediaAsset.id == media_id)
        )
        media = result.scalar_one_or_none()
        
        if not media:
            return False
        
        # Delete from storage
        if self.storage_type == "local":
            file_path = os.path.join(self.local_storage_path, media.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
        # TODO: Implement S3/R2 deletion
        
        # Delete from database
        await self.db.delete(media)
        await self.db.commit()
        
        return True
    
    async def get_media_by_brand(self, brand_id: uuid.UUID, limit: int = 50) -> list:
        """Get all media assets for a brand"""
        result = await self.db.execute(
            select(MediaAsset)
            .where(MediaAsset.brand_id == brand_id)
            .order_by(MediaAsset.created_at.desc())
            .limit(limit)
        )
        
        return result.scalars().all()
    
    def _get_file_type(self, mime_type: Optional[str]) -> str:
        """Determine file type from MIME type"""
        if not mime_type:
            return "document"
        
        if mime_type.startswith("image/"):
            if mime_type == "image/gif":
                return "gif"
            return "image"
        elif mime_type.startswith("video/"):
            return "video"
        else:
            return "document"

