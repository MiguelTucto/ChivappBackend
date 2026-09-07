import uuid
from pathlib import Path

from fastapi import UploadFile

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
}


def ensure_upload_dir() -> Path:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    return UPLOAD_DIR


def save_upload(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValueError("Tipo de archivo no permitido. Usa JPG, PNG, WEBP o PDF.")

    extension = Path(file.filename or "file").suffix.lower()
    if not extension:
        extension = ".jpg" if file.content_type.startswith("image/") else ".pdf"

    filename = f"{uuid.uuid4()}{extension}"
    destination = ensure_upload_dir() / filename

    with destination.open("wb") as buffer:
        buffer.write(file.file.read())

    return f"/uploads/{filename}"
