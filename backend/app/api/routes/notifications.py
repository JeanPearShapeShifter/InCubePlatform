import math
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import PaginationMeta, ResponseEnvelope
from app.schemas.notification import NotificationCount, NotificationResponse
from app.services import notification as notification_service

router = APIRouter(prefix="/notifications")


@router.get("", response_model=ResponseEnvelope[list[NotificationResponse]])
async def list_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    notifications, total = await notification_service.list_notifications(db, current_user.id, page, per_page)
    total_pages = math.ceil(total / per_page) if total else 0
    return ResponseEnvelope(
        data=[NotificationResponse.model_validate(n) for n in notifications],
        meta=PaginationMeta(page=page, per_page=per_page, total=total, total_pages=total_pages).model_dump(),
    )


@router.get("/unread-count", response_model=ResponseEnvelope[NotificationCount])
async def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count = await notification_service.get_unread_count(db, current_user.id)
    return ResponseEnvelope(data=NotificationCount(unread=count))


@router.put("/{notification_id}/read", response_model=ResponseEnvelope[NotificationResponse])
async def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    notification = await notification_service.mark_read(db, notification_id, current_user.id)
    return ResponseEnvelope(data=NotificationResponse.model_validate(notification))


@router.put("/read-all")
async def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    count = await notification_service.mark_all_read(db, current_user.id)
    return ResponseEnvelope(data={"marked_read": count})
