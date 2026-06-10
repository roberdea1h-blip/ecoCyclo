import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.role import Role
from app.models.user import User
from app.models.waste_type import WasteType


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

    waste_types = [
        WasteType(id=uuid.uuid4(), name="Plástico", description="Botellas, bolsas, envases y otros plásticos", icon="plastic", points_per_report=10),
        WasteType(id=uuid.uuid4(), name="Vidrio", description="Botellas, frascos y otros artículos de vidrio", icon="glass", points_per_report=15),
        WasteType(id=uuid.uuid4(), name="Papel / Cartón", description="Periódicos, cajas, cartón y papel en general", icon="paper", points_per_report=10),
        WasteType(id=uuid.uuid4(), name="Metal", description="Latas, chatarra y otros metales", icon="metal", points_per_report=20),
        WasteType(id=uuid.uuid4(), name="Residuos orgánicos", description="Restos de comida, jardinería y materia orgánica", icon="organic", points_per_report=8),
        WasteType(id=uuid.uuid4(), name="Electrónicos", description="Aparatos electrónicos y eléctricos en desuso", icon="electronic", points_per_report=25),
        WasteType(id=uuid.uuid4(), name="Residuos peligrosos", description="Pilas, aceites, químicos y materiales peligrosos", icon="hazardous", points_per_report=30),
        WasteType(id=uuid.uuid4(), name="Residuos de construcción", description="Esm tiles, ladrillos, concreto y materiales de obra", icon="construction", points_per_report=20),
        WasteType(id=uuid.uuid4(), name="Neumáticos", description="Llantas y neumáticos fuera de uso", icon="tires", points_per_report=25),
        WasteType(id=uuid.uuid4(), name="Textiles", description="Ropa, telas y productos textiles en desuso", icon="textile", points_per_report=10),
    ]
    db.add_all(waste_types)

    await db.flush()
