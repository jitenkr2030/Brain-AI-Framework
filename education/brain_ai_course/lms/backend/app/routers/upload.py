"""
File Upload Router for Brain AI LMS
API endpoints for file uploads
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from typing import Optional, List
from pydantic import BaseModel
import os
import logging

from app.services.file_upload_service import get_file_upload_service, FileUploadService, FileUploadError
from app.utils.password import decode_token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


class UploadResponse(BaseModel):
    """Response model for file upload"""
    url: str
    filename: str
    original_filename: str
    mime_type: str
    size: int


class UploadError(BaseModel):
    """Error response for file upload"""
    error: str
    code: str


def get_current_user_id(token: str = Depends(lambda x: x)):
    """Extract user ID from JWT token"""
    if not token:
        raise HTTPException(status_code=401, detail="Authentication required")
    try:
        payload = decode_token(token)
        return int(payload.get("sub", 0))
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder: str = Form("uploads"),
    process_image: bool = Form(False),
    token: Optional[str] = None
):
    """
    Upload a single file
    
    Args:
        file: The file to upload
        folder: Destination folder (default: "uploads")
        process_image: Whether to optimize images (default: False)
        token: Optional JWT token for authentication
    
    Returns:
        UploadResponse with file details
    """
    try:
        # Read file content
        content = await file.read()
        
        # Get upload service
        service = get_file_upload_service()
        
        # Upload file
        result = await service.upload_file(
            file_content=content,
            filename=file.filename,
            mime_type=file.content_type or "application/octet-stream",
            folder=folder,
            process_image=process_image
        )
        
        logger.info(f"File uploaded successfully: {result['filename']}")
        
        return UploadResponse(
            url=result["url"],
            filename=result["filename"],
            original_filename=result["original_filename"],
            mime_type=result["mime_type"],
            size=result["size"]
        )
    
    except FileUploadError as e:
        logger.error(f"Upload failed: {e.message}")
        raise HTTPException(status_code=400, detail=UploadError(error=e.message, code=e.code))
    
    except Exception as e:
        logger.error(f"Unexpected upload error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/upload/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    token: str = Depends(get_current_user_id)
):
    """
    Upload a user avatar
    
    Args:
        file: The avatar image to upload
        token: JWT token for authentication
    
    Returns:
        UploadResponse with file details
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files are allowed for avatars")
        
        # Read file content
        content = await file.read()
        
        # Validate image size (max 5MB)
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image size must be less than 5MB")
        
        # Get upload service
        service = get_file_upload_service()
        
        # Upload file to avatars folder with image processing
        result = await service.upload_file(
            file_content=content,
            filename=file.filename,
            mime_type=file.content_type,
            folder=f"avatars/user_{token}",
            process_image=True
        )
        
        logger.info(f"Avatar uploaded successfully for user {token}")
        
        return UploadResponse(
            url=result["url"],
            filename=result["filename"],
            original_filename=result["original_filename"],
            mime_type=result["mime_type"],
            size=result["size"]
        )
    
    except FileUploadError as e:
        logger.error(f"Avatar upload failed: {e.message}")
        raise HTTPException(status_code=400, detail=UploadError(error=e.message, code=e.code))
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Unexpected avatar upload error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/upload/course-media")
async def upload_course_media(
    file: UploadFile = File(...),
    course_id: int = Form(...),
    media_type: str = Form(...),  # "thumbnail", "video", "document"
    token: str = Depends(get_current_user_id)
):
    """
    Upload course media (thumbnails, videos, documents)
    
    Args:
        file: The media file to upload
        course_id: The course ID
        media_type: Type of media (thumbnail, video, document)
        token: JWT token for authentication
    
    Returns:
        UploadResponse with file details
    """
    try:
        # Validate media type
        valid_types = ["thumbnail", "video", "document", "attachment"]
        if media_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid media type. Must be one of: {valid_types}")
        
        # Read file content
        content = await file.read()
        
        # Get upload service
        service = get_file_upload_service()
        
        # Determine folder and processing based on media type
        process_image = media_type == "thumbnail"
        max_size = 10 * 1024 * 1024 if media_type == "thumbnail" else 500 * 1024 * 1024  # 10MB for images, 500MB for videos
        
        # Validate file size
        if len(content) > max_size:
            size_limit = f"{max_size // (1024*1024)}MB"
            raise HTTPException(status_code=400, detail=f"File size must be less than {size_limit}")
        
        # Upload file
        result = await service.upload_file(
            file_content=content,
            filename=file.filename,
            mime_type=file.content_type or "application/octet-stream",
            folder=f"courses/{course_id}/{media_type}s",
            process_image=process_image
        )
        
        logger.info(f"Course media uploaded: {media_type} for course {course_id}")
        
        return {
            **UploadResponse(
                url=result["url"],
                filename=result["filename"],
                original_filename=result["original_filename"],
                mime_type=result["mime_type"],
                size=result["size"]
            ).dict(),
            "media_type": media_type,
            "course_id": course_id
        }
    
    except FileUploadError as e:
        logger.error(f"Course media upload failed: {e.message}")
        raise HTTPException(status_code=400, detail=UploadError(error=e.message, code=e.code))
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Unexpected course media upload error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.post("/upload/multiple")
async def upload_multiple_files(
    files: List[UploadFile] = File(...),
    folder: str = Form("uploads"),
    token: Optional[str] = None
):
    """
    Upload multiple files at once
    
    Args:
        files: List of files to upload
        folder: Destination folder (default: "uploads")
        token: Optional JWT token for authentication
    
    Returns:
        List of UploadResponse or error objects
    """
    try:
        service = get_file_upload_service()
        results = []
        
        for file in files:
            try:
                content = await file.read()
                result = await service.upload_file(
                    file_content=content,
                    filename=file.filename,
                    mime_type=file.content_type or "application/octet-stream",
                    folder=folder
                )
                results.append({
                    "filename": file.filename,
                    "status": "success",
                    **UploadResponse(
                        url=result["url"],
                        filename=result["filename"],
                        original_filename=result["original_filename"],
                        mime_type=result["mime_type"],
                        size=result["size"]
                    ).dict()
                })
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "status": "error",
                    "error": str(e)
                })
        
        return {"results": results, "total": len(files), "successful": sum(1 for r in results if r["status"] == "success")}
    
    except Exception as e:
        logger.error(f"Multiple file upload error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.delete("/upload/{filename}")
async def delete_file(
    filename: str,
    folder: str = "uploads",
    token: str = Depends(get_current_user_id)
):
    """
    Delete an uploaded file
    
    Args:
        filename: The filename to delete
        folder: The folder containing the file
        token: JWT token for authentication
    
    Returns:
        Success message
    """
    try:
        service = get_file_upload_service()
        file_path = f"{folder}/{filename}"
        success = await service.delete_file(file_path)
        
        if success:
            logger.info(f"File deleted: {file_path}")
            return {"status": "success", "message": f"File {filename} deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="File not found")
    
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"File deletion error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/upload/presigned-url")
async def get_presigned_upload_url(
    filename: str,
    content_type: str,
    folder: str = "uploads",
    token: str = Depends(get_current_user_id)
):
    """
    Get a presigned URL for direct upload to S3
    
    Args:
        filename: The filename to upload
        content_type: The MIME type of the file
        folder: Destination folder
        token: JWT token for authentication
    
    Returns:
        Presigned URL for upload
    """
    try:
        import boto3
        from botocore.config import Config
        from botocore.exceptions import ClientError
        
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            config=Config(signature_version='s3v4')
        )
        
        bucket_name = os.getenv("S3_BUCKET_NAME")
        unique_filename = f"{folder}/{token}_{filename}"
        
        # Generate presigned URL
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': unique_filename,
                'ContentType': content_type
            },
            ExpiresIn=3600  # 1 hour
        )
        
        return {
            "upload_url": presigned_url,
            "file_key": unique_filename,
            "expires_in": 3600
        }
    
    except ClientError as e:
        logger.error(f"S3 presigned URL error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate upload URL")
    
    except Exception as e:
        logger.error(f"Unexpected presigned URL error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
