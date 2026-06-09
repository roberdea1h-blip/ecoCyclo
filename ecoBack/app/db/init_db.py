import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User


async def init_db(db: AsyncSession) -> None:
    result = await db.execute(select(Role).limit(1))
    if result.scalar_one_or_none() is not None:
        return

    admin_role = Role(id=uuid.uuid4(), name="admin", description="System administrator")
    user_role = Role(id=uuid.uuid4(), name="user", description="Regular user")
    moderator_role = Role(id=uuid.uuid4(), name="moderator", description="Moderator")

    db.add_all([admin_role, user_role, moderator_role])
    await db.flush()

    admin_user = User(
        id=uuid.uuid4(),
        email="admin@ecocycle.app",
        username="admin",
        hashed_password=hash_password("admin123"),
        full_name="System Admin",
        is_active=True,
        is_verified=True,
        role_id=admin_role.id,
    )
    db.add(admin_user)
    await db.flush()
