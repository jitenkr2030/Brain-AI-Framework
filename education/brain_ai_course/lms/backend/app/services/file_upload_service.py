"""
File Upload Service for Brain AI LMS
Handles file uploads to S3 and local storage
"""

import os
import uuid
import aiofiles
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path
import logging
import magic
from PIL import Image
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "104857600"))  # 100MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp", "image/svg+xml"}
ALLOWED_DOCUMENT_TYPES = {"application/pdf", "text/plain", "application/msword",
                          "application/vnd.openxmlformats-officedocument.wordprocessingml.document"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}
ALLOWED_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_DOCUMENT_TYPES | ALLOWED_VIDEO_TYPES


class FileUploadError(Exception):
    """Custom exception for file upload errors"""
    def __init__(self, message: str, code: str = "UPLOAD_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class FileValidator:
    """Validates uploaded files"""
    
    @staticmethod
    def validate_file_type(mime_type: str) -> bool:
        """Check if file type is allowed"""
        return mime_type in ALLOWED_TYPES
    
    @staticmethod
    def validate_file_size(size: int) -> bool:
        """Check if file size is within limit"""
        return size <= MAX_FILE_SIZE
    
    @staticmethod
    def validate_filename(filename: str) -> bool:
        """Check if filename is safe"""
        # Check for path traversal attempts
        if ".." in filename or "/" in filename or "\\" in filename:
            return False
        # Check for potentially dangerous extensions
        dangerous_extensions = {".exe", ".bat", ".cmd", ".sh", ".php", ".js", ".py", ".html", ".htm"}
        ext = Path(filename).suffix.lower()
        return ext not in dangerous_extensions
    
    @staticmethod
    def get_mime_type(file_content: bytes) -> str:
        """Detect MIME type from file content"""
        mime = magic.Magic(mime=True)
        return mime.from_buffer(file_content)
    
    @staticmethod
    def validate_image_dimensions(image: Image.Image, max_width: int = 4096, max_height: int = 4096) -> bool:
        """Check if image dimensions are within limits"""
        width, height = image.size
        return width <= max_width and height <= max_height


class S3Uploader:
    """Handles uploads to AWS S3"""
    
    def __init__(self):
        import boto3
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", "us-east-1")
        )
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        self.bucket_url = f"https://{self.bucket_name}.s3.{os.getenv('AWS_REGION', 'us-east-1')}.amazonaws.com"
    
    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        mime_type: str,
        folder: str = "uploads"
    ) -> Dict:
        """Upload a file to S3"""
        try:
            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}{Path(filename).suffix}"
            s3_key = f"{folder}/{unique_filename}"
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=mime_type,
                ACL="public-read"
            )
            
            # Return file info
            return {
                "url": f"{self.bucket_url}/{s3_key}",
                "key": s3_key,
                "filename": unique_filename,
                "original_filename": filename,
                "mime_type": mime_type,
                "size": len(file_content)
            }
        except Exception as e:
            logger.error(f"S3 upload error: {e}")
            raise FileUploadError(f"Failed to upload file: {str(e)}", "S3_UPLOAD_ERROR")
    
    async def delete_file(self, s3_key: str) -> bool:
        """Delete a file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            return True
        except Exception as e:
            logger.error(f"S3 delete error: {e}")
            return False


class LocalUploader:
    """Handles uploads to local storage"""
    
    def __init__(self, upload_dir: str = UPLOAD_DIR):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        mime_type: str,
        folder: str = "uploads"
    ) -> Dict:
        """Upload a file to local storage"""
        try:
            # Generate unique filename
            unique_filename = f"{uuid.uuid4()}{Path(filename).suffix}"
            
            # Create folder structure
            folder_path = self.upload_dir / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            
            # Save file
            file_path = folder_path / unique_filename
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
            
            # Return file info
            file_url = f"/uploads/{folder}/{unique_filename}"
            return {
                "url": file_url,
                "path": str(file_path),
                "filename": unique_filename,
                "original_filename": filename,
                "mime_type": mime_type,
                "size": len(file_content)
            }
        except Exception as e:
            logger.error(f"Local upload error: {e}")
            raise FileUploadError(f"Failed to upload file: {str(e)}", "LOCAL_UPLOAD_ERROR")
    
    async def delete_file(self, file_path: str) -> bool:
        """Delete a file from local storage"""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            logger.error(f"Local delete error: {e}")
            return False


class ImageProcessor:
    """Processes uploaded images"""
    
    @staticmethod
    async def process_image(
        file_content: bytes,
        filename: str,
        quality: int = 85,
        max_width: int = 1920
    ) -> Dict:
        """Process and optimize an image"""
        try:
            # Open image
            image = Image.open(io.BytesIO(file_content))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
            
            # Resize if too large
            if image.width > max_width:
                ratio = max_width / image.width
                new_height = int(image.height * ratio)
                image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=quality, optimize=True)
            processed_content = output.getvalue()
            
            # Return processed image info
            return {
                "content": processed_content,
                "mime_type": "image/jpeg",
                "width": image.width,
                "height": image.height
            }
        except Exception as e:
            logger.error(f"Image processing error: {e}")
            raise FileUploadError(f"Failed to process image: {str(e)}", "IMAGE_PROCESSING_ERROR")


class FileUploadService:
    """Main file upload service"""
    
    def __init__(self):
        self.use_s3 = os.getenv("USE_S3", "false").lower() == "true"
        self.validator = FileValidator()
        
        if self.use_s3:
            self.uploader = S3Uploader()
        else:
            self.uploader = LocalUploader()
    
    async def upload_file(
        self,
        file_content: bytes,
        filename: str,
        mime_type: str,
        folder: str = "uploads",
        process_image: bool = False
    ) -> Dict:
        """Upload a file with validation"""
        # Validate file type
        if not self.validator.validate_file_type(mime_type):
            raise FileUploadError(
                f"File type {mime_type} is not allowed",
                "INVALID_FILE_TYPE"
            )
        
        # Validate file size
        if not self.validator.validate_file_size(len(file_content)):
            raise FileUploadError(
                f"File size exceeds maximum limit of {MAX_FILE_SIZE} bytes",
                "FILE_TOO_LARGE"
            )
        
        # Validate filename
        if not self.validator.validate_filename(filename):
            raise FileUploadError(
                "Invalid filename",
                "INVALID_FILENAME"
            )
        
        # Process image if requested
        if process_image and mime_type in ALLOWED_IMAGE_TYPES:
            processed = await ImageProcessor.process_image(file_content, filename)
            file_content = processed["content"]
            mime_type = processed["mime_type"]
        
        # Upload file
        result = await self.uploader.upload_file(
            file_content=file_content,
            filename=filename,
            mime_type=mime_type,
            folder=folder
        )
        
        return result
    
    async def upload_multiple_files(
        self,
        files: List[tuple],
        folder: str = "uploads"
    ) -> List[Dict]:
        """Upload multiple files"""
        results = []
        for file_content, filename, mime_type in files:
            try:
                result = await self.upload_file(file_content, filename, mime_type, folder)
                results.append({**result, "status": "success"})
            except FileUploadError as e:
                results.append({
                    "filename": filename,
                    "status": "error",
                    "error": e.message,
                    "code": e.code
                })
        return results
    
    async def delete_file(self, file_identifier: str) -> bool:
        """Delete a file"""
        if self.use_s3:
            return await self.uploader.delete_file(file_identifier)
        else:
            return await self.uploader.delete_file(file_identifier)


# Get service instance
def get_file_upload_service() -> FileUploadService:
    """Get the file upload service instance"""
    return FileUploadService()
