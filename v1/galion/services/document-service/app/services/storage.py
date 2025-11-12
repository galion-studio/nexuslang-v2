"""
File storage service - handles document upload and retrieval
"""

import os
import uuid
import shutil
import magic
import aiofiles
from pathlib import Path
from typing import Tuple, BinaryIO
from fastapi import UploadFile, HTTPException

# Storage configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/app/uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "10")) * 1024 * 1024  # Convert MB to bytes

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/jpg": ".jpg",
}

class StorageService:
    """Service for handling file storage operations"""
    
    def __init__(self):
        self.upload_dir = Path(UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_file(self, file: UploadFile, user_id: str, document_type: str) -> Tuple[str, str, int]:
        """
        Save uploaded file to disk
        
        Args:
            file: Uploaded file
            user_id: User ID (for organizing storage)
            document_type: Type of document
            
        Returns:
            Tuple of (file_path, mime_type, file_size)
        """
        # Validate file exists
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate file size
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        if file_size == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Detect MIME type
        mime = magic.Magic(mime=True)
        mime_type = mime.from_buffer(content)
        
        # Validate MIME type
        if mime_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type: {mime_type}. Allowed types: {', '.join(ALLOWED_MIME_TYPES.keys())}"
            )
        
        # Generate unique filename
        file_extension = ALLOWED_MIME_TYPES[mime_type]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        
        # Create user directory
        user_dir = self.upload_dir / str(user_id) / document_type
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Full file path
        file_path = user_dir / unique_filename
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(content)
        
        # Return relative path from upload_dir
        relative_path = str(file_path.relative_to(self.upload_dir))
        
        return relative_path, mime_type, file_size
    
    def get_file_path(self, relative_path: str) -> Path:
        """Get absolute file path from relative path"""
        file_path = self.upload_dir / relative_path
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Security check: ensure file is within upload directory
        try:
            file_path.resolve().relative_to(self.upload_dir.resolve())
        except ValueError:
            raise HTTPException(status_code=403, detail="Access denied")
        
        return file_path
    
    def delete_file(self, relative_path: str) -> bool:
        """Delete file from storage"""
        try:
            file_path = self.get_file_path(relative_path)
            file_path.unlink()
            
            # Try to remove empty directories
            try:
                file_path.parent.rmdir()
                file_path.parent.parent.rmdir()
            except OSError:
                pass  # Directory not empty, that's fine
            
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent directory traversal"""
        # Remove path components
        filename = os.path.basename(filename)
        
        # Remove special characters
        allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.")
        filename = ''.join(c for c in filename if c in allowed_chars)
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:250] + ext
        
        return filename or "document"

# Singleton instance
storage_service = StorageService()

