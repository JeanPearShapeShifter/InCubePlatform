import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.document import DocumentCreate, DocumentListResponse, DocumentResponse
from app.services import document as document_service

router = APIRouter()


@router.post("/perspectives/{perspective_id}/documents", response_model=DocumentResponse, status_code=201)
async def create_document(
    perspective_id: uuid.UUID,
    data: DocumentCreate,
    # TODO: replace with get_current_user dependency
    user_id: uuid.UUID = Query(...),
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    doc = await document_service.create_document(
        db, perspective_id, user_id, data.filename, data.file_type, data.minio_key, data.file_size
    )
    return DocumentResponse.model_validate(doc)


@router.get("/perspectives/{perspective_id}/documents", response_model=DocumentListResponse)
async def list_documents(
    perspective_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> DocumentListResponse:
    docs = await document_service.list_documents(db, perspective_id)
    return DocumentListResponse(documents=[DocumentResponse.model_validate(d) for d in docs])


@router.delete("/documents/{document_id}", status_code=204)
async def delete_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    await document_service.delete_document(db, document_id)
