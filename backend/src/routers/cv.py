import os
from fastapi import APIRouter, Depends, HTTPException
from schemas import CVDownloadResponse
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
