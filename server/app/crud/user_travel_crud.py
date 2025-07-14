from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


from app.models import UserTravel
from app.schemas.user_travel_schema import UserTravelCreate, UserTravelUpdate


async def create_user_travel(
    db: AsyncSession, user_id: int, user_travel: UserTravelCreate
) -> UserTravel:
    db_travel = UserTravel(
        user_id=user_id,
        province_id=user_travel.province_id,
        start_date=user_travel.start_date,
        end_date=user_travel.end_date,
        notes=user_travel.notes,
    )
    db.add(db_travel)
    await db.commit()
    await db.refresh(db_travel)
    result = await db.execute(
        select(UserTravel)
        .options(selectinload(UserTravel.province))
        .filter(UserTravel.id == db_travel.id)
    )
    db_travel_with_province = result.scalar_one_or_none()

    if not db_travel_with_province:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve created user travel plan with province data after creation.",
        )

    return db_travel_with_province


async def get_user_travel_by_id(db: AsyncSession, id: int, user_id: int) -> UserTravel | None:
    result = await db.execute(
        select(UserTravel)
        .options(selectinload(UserTravel.province))
        .filter(UserTravel.id == id, UserTravel.user_id == user_id)
    )
    return result.scalars().first()


async def get_user_travels_by_user_id(db: AsyncSession, user_id: int) -> list[UserTravel]:
    result = await db.execute(
        select(UserTravel)
        .options(selectinload(UserTravel.province))
        .filter(UserTravel.user_id == user_id)
    )
    return list(result.scalars().all())


async def update_user_travel(
    db: AsyncSession, id: int, user_id: int, travel_update: UserTravelUpdate
) -> UserTravel:
    db_travel = await get_user_travel_by_id(db, id, user_id)
    if not db_travel:
        raise HTTPException(status_code=404, detail="Travel  not found or not authorized")

    for field, value in travel_update.dict(exclude_unset=True).items():
        setattr(db_travel, field, value)

    db.add(db_travel)
    await db.commit()
    await db.refresh(db_travel)
    return db_travel


async def delete_user_travel(db: AsyncSession, id: int, user_id: int):
    db_travel = await get_user_travel_by_id(db, id, user_id)
    if not db_travel:
        raise HTTPException(status_code=404, detail="Travel  not found or not authorized")

    await db.delete(db_travel)
    await db.commit()
    return {"message": "Travel  deleted successfully"}
