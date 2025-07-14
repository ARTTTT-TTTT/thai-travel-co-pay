from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database.session import get_db
from app.schemas.user_travel_schema import (
    UserTravelCreate,
    UserTravelUpdate,
    UserTravelOut,
)
from app.crud import user_travel_crud, province_crud
from app.security import get_current_user_with_access_token
from app.models import User

router = APIRouter(prefix="/users/me/travels", tags=["User Travels"])


@router.post(
    "/",
    response_model=UserTravelOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_travel(
    user_travel: UserTravelCreate,
    current_user: User = Depends(get_current_user_with_access_token),
    db: AsyncSession = Depends(get_db),
):
    province = await province_crud.get_province_by_id(db, user_travel.province_id)
    if not province:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Province not found")

    if user_travel.start_date > user_travel.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Start date cannot be after end date"
        )

    travel = await user_travel_crud.create_user_travel(
        db, user_id=current_user.id, user_travel=user_travel  # type: ignore
    )
    return travel


@router.get("/", response_model=List[UserTravelOut])
async def read_travels(
    current_user: User = Depends(get_current_user_with_access_token),
    db: AsyncSession = Depends(get_db),
):
    travels = await user_travel_crud.get_user_travels_by_user_id(
        db, user_id=current_user.id  # type: ignore
    )
    return travels


@router.get("/{id}", response_model=UserTravelOut)
async def read_travel(
    id: int,
    current_user: User = Depends(get_current_user_with_access_token),
    db: AsyncSession = Depends(get_db),
):
    travel = await user_travel_crud.get_user_travel_by_id(db, id=id, user_id=current_user.id)  # type: ignore
    if not travel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Travel not found or not authorized"
        )
    return travel


@router.put("/{id}", response_model=UserTravelOut)
async def update_travel(
    id: int,
    travel_update: UserTravelUpdate,
    current_user: User = Depends(get_current_user_with_access_token),
    db: AsyncSession = Depends(get_db),
):
    if travel_update.province_id:
        province = await province_crud.get_province_by_id(db, travel_update.province_id)
        if not province:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Province not found")

    if (
        travel_update.start_date
        and travel_update.end_date
        and travel_update.start_date > travel_update.end_date
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Start date cannot be after end date"
        )

    travel = await user_travel_crud.update_user_travel(
        db, id=id, user_id=current_user.id, travel_update=travel_update  # type: ignore
    )
    return travel


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_travel(
    id: int,
    current_user: User = Depends(get_current_user_with_access_token),
    db: AsyncSession = Depends(get_db),
):

    await user_travel_crud.delete_user_travel(db, id=id, user_id=current_user.id)  # type: ignore
    return
