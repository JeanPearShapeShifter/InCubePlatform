import uuid

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models.document import Document
from app.services.minio import delete_file, download_file, get_minio_client, upload_file


async def create_document(
    db: AsyncSession,
    perspective_id: uuid.UUID,
    user_id: uuid.UUID,
    file: UploadFile,
) -> Document:
    file_data = await file.read()
    content_type = file.content_type or "application/octet-stream"

    client = get_minio_client()
    minio_key = await upload_file(client, file_data, file.filename or "upload", content_type, str(perspective_id))

    doc = Document(
        perspective_id=perspective_id,
        uploaded_by=user_id,
        filename=file.filename or "upload",
        file_type=content_type,
        minio_key=minio_key,
        file_size=len(file_data),
    )
    db.add(doc)
    await db.flush()
    return doc


async def list_documents(db: AsyncSession, perspective_id: uuid.UUID) -> list[Document]:
    result = await db.execute(
        select(Document).where(Document.perspective_id == perspective_id).order_by(Document.created_at.desc())
    )
    return list(result.scalars().all())


async def get_document(db: AsyncSession, document_id: uuid.UUID) -> Document:
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise NotFoundError("Document not found")
    return doc


async def get_document_content(db: AsyncSession, document_id: uuid.UUID) -> tuple[Document, bytes]:
    doc = await get_document(db, document_id)
    client = get_minio_client()
    data = await download_file(client, doc.minio_key)
    return doc, data


async def delete_document(db: AsyncSession, document_id: uuid.UUID) -> None:
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise NotFoundError("Document not found")

    client = get_minio_client()
    await delete_file(client, doc.minio_key)

    await db.delete(doc)
    await db.flush()
