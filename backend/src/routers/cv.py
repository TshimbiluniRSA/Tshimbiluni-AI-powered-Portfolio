import logging
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_db
from services.cv_parser import save_cv, get_active_cv, CVParserError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cv", tags=["CV"])

# CV storage directory
CV_STORAGE_DIR = Path("backend/data/cvs")
CV_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
async def upload_cv(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_db)
):
    """
    Upload CV and parse with AI.
    
    - Accepts PDF files only
    - Extracts text content
    - Uses Gemini AI to parse structured data
    - Stores in database
    """
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF files are accepted")
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Validate file size (max 10MB)
    if file_size > 10 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 10MB)")
    
    # Save file
    file_path = CV_STORAGE_DIR / file.filename
    with open(file_path, "wb") as f:
        f.write(content)
    
    try:
        # Save to database and parse with AI
        cv_record = await save_cv(
            session=session,
            file_path=file_path,
            filename=file.filename,
            file_size=file_size
        )
        
        return {
            "success": True,
            "cv_id": cv_record.id,
            "filename": cv_record.filename,
            "parsing_status": cv_record.parsing_status,
            "message": "CV uploaded and parsed successfully" if cv_record.parsing_status == "success" else "CV uploaded but parsing failed"
        }
        
    except CVParserError as e:
        raise HTTPException(500, f"Failed to process CV: {str(e)}")


@router.get("/download")
async def download_cv(session: AsyncSession = Depends(get_async_db)):
    """Download the active CV file."""
    cv = await get_active_cv(session)
    
    if not cv:
        raise HTTPException(404, "No active CV found")
    
    return FileResponse(
        path=cv.file_path,
        filename=cv.filename,
        media_type="application/pdf"
    )


@router.get("/info")
async def get_cv_info(session: AsyncSession = Depends(get_async_db)):
    """Get CV information with parsed data."""
    cv = await get_active_cv(session)
    
    if not cv:
        raise HTTPException(404, "No active CV found")
    
    return {
        "id": cv.id,
        "filename": cv.filename,
        "file_size_bytes": cv.file_size_bytes,
        "summary": cv.summary,
        "skills": cv.skills,
        "experience": cv.experience,
        "education": cv.education,
        "certifications": cv.certifications,
        "languages": cv.languages_spoken,
        "parsing_status": cv.parsing_status,
        "ai_model_used": cv.ai_model_used,
        "uploaded_at": cv.uploaded_at,
        "parsed_at": cv.parsed_at,
        "download_url": "/api/cv/download"
    }
