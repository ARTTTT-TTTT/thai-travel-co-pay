from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Province, CityTierEnum
from app.schemas.province_schema import ProvinceCreate


async def get_province_by_id(db: AsyncSession, province_id: int) -> Province | None:
    result = await db.execute(select(Province).filter(Province.id == province_id))
    return result.scalars().first()


async def get_province_by_name_th(db: AsyncSession, name_th: str) -> Province | None:
    result = await db.execute(select(Province).filter(Province.name_th == name_th))
    return result.scalars().first()


async def get_all_provinces(
    db: AsyncSession, city_tier: CityTierEnum | None = None
) -> list[Province]:
    query = select(Province)
    if city_tier:
        query = query.filter(Province.city_tier == city_tier)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_province(db: AsyncSession, province: ProvinceCreate) -> Province:
    existing_province = await get_province_by_name_th(db, province.name_th)
    if existing_province:
        raise HTTPException(status_code=409, detail="Province with this Thai name already exists")

    db_province = Province(**province.dict())
    db.add(db_province)
    await db.commit()
    await db.refresh(db_province)
    return db_province
