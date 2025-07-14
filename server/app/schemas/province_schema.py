from pydantic import BaseModel
from decimal import Decimal

from app.models import CityTierEnum


class ProvinceBase(BaseModel):
    name_th: str
    name_en: str | None = None
    region: str
    city_tier: CityTierEnum
    tax_reduction_rate: Decimal
    tax_description: str | None = None


class ProvinceCreate(ProvinceBase):
    pass


class ProvinceOut(ProvinceBase):
    id: int

    class Config:
        model_config = {"from_attributes": True}
