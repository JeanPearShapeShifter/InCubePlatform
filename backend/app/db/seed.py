"""Seed the database with initial admin user and organization."""

import asyncio
import uuid

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import async_session_factory
from app.models.organization import Organization
from app.models.user import User


async def seed() -> None:
    async with async_session_factory() as session:
        # Check if admin user already exists
        result = await session.execute(select(User).where(User.email == "admin@incube.ai"))
        if result.scalar_one_or_none():
            print("Admin user already exists, skipping seed.")
            return

        org_id = uuid.uuid4()
        org = Organization(
            id=org_id,
            name="InCube",
            slug="incube",
            monthly_budget_cents=10000,
        )
        session.add(org)

        user = User(
            id=uuid.uuid4(),
            organization_id=org_id,
            email="admin@incube.ai",
            name="Admin User",
            password_hash=hash_password("Admin1234"),
            role="admin",
        )
        session.add(user)
        await session.commit()
        print("Seeded admin user: admin@incube.ai / Admin1234")


if __name__ == "__main__":
    asyncio.run(seed())
