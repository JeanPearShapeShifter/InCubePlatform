import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db, require_role
from app.core.errors import ForbiddenError, NotFoundError
from app.models.organization import Organization
from app.models.user import User
from app.schemas.organization import OrganizationResponse, OrganizationUpdate

router = APIRouter(prefix="/organizations")


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.organization_id != org_id:
        raise ForbiddenError("You can only access your own organization")

    org = await db.get(Organization, org_id)
    if not org:
        raise NotFoundError("Organization not found")
    return OrganizationResponse.model_validate(org)


@router.put("/{org_id}", response_model=OrganizationResponse)
async def update_organization(
    org_id: uuid.UUID,
    data: OrganizationUpdate,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
):
    if current_user.organization_id != org_id:
        raise ForbiddenError("You can only update your own organization")

    org = await db.get(Organization, org_id)
    if not org:
        raise NotFoundError("Organization not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(org, field, value)
    await db.flush()

    return OrganizationResponse.model_validate(org)
