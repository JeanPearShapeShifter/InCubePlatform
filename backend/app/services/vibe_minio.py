"""MinIO helpers for vibe audio file storage."""

import io
import uuid

from miniopy_async import Minio

from app.core.config import settings


def get_minio_client() -> Minio:
    """Create a MinIO client from settings."""
    return Minio(
        settings.minio_endpoint,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=False,
    )


async def ensure_bucket(client: Minio) -> None:
    """Ensure the default bucket exists."""
    if not await client.bucket_exists(settings.minio_bucket):
        await client.make_bucket(settings.minio_bucket)


async def upload_audio(client: Minio, audio_data: bytes, perspective_id: str) -> str:
    """Upload audio to MinIO. Returns the minio object key."""
    key = f"vibes/{perspective_id}/{uuid.uuid4()}.webm"
    await client.put_object(
        settings.minio_bucket,
        key,
        io.BytesIO(audio_data),
        len(audio_data),
        content_type="audio/webm",
    )
    return key


async def download_audio(client: Minio, minio_key: str) -> bytes:
    """Download audio from MinIO."""
    response = await client.get_object(settings.minio_bucket, minio_key)
    data = await response.read()
    await response.close()
    await response.release()
    return data
