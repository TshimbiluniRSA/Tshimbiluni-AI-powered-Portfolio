import os
import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import get_async_db
from schemas import CVDownloadResponse
from services.cv_parser import save_cv, get_active_cv, CVParserError
from services.s3_storage import S3Storage, S3StorageError

router = APIRouter(prefix="/cv", tags=["CV"])


def storage():
    return S3Storage()


@router.get("/download", response_model=CVDownloadResponse)
async def download_cv(store: S3Storage = Depends(storage)):
    key = os.getenv("S3_PUBLIC_CV_KEY", "cv/public/tshimbiluni-nedambale-cv.pdf")
    expiry = int(os.getenv("S3_PRESIGNED_URL_EXPIRY_SECONDS", "300"))
    filename = "Tshimbiluni-Nedambale-CV.pdf"
    try:
        if not await store.exists(key):
            raise HTTPException(404, "Portfolio CV is not available")
        return {
            "download_url": await store.presigned_download(key, filename, expiry),
            "expires_in": expiry,
            "filename": filename,
        }
    except HTTPException:
        raise
    except S3StorageError as exc:
        raise HTTPException(503, str(exc)) from None


@router.post("/upload")
async def upload_cv(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_db),
    store: S3Storage = Depends(storage),
):
    if (
        file.content_type != "application/pdf"
        or Path(file.filename or "").suffix.lower() != ".pdf"
    ):
        raise HTTPException(400, "Only PDF files are accepted")
    content = await file.read()
    maximum = int(os.getenv("CV_MAX_UPLOAD_SIZE_MB", "10")) * 1024 * 1024
    if not content:
        raise HTTPException(400, "PDF file is empty")
    if len(content) > maximum:
        raise HTTPException(413, "PDF file exceeds the configured size limit")
    key = None
    temp_path = None
    try:
        key = await store.upload_pdf(content)
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temporary:
            temporary.write(content)
            temp_path = Path(temporary.name)
        record = await save_cv(session, temp_path, file.filename, len(content))
        record.file_path = key
        await session.commit()
        return {
            "success": True,
            "cv_id": record.id,
            "filename": record.filename,
            "parsing_status": record.parsing_status,
        }
    except (S3StorageError, CVParserError):
        raise HTTPException(503, "CV processing is temporarily unavailable") from None
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)
        if key and os.getenv("CV_DELETE_AFTER_PROCESSING", "true").lower() == "true":
            try:
                await store.delete(key)
            except S3StorageError:
                pass


@router.get("/info")
async def info(session: AsyncSession = Depends(get_async_db)):
    cv = await get_active_cv(session)
    if not cv:
        raise HTTPException(404, "No active CV found")
    return {
        "id": cv.id,
        "filename": cv.filename,
        "summary": cv.summary,
        "skills": cv.skills,
        "experience": cv.experience,
        "education": cv.education,
        "parsing_status": cv.parsing_status,
    }
