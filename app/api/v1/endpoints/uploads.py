from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api import deps
from app.services.uploads import save_upload

router = APIRouter(prefix="/uploads", tags=["Uploads"])


@router.post("/")
async def upload_file(
    file: UploadFile = File(...),
    current_user=Depends(deps.get_current_user),
):
    try:
        url = save_upload(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {"url": url}
