from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sqlite import models


async def get_roboflow_status(db: AsyncSession):
    result = await db.execute(select(models.TemporaryModel))

    return result.scalar_one_or_none()


async def flip_roboflow_status(
    db_temporary: models.TemporaryModel,
    db: AsyncSession,
):
    db_temporary.flip_status()

    await db.commit()

    await db.refresh(db_temporary)

    return db_temporary
