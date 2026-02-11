import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models.document import Document


async def create_document(
    db: AsyncSession,
    perspective_id: uuid.UUID,
    user_id: uuid.UUID,
    filename: str,
    file_type: str,
    minio_key: str,
    file_size: int,
) -> Document:
    doc = Document(
        perspective_id=perspective_id,
        uploaded_by=user_id,
        filename=filename,
        file_type=file_type,
        minio_key=minio_key,
        file_size=file_size,
    )
    db.add(doc)
    await db.flush()
    return doc


async def list_documents(db: AsyncSession, perspective_id: uuid.UUID) -> list[Document]:
    result = await db.execute(
        select(Document).where(Document.perspective_id == perspective_id).order_by(Document.created_at.desc())
    )
    return list(result.scalars().all())


async def delete_document(db: AsyncSession, document_id: uuid.UUID) -> None:
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise NotFoundError("Document not found")
    await db.delete(doc)
    await db.flush()
