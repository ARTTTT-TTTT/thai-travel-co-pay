from pydantic import BaseModel
from datetime import date, datetime

from app.schemas.province_schema import ProvinceOut


class UserTravelBase(BaseModel):
    province_id: int
    start_date: date
    end_date: date
    notes: str | None = None


class UserTravelCreate(UserTravelBase):
    pass


class UserTravelUpdate(UserTravelBase):
    pass


class UserTravelOut(UserTravelBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    province: ProvinceOut

    class Config:
        model_config = {"from_attributes": True}
