"""
File ingestion endpoints
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging
import uuid
from pathlib import Path

from app.core.config import settings
from app.services.ingest_service import IngestService
from app.services.progress_service import ProgressService
from app.utils.security import validate_file_type, scan_file_content

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize services
ingest_service = IngestService()
progress_service = ProgressService()

@router.post("/ingest/file")
async def ingest_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_type: Optional[str] = "educational_content",
    metadata: Optional[str] = "{}"  # JSON string
):
    """
    Ingest a file for educational content processing
    """
    try:
        # Validate file
        if not validate_file_type(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed types: {settings.ALLOWED_FILE_TYPES}"
            )
        
        if file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE} bytes"
            )
        
        # Generate unique file ID
        file_id = str(uuid.uuid4())
        
        # Create safe filename
        safe_filename = f"{file_id}_{file.filename}"
        file_path = settings.UPLOAD_DIR / safe_filename
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            
            # Security scan
            if not scan_file_content(content):
                file_path.unlink()  # Delete file
                raise HTTPException(
                    status_code=400,
                    detail="File content validation failed"
                )
            
            buffer.write(content)
        
        logger.info(f"File uploaded: {safe_filename}")
        
        # Start background processing
        progress_id = await progress_service.start_task(
            task_type="file_ingestion",
            metadata={"file_id": file_id, "filename": file.filename}
        )
        
        background_tasks.add_task(
            ingest_service.process_file,
            file_path,
            file_id,
            document_type,
            metadata,
            progress_id
        )
        
        return JSONResponse(
            status_code=202,
            content={
                "file_id": file_id,
                "progress_id": progress_id,
                "message": "File upload successful, processing started",
                "filename": file.filename
            }
        )
        
    except Exception as e:
        logger.error(f"File ingestion failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"File ingestion failed: {str(e)}"
        )

@router.post("/ingest/batch")
async def ingest_batch(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    document_type: Optional[str] = "educational_content"
):
    """
    Ingest multiple files in batch
    """
    try:
        if len(files) > 10:  # Reasonable batch limit
            raise HTTPException(
                status_code=400,
                detail="Batch size too large. Maximum 10 files per batch."
            )
        
        batch_id = str(uuid.uuid4())
        file_results = []
        
        # Start batch progress tracking
        batch_progress_id = await progress_service.start_task(
            task_type="batch_ingestion",
            metadata={"batch_id": batch_id, "file_count": len(files)}
        )
        
        # Process each file
        for file in files:
            try:
                # Validate individual file
                if not validate_file_type(file.filename):
                    file_results.append({
                        "filename": file.filename,
                        "status": "failed",
                        "error": "Unsupported file type"
                    })
                    continue
                
                # Generate file ID and save
                file_id = str(uuid.uuid4())
                safe_filename = f"{file_id}_{file.filename}"
                file_path = settings.UPLOAD_DIR / safe_filename
                
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    if not scan_file_content(content):
                        file_results.append({
                            "filename": file.filename,
                            "status": "failed",
                            "error": "Content validation failed"
                        })
                        continue
                    buffer.write(content)
                
                # Add to background processing
                background_tasks.add_task(
                    ingest_service.process_file,
                    file_path,
                    file_id,
                    document_type,
                    "{}",
                    batch_progress_id
                )
                
                file_results.append({
                    "filename": file.filename,
                    "file_id": file_id,
                    "status": "accepted"
                })
                
            except Exception as e:
                file_results.append({
                    "filename": file.filename,
                    "status": "failed",
                    "error": str(e)
                })
        
        return JSONResponse(
            status_code=202,
            content={
                "batch_id": batch_id,
                "progress_id": batch_progress_id,
                "results": file_results,
                "message": "Batch upload completed, processing started"
            }
        )
        
    except Exception as e:
        logger.error(f"Batch ingestion failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch ingestion failed: {str(e)}"
        )

@router.get("/ingest/status/{progress_id}")
async def get_ingestion_status(progress_id: str):
    """
    Get the status of a file ingestion process
    """
    try:
        status = await progress_service.get_task_status(progress_id)
        
        if not status:
            raise HTTPException(
                status_code=404,
                detail="Progress ID not found"
            )
        
        return status
        
    except Exception as e:
        logger.error(f"Failed to get ingestion status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get ingestion status: {str(e)}"
        )

@router.delete("/ingest/file/{file_id}")
async def delete_ingested_file(file_id: str):
    """
    Delete an ingested file and its processed data
    """
    try:
        success = await ingest_service.delete_file(file_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="File not found or already deleted"
            )
        
        return {"message": f"File {file_id} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to delete file: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )