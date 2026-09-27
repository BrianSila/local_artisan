import uuid
from pathlib import Path
from flask import current_app
from PIL import Image, UnidentifiedImageError
from werkzeug.datastructures import FileStorage
from .errors import APIError

ALLOWED_FORMATS = {
    "png": "PNG",
    "jpg": "JPEG",
    "jpeg": "JPEG",
    "gif": "GIF",
    "webp": "WEBP",
}

def allowed_file(filename: str) -> bool:
    extension = Path(filename).suffix.lower().lstrip(".")
    return extension in ALLOWED_FORMATS


def save_image(file: FileStorage | None) -> str:
    """Validate and save an image; return its path relative to Flask's static folder."""
    if not file or not file.filename:
        raise APIError("Empty file", status_code=400)
    if not allowed_file(file.filename):
        raise APIError(f"Unsupported file type: {file.filename}", status_code=400)

    extension = Path(file.filename).suffix.lower().lstrip(".")
    try:
        with Image.open(file.stream) as image:
            image_format = image.format
            image.verify()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        raise APIError("Uploaded file is not a valid image", status_code=400) from None

    if image_format != ALLOWED_FORMATS[extension]:
        raise APIError("Image content does not match its file extension", status_code=400)

    file.stream.seek(0)
    static_dir = Path(current_app.static_folder).resolve()
    upload_dir = Path(current_app.config["UPLOAD_FOLDER"]).resolve()
    try:
        relative_dir = upload_dir.relative_to(static_dir)
    except ValueError:
        raise RuntimeError("UPLOAD_FOLDER must be inside Flask's static folder") from None

    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}.{extension}"
    file.save(upload_dir / filename)
    return (relative_dir / filename).as_posix()


def delete_image(relative_path: str) -> None:
    """Remove a file from disk; ignore if missing."""
    if not relative_path:
        return
    static_dir = Path(current_app.static_folder).resolve()
    full_path = (static_dir / relative_path).resolve()
    if static_dir not in full_path.parents:
        raise APIError("Invalid image path", status_code=400)
    try:
        full_path.unlink()
    except FileNotFoundError:
        pass