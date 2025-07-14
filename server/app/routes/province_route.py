from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.session import get_db
from app.schemas.province_schema import ProvinceCreate, ProvinceOut
from app.crud import province_crud
from app.models import CityTierEnum

router = APIRouter(prefix="/provinces", tags=["Provinces"], redirect_slashes=False)


@router.post(
    "/",
    response_model=ProvinceOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_province(
    province_create: ProvinceCreate,
    db: AsyncSession = Depends(get_db),
):
    new_province = await province_crud.create_province(db, province_create)
    return new_province


@router.get("/", response_model=List[ProvinceOut])
async def read_provinces(
    city_tier: CityTierEnum | None = None,
    db: AsyncSession = Depends(get_db),
):
    provinces = await province_crud.get_all_provinces(db, city_tier=city_tier)
    return provinces


@router.get("/{province_id}", response_model=ProvinceOut)
async def read_province(province_id: int, db: AsyncSession = Depends(get_db)):
    province = await province_crud.get_province_by_id(db, province_id)
    if not province:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Province not found")
    return province


@router.get(
    "/secondary",
    response_model=List[ProvinceOut],
)
async def read_secondary_provinces(db: AsyncSession = Depends(get_db)):
    provinces = await province_crud.get_all_provinces(db, city_tier=CityTierEnum.SECONDARY)
    return provinces
