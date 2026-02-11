import io
import uuid
from pathlib import PurePosixPath

from miniopy_async import Minio

from app.core.config import settings
from app.core.errors import ValidationError

ALLOWED_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "text/plain",
    "text/markdown",
    "text/csv",
    "image/png",
    "image/jpeg",
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def get_minio_client() -> Minio:
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=False,
    )


async def ensure_bucket(client: Minio) -> None:
    exists = await client.bucket_exists(settings.minio_bucket)
    if not exists:
        await client.make_bucket(settings.minio_bucket)


def _sanitize_filename(filename: str) -> str:
    safe = PurePosixPath(filename).name
    safe = safe.replace(" ", "_")
    # Keep only alphanumeric, dots, hyphens, underscores
    return "".join(c for c in safe if c.isalnum() or c in "._-")


async def upload_file(
    client: Minio,
    file_data: bytes,
    filename: str,
    content_type: str,
    perspective_id: str,
) -> str:
    if len(file_data) > MAX_FILE_SIZE:
        raise ValidationError(f"File exceeds maximum size of {MAX_FILE_SIZE // (1024 * 1024)}MB")
    if len(file_data) == 0:
        raise ValidationError("File is empty")
    if content_type not in ALLOWED_TYPES:
        raise ValidationError(f"File type '{content_type}' is not allowed")

    await ensure_bucket(client)

    safe_name = _sanitize_filename(filename)
    minio_key = f"perspectives/{perspective_id}/{uuid.uuid4()}_{safe_name}"

    data_stream = io.BytesIO(file_data)
    await client.put_object(
        settings.minio_bucket,
        minio_key,
        data_stream,
        length=len(file_data),
        content_type=content_type,
    )
    return minio_key


async def download_file(client: Minio, minio_key: str) -> bytes:
    response = await client.get_object(settings.minio_bucket, minio_key)
    try:
        return await response.read()
    finally:
        response.close()
        await response.release()


async def delete_file(client: Minio, minio_key: str) -> None:
    await client.remove_object(settings.minio_bucket, minio_key)
