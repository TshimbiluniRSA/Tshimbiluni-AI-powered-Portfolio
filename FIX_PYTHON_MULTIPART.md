# Fix: Missing python-multipart Dependency

## Issue
Docker container failed to start with the error:
```
Form data requires "python-multipart" to be installed.
You can install "python-multipart" with:
pip install python-multipart
```

## Root Cause
The CV upload feature in `backend/src/routers/cv.py` uses FastAPI's `UploadFile` and `File` for handling file uploads. These require the `python-multipart` package to parse multipart form data, but this dependency was not included in `requirements.txt`.

## Fix
Added `python-multipart==0.0.9` to `backend/src/requirements.txt`.

## Files Changed
- `backend/src/requirements.txt` - Added python-multipart dependency

## Affected Endpoints
The following endpoints require this dependency:
- `POST /api/cv/upload` - CV file upload endpoint

## Verification
After this fix, the Docker container should:
1. Start successfully without errors
2. Handle file uploads correctly
3. Parse multipart form data properly

## Technical Details
`python-multipart` is a required dependency for FastAPI when using:
- `UploadFile` type hints
- `File()` form parameters
- Any multipart/form-data content type

Without this package, FastAPI/Starlette cannot parse file uploads and the application will crash on startup when it encounters routes that use these features.

## Related Code
```python
# backend/src/routers/cv.py
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

@router.post("/upload")
async def upload_cv(
    file: UploadFile = File(...),  # Requires python-multipart
    session: AsyncSession = Depends(get_async_db)
):
    ...
```

## References
- [FastAPI File Upload Documentation](https://fastapi.tiangolo.com/tutorial/request-files/)
- [python-multipart on PyPI](https://pypi.org/project/python-multipart/)
