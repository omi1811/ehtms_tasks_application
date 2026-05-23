import os
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()

UPLOAD_DIR = "uploads"  # Directory to save uploaded files
ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]  # Allowed photo types
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_media(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    # 1. Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # 2. Read file contents and validate size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 5 MB)")
    
    # 3. Generate unique filename
    ext = os.path.splitext(file.filename)[1]  # Get original file extension
    safe_name = f"{current_user.id}_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}{ext}"

    # 4. Ensure upload directory exists
    user_dir = os.path.join(UPLOAD_DIR, str(current_user.id))
    os.makedirs(user_dir, exist_ok=True)

    # 5. Save the file to disk
    file_path = os.path.join(user_dir, safe_name)
    with open(file_path, "wb") as buffer:
        buffer.write(contents)
    
    # 6. Return the URL or path to the uploaded media
    file_url = f"/{UPLOAD_DIR}/{current_user.id}/{safe_name}"  # Adjust as needed for your static files setup
    return JSONResponse(content={"file_url": file_url,"size_bytes": len(contents),"content_type": file.content_type })
