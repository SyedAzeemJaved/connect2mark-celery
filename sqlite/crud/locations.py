from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from sqlite import models
from sqlite.schemas import LocationCreateOrUpdateClass


def get_all_locations_query():
    return select(models.LocationModel)


async def get_location_by_id(location_id: int, db: AsyncSession):
    return await db.scalar(
        select(models.LocationModel).where(
            models.LocationModel.id == location_id
        )
    )


async def get_location_by_title(location_title: str, db: AsyncSession):
    return await db.scalar(
        select(models.LocationModel).where(
            models.LocationModel.title == location_title
        )
    )


async def get_location_by_bluetooth_address(
    bluetooth_address: str, db: AsyncSession
):
    return await db.scalar(
        select(models.LocationModel).where(
            models.LocationModel.bluetooth_address == bluetooth_address
        )
    )


async def get_location_by_coordinates(coordinates: str, db: AsyncSession):
    return await db.scalar(
        select(models.LocationModel).where(
            models.LocationModel.coordinates == coordinates
        )
    )


async def get_location(
    bluetooth_address: str, coordinates: str, db: AsyncSession
):
    return await db.scalar(
        select(models.LocationModel).where(
            or_(
                models.LocationModel.bluetooth_address == bluetooth_address,
                models.LocationModel.coordinates == coordinates,
            )
        )
    )


async def create_location(
    location: LocationCreateOrUpdateClass, db: AsyncSession
):
    db_location = models.LocationModel(**location.__dict__)

    db.add(db_location)

    await db.commit()

    return db_location


async def update_location(
    location: LocationCreateOrUpdateClass,
    db_location: models.LocationModel,
    db: AsyncSession,
):
    db_location.update(location=location)

    await db.commit()
    await db.refresh(db_location)

    return db_location


async def delete_location(db_location: models.LocationModel, db: AsyncSession):
    await db.delete(db_location)
    await db.commit()
