import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.notification import create_notification


async def notify_vdba_published(
    db: AsyncSession, org_id: uuid.UUID, user_id: uuid.UUID, vdba_title: str
) -> None:
    await create_notification(
        db,
        user_id,
        org_id,
        title="VDBA Published",
        body=f'"{vdba_title}" has been published and is ready for export.',
        link="/vdbas",
    )
