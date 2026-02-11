import uuid

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.schemas.common import PaginationMeta, ResponseEnvelope
from app.schemas.vdba import VdbaCreate, VdbaDetailResponse, VdbaListItem, VdbaResponse
from app.services import export as export_service
from app.services import vdba as vdba_service
from app.services.minio import download_file, get_minio_client

router = APIRouter()

EXPORT_CONTENT_TYPES = {
    "json": "application/json",
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@router.post("/journeys/{journey_id}/publish", status_code=201)
async def publish_journey(
    journey_id: uuid.UUID,
    body: VdbaCreate,
    current_user: User = Depends(require_role("editor")),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[VdbaResponse]:
    vdba = await vdba_service.publish_journey(
        db, journey_id, current_user.organization_id, body
    )
    # Trigger export generation
    await export_service.generate_export(db, vdba.id)
    return ResponseEnvelope(data=VdbaResponse.model_validate(vdba))


@router.get("/vdbas")
async def list_vdbas(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[list[VdbaListItem]]:
    vdbas, total = await vdba_service.list_vdbas(
        db, current_user.organization_id, page, per_page
    )
    total_pages = (total + per_page - 1) // per_page
    return ResponseEnvelope(
        data=[VdbaListItem.model_validate(v) for v in vdbas],
        meta=PaginationMeta(
            page=page, per_page=per_page, total=total, total_pages=total_pages
        ).model_dump(),
    )


@router.get("/vdbas/{vdba_id}")
async def get_vdba(
    vdba_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ResponseEnvelope[VdbaDetailResponse]:
    vdba = await vdba_service.get_vdba(db, vdba_id, current_user.organization_id)
    return ResponseEnvelope(data=VdbaDetailResponse.model_validate(vdba))


@router.get("/vdbas/{vdba_id}/export")
async def download_export(
    vdba_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    vdba = await vdba_service.get_vdba(db, vdba_id, current_user.organization_id)
    if not vdba.export_url:
        # Generate export on demand if not yet created
        await export_service.generate_export(db, vdba.id)
        # Re-fetch to get updated export_url
        vdba = await vdba_service.get_vdba(db, vdba_id, current_user.organization_id)

    client = get_minio_client()
    file_bytes = await download_file(client, vdba.export_url)
    content_type = EXPORT_CONTENT_TYPES.get(vdba.export_format, "application/octet-stream")
    extension = vdba.export_format or "json"

    import io

    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="vdba-{vdba.id}.{extension}"'
        },
    )
